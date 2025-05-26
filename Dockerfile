FROM python:3.11-slim
# 将本地缓存好的模型复制到容器中
COPY Resource/models/official_models /root/.paddlex/official_models

# 本地的 fonts 目录，将字体文件复制到容器中
COPY Resource/fonts/PingFang-SC-Regular.ttf /usr/local/lib/python3.11/site-packages/paddlex/utils/fonts/
COPY Resource/fonts/simfang.ttf /usr/local/lib/python3.11/site-packages/paddlex/utils/fonts/

# 安装构建 numpy / scipy / paddlex 等库所需的依赖
# 替换 apt 源为阿里云（适用于 debian-slim）
RUN echo "deb http://mirrors.aliyun.com/debian bullseye main contrib non-free\n\
deb http://mirrors.aliyun.com/debian bullseye-updates main contrib non-free\n\
deb http://mirrors.aliyun.com/debian-security bullseye-security main contrib non-free" \
> /etc/apt/sources.list && \
    apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gfortran \
    libopenblas-dev \
    liblapack-dev \
    libgl1 \
    libglib2.0-0 \
    libxml2-dev \
    libxslt1-dev \
    libffi-dev \
    ffmpeg \
    python3-dev \
    gcc \
    binutils \
    patchelf \
    curl \
    git \
    && apt-get clean && rm -rf /var/lib/apt/lists/*




# 设置工作目录
WORKDIR /app

# 复制项目文件
COPY . .

# 升级 pip 和构建工具
RUN pip install --upgrade pip setuptools wheel -i https://mirrors.aliyun.com/pypi/simple/ --timeout 100

# 安装依赖
RUN pip install --no-cache-dir -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/

# 设置默认端口和环境变量
EXPOSE 5600
ENV FLASK_APP=run.py
ENV FLASK_RUN_HOST=0.0.0.0

CMD ["python", "run.py"]

