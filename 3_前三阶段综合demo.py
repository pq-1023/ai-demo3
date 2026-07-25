# ==============================
# 三阶段综合复盘项目：垃圾短信分类器
# 项目目标：输入短信文本，AI区分垃圾短信(1)/正常短信(0)
# 完整链路：Python工程脚本 → Pandas数据清洗可视化 → PyTorch NLP词向量训练推理
# ==============================

# ============ 阶段1：Python基础内置库（Day1~Day10） ============
import os
# os：文件路径操作，本项目用来存放模型、日志文件，阶段1文件操作知识点
import logging
# logging：专业日志打印，替代print，对应阶段1 Day8 日志模块

# ============ 阶段2：科学计算三剑客（Day11~Day17） ============
import numpy as np
# Numpy：底层数值数组，张量互转、数值计算，Day11 Numpy入门
import pandas as pd
# Pandas：表格数据处理、清洗数据集，Day13 DataFrame、Day14数据清洗
import matplotlib.pyplot as plt
# Matplotlib：数据可视化绘图，查看样本分布，Day15 基础绘图

# ============ 阶段3：PyTorch深度学习全套（Day18~Day26） ============
import torch
# 深度学习核心库，张量、自动求导、GPU设备切换 Day19 Tensor
import torch.nn as nn
# nn：神经网络层仓库（线性层、卷积、Embedding词向量、激活函数）Day21
from torch.utils.data import Dataset, DataLoader
# Dataset：自定义数据集模板；DataLoader：批量加载数据 Day22

# --------------------------
# 阶段1：初始化日志系统（Day8）
# 作用：统一格式化打印训练信息、数据信息，保存运行记录
# --------------------------
logging.basicConfig(
    level=logging.INFO, # 日志级别：只打印INFO及以上重要信息
    format="%(asctime)s %(message)s" # 日志格式：打印时间 + 内容
)
logger = logging.getLogger()
# 创建日志实例，后续所有打印统一用logger.info()，不使用print

# --------------------------
# 阶段2：Pandas构建+清洗数据（Day13 Day14核心）
# 模拟短信数据集
# --------------------------
def create_clean_data():
    # 1. 构造原始字典数据，key=列名，value=整列数据
    data = {
        "sms":["恭喜你中奖","在吗吃饭吗","免费领取礼包","今天天气不错","限时免费话费","晚上一起学习"],
        "label":[1,0,1,0,1,0] # 标签：1=垃圾短信，0=正常短信
    }
    # 2. 字典转为Pandas表格DataFrame，Day13核心知识点
    df = pd.DataFrame(data)

    # 3. 数据清洗操作（Day14 数据清洗全套）
    df = df.drop_duplicates()   # 删除完全重复的样本行，避免重复训练
    df = df.dropna()            # 删除存在空值的行，脏数据过滤
    # 打印清洗后的完整表格
    logger.info("清洗后数据：\n"+str(df))

    # 4. 数据可视化（Day15 Matplotlib绘图）
    plt.rcParams["font.sans-serif"] = ["SimHei"] # 解决图表中文乱码
    df["label"].value_counts().plot(kind="bar") # 统计0/1标签数量，画柱状图
    plt.title("垃圾/正常短信数量分布") # 图表标题
    plt.show() # 弹出图表窗口

    # 返回清洗完毕的干净表格，交给后续词表构建、数据集加载
    return df

# --------------------------
# 字典构建：文字转数字（为Day26 Embedding做准备）
# 核心逻辑：计算机只识别数字，汉字必须映射成唯一数字索引
# --------------------------
def build_vocab(df):
    # 初始化词表字典：key=汉字，value=数字编号
    # <PAD> 特殊占位符，编号固定0，用来填充短句补齐长度
    vocab = {"<PAD>":0}
    # 第一层循环：遍历表格里每一条短信sent
    for sent in df["sms"]:
        # 第二层循环：遍历单条短信里的每一个汉字word
        for word in sent:
            # 判断：当前汉字不在词表里，就分配新编号
            if word not in vocab:
                # len(vocab) = 当前词表已有字符总数，作为新字符的唯一ID
                vocab[word] = len(vocab)
    # 遍历全部文字后，返回完整映射字典
    return vocab
# 初始vocab = {"<PAD>":0}，长度 = 1
# 读到第一个汉字恭：不在字典，vocab["恭"]=1，字典长度变为 2
# 读到第二个汉字喜：不在字典，vocab["喜"]=2，字典长度变为 3
# 以此类推，每个独一汉字拥有专属数字。

# --------------------------
# 阶段3：自定义数据集 Dataset（Day22）
# 作用：把Pandas表格数据转为模型可读取的张量样本，必须继承Dataset父类
# --------------------------
class SmsDataset(Dataset):
    # 构造函数：传入清洗后的表格df、文字数字映射表vocab
    def __init__(self, df, vocab):
        self.df = df     # 保存表格到实例属性
        self.vocab = vocab # 保存词表映射字典

    # 必须实现方法1：__len__，返回数据集总样本数量
    def __len__(self):
        return len(self.df)

    # 必须实现方法2：__getitem__，按下标idx取出单条样本（文本+标签）
    def __getitem__(self, idx):
        # 根据下标取单行短信文本、标签
        text = self.df.iloc[idx]["sms"]
        label = self.df.iloc[idx]["label"]

        # 文字转数字索引列表：遍历句子每个汉字，查表转数字
        idx_list = [self.vocab[w] for w in text]

        # 统一句子长度为10（模型输入维度必须固定）
        if len(idx_list) < 10:
            # 句子不足10个字，末尾补0（对应<PAD>占位符）
            idx_list += [0]*(10-len(idx_list))
        else:
            # 句子超过10个字，只截取前10个字
            idx_list = idx_list[:10]

        # 列表转为torch张量（Day19 Tensor，模型唯一输入格式）
        # 返回一组样本：(文本数字张量, 标签张量)
        return torch.tensor(idx_list), torch.tensor(label)

# --------------------------
# 阶段3：NLP词向量模型（Day26 Embedding + 全连接网络）
# 继承nn.Module：所有神经网络的标准父类 Day21
# --------------------------
class SmsModel(nn.Module):
    # 构造函数：vocab_size=词表里所有字符总数量
    def __init__(self, vocab_size):
        super().__init__() # 固定写法：调用父类nn.Module构造方法
        # Day26 词向量核心层
        # num_embeddings=词表总大小；embedding_dim=每个汉字映射为16维语义向量
        self.emb = nn.Embedding(num_embeddings=vocab_size, embedding_dim=16)
        # Day21 全连接线性层1：输入16维向量，输出8维特征
        self.fc1 = nn.Linear(16,8)
        # Day21 全连接线性层2：输入8维特征，输出2分类（0/1）
        self.fc2 = nn.Linear(8,2)
        # 激活函数ReLU：给网络增加非线性，否则无法学习复杂语义
        self.relu = nn.ReLU()

    # forward函数：定义数据前向传播流程，调用模型实例时自动执行（不能改名）
    def forward(self,x):
        # 步骤1：数字索引 → 16维语义词向量（Embedding核心作用 Day26）
        x = self.emb(x)
        # 步骤2：对一句话所有字向量求平均值，得到整句统一向量
        # dim=1：沿着单词维度做平均，保留batch维度
        x = torch.mean(x,dim=1)
        # 步骤3：第一层全连接+激活
        x = self.relu(self.fc1(x))
        # 步骤4：第二层全连接，输出2个分类分数
        out = self.fc2(x)
        return out

# --------------------------
# 阶段3：标准训练四步循环（Day23核心万能模板）
# 整合：数据准备、数据集加载、模型初始化、训练、保存、推理
# --------------------------
def train():
    # ========== 1.数据准备（阶段2 Pandas） ==========
    df = create_clean_data() # 调用函数生成清洗后的表格
    vocab = build_vocab(df)  # 根据表格构建文字数字映射表

    # ========== 2.数据集批量加载（Day22 Dataset+DataLoader） ==========
    dataset = SmsDataset(df, vocab) # 实例化自定义数据集
    # DataLoader：按批次打包样本，batch_size=一批2条，shuffle=True每轮打乱数据
    loader = DataLoader(dataset, batch_size=2, shuffle=True)

    # ========== 3.设备、模型、损失函数、优化器初始化（Day19/20/21） ==========
    # 自动判断设备：有GPU用cuda加速，无GPU用cpu运行
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    # 实例化网络模型，搬运到对应设备(GPU/CPU)
    model = SmsModel(len(vocab)).to(device)
    # 损失函数：CrossEntropy交叉熵，二分类任务专用损失 Day18损失函数概念
    loss_fn = nn.CrossEntropyLoss()
    # 优化器Adam：自动更新模型权重，lr=学习率0.001 Day20梯度下降
    opt = torch.optim.Adam(model.parameters(), lr=1e-3)

    # ========== 4.训练循环（Day23 AI万能四步循环，所有模型通用） ==========
    # epoch=10：完整遍历全部数据集10轮
    for epoch in range(10):
        model.train() # 切换模型为训练模式，开启梯度计算
        total_loss = 0 # 记录一轮训练所有批次损失总和
        # 循环遍历DataLoader每一批数据
        for batch_x, batch_y in loader:
            # 把批量文本、批量标签全部搬运到GPU/CPU设备
            batch_x, batch_y = batch_x.to(device), batch_y.to(device)

            opt.zero_grad()       # ①梯度清零：梯度会自动累加，每轮必须清空
            pred = model(batch_x) # ②前向传播：输入数据，模型输出分类预测分数
            loss = loss_fn(pred, batch_y) # 计算预测值和真实标签的差距（损失）
            loss.backward()       # ③反向传播：自动链式求导，计算所有参数梯度 Day20
            opt.step()            # ④参数更新：依靠梯度、学习率修改模型权重

            total_loss += loss.item() # item()把张量loss转为普通数字，累加总损失

        # 打印本轮平均损失，损失持续下降代表模型在学习
        logger.info(f"Epoch{epoch+1} Loss:{total_loss:.3f}")

    # ========== 5.模型权重保存（Day21 模型保存加载） ==========
    # state_dict()只保存网络权重，不保存代码，文件体积更小
    torch.save(model.state_dict(), "sms_model.pth")
    logger.info("模型保存完成")

    # ========== 6.推理预测（Day24 模型推理流程） ==========
    model.eval() # 切换模型为评估推理模式，关闭训练专用逻辑
    with torch.no_grad(): # 上下文管理器：全程不计算梯度，节省显存、提升速度
        test_text = "免费领取" # 待预测测试短信
        # 测试文字转为数字索引列表
        idx_list = [vocab[w] for w in test_text]
        # 补齐到固定长度10，不足补0
        idx_list += [0]*(10-len(idx_list))
        # 转为张量，unsqueeze(0)手动增加batch维度，模型输入必须带批次维度
        x = torch.tensor(idx_list).unsqueeze(0).to(device)
        out = model(x) # 输入模型得到预测分数
        res = torch.argmax(out,dim=1).item() # argmax取分数最大的下标，即预测类别
        # 判断输出文字结果
        logger.info(f"测试短信：{test_text} → 预测结果：{'垃圾短信' if res==1 else '正常短信'}")

if __name__ == "__main__":
    train()