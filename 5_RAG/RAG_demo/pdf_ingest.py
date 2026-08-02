import os
import time
import uuid
import re
import pdfplumber
import chromadb
from chromadb.config import Settings
from embedding_provider import get_embedding_client

# =====================全局配置区=====================
CHROMA_PATH = "./chroma_db"             # Chroma向量库持久化存储文件夹
COLLECTION_NAME = "knowledge_base"      # 向量库集合名称（类似数据表）
CHUNK_SIZE = 200                       # 单个文本块最大字符长度
CHUNK_OVERLAP = 50                     # 文本块重叠字符，防止上下文断裂
SIM_THRESHOLD = 0.8                     # 余弦距离阈值，小于阈值代表语义相关
# ====================================================

# 【关键】全局只创建一次客户端，复用！
chroma_settings = Settings(allow_reset=True)
client = chromadb.PersistentClient(path=CHROMA_PATH, settings=chroma_settings)

def clean_text(raw_text: str) -> str:
    """
    PDF原始文本数据清洗
    解决PDF导出文本常见问题：断行连字符、大量换行、连续空格、制表符
    :param raw_text: pdfplumber提取的未处理原始文本
    :return: 清洗完毕的规整文本
    """
    # 去除PDF段落分割产生的连字符：例 数-\n据 → 数据
    raw_text = re.sub(r"-\n", "", raw_text)
    # 所有换行、回车、制表符替换为空格
    raw_text = re.sub(r"[\r\n\t]", " ", raw_text)
    # 连续多个空格合并为单个空格
    raw_text = re.sub(r"\s+", " ", raw_text)
    # 去除首尾多余空白
    clean_result = raw_text.strip()
    return clean_result

def split_text(text: str) -> list[str]:
    """
    简易文本分割函数
    将超长文本按照 chunk_size 和 overlap 切割成多个片段
    """
    chunks = []
    start = 0
    text_len = len(text)
    while start < text_len:
        end = start + CHUNK_SIZE
        chunk = text[start:end]
        chunks.append(chunk)
        # 下一段起始位置 = 当前起点 + 块大小 - 重叠长度
        start += (CHUNK_SIZE - CHUNK_OVERLAP)
    return chunks


def extract_pdf_text(pdf_path: str) -> str:
    """
    使用pdfplumber解析PDF，提取所有页面纯文本
    :param pdf_path: pdf文件路径
    :return: PDF完整拼接原始文本
    """
    full_text = ""
    # 打开pdf文件
    with pdfplumber.open(pdf_path) as pdf:
        # 遍历每一页
        for page in pdf.pages:
            page_text = page.extract_text()
            # 当前页面存在文本才拼接
            if page_text:
                full_text += page_text + "\n"
    return full_text


def pdf_to_vector_db(pdf_file_path: str):
    """
    完整PDF入库流水线
    PDF解析 → 文本清洗 → 文本切块 → 向量化 → 存入Chroma向量库
    """
    # 复用全局client
    coll = client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"}
    )
    # 通过工厂函数获取嵌入模型实例（自动本地/云端切换）
    embed_client = get_embedding_client()

    # 获取文件名，用于元数据标记 & 清除旧数据，防止重复入库
    file_name = os.path.basename(pdf_file_path)
    try:
        # 删除向量库内同名文件历史数据
        coll.delete(where={"file_name": file_name})
    except Exception:
        pass

    print("解析PDF...")
    raw_text = extract_pdf_text(pdf_file_path)
    # 【新增：文本清洗】
    raw_text = clean_text(raw_text)

    # 判断PDF是否提取到有效内容
    if not raw_text.strip():
        print("PDF无有效文本！")
        return

    # 文本切块
    chunks = split_text(raw_text)
    print(f"分割完成，共 {len(chunks)} 个文本块")

    # 批量文本向量化
    print("开始向量化...")
    embeddings = embed_client.encode(chunks)

    # 构造元数据：标记文件名称、路径、入库时间，用于后续过滤检索
    now = time.strftime("%Y-%m-%d %H:%M:%S")
    metadatas = [
        {
            "file_name": file_name,
            "source_path": pdf_file_path,
            "create_time": now
        } for _ in chunks
    ]
    # 生成唯一ID，每条向量一条唯一标识
    ids = [str(uuid.uuid4()) for _ in chunks]

    # 将文本、向量、元数据批量写入向量库
    coll.add(
        ids=ids,
        documents=chunks,
        embeddings=embeddings,
        metadatas=metadatas
    )
    print(f"✅ {file_name} 成功入库！")


def test_search(query: str):
    """
    向量检索测试函数
    用户问题向量化 → 在向量库相似度检索 → 根据阈值过滤无关片段
    """
    # 复用全局client，不再新建
    coll = client.get_collection(COLLECTION_NAME)
    embed_client = get_embedding_client()

    # 查询文本转为向量
    q_vec = embed_client.encode([query])

    # 执行相似度检索，额外返回距离分数、元数据
    result = coll.query(
        query_embeddings=q_vec,
        n_results=2,
        include=["documents", "metadatas", "distances"]
    )

    print("\n检索结果详情：")
    docs = result["documents"][0]
    distances = result["distances"][0]
    metas = result["metadatas"][0]

    valid_context = []  # 存放筛选后有效的相关文本片段
    for idx, (doc, dist, meta) in enumerate(zip(docs, distances, metas)):
        print(f"\n【片段{idx+1} | 余弦距离：{dist:.3f}】")
        print(f"{doc[:250]}...")
        print("元数据：", meta)

        # 距离小于阈值，判定为相关内容，保留
        if dist < SIM_THRESHOLD:
            valid_context.append(doc)

    # 输出筛选结果
    print("\n====================筛选完成====================")
    if len(valid_context) == 0:
        print("❌ 没有找到语义相关的参考资料！")
    else:
        print(f"✅ 有效相关片段数量：{len(valid_context)}")
        for content in valid_context:
            print("-" * 30)
            print(content)


# 程序入口
if __name__ == "__main__":
    # 执行PDF入库
    pdf_to_vector_db("./test.pdf")
    # 执行检索测试，修改引号内内容更换问题
    test_search("向量数据库有什么作用？")