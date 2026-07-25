# ========== 2.Numpy 进阶：代码结果 + 逐点详解 ==========
# reshape() 修改数组维度，ravel() 多维摊平一维；
# hstack/vstack 横向 / 纵向拼接数组；hsplit/vsplit 切分数组；
# np.random：生成随机样本（数据集初始化、权重随机初始化）；
# 聚合函数：sum/mean/max/min/std 求和、均值、最值、标准差。

import numpy as np
# 1.形状变换
arr = np.arange(12)        # [ 0  1  2  3  4  5  6  7  8  9 10 11]
# reshape(行,列)：元素总数必须匹配，3*4=12刚好；
arr2d = arr.reshape(3,4)   # 改成3行4列
print("变形：\n",arr2d)
'''
[[ 0  1  2  3]
 [ 4  5  6  7]
 [ 8  9 10 11]]
'''
# ravel()：不管几维，全部拉成一维数组。
arr_1d = arr2d.ravel()     # 多维压扁成一维
print("摊平：",arr_1d)
'''
[ 0  1  2  3  4  5  6  7  8  9 10 11]
'''

# 2.拼接分割
# 口诀：h=horizontal 左右、v=vertical 上下
a = np.array([[1,2],[3,4]])
b = np.array([[5,6],[7,8]])
cat_h = np.hstack([a,b]) # 横向(左右拼，列变多)
cat_v = np.vstack([a,b]) # 纵向(上下拼，行变多)
print("横向拼接\n",cat_h)
'''
[[1 2 5 6]
 [3 4 7 8]]
'''
print("纵向拼接\n",cat_v)
'''
[[1 2]
 [3 4]
 [5 6]
 [7 8]]
'''

#3.随机数
# rand ()：只有 0～1 正数小数
# randn ()：围绕 0 上下浮动，有正有负（AI 权重）
# randint (a,b,size)：[a,b-1] 的整数

# 1. np.random.rand(行,列) → 【0~1均匀浮点数】
r1 = np.random.rand(2,3)
print("rand 0~1：\n",r1)
# 2. np.random.randn(行,列) → 标准正态 N(0,1)，正负都有
# 深度学习初始化权重首选
r2 = np.random.randn(3,3)
print("randn正态：\n",r2)
# 3. randint(起始,终止,size=(行,列)) 左闭右开 [low, high)
# 1~9的整数，2行3列
r3 = np.random.randint(1,10,size=(2,3))
print("randint整数：\n",r3)
print()

# 不带seed：每次结果不一样
a = np.random.randint(1,10,(2,3))
print(a)
print()
# 带seed：永久固定
np.random.seed(666)
b = np.random.randint(1,10,(2,3))
print(b)

#4.聚合函数 axis坐标轴重点、
# axis=0：沿着列上下压缩，对每一列运算
# axis=1：沿着行左右压缩，对每一行运算
'''
[[ 0  1  2  3]
 [ 4  5  6  7]
 [ 8  9 10 11]]
'''
print("总和:",arr2d.sum()) #全部数字相加 = 66
print("每行均值:",arr2d.mean(axis=1))
# axis=1 → 横向、按行算均值 → [1.5 5.5 9.5]
print("每列均值:",arr2d.mean(axis=0))
# axis=0 → 纵向、按列算均值 → [4. 5. 6. 7.]

