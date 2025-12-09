FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    g++ \
    make \
    && rm -rf /var/lib/apt/lists/*

# 复制项目文件
COPY . .

# 安装Python依赖
RUN pip install --no-cache-dir fastapi==0.104.1 uvicorn==0.24.0 python-multipart==0.0.6 pydantic==2.5.0

# 编译LinearDesign程序
RUN make

# 验证编译结果
RUN ls -la bin/ && test -f bin/LinearDesign_2D

# 验证依赖文件存在
RUN test -f codon_usage_freq_table_human.csv && \
    test -f codon_usage_freq_table_yeast.csv && \
    test -f coding_wheel.txt

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]