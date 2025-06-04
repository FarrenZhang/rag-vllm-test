#!/bin/bash
# 将数据和模型复制到AI Cloud平台私有数据路径
# 使用方法: sudo ./copy_to_private_data.sh

# 确保以root权限运行
if [ "$EUID" -ne 0 ]; then
  echo "请使用sudo运行此脚本"
  exit 1
fi

# 私有数据路径
PRIVATE_DATA_PATH="/data/glusterfs/brick1/demo-project"

# 创建必要的目录
mkdir -p "$PRIVATE_DATA_PATH/rag-data"
mkdir -p "$PRIVATE_DATA_PATH/rag-data/models"
mkdir -p "$PRIVATE_DATA_PATH/rag-data/data"

# 检查SQuAD数据集是否已存在，如果不存在则下载
if [ ! -f "$PRIVATE_DATA_PATH/rag-data/data/squad.json" ]; then
  echo "下载SQuAD数据集..."
  wget -q https://rajpurkar.github.io/SQuAD-explorer/dataset/train-v2.0.json -O "$PRIVATE_DATA_PATH/rag-data/data/squad.json"
  echo "SQuAD数据集已下载到私有数据路径"
else
  echo "SQuAD数据集已存在"
fi

# 检查是否已有本地Contriever模型，如有则复制
if [ -d "/home/feiyuan/rag-vllm-test/models/contriever" ]; then
  echo "复制本地Contriever模型..."
  cp -r /home/feiyuan/rag-vllm-test/models/contriever "$PRIVATE_DATA_PATH/rag-data/models/"
  echo "Contriever模型已复制到私有数据路径"
else
  # 如果本地没有模型，下载到私有数据路径
  if [ ! -d "$PRIVATE_DATA_PATH/rag-data/models/contriever" ]; then
    echo "下载Contriever模型到私有数据路径..."
    # 首先安装必要的Python包
    pip install -q transformers torch --no-cache-dir
    python3 -c "
from transformers import AutoTokenizer, AutoModel
import os
os.makedirs('$PRIVATE_DATA_PATH/rag-data/models/contriever', exist_ok=True)
tokenizer = AutoTokenizer.from_pretrained('facebook/contriever-msmarco')
model = AutoModel.from_pretrained('facebook/contriever-msmarco')
tokenizer.save_pretrained('$PRIVATE_DATA_PATH/rag-data/models/contriever')
model.save_pretrained('$PRIVATE_DATA_PATH/rag-data/models/contriever')
print('Contriever模型已下载到私有数据路径')
"
  else
    echo "Contriever模型已存在"
  fi
fi

# 设置正确的权限
chown -R feiyuan:feiyuan "$PRIVATE_DATA_PATH/rag-data"

echo "完成! 数据和模型已准备好在私有数据路径: $PRIVATE_DATA_PATH/rag-data"
echo "在AI Cloud平台上启动任务时，请设置以下环境变量:"
echo "MODEL_PATH=/path/to/mounted/private-data/rag-data/models/contriever"
echo "DATA_PATH=/path/to/mounted/private-data/rag-data/data/squad.json"
