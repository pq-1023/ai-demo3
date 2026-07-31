import os
# ==========【必须放在所有导入最上方】==========
# HuggingFace国内镜像加速
os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"
# 模型缓存放到D盘，不占用C盘
os.environ["HF_HOME"] = "D:/py/huggingface_cache"
# ===========================================

import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

# 中文模型，本地运行，不需要密钥
embedding_func = SentenceTransformerEmbeddingFunction(
    model_name="BAAI/bge-small-zh-v1.5"
)

# 向量库业务数据，存项目文件夹 ./chroma_db 你的资料（你存进去的一段段文字、生成的向量）
client = chromadb.PersistentClient(path="./chroma_db")

collection = client.get_or_create_collection(
    name="knowledge_base",
    metadata={"description": "本地测试知识库"},
    embedding_function=embedding_func
)

# 插入测试文本
documents = [
    "Chroma是轻量级本地向量数据库，无需启动服务",
    "RAG检索增强生成依靠向量相似度匹配文本",
    "向量数据库可以实现语义搜索，而非关键词搜索",
    "Collection是Chroma中存储向量的集合，类似数据表"
]
#给每一段文字贴标签 来源：笔记，分类：向量库后面搜索的时候可以设置条件：只搜索「向量库」分类的内容
metadatas = [{"source": "note", "category": "vector_db"} for _ in documents]
ids = [f"doc_{i}" for i in range(len(documents))]#给每一条文字分配唯一编号 doc_0、doc_1……

#执行存入操作！后台悄悄自动完成 3 步（你看不到）：
#① 调用中文 AI 模型
#② 把 4 段文字全部转换成数字向量
#③ 文字、数字、标签、编号一起保存到 chroma_db 文件夹
collection.add(
    documents=documents,
    metadatas=metadatas,
    ids=ids
)

# 语义查询
query_texts = ["向量数据库有什么作用？"]
results = collection.query(
    query_texts=query_texts,
    n_results=3#n_results=3：只返回相似度最高的 3 条内容
)

print("检索结果：")
#results["documents"][0] → 拿到第一个问题匹配出来的文本数组
#results["distances"][0] → 拿到第一个问题匹配出来的文本的相似度分数数组
#enumerate(数组) 作用：循环的时候，同时拿到【下标索引】和【数组里的值】
for idx, doc in enumerate(results["documents"][0]):
    print(f"相似度文本：{doc}")
    print(f"距离分数：{results['distances'][0][idx]}")
    print("-" * 50)