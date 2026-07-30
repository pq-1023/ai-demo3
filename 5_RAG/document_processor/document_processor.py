import re
import pdfplumber

class DocumentLoader:
    @staticmethod
    def clean_text(text: str) -> str:
        """脏文本清洗"""
        # 去除连续换行、多余空格
        text = re.sub(r"\n+", "\n", text)
        text = re.sub(r"\s+", " ", text)
        return text.strip()

    @staticmethod#简单理解：调用这个函数不需要创建对象，直接使用
    def load_txt(file_path: str) -> str:
        """加载TXT文件"""
        with open(file_path, "r", encoding="utf-8") as f:#with ... as f 语句自动关闭文件
            raw_text = f.read()
        return DocumentLoader.clean_text(raw_text)

    @staticmethod
    def load_pdf(file_path: str) -> str:
        """加载可解析PDF（非扫描件）"""
        all_text = []
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:#循环遍历 PDF每一页
                page_text = page.extract_text()#提取每一页文本
                if page_text:#如果每一页文本不为空
                    all_text.append(page_text)#将每一页文本添加到 all_text 列表中
        raw_text = "\n".join(all_text)
        return DocumentLoader.clean_text(raw_text)

class TextSplitter:
    def __init__(self, chunk_size: int, chunk_overlap: int):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        if chunk_overlap >= chunk_size:
            raise ValueError("重叠长度不能大于等于块大小")

    def split_text(self, text: str) -> list[str]:
        chunks = []
        start = 0
        text_len = len(text)
        while start < text_len:
            end = start + self.chunk_size
            chunk = text[start:end]#提取当前块文本
            chunks.append(chunk)#将当前块文本添加到 chunks 列表中
            start += self.chunk_size - self.chunk_overlap#滑动窗口：前进长度 = 块大小 - 重叠
        return chunks

# ========== 测试Demo ==========
if __name__ == "__main__":
    loader = DocumentLoader()
    text = loader.load_txt("test.txt")
    pdf_text = loader.load_pdf("test.pdf")

    test_text = """
    RAG检索增强生成分为几个阶段：文档加载、文本切片、向量化存入向量库。
    用户提问后，问题向量化，在向量库检索相似文本片段。
    将检索到的上下文和用户问题一起送入大模型，生成答案，缓解大模型幻觉。
    文本切片参数直接影响检索准确率，块太大语义混杂，块太小信息不足。
    RAG检索增强生成分为几个阶段：文档加载、文本切片、向量化存入向量库。
    用户提问后，问题向量化，在向量库检索相似文本片段。
    将检索到的上下文和用户问题一起送入大模型，生成答案，缓解大模型幻觉。
    文本切片参数直接影响检索准确率，块太大语义混杂，块太小信息不足。
    """
    splitter = TextSplitter(chunk_size=120, chunk_overlap=30)
    print("测试文本切片：-------------------------------定义文本---------------------------------")
    chunk_list1 = splitter.split_text(test_text)
    for idx, chunk in enumerate(chunk_list1):
        print(f"===== 块{idx+1} =====")
        print(chunk)
        print(f"长度：{len(chunk)}\n")
    print("测试文本切片：-------------------------------TXT文本---------------------------------")
    chunk_list2 = splitter.split_text(text)
    for idx, chunk in enumerate(chunk_list2):
        print(f"===== 块{idx+1} =====")
        print(chunk)
        print(f"长度：{len(chunk)}\n")
    print("测试文本切片：-------------------------------PDF文本---------------------------------")
    chunk_list3 = splitter.split_text(pdf_text)
    for idx, chunk in enumerate(chunk_list3):
        print(f"===== 块{idx+1} =====")
        print(chunk)
        print(f"长度：{len(chunk)}\n")


