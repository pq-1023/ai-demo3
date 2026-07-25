# pip install torch torchvision torchaudio numpy pandas matplotlib -i https://pypi.tuna.tsinghua.edu.cn/simple
# 环境说明：有 Numpy 基础，torch.Tensor对标 np.array，是深度学习底层数据结构；优先 CPU 运行，代码自动适配 GPU。

# ========== 1.PyTorch 环境 + Tensor 张量操作 ==========
# Tensor 是 PyTorch 的数组，比 NumPy 多了 GPU 加速和自动求导，是深度学习的数据载体。
# 设备切换：.to("cuda")GPU / .to("cpu")CPU；判断 GPU：torch.cuda.is_available()
# 常用：创建张量、维度查看 shape、张量与 numpy 互转、四则运算
import torch
import numpy as np

# 1.创建张量
t1 = torch.tensor([1,2,3])         # 普通自定义张量，对标np.array
t2 = torch.zeros((2,3))            # 2行3列全0张量，初始化权重常用
t3 = torch.randn(3,3)              # 3*3正态分布随机数，模型权重初始化标配
print("张量形状：", t3.shape)        # shape查看维度，和numpy一模一样

# 2.张量与numpy互转
# 如果 Tensor 在 CPU 上，.numpy() 会共享内存，修改一个会影响另一个。如果 Tensor 在 GPU 上，需先 .cpu() 再转 NumPy。
arr = t1.numpy() # Tensor → NumPy（共享内存，注意类型）
t_from_np = torch.from_numpy(arr) # numpy转回tensor

# 3. 自动判断设备：有GPU用cuda，没有用cpu
# torch.cuda.is_available() 判断是否有 NVIDIA GPU 以及 CUDA 驱动正确安装。
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
t_gpu = t3.to(device) # 把张量搬运到GPU显存加速运算
print("张量所在设备：", t_gpu.device)

# 4.张量四则运算（同numpy逐元素运算）
a = torch.tensor([1,2])
b = torch.tensor([3,4])
print(a + b, a * b)