FROM python:3.10-slim

WORKDIR /app

# Install basic dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    git \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Download small open source datasets and models
RUN mkdir -p /app/data /app/models

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
ENV VLLM_HOST="10.233.91.39" \
VLLM_PORT="2345"

# Expose service port
EXPOSE 3456

# Start the service
CMD ["python", "src/main.py"]