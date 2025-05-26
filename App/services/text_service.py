import os
from pathlib import Path
from typing import Dict, List, Optional
import PyPDF2
from docx import Document
from openai import OpenAI
from flask import current_app


class TextService:
    def __init__(self):
        """初始化文本服务类"""
        self.api_key = "sk-5ee6f8fa40224f1f97de2f5afaf145d8"
        self.base_url = "https://api.deepseek.com"
        # 专业合同版本比对提示词
        self.prompt_templates = {
            "contract_version_diff": {
                "system": "你是一位资深合同审计专家，专门分析合同版本更新内容。请仔细比对以下两个合同版本，聚焦实质性条款变化。",
                "user": """【任务说明】
                    请对比分析以下合同新版本（文档2）相对于旧版本（文档1）的关键修改内容，需特别注意：
                    1. 仅关注具有法律或商业实质的条款变化
                    2. 忽略格式调整、标点修正等非实质性修改
                    3. 对修改条款按商业影响分级（重大/一般/微小）

                    【合同内容】
                    -----旧版本-----
                    {text1}
                    -----新版本-----
                    {text2}

                    【输出要求】
                    用中文按以下框架输出分析报告：
                    ### 一、核心条款变更
                    1. **合同标的变更**
                       - 旧版：[...]
                       - 新版：[...]
                       - 影响等级：[√重大/○一般/△微小]

                    2. **付款条件变更**
                       - (同上结构)

                    3. **违约责任变更**
                       - (同上结构)

                    ### 二、风险提示
                    1. 对甲方的风险：[...]
                    2. 对乙方的风险：[...]

                    ### 三、修改建议
                    1. 建议接受的改进：[...]
                    2. 建议协商的条款：[...]
                    3. 需法律复核的条款：[...]"""
            },
            "contract_key_info_extractor": {
                "system": "你是一位资深合同分析师，擅长从复杂合同中精准提取核心条款和签约方完整信息。请严格按模板要求提取数据。",
                "user": """【任务说明】
                    请从以下合同文本中提取关键信息，特别注意：
                    1. 必须完整提取双方主体信息（含银行账户等关键数据）
                    2. 空白字段用【/】表示未找到
                    3. 对模糊信息标注【待确认】

                    【合同文本】
                    {text}

                    【输出要求】
                    按以下框架用中文输出报告：

                    ### 一、基础信息
                    1. **合同名称**：[...]
                    2. **签署日期**：[...]
                    3. **合同有效期**：[...]

                    ### 二、签约方信息
                    #### 甲方：
                    - 全称：【】
                    - 法定代表人：【】
                    - 地址：【】
                    - 联系人：【】
                    - 邮编：【】
                    - 电话：【】
                    - 传真：【/】
                    - 电子邮箱：【】 
                    - 纳税人识别号：【】 
                    - 银行账户：
                      - 开户名：【】
                      - 开户行：【】
                      - 账号：【】

                    #### 乙方：
                    - 全称：【】
                    - 法定代表人：【】
                    - 地址：【】
                    - 联系人：【】
                    - 邮编：【】
                    - 电话：【】
                    - 传真：【/】
                    - 电子邮箱：【】 
                    - 纳税人识别号：【】 
                    - 银行账户：
                      - 开户名：【】
                      - 开户行：【】
                      - 账号：【】

                    ### 三、核心条款
                    1. **合同标的**：
                       - 内容描述：[...]
                       - 数量/规格：[...]
                       - 交付标准：[...]

                    2. **价款条款**：
                       - 总金额：[...]
                       - 支付方式：[...]
                       - 结算周期：[...]

                    3. **履行条款**：
                       - 关键时间节点：[...]
                       - 验收标准：[...]
                       - 质量保证：[...]

                    4. **违约责任**：
                       - 违约金比例：[...]
                       - 解约条件：[...]
                       - 赔偿上限：[...]

                    ### 四、特别提示
                    1. **信息缺失项**：[...]
                    2. **矛盾信息项**：[...]
                    3. **异常条款**：[...]

                    ### 五、验证建议
                    1. 需人工复核字段：[...]
                    2. 建议补充材料：[...]"""
            }
        }

    def _extract_text(self, file_path: str) -> Optional[str]:
        """通用文本提取方法"""
        # 确保 file_path 是 Path 对象
        file_path = Path(file_path)

        if not file_path.exists():
            print(f"文件不存在: {file_path}")
            return None

        try:
            if file_path.suffix.lower() == '.pdf':
                with open(file_path, 'rb') as f:
                    reader = PyPDF2.PdfReader(f)
                    return "\n".join([page.extract_text() for page in reader.pages])
            elif file_path.suffix.lower() == '.docx':
                doc = Document(file_path)
                return "\n".join([para.text for para in doc.paragraphs])
            else:
                with open(file_path, 'r', encoding='utf-8') as f:
                    return f.read()
        except Exception as e:
            print(f"文本提取失败 {file_path}: {str(e)}")
            return None

    def compare_documents(
            self,
            paths: List[str],
            prompt_type: str = "contract_version_diff",
            max_tokens: int = 2000
    ) -> Dict:
        """
        专业文档比对（使用大模型）
        :param file_ids: 需要比对的文件ID列表(支持2个文件)
        :param prompt_type: 使用的提示词模板
        :param max_tokens: 最大返回token数
        :return: 结构化比对结果
        """
        if len(paths) != 2:
            return {"error": "目前仅支持两个文件的比对"}
        # 1. 提取文本内容
        texts = []
        for file_path in paths:
            text = self._extract_text(file_path)
            if not text:
                return {"error": f"无法提取文件的内容"}
            texts.append(text[:10000])  # 限制文本长度

        template = self.prompt_templates[prompt_type]

        # 3. 调用大模型API
        try:
            client = OpenAI(api_key=self.api_key, base_url=self.base_url)
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": template["system"]},
                    {
                        "role": "user",
                        "content": template["user"].format(text1=texts[0], text2=texts[1])
                    }
                ],
                temperature=0.3,
                max_tokens=max_tokens,
                stream=False
            )
            all_result = []
            all_result.append({"analysis": response.choices[0].message.content})
            return all_result

        except Exception as e:
            print(f"文档比对失败: {str(e)}")
            return {"error": f"文档比对服务暂时不可用: {str(e)}"}

    def extract_contract_info(
            self,
            paths: List[str],
            prompt_type: str = "contract_key_info_extractor",
            max_tokens: int = 2000
    ) -> Dict:
        """
        合同核心信息提取（使用大模型），支持处理多个文件
        :param paths: 需要分析的多个文件路径
        :param prompt_type: 使用的提示词模板
        :param max_tokens: LLM返回最大token数
        :return: 每个文件的提取结果列表
        """
        results = []

        # 模板准备
        template = self.prompt_templates.get(prompt_type)
        if not template:
            return {"error": f"未找到提示词模板: {prompt_type}"}

        # 初始化大模型客户端
        client = OpenAI(api_key=self.api_key, base_url=self.base_url)

        for path in paths:
            try:
                # 1. 文本提取与预处理
                text = self._extract_text(path)
                processed_text = text[:10000].replace('\x0c', '').strip()

                # 2. 调用大模型 API
                response = client.chat.completions.create(
                    model="deepseek-chat",
                    messages=[
                        {"role": "system", "content": template["system"]},
                        {
                            "role": "user",
                            "content": template["user"].format(text=processed_text)
                        }
                    ],
                    temperature=0.2,
                    max_tokens=max_tokens,
                    stream=False
                )

                raw_content = response.choices[0].message.content

                # 3. 添加结果
                results.append({
                    "analysis": raw_content,
                })

            except Exception as e:
                print(f"[合同解析失败] 文件: {path}, 错误: {str(e)}")
                results.append({
                    "file_path": path,
                    "status": "failed",
                    "error": f"合同解析失败: {str(e)}"
                })

        return results
