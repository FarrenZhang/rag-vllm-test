import os
import json
import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import httpx
import uvicorn
from src.rag_engine import RAGEngine

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 获取环境变量
VLLM_HOST = os.getenv("VLLM_HOST", "10.233.91.39")
VLLM_PORT = os.getenv("VLLM_PORT", "2345")
VLLM_URL = f"http://{VLLM_HOST}:{VLLM_PORT}/v1/completions"

# 初始化FastAPI应用
app = FastAPI(title="RAG服务")

# 初始化RAG引擎
rag_engine = RAGEngine(
    model_path="/app/models/contriever",
    data_path="/app/data/squad.json"
)

class QueryRequest(BaseModel):
    query: str
    max_tokens: int = 512
    temperature: float = 0.7
    model: str = "facebook/opt-6.7b"  # 默认模型，可以被请求覆盖

class RAGRequest(BaseModel):
    query: str
    max_tokens: int = 512
    temperature: float = 0.7
    model: str = "facebook/opt-6.7b"
    top_k: int = 3

@app.get("/")
async def health_check():
    return {"status": "healthy", "service": "RAG"}

@app.post("/query")
async def query(request: QueryRequest):
    """直接查询LLM，不使用RAG功能"""
    try:
        # 准备请求
        payload = {
            "model": request.model,
            "prompt": request.query,
            "max_tokens": request.max_tokens,
            "temperature": request.temperature
        }
        
        # 向vLLM服务发送请求
        async with httpx.AsyncClient() as client:
            response = await client.post(
                VLLM_URL,
                json=payload,
                timeout=60.0
            )
            
        # 检查是否成功
        if response.status_code != 200:
            logger.error(f"vLLM服务响应错误: {response.status_code} - {response.text}")
            raise HTTPException(status_code=500, detail="vLLM服务响应错误")
            
        # 解析结果
        result = response.json()
        return result
        
    except Exception as e:
        logger.error(f"查询处理过程中出错: {str(e)}")
        raise HTTPException(status_code=500, detail=f"服务错误: {str(e)}")

@app.post("/rag")
async def rag_query(request: RAGRequest):
    """使用RAG增强查询LLM"""
    try:
        # 获取相关上下文
        contexts = rag_engine.retrieve(request.query, k=request.top_k)
        context_str = "\n".join(contexts)
        
        # 构建RAG提示
        rag_prompt = f"""使用以下信息回答问题:

上下文信息:
{context_str}

问题: {request.query}

答案:"""
        
        # 准备请求
        payload = {
            "model": request.model,
            "prompt": rag_prompt,
            "max_tokens": request.max_tokens,
            "temperature": request.temperature
        }
        
        # 向vLLM服务发送请求
        async with httpx.AsyncClient() as client:
            response = await client.post(
                VLLM_URL,
                json=payload,
                timeout=60.0
            )
            
        # 检查是否成功
        if response.status_code != 200:
            logger.error(f"vLLM服务响应错误: {response.status_code} - {response.text}")
            raise HTTPException(status_code=500, detail="vLLM服务响应错误")
            
        # 解析结果
        llm_result = response.json()
        
        # 增加RAG信息
        result = {
            "llm_response": llm_result,
            "contexts": contexts[:request.top_k],
            "query": request.query
        }
        
        return result
        
    except Exception as e:
        logger.error(f"RAG查询处理过程中出错: {str(e)}")
        raise HTTPException(status_code=500, detail=f"服务错误: {str(e)}")

if __name__ == "__main__":
    logger.info(f"启动RAG服务，连接vLLM服务: {VLLM_URL}")
    uvicorn.run(app, host="0.0.0.0", port=8000)