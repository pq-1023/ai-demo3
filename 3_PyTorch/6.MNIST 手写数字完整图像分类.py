import torch #torch：PyTorch深度学习框架的核心库，用来做张量计算和自动求导
import torch.nn as nn #torch.nn：神经网络模块，提供各种层和损失函数
from torch.utils.data import DataLoader #DataLoader：数据加载器，用于批量加载数据集
from torchvision import datasets, transforms #torchvision：图像处理模块，提供数据集和预处理工具

# 图像预处理流水线
trans = transforms.Compose([
    transforms.ToTensor(), # ToTensor()：把图片从像素值0-255转换成0-1之间的小数，方便神经网络处理
    transforms.Normalize((0.1307,),(0.3081,)) # 按固定的均值(0.1307)和标准差(0.3081)做标准化，这是MNIST数据集的经验值，能让模型收敛更快
])
# 自动下载MNIST手写数字数据集
train_data = datasets.MNIST(root="./data", train=True, download=True, transform=trans)
#datasets.MNIST：自动下载MNIST手写数字数据集（7万张28×28的手写数字图片）
train_loader = DataLoader(train_data, batch_size=64, shuffle=True)
#把数据分成每批64张（batch_size=64），并且打乱顺序(shuffle=True)，让训练更高效

# 全连接手写数字网络
class MNISTNet(nn.Module):
    def __init__(self):
        super().__init__()
        #fc1/fc2：全连接层，可以理解为神经网络的"神经元"层
        self.fc1 = nn.Linear(28*28, 128) # 原图28*28像素，第一层：784个输入→128个输出
        self.fc2 = nn.Linear(128,10) # 第二层：128个输入→10个输出(0-9)
        #ReLU：激活函数，让网络能学习复杂的非线性关系（像一个开关）
        self.relu = nn.ReLU()
    #forward：定义数据如何在网络中流动，从输入层到输出层的计算流程
    def forward(self,x):
        # 把28×28的图片摊平成784个数字
        x = x.view(-1,28*28) # view等价reshape，把[batch,1,28,28]摊平 [batch,784]
        x = self.relu(self.fc1(x))# 第一层计算+激活函数
        return self.fc2(x)# 第二层计算，输出10个数字的概率

# 自动选GPU/CPU
device = "cuda" if torch.cuda.is_available() else "cpu"#device：自动检测是否有GPU，有的话用cuda，没有用cpu
model = MNISTNet().to(device) # 模型搬运到GPU
loss_fn = nn.CrossEntropyLoss()#loss_fn：损失函数，衡量模型预测的错误程度
opt = torch.optim.Adam(model.parameters(), lr=1e-3) #优化器(Adam)，像一个"纠错专家"，根据错误程度调整网络参数，让模型越来越准
# Adam比SGD收敛更快

# ====== 训练阶段 ======
model.train() # 开启训练模式（启用dropout、梯度计算）
for epoch in range(2): # epoch=完整遍历全部数据集2轮
    total_loss = 0
    for img, label in train_loader:# 每次取64张图片和对应的标签
        img, label = img.to(device), label.to(device) # 数据也搬到GPU
        opt.zero_grad() # 清空之前的梯度
        pred = model(img) # 模型预测
        loss = loss_fn(pred, label) # 计算错误
        loss.backward()# 反向传播：计算每个参数需要调整多少
        opt.step()# 更新参数
        total_loss += loss.item()
    print(f"Epoch{epoch}, Loss:{total_loss/len(train_loader):.3f}")

# ====== 推理预测阶段 ======
model.eval() # 切换到推理模式，关闭一些训练时用的功能，更快更省内存
with torch.no_grad(): # 上下文环境，全程不记录梯度，省显存
    sample_img, sample_label = train_data[0] # 取第一张图
    out = model(sample_img.unsqueeze(0).to(device)) # unsqueeze加batch维度
    pred_idx = torch.argmax(out, dim=1) # 从10个输出中选概率最大的那个，就是预测的数字
    print(f"真实标签:{sample_label},预测标签:{pred_idx.item()}")