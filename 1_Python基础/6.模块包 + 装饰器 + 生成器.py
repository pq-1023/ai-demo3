# ========== 6. 模块包 + 装饰器 + 生成器 ==========

# 装饰器：不修改原函数代码，给函数新增功能，AI 框架、日志、权限大量使用
# 生成器：yield 关键字，按需生成数据，节省内存，适合海量数据遍历

# ========== 1. 装饰器（任务重点） ==========
# 定义装饰器：给函数增加「执行前后日志」功能
def log_decorator(func):
    # 内层函数：包装原函数
    def wrapper():
        print("【日志】函数开始执行")
        func()
        print("【日志】函数执行结束")
    return wrapper

# 使用装饰器 @装饰器名
@log_decorator
def business_func():
    print("执行业务逻辑：数据处理")

# 调用函数
business_func()

# ========== 2. 生成器 yield ==========
def num_generator(max_num):
    n = 0
    while n < max_num:
        yield n   # 暂停并返回值，下次迭代继续执行
        n += 1

# 遍历生成器
g = num_generator(5)
print("\n生成器输出：")
for x in g:
    print(x)