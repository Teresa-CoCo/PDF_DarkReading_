# 使用官方Python运行时作为父镜像
FROM python:3.8-slim

# 设置工作目录为/app
WORKDIR /app

# 将当前目录内容复制到位于/app中的容器中
COPY . /app

# 安装requirements.txt中的所有依赖
# 如果你的项目中有这个文件，请取消下一行的注释并确保requirements.txt在你的项目目录中
# RUN pip install --no-cache-dir -r requirements.txt

# 安装pdf2image, Pillow, numpy等依赖
RUN pip install --no-cache-dir pdf2image Pillow numpy
RUN apt update
RUN apt-get install poppler-utils -y

# 运行HTTP服务器时的端口
EXPOSE 8000

# 运行http服务器
CMD ["python", "./app.py"]
