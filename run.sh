#!/bin/bash

# 设置环境变量
VLLM_HOST=${VLLM_HOST:-"10.233.91.39"}
VLLM_PORT=${VLLM_PORT:-"2345"}
RAG_PORT=3456

# 显示配置信息
echo "启动RAG服务，配置如下:"
echo "vLLM服务地址: $VLLM_HOST:$VLLM_PORT"
echo "RAG服务端口: $RAG_PORT"

# 确认是否继续
read -p "是否继续启动服务？ (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "已取消启动"
    exit 1
fi

# 运行Docker容器
docker run -d \
    --name rag-service \
    --network host \
    -e VLLM_HOST=$VLLM_HOST \
    -e VLLM_PORT=$VLLM_PORT \
    --restart unless-stopped \
    rag-service:latest
    tail -f /dev/null


if [ $? -eq 0 ]; then
    echo "RAG服务已启动!"
    echo "您可以通过以下URL访问服务:"
    echo "- 健康检查: http://localhost:$RAG_PORT/"
    echo "- 直接查询端点: http://localhost:$RAG_PORT/query"
    echo "- RAG查询端点: http://localhost:$RAG_PORT/rag"
    echo
    echo "使用以下命令查看日志:"
    echo "docker logs -f rag-service"
else
    echo "启动服务失败，请检查错误信息"
fi