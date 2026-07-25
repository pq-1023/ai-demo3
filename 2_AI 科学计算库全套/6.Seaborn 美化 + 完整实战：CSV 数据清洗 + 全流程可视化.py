# ========== 6.Seaborn 美化 + 完整实战：CSV 数据清洗 + 全流程可视化 ==========
# 整套流水线：读取 csv→清洗脏数据→统计→多图可视化
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# 中文支持
plt.rcParams["font.sans-serif"] = ["SimHei"]
plt.rcParams["axes.unicode_minus"] = False

# 读取
df = pd.read_csv("data.csv")
print("原始数据\n", df)


df["age"] = df["age"].fillna(df["age"].median())
df["score"] = df["score"].fillna(df["score"].median())

# 去重：按姓名+性别去重，保留第一次（同样用赋值）
df = df.drop_duplicates(subset=["name", "gender"], keep="first")

# 统计
print("\n清洗后数据\n", df)
print("\n男女平均分\n", df.groupby("gender")["score"].mean())

# 绘图
plt.figure(figsize=(12, 4))

plt.subplot(1, 2, 1)
# 修正：去掉 ci 和 palette，使用 errorbar=None
sns.barplot(x="gender", y="score", data=df, errorbar=None)
plt.title("男女平均分柱状图")

plt.subplot(1, 2, 2)
sns.histplot(df["score"], kde=True, bins=5, color="skyblue")
plt.title("分数分布直方图（带KDE）")

plt.tight_layout()
plt.savefig("analysis_result.png", dpi=300)
plt.show()