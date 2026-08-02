import os
from abc import ABC, abstractmethod
from sentence_transformers import SentenceTransformer
import requests
from dotenv import load_dotenv

# 加载.env环境配置文件，读取密钥、模型路径、运行模式等配置
load_dotenv()

# 嵌入层（核心：抽象类 + 工厂模式，实现一键切换本地 / 云端Embedding）
class BaseEmbedding(ABC):
    """
    嵌入模型抽象基类
    定义统一接口标准：本地模型、云端API都必须实现encode方法
    好处：上层业务代码无需关心底层是本地还是云端，解耦
    """
    @abstractmethod
    def encode(self, texts: list[str]) -> list[list[float]]:
        """
        将一批文本转为向量
        :param texts: 字符串列表，多个文本块
        :return: 二维列表，每个文本对应的浮点向量
        """
        pass

# 本地sentence-transformers实现【改造：支持离线本地模型】
class LocalEmbedding(BaseEmbedding):
    def __init__(self):
        # 优先读取.env中的本地模型路径；没有配置则使用默认 all-MiniLM-L6-v2
        self.model_path = os.getenv("LOCAL_EMBED_MODEL_PATH", "all-MiniLM-L6-v2")
        # local_files_only=True：强制禁止联网访问huggingface，纯离线加载模型
        self.model = SentenceTransformer(
            self.model_path,
            local_files_only=True
        )

    def encode(self, texts: list[str]) -> list[list[float]]:
        # normalize_embeddings=True 向量归一化，搭配余弦相似度检索
        emb = self.model.encode(texts, normalize_embeddings=True)
        # numpy数组转为普通list，Chroma向量库可识别
        return emb.tolist()

# 云端豆包Embedding接口实现
class CloudEmbedding(BaseEmbedding):
    def __init__(self):
        # 从环境变量读取API密钥、接口地址
        self.api_key = os.getenv("DOUBAO_API_KEY")
        self.url = os.getenv("DOUBAO_EMBED_URL")
        # 构造请求头
        self.headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}

    def encode(self, texts: list[str]) -> list[list[float]]:
        # 组装请求体，传入待向量化文本数组
        payload = {"model": "text-embedding", "input": texts}
        # Post请求调用云端Embedding接口
        resp = requests.post(self.url, json=payload, headers=self.headers)
        # 请求异常自动抛出错误（网络错误、密钥错误、限流等）
        resp.raise_for_status()
        data = resp.json()
        # 提取接口返回的向量列表
        embeddings = [item["embedding"] for item in data["data"]]
        return embeddings

# 工厂方法：根据配置自动选择嵌入方案
def get_embedding_client() -> BaseEmbedding:
    """
    工厂函数：读取配置自动创建嵌入实例
    EMBED_MODE = local：本地模型
    EMBED_MODE = cloud：云端API
    未配置时，默认使用本地模型
    """
    mode = os.getenv("EMBED_MODE", "local")
    if mode == "cloud":
        return CloudEmbedding()
    return LocalEmbedding()