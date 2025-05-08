#!/bin/bash

# 确保novels目录存在
mkdir -p novels

# 允许Docker连接到X服务器
xhost +local:docker

# 构建并启动Docker容器
docker-compose up --build

# 恢复X服务器安全设置
xhost -local:docker
