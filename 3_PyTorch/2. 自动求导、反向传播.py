# ========== 2.自动求导、反向传播 ==========

# 告诉 PyTorch：“这个变量需要自动计算梯度（导数）
# requires_grad=True = 告诉 PyTorch“这个参数我要优化，帮我算它的导数”。

# 从 y 开始反向传播，自动计算所有带requires_grad=True的变量对y的梯度
# backward() = 自动执行链式求导，算出所有参数的偏导数
import torch

# 1. requires_grad=True 开启梯度记录，只有参数需要开
# 创建一个张量（可以理解为“装着数字 2.0 的盒子”），并告诉 PyTorch：“这个变量需要计算梯度（导数），因为它是一个参数，以后要根据梯度来更新它
w = torch.tensor(2.0, requires_grad=True) # 开启梯度记录。w 通常代表权重（weight），是需要学习的
x = torch.tensor(3.0) #如果不写，默认是 False，PyTorch 不会为它算导数。
# 类比：w 像是“可调的旋钮”，x 像是“固定输入值

# 前向计算：y = w * x
y = w * x

# 反向传播，自动链式求导，在这里，只有 w 开启了梯度，所以会计算dy/dw = x = 3 PyTorch 算出结果后，会把值存入 w.grad 属性中
y.backward()

# .grad 属性储存计算出来的梯度值
print("w的梯度：", w.grad) # 输出 tensor(3.)

# 多变量求导示例 out = a² + 3b
a = torch.tensor(1., requires_grad=True)
b = torch.tensor(2., requires_grad=True)
out = a**2 + 3*b
out.backward()
print(a.grad, b.grad) # da=2a=2，db=3