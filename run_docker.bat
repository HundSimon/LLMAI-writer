@echo off
REM 确保novels目录存在
if not exist novels mkdir novels

REM 构建并启动Docker容器
docker-compose up --build
