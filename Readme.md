# 基础RAG服务

这个项目实现了一个基本的检索增强生成(RAG)服务，它使用外部的vLLM服务作为大语言模型后端。

## 项目特点

- 轻量级RAG实现
- 使用Contriever作为检索模型
- 包含预处理的SQuAD数据集（限制为1000条文档）
- 支持可配置的外部vLLM服务连接
- 提供HTTP API接口

## 项目结构

```
rag-service/
├── Dockerfile          # Docker镜像构建文件
├── requirements.txt    # Python依赖列表
├── .dockerignore       # Docker构建忽略文件
├── build.sh            # 构建脚本
├── run.sh              # 运行脚本
├── test.py             # 测试脚本
└── src/                # 源代码目录
    ├── __init__.py     
    ├── main.py         # 主应用程序
    └── rag_engine.py   # RAG引擎实现
```

## 使用方法

### 1. 构建镜像

执行以下命令构建Docker镜像：

```bash
./build.sh
```

### 2. 运行服务

使用以下命令运行服务：

```bash
VLLM_HOST=10.233.91.39 VLLM_PORT=2345 ./run.sh
```

或者直接运行（将使用默认值）：

```bash
./run.sh
```

### 3. 测试服务

使用提供的测试脚本测试服务：

```bash
python test.py
```

或者手动使用curl测试：

```bash
# 测试健康检查
curl http://localhost:8000/

# 测试直接查询
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "什么是人工智能?", "max_tokens": 100}'

# 测试RAG查询
curl -X POST http://localhost:8000/rag \
  -H "Content-Type: application/json" \
  -d '{"query": "谁是爱因斯坦?", "max_tokens": 100, "top_k": 3}'
```

## API接口

### 健康检查

```
GET /
```

返回服务状态。

### 直接查询

```
POST /query
```

参数：
- `query`: 查询文本
- `max_tokens`: (可选) 最大生成token数，默认为512
- `temperature`: (可选) 生成温度，默认为0.7
- `model`: (可选) 使用的模型名称，默认为"facebook/opt-6.7b"

### RAG查询

```
POST /rag
```

参数：
- `query`: 查询文本
- `max_tokens`: (可选) 最大生成token数，默认为512
- `temperature`: (可选) 生成温度，默认为0.7
- `model`: (可选) 使用的模型名称，默认为"facebook/opt-6.7b"
- `top_k`: (可选) 检索的上下文数量，默认为3

## 环境变量

- `VLLM_HOST`: vLLM服务的主机地址，默认为"10.233.91.39"
- `VLLM_PORT`: vLLM服务的端口，默认为"2345"