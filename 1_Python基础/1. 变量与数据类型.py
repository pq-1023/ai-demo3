# ========== 1. 变量与数据类型 ==========

# 弱类型语言：变量无需声明类型，赋值即定义
# 代码块靠缩进（4 个空格），无 {}，和 Java 最大区别
# 分支：if / elif / else；循环：for / while

# 不用指定类型，自动推断
name = "Python AI"   # 字符串 str
age = 22             # 整数 int
score = 99.5         # 浮点数 float
is_run = True        # 布尔 bool

print(name, age, score, is_run)

# ========== 2. 运算符 ==========
a = 10
b = 3
print(a + b)   # 加法
print(a / b)   # 除法(结果永远浮点) 3.333
print(a // b)  # 整除(取整数部分) 3，对应Java /
print(a % b)   # 取余 1

# ========== 3. 分支判断 if ==========
if age >= 20:
    print("成年人")
elif age >= 16:
    print("青少年")
else:
    print("未成年")

# ========== 4. 循环 ==========
# for 循环：遍历可迭代对象，range(起始,结束,步长)，左闭右开
for i in range(1, 6):
    print(f"for循环：{i}")

# while 循环：条件为真持续执行
count = 0
while count < 3:
    print(f"while循环：{count}")
    count += 1

# 练习1：计算 1~100 累加和
total = 0
for num in range(1, 101):
    total += num
print(f"1-100累加和：{total}")

# 练习2：输入数字，判断奇偶
num = int(input("请输入一个整数："))
if num % 2 == 0:
    print("偶数")
else:
    print("奇数")

# 练习3：循环打印3遍欢迎语
for _ in range(3):
    print("欢迎学习Python AI开发！")
