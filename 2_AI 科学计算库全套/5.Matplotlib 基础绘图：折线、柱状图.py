# ========== 5.Matplotlib 基础绘图：折线、柱状图 ==========
# plt.plot()折线（趋势）、
# plt.bar()柱状（对比数值）；
# x/y坐标轴、标题、图例、图片展示；
# AI 用来查看数据分布、指标变化。
import numpy as np
import matplotlib.pyplot as plt

# 解决中文显示问题
plt.rcParams['font.sans-serif'] = ['SimHei']        # 黑体，也可用 'Microsoft YaHei'
plt.rcParams['axes.unicode_minus'] = False          # 解决负号 '-' 显示为方块的问题
# 1.折线图
x = np.arange(1,6) # [1,2,3,4,5]
y = [20,35,30,35,27]
plt.plot(x,y,label="样本数据")
plt.title("数据趋势折线图")
plt.xlabel("序号")
plt.ylabel("数值")
plt.legend()
plt.show()

# 2.柱状图
name = ["A组","B组","C组"]
score = [85,92,78]
plt.bar(name,score,color=["#1f77b4","#ff7f0e","#2ca02c"])
plt.title("各组分数柱状图")
plt.show()