FROM python:3.12-slim

# 设置工作目录
WORKDIR /app

# 安装必要的系统依赖
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libxkbcommon-x11-0 \
    libdbus-1-3 \
    libxcb-icccm4 \
    libxcb-image0 \
    libxcb-keysyms1 \
    libxcb-randr0 \
    libxcb-render-util0 \
    libxcb-xinerama0 \
    libxcb-xkb1 \
    libxkbcommon-x11-0 \
    libfontconfig1 \
    libxcb-shape0 \
    libxcb-cursor0 \
    libxcb-util1 \
    xvfb \
    x11-utils \
    fonts-noto-cjk \
    && rm -rf /var/lib/apt/lists/*

# 复制requirements.txt
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用程序代码
COPY . .

# 创建配置目录
RUN mkdir -p /root/.config/LLMAI-writer

# 设置环境变量
ENV DISPLAY=:99
ENV QT_QPA_PLATFORM=xcb
ENV PYTHONIOENCODING=utf-8
ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8

# 创建启动脚本
RUN echo '#!/bin/bash\nXvfb :99 -screen 0 1920x1080x24 &\nsleep 1\npython main.py "$@"\n' > /app/start.sh && \
    chmod +x /app/start.sh

# 设置入口点
ENTRYPOINT ["/app/start.sh"]
