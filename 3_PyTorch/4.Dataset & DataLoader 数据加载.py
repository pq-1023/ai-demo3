import torch
from torch.utils.data import Dataset, DataLoader

# Dataset：管单条数据怎么取
# DataLoader：管批量、打乱、并行加载，训练循环只遍历 loader

# 1. 自定义数据集类，继承Dataset
class MyDataset(Dataset):
    def __init__(self, data, label):
        self.data = data   # 全部样本特征
        self.label = label # 全部样本标签

    # 必须实现1：返回总样本数量
    def __len__(self):
        return len(self.data)

    # 必须实现2：按下标取单条 (特征,标签)
    def __getitem__(self, idx):
        return self.data[idx], self.label[idx]

# 模拟100条训练数据，每条3个特征，标签0/1二分类
x_data = torch.randn(100,3)
y_label = torch.randint(0,2,(100,))

dataset = MyDataset(x_data, y_label)

# DataLoader：打包批量、打乱、多线程读取
# batch_size=10：一次拿10个样本；shuffle=True每轮打乱顺序
loader = DataLoader(dataset, batch_size=10, shuffle=True)

# 循环遍历每一批数据
for batch_x, batch_y in loader:
    print(batch_x.shape, batch_y.shape)
    print(batch_x)
    print(batch_y)
    break # 只打印第一批就停止