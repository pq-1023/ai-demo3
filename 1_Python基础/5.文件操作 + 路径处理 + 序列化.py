# ========== 5.文件操作 + 路径处理 + 序列化 ==========

#文件读写：推荐 with open(...) 语法，自动关闭文件，不用手动 close()
# 1.模式：r 读、w 清空写入、a 追加写入
# 2.编码：统一指定 encoding="utf-8"，避免中文乱码

# pathlib：Python3.4+ 标准路径库，优雅处理文件 / 文件夹路径
# JSON 序列化：json.dump 写入文件、json.load 读取文件，AI 数据交互必备
import json
from pathlib import Path

# ========== 1. pathlib 路径处理 ==========
# 当前文件所在路径
current_path = Path.cwd()
print("当前路径：", current_path)

# 拼接文件路径
file_path = current_path / "test.txt"
json_path = current_path / "data.json"
print("拼接文件路径：", file_path, " ", json_path)

# ========== 2. TXT 文件读写 ==========
# 写入txt
with open(file_path, "w", encoding="utf-8") as f:
    f.write("Python 文件操作\nAI 数据处理")

# 读取txt
with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()
print("读取txt内容：\n", content)

# ========== 3. JSON 读写（序列化） ==========
# 字典数据
data = {
    "project": "AI脚本",
    "version": "1.0",
    "author": "dev"
}

# 写入JSON文件
with open(json_path, "w", encoding="utf-8") as f:
    # ensure_ascii=False 保留中文，indent=2 格式化缩进
    json.dump(data, f, ensure_ascii=False, indent=2)

# 读取JSON文件
with open(json_path, "r", encoding="utf-8") as f:
    json_data = json.load(f)
print("\n读取JSON数据：", json_data["project"])
print("\n读取JSON数据：", json_data)
