import torch
import torch.nn as nn

# Embedding(词表总大小, 每个词映射多少维向量)
# 词表里一共有10个不同单词，每个词变成3维数字向量
emb = nn.Embedding(num_embeddings=10, embedding_dim=3)

# 文字不能直接进模型，先转成数字索引
word_idx = torch.tensor([1,3,5])
vec = emb(word_idx) # 索引自动查表输出词向量
print("词向量：\n",vec)