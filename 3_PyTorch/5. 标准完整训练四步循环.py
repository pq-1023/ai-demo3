import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader, TensorDataset  # 导入 TensorDataset
#让模型在一个个批次（batch）的数据上学习，逐步减小预测错误

# 创建一个极简的神经网络，只有一个全连接层。
class Net(nn.Module):
    def __init__(self):
        super().__init__()
        self.fc = nn.Linear(3, 2) # 输入3个特征，输出2个数字（二分类得分）
    def forward(self, x):
        return self.fc(x)

net = Net()
loss_fn = nn.CrossEntropyLoss()
# 损失函数：用来衡量“模型的预测有多离谱”
# 如果预测的类别得分和真实标签（0 或 1）差距很大，损失值就很大。
# CrossEntropyLoss 内部会自动把输出分数转成概率，适合分类任务。
opt = torch.optim.SGD(net.parameters(), lr=0.01)
# 优化器：负责根据损失计算出的梯度，去更新网络参数，让损失逐渐变小。
# SGD 是最简单的优化器：参数 = 参数 - 学习率 × 梯度
# lr=0.01 是学习率，控制每次更新步长。

# 准备数据
x = torch.randn(50, 3)
y = torch.randint(0, 2, (50,))

# 直接用 TensorDataset，不再需要自定义 MyDataset
dataset = TensorDataset(x, y)
loader = DataLoader(dataset, batch_size=5)

# 训练循环
for batch_x, batch_y in loader:# 每次拿 5 条数据
    opt.zero_grad()  # 梯度清零：上一轮梯度会累加，必须清空 ① 忘掉上一次的错误反馈
    pred = net(batch_x)  # 前向传播：模型算出预测值 ② 用当前知识猜答案
    loss = loss_fn(pred, batch_y)  # 计算损失：预测和真实标签差距③ 看看猜得有多离谱（算损失）
    loss.backward()  # 反向传播：自动计算所有参数梯度 ④ 反思：错在哪个环节？（反向传播）
    opt.step()  # 参数更新：w = w - lr * grad ⑤ 根据反思结果改进自己（更新参数）
print("本轮loss:", loss.item())  # item()把tensor数值转普通数字