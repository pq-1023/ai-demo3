import torch
import torch.nn as nn

class SimpleCNN(nn.Module):
    def __init__(self):
        super().__init__()
        # Conv2d(输入通道数,输出通道数,卷积核大小,padding填充)
        # 灰度图通道=1；输出16个特征图；3*3卷积核；padding=1尺寸不变
        # 第一个参数1：输入通道in_channels：灰度黑白图片只有 1 个通道；彩色 RGB 图是 3 通道。
        # 第二个参数 16：输出通道 out_channels：代表这一层会生成16 张不同的特征图，每张特征图用一套独立 3×3 卷积核，分别提取边缘、横线、竖线、拐角等不同图像特征
        # kernel_size=3：卷积核是 3×3 大小（最通用尺寸，小范围抓取局部像素关系）
        # padding=1：图片四周填充 1 圈 0 像素公式：输出宽高 = 输入宽高 如果不加 padding，3×3 卷积会让长宽各缩小 2 像素
        self.conv1 = nn.Conv2d(1,16,kernel_size=3,padding=1)
        self.pool = nn.MaxPool2d(2,2) # 池化：长宽缩小一半
        #和全连接网络作用一致，给网络增加非线性能力；没有激活的多层卷积等价于单层卷积，无法学习复杂图案。
        self.relu = nn.ReLU()
    def forward(self,x):
        x = self.conv1(x) # 卷积提取边缘纹理特征
        x = self.relu(x)  # 激活
        x = self.pool(x)  # 压缩尺寸减少计算量
        return x

# 模拟一张灰度图：格式 [batch, channel, Height, Width]
img = torch.randn(1,1,28,28)
cnn = SimpleCNN()
out = cnn(img)
print("输入尺寸",img.shape,"卷积后尺寸",out.shape)