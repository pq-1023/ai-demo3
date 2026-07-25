#====Numpy常用模板====
import numpy as np
def create_rand(shape):
    return np.random.randn(*shape)

#====Pandas数据清洗模板====
import pandas as pd
def clean_csv(path):
    df = pd.read_csv(path)
    df = df.drop_duplicates()
    df = df.fillna(df.mean(numeric_only=True))
    return df

#====绘图模板====
import matplotlib.pyplot as plt
import seaborn as sns
plt.rcParams["font.sans-serif"] = ["SimHei"]
def draw_bar(df,x,y):
    sns.barplot(x=x,y=y,data=df)
    plt.show()