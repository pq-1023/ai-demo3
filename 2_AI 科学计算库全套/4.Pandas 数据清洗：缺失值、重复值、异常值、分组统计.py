# ========== 4.Pandas 数据清洗：缺失值、重复值、异常值、分组统计 ==========
# isnull() 判断空值；
# dropna() 删除空；
# fillna() 填充空；
# drop_duplicates() 删除重复行；
# groupby() 分组聚合（特征分组统计）
import pandas as pd
import numpy as np

# 构造带脏数据的表格
data = {
    "name":["张三","李四","王五","李四","赵六",None],
    "age":[22,np.nan,19,25,28,23],
    "class":["A","A","B","A","B","B"]
}
df = pd.DataFrame(data)
print("原始数据：\n",df)

# 1.缺失值处理
print("空值统计:\n",df.isnull().sum())

df["age"] = df["age"].fillna(df["age"].mean()) # 均值填充年龄空值
print("均值填充年龄空值：\n",df)
df = df.dropna(subset=["name"]) # 删除姓名为空的行
print("删除姓名为空的行：\n",df)

# 2.删除name重复行
df = df.drop_duplicates(subset=["name"])
print("删除重复行：\n",df)

# 3.分组统计：按班级分组求平均年龄
group = df.groupby("class")["age"].mean()
print("\n各班平均年龄：\n",group)