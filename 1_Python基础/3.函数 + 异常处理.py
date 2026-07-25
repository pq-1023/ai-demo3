# ========== 3.函数 + 异常处理 ==========

# 函数：def 关键字定义，无需返回值类型声明:
# 1.缺省参数：参数设置默认值，调用时可省略
# 2.返回值：return，可返回单个 / 多个数据

# 异常处理：try-except-finally，捕获运行时错误，类比 Java try-catch-finally:
# 1.try：执行可能报错的代码
# 2.except：捕获指定异常并处理
# 3.finally：无论是否报错，一定会执行

# ========== 1. 基础函数 + 缺省参数 ==========
# b=0 为缺省参数，不传参时默认使用0
def add(a, b=0):
    return a + b

print(add(3, 5))
print(add(3))  # 只传a，b使用默认值0

# ========== 2. 封装工具函数（任务要求） ==========
# 工具1：判断字符串是否为空
def str_is_empty(s):
    if s is None or len(s.strip()) == 0:
        return True
    return False

# 工具2：数字平方计算
def square(num):
    return num ** 2

# ========== 3. 异常处理 try-except ==========
def test_exception():
    try:
        # 强制转数字，非数字会触发 ValueError
        text = "abc"
        num = int(text)
        print(num)
    except ValueError as e:
        print(f"类型转换异常：{e}")
    except Exception as e:
        # 捕获所有未知异常
        print(f"通用异常：{e}")
    finally:
        print("代码执行完毕")

# 调用测试
print(str_is_empty("   "))
print(square(6))
test_exception()