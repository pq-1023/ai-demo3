import torch
# 导入 PyTorch 主库和神经网络模块（nn = neural network
import torch.nn as nn

# 定义网络结构（继承 nn.Module）
# 前向传播（forward）
# 保存 / 加载权重（state_dict）

# 1. 所有网络必须继承 nn.Module（类比Java父类）
class SimpleNet(nn.Module):#定义一个自己的网络类，必须继承 nn.Module
    #类比：__init__ 是图纸（画好了哪些房间），forward 是行走路线（先到客厅，再到卧室）
    def __init__(self, in_dim, hidden_dim, out_dim):
        # __init__里只定义层结构（相当于声明成员变量，只负责声明网络有哪些层，不负责数据怎么流动）
        super().__init__()  # 调用父类 nn.Module 的构造函数，必须写，否则网络没有基础功能

        self.fc1 = nn.Linear(in_dim, hidden_dim)
        # 定义一个全连接层（也叫线性层）。in_dim：输入特征数（比如3个特征） hidden_dim：输出特征数（隐藏层神经元个数，比如8）
        # 权重矩阵 W（形状 hidden_dim × in_dim）+偏置b（形状hidden_dim）
        # 数学：output = input @ W.T + b
        self.relu = nn.ReLU()
        # 定义一个ReLU激活函数层（非线性）。负数变 0，正数不变，没有参数，只做变换。
        self.fc2 = nn.Linear(hidden_dim, out_dim)
        #作用：第二个全连接层，将隐藏层（8维）映射到输出维度（比如2维，用于二分类）。

    # forward 固定方法：定义数据前向流动逻辑（必须写，相当于模型运行逻辑）
    #forw为什么叫forward：因为 nn.Module 内部会调用这个方法。当你写 net(x) 时，PyTorch 自动执行 net.forward(x)。
    # x进来 → 先经过 fc1 → 再经过 relu → 最后经过 fc2 → 输出 out
    def forward(self, x):
        x = self.fc1(x)
        x = self.relu(x)
        out = self.fc2(x)
        return out


# 实例化网络：输入3个特征，隐藏层8个神经元，输出2分类
net = SimpleNet(3, 8, 2)
test_x = torch.randn(1, 3)  # 1组样本、3个特征
print(test_x )
pred = net(test_x)  # 直接调用net(x)会自动执行forward 前向推理。实际上等价于 net.forward(test_x)
#输出形状 (1, 2)，表示两个类别的原始得分（logits），还没经过 Softmax
print("网络输出：", pred)

# 2. 模型权重保存与加载
# state_dict() 只保存权重参数（推荐，体积小）
torch.save(net.state_dict(), "simple_net.pth")
print(net.state_dict())

# 新建空网络结构，再加载权重
new_net = SimpleNet(3, 8, 2)
new_net.load_state_dict(torch.load("simple_net.pth"))