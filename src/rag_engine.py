import json
import logging
import numpy as np
from typing import List, Dict, Any
from transformers import AutoTokenizer, AutoModel
import torch
from tqdm import tqdm

logger = logging.getLogger(__name__)

class RAGEngine:
    def __init__(self, model_path: str, data_path: str):
        """
        初始化RAG引擎
        
        Args:
            model_path: Contriever模型路径
            data_path: 数据集路径
        """
        logger.info(f"初始化RAG引擎，加载模型: {model_path}")
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"使用设备: {self.device}")
        
        # 加载模型和分词器
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        self.model = AutoModel.from_pretrained(model_path).to(self.device)
        
        # 加载数据并处理
        self.documents, self.embeddings = self._process_dataset(data_path)
        logger.info(f"成功加载 {len(self.documents)} 个文档")
    
    def _process_dataset(self, data_path: str) -> tuple:
        """处理数据集并创建文档嵌入"""
        logger.info(f"处理数据集: {data_path}")
        
        # 加载SQuAD数据集
        with open(data_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        documents = []
        
        # 从SQuAD数据集中提取段落
        for article in data['data']:
            title = article.get('title', '')
            for paragraph in article['paragraphs']:
                context = paragraph['context']
                # 为每个段落创建一个文档
                documents.append({
                    'id': len(documents),
                    'title': title,
                    'text': context
                })
        
        # 只处理前10个文档以保持镜像大小合理
        documents = documents[:10]
        logger.info(f"生成嵌入向量 (总共 {len(documents)} 个文档)")
        
        # 计算文档嵌入
        embeddings = []
        batch_size = 16
        
        for i in tqdm(range(0, len(documents), batch_size)):
            batch_docs = documents[i:i+batch_size]
            batch_texts = [doc['text'] for doc in batch_docs]
            
            # 编码文本
            inputs = self.tokenizer(
                batch_texts, 
                max_length=512, 
                padding=True, 
                truncation=True, 
                return_tensors="pt"
            ).to(self.device)
            
            # 计算嵌入
            with torch.no_grad():
                outputs = self.model(**inputs)
                
            # 使用[CLS]嵌入作为文档嵌入
            batch_embeddings = outputs.last_hidden_state[:, 0, :].cpu().numpy()
            embeddings.extend(batch_embeddings)
        
        # 转换为numpy数组以便快速检索
        embeddings = np.vstack(embeddings)
        
        return documents, embeddings
    
    def _get_query_embedding(self, query: str) -> np.ndarray:
        """计算查询嵌入"""
        inputs = self.tokenizer(
            query, 
            max_length=512, 
            padding=True, 
            truncation=True, 
            return_tensors="pt"
        ).to(self.device)
        
        with torch.no_grad():
            outputs = self.model(**inputs)
        
        # 使用[CLS]嵌入作为查询嵌入
        query_embedding = outputs.last_hidden_state[:, 0, :].cpu().numpy()
        return query_embedding
    
    def retrieve(self, query: str, k: int = 3) -> List[str]:
        """根据查询检索相关文档"""
        # 计算查询嵌入
        query_embedding = self._get_query_embedding(query)
        
        # 计算余弦相似度
        scores = np.dot(self.embeddings, query_embedding.T).flatten()
        
        # 获取前k个相关文档
        top_indices = np.argsort(scores)[::-1][:k]
        
        # 返回相关文档文本
        contexts = [self.documents[idx]['text'] for idx in top_indices]
        return contexts