FROM python:3.10-slim

WORKDIR /app

# Install basic dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    git \
    wget \
    iputils-ping \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt .
# 使用清华镜像源，安装CPU版PyTorch和其他依赖，增加超时时间
RUN pip install --no-cache-dir -r requirements.txt \
    -i https://pypi.tuna.tsinghua.edu.cn/simple \
    --extra-index-url https://download.pytorch.org/whl/cpu \
    --timeout 300

# Create directories for data and models
RUN mkdir -p /app/data /app/models

# Default datasets and models (can be overridden with mounted volumes)
# Download small datasets - use the SQuAD dataset as an example
RUN wget -q https://rajpurkar.github.io/SQuAD-explorer/dataset/train-v2.0.json -O /app/data/squad.json

# Download Contriever model - use a smaller version
RUN python -c "from transformers import AutoTokenizer, AutoModel; \
    tokenizer = AutoTokenizer.from_pretrained('facebook/contriever-msmarco'); \
    model = AutoModel.from_pretrained('facebook/contriever-msmarco'); \
    tokenizer.save_pretrained('/app/models/contriever'); \
    model.save_pretrained('/app/models/contriever')"

# Copy application code
COPY src/ /app/src/

# Set environment variables to make the vLLM service address configurable
ENV VLLM_HOST="10.233.91.40" \
    VLLM_PORT="2345" \
    SERVICE_PORT="3456" \
    MODEL_PATH="/app/models/contriever" \
    DATA_PATH="/app/data/squad.json"

# Expose service port
EXPOSE 3456

# Start the service
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "3456"]
