# PaddleX-backend

## Flask后端项目说明文档

---

## 项目概述

基于 **Flask** 框架构建的多模态处理后端系统，集成语音、图像、文本、视频处理功能，采用模块化设计支持 OCR、印章识别、表格解析等 AI 能力。

**技术栈**：

- **核心框架**：Flask  
- **AI引擎**：PaddleX（模型目录）、Vosk（语音模型）  
- **部署支持**：Docker  
- **依赖管理**：venv 虚拟环境  

---

## 目录结构说明

```plaintext
paddlex/
├── .venv/                     # Python虚拟环境目录
├── App/                       # 核心应用模块
├── models/                    # 模型存储
│   └── vosk-model-cn-0.22     # 中文语音识别模型
├── outputs/                   # 处理结果输出
│   ├── doc/                   # 文档类输出
│   ├── ocr/                   # OCR识别结果
│   ├── seal/                  # 印章识别结果
│   └── table/                 # 表格解析结果
├── routes/                    # API路由定义
│   ├── audioInterface.py      # 音频接口
│   ├── imageInterface.py      # 图像接口
│   ├── text_interface.py      # 文本接口
│   └── video_interface.py     # 视频接口
├── services/                  # 业务逻辑层
│   ├── audio_service.py       # 音频处理服务
│   ├── image_service.py       # 图像处理服务
│   ├── text_service.py        # 文本处理服务
│   └── video_service.py       # 视频处理服务
├── uploadedFiles/             # 上传文件存储
├── config.py                  # 应用配置
├── utils.py                   # 工具函数
├── logs/                      # 系统日志目录
├── Resource/                  # 静态资源文件
├── Dockerfile                 # Docker容器化配置
├── requirements.txt           # Python依赖清单
└── run.py                     # 应用启动入口
````

---

## 核心模块说明

### 路由层（routes/）

* **接口规范**：遵循 RESTful 设计原则
* **功能划分**：

  * `*Interface.py` 文件处理对应类型的 HTTP 请求
  * 实现请求参数校验、响应格式封装
  * 调用 services 层进行业务处理

### 服务层（services/）

* 业务逻辑核心实现
* 集成 AI 模型调用（语音识别、图像处理等）
* 包含异常处理和数据转换逻辑

---

## 文件管理

* `uploadedFiles/`：临时存储上传文件，**建议配合定期清理机制**
* `outputs/`：结构化存储处理结果，按类型分目录管理

---

## 部署指南

### 本地运行

```bash
# 安装依赖
pip install -r requirements.txt

# 启动应用
python run.py --port 5000 --debug
```

### Docker部署

```bash
# 构建镜像
docker build -t paddlex-api .

# 运行容器
docker run -p 5000:5000 paddlex-api
```

---

## 附加信息

### 依赖管理

* 虚拟环境：`.venv` 使用 `python -m venv` 创建
* 依赖冻结：`pip freeze > requirements.txt`

### 日志系统

* **日志路径**：`App/logs/`
* **建议配置**：

  * 按日期滚动记录
  * 区分访问日志与错误日志

    
> 本文档旨在为 PaddleX-backend 项目提供快速了解与部署指南，您可以根据实际情况进行扩展与优化。

