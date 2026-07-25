# ========== 3.Pandas 核心：Series、DataFrame、行列取值、条件筛选 ==========

# Series：一维带标签的数组，类似带行索引的列。；
# DataFrame=二维表格，既有行索引也有列名，类似 Excel 或 SQL 表，每个 DataFrame 的列本质上都是一个 Series，对标 Excel / 数据库表，AI 数据集载体；
# 取列：df['列名']；取行：loc[索引] / iloc[下标]；
# 布尔条件筛选：按数值过滤数据（样本筛选）。
import pandas as pd

# 1. 构造DataFrame表格
data = {
    "name":["张三","李四","王五","赵六"],
    "age":[22,25,19,28],
    "score":[88,92,75,96]
}
df = pd.DataFrame(data)
print(df)

# 2. 列操作
print(df["name"])          # 单列
print(df[["name","score"]])# 多列

# 3. 行操作 loc(名称索引) iloc(数字下标)
print(df.loc[1])
print(df.iloc[0:2])

# 4. 条件筛选：筛选age>23的数据
filter_df = df[df["age"]>23]
print("\n年龄大于23：\n",filter_df)