# services/image_service.py (业务逻辑层)
import os
import uuid
from pathlib import Path

import numpy as np
from flask import url_for, current_app
from paddlex import create_pipeline
from itertools import tee
import cv2


class ImageService:
    def __init__(self):
        """初始化图像服务类"""
        self.ocr_pipeline = None
        self.table_pipeline = None
        self.seal_pipeline = None
        self.doc_pipeline = None
        # self.default_device = 'gpu:0'  # 可配置化设备参数
        self.default_device = 'cpu'  # 可配置化设备参数

    def _generate_session_id(self):
        """生成唯一的会话ID"""
        return str(uuid.uuid4())

    def _create_output_directory(self, type_: str):
        """根据类型在OUTPUT_FOLDER下创建一个会话文件夹"""
        session_id = self._generate_session_id()
        output_dir = os.path.join(current_app.config['OUTPUT_FOLDER'], type_, session_id)

        # 确保目标目录存在
        Path(output_dir).mkdir(parents=True, exist_ok=True)

        return output_dir, session_id

    def _initialize_ocr_model(self):
        """初始化OCR模型管道"""
        try:
            self.ocr_pipeline = create_pipeline(
                pipeline="OCR",
                device=self.default_device
            )
        except Exception as e:
            raise RuntimeError(f"OCR模型加载失败: {str(e)}")

    def _initialize_table_model(self):
        """初始化表格识别模型管道"""
        try:
            self.table_pipeline = create_pipeline(
                pipeline="table_recognition",
                device=self.default_device
            )
        except Exception as e:
            raise RuntimeError(f"表格识别模型加载失败: {str(e)}")

    def _initialize_seal_model(self):
        """初始化表格识别模型管道"""
        try:
            self.seal_pipeline = create_pipeline(
                pipeline="seal_recognition",
                device=self.default_device
            )
        except Exception as e:
            raise RuntimeError(f"印章识别模型加载失败: {str(e)}")

    def _initialize_doc_preprocessor_model(self):
        """初始化表格识别模型管道"""
        try:
            self.doc_pipeline = create_pipeline(
                pipeline="doc_preprocessor",
                device=self.default_device
            )
        except Exception as e:
            raise RuntimeError(f"文档矫正模型加载失败: {str(e)}")

    def _get_file_paths(self, file_id, output_type='ocr'):
        """动态生成路径，支持目录型输出"""
        output_config = {
            'ocr': {
                'outputs': {
                    'image_dir': {'type': 'dir'},
                }
            },
            'table': {
                'outputs': {
                    'image_dir': {'type': 'dir'},
                    'data_dir': {'type': 'dir'}
                }
            },
            'doc': {
                'outputs': {
                    'image': {'type': 'file', 'ext': 'png'},  # 目录类型
                }
            },
            'seal': {
                'outputs': {
                    'image': {'type': 'file', 'ext': 'png'},  # 目录类型
                }
            }
        }

        # 生成唯一会话ID
        session_id = uuid.uuid4().hex[:8]
        base_dir = os.path.join(
            current_app.config['OUTPUT_FOLDER'],
            output_type,
            session_id
        )
        os.makedirs(base_dir, exist_ok=True)

        paths = {
            'input': os.path.join(current_app.config['UPLOAD_FOLDER'], file_id),
            'session_id': session_id
        }

        # 动态构建输出路径
        for key, config in output_config.get(output_type, {}).get('outputs', {}).items():
            if config['type'] == 'dir':
                paths[key] = os.path.join(base_dir, key)  # 生成子目录路径
                os.makedirs(paths[key], exist_ok=True)
            elif config['type'] == 'file':
                paths[key] = os.path.join(base_dir, f"result_{uuid.uuid4().hex[:8]}.{config['ext']}")
        # print(paths)
        return paths

    def process_ocr(self, paths):
        """
        完整的OCR处理流程，处理多个文件路径。
        :param paths: 一个包含多个文件路径的列表
        :return: 包含每个文件OCR结果的字典列表
        """
        if not self.ocr_pipeline:
            self._initialize_ocr_model()

        all_results = []

        try:
            # 创建 OCR 总输出文件夹
            output_dir, session_id = self._create_output_directory('ocr')

            for idx, file_path in enumerate(paths):
                # 单独为每个文件创建子文件夹
                image_subdir = os.path.join(output_dir, f'file_{idx}')
                os.makedirs(image_subdir, exist_ok=True)

                # 执行OCR识别
                output = self.ocr_pipeline.predict(
                    input=file_path,
                    use_doc_orientation_classify=False,
                    use_doc_unwarping=False,
                    use_textline_orientation=False
                )

                # 复制生成器
                img_saver, text_extractor = tee(output)

                # 保存图像到该文件专属文件夹
                for res in img_saver:
                    res.save_to_img(save_path=image_subdir)

                # 提取文本
                results = list(text_extractor)[0]

                # 构建图像 URL 列表
                image_urls = [
                    url_for(
                        'image.get_ocr_output',
                        filename=f'file_{idx}/{filename}',  # 注意添加子路径
                        session_id=session_id,
                        _external=True
                    )
                    for filename in os.listdir(image_subdir)
                ]

                # 封装结果
                all_results.append({
                    "text": "\n".join(results['rec_texts']),
                    "image_urls": image_urls
                })

            return all_results

        except Exception as e:
            raise RuntimeError(f"OCR识别失败: {str(e)}")

    def process_table_recognise(self, paths):
        """表格识别处理多个文件，结构与 OCR 保持一致"""
        if not self.table_pipeline:
            self._initialize_table_model()

        all_results = []

        try:
            # 创建总输出目录（session_id + 路径）
            output_dir, session_id = self._create_output_directory('table')

            for idx, file_path in enumerate(paths):
                # 每个文件一个子目录
                sub_output_dir = os.path.join(output_dir, f'file_{idx}')
                image_dir = os.path.join(sub_output_dir, 'images')
                data_dir = os.path.join(sub_output_dir, 'data')
                os.makedirs(image_dir, exist_ok=True)
                os.makedirs(data_dir, exist_ok=True)

                # 执行表格识别
                output = self.table_pipeline.predict(
                    input=file_path,
                    use_doc_orientation_classify=False,
                    use_doc_unwarping=False,
                )

                # 拷贝生成器
                output_copy1, output_copy2 = tee(output)

                # 保存图像 & xlsx
                for res in output_copy1:
                    res.save_to_img(image_dir)
                    res.save_to_xlsx(data_dir)

                # 构建图像 URL
                image_urls = [
                    url_for('image.get_table_output',
                            filename=f'file_{idx}/images/{filename}',
                            session_id=session_id,
                            _external=True)
                    for filename in os.listdir(image_dir) if filename.endswith('.png')
                ]

                # 构建数据下载 URL
                downloads = [
                    {
                        "name": filename,
                        "url": url_for('image.get_table_data',
                                       filename=f'file_{idx}/data/{filename}',
                                       session_id=session_id,
                                       _external=True),
                        "type": "excel" if filename.endswith('.xlsx') else "other"
                    }
                    for filename in os.listdir(data_dir)
                    if os.path.isfile(os.path.join(data_dir, filename))
                ]

                # 汇总结果
                all_results.append({
                    "image_urls": image_urls,
                    "download_url": downloads
                })

            return all_results

        except Exception as e:
            raise RuntimeError(f"表格识别失败: {str(e)}")

    def process_seal_recognise(self, paths):
        if not self.seal_pipeline:
            self._initialize_seal_model()

        output_dir, session_id = self._create_output_directory('seal')
        all_results = []

        for idx, input_path in enumerate(paths):
            subdir = os.path.join(output_dir, f'file_{idx}')
            os.makedirs(subdir, exist_ok=True)

            output = self.seal_pipeline.predict(
                input_path,
                use_doc_orientation_classify=False,
                use_doc_unwarping=False,
            )

            o1, o2 = tee(output)
            text_results = list(o1)[0]['seal_res_list'][0]['rec_texts']
            output_img = list(o2)[0]['doc_preprocessor_res']['output_img']

            image_path = os.path.join(subdir, 'result.png')
            cv2.imwrite(image_path, output_img)

            all_results.append({
                "text": "\n".join(text_results),
                "image_urls": [
                    url_for(
                        'image.get_seal_output',
                        filename=f"file_{idx}/result.png",
                        session_id=session_id,
                        _external=True
                    )
                ]
            })

        return all_results

    def process_doc(self, paths):
        if not self.doc_pipeline:
            self._initialize_doc_preprocessor_model()

        output_dir, session_id = self._create_output_directory('doc')
        all_results = []

        for idx, input_path in enumerate(paths):
            subdir = os.path.join(output_dir, f'file_{idx}')
            os.makedirs(subdir, exist_ok=True)

            output = self.doc_pipeline.predict(
                input=input_path,
                use_doc_orientation_classify=False,
                use_doc_unwarping=True,
            )

            output_img = list(output)[0]['output_img']
            if output_img.dtype != np.uint8:
                output_img = output_img.astype(np.uint8)

            image_path = os.path.join(subdir, 'result.png')
            cv2.imwrite(image_path, output_img)

            all_results.append({
                "image_urls": [
                    url_for(
                        'image.get_correct_output',
                        filename=f"file_{idx}/result.png",
                        session_id=session_id,
                        _external=True
                    )
                ]
            })

        return all_results
