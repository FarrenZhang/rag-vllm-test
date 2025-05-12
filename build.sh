#!/bin/bash

# 构建RAG服务镜像
IMAGE_NAME="rag-service:latest"

echo "开始构建RAG服务镜像: $IMAGE_NAME"

# 构建Docker镜像
docker build -t $IMAGE_NAME .

if [ $? -eq 0 ]; then
    echo "构建成功！镜像名称: $IMAGE_NAME"
    echo "你可以使用以下命令运行服务:"
    echo "./run.sh"
else
    echo "构建失败，请检查错误信息"
fi