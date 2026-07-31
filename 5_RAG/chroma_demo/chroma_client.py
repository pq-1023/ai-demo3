# =========【最顶部！环境变量必须放在所有导入之前】=========
import os
# HuggingFace国内镜像加速
os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"
# 模型缓存放到D盘，防止C盘爆满
os.environ["HF_HOME"] = "D:/py/huggingface_cache"
# =======================================================

import chromadb
from typing import List, Dict, Optional
# 替换！使用SentenceTransformer本地嵌入
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction


class ChromaVectorStore:
    def __init__(self, persist_path: str = "./chroma_db", embedding_func=None):
        # 初始化持久化客户端
        self.client = chromadb.PersistentClient(path=persist_path)
        # 接收自定义嵌入模型（BGE中文模型）
        self.embedding_func = embedding_func

    def get_or_create_collection(self, coll_name: str, coll_meta: Optional[Dict] = None):
        """获取或新建集合，自动绑定嵌入模型"""
        coll = self.client.get_or_create_collection(
            name=coll_name,
            metadata=coll_meta,
            embedding_function=self.embedding_func  # 传入中文嵌入模型
        )
        return coll

    def add_texts(self,
                  coll_name: str,
                  texts: List[str],
                  metadatas: Optional[List[Dict]] = None,
                  ids: Optional[List[str]] = None):
        """批量新增文本向量"""
        coll = self.get_or_create_collection(coll_name)
        coll.add(
            documents=texts,
            metadatas=metadatas,
            ids=ids
        )

    def search(self,
               coll_name: str,
               query_texts: List[str],
               top_k: int = 3,
               where_filter: Optional[Dict] = None):
        """语义检索，支持元数据过滤
        where_filter示例: {"category": "vector_db"}
        """
        coll = self.get_or_create_collection(coll_name)
        result = coll.query(
            query_texts=query_texts,
            n_results=top_k,
            where=where_filter
        )
        return result

    def delete_by_ids(self, coll_name: str, del_ids: List[str]):
        """根据id删除文档"""
        coll = self.get_or_create_collection(coll_name)
        coll.delete(ids=del_ids)

    def clear_collection(self, coll_name: str):
        """清空整个集合（删除重建）"""
        try:
            self.client.delete_collection(name=coll_name)
        except Exception:
            pass
        return self.get_or_create_collection(coll_name)


# 测试工具类入口
if __name__ == "__main__":
    # 【修复重点】本地加载BGE模型，不需要API密钥
    bge_embedding = SentenceTransformerEmbeddingFunction(
        model_name="BAAI/bge-small-zh-v1.5"
    )
    # 传入嵌入模型给向量库
    db = ChromaVectorStore(persist_path="./chroma_db", embedding_func=bge_embedding)
    coll_name = "ai_knowledge"

    # 插入数据
    texts = [
        "大语言模型可以理解人类自然语言",
        "RAG解决大模型知识过时、幻觉问题",
        "向量嵌入将文本转为多维向量用于语义检索"
    ]
    meta = [{"tag": "llm"}, {"tag": "rag"}, {"tag": "embedding"}]
    doc_ids = ["d1", "d2", "d3"]
    db.add_texts(coll_name, texts, meta, doc_ids)

    # 语义搜索
    res = db.search(coll_name, query_texts=["如何解决大模型幻觉"], top_k=2)
    print("匹配文本结果：")
    print(res["documents"][0])
    print("对应距离分数：")
    print(res["distances"][0])