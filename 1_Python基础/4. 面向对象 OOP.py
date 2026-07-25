# ========== 4.面向对象 OOP ==========

# 1.关键字：class 定义类，和 Java 一致
# 2.构造方法：固定名称 __init__，对应 Java 构造函数
# 3.self：必须作为方法第一个参数，等价于 Java 的 this

# 访问权限：
# 1.公有属性 / 方法：直接定义
# 2.私有属性：双下划线 __ 开头，无 private 关键字

# 继承：子类 (父类) 写法，语法比 Java 更简洁

# ========== 1. 实体类（封装） ==========
class Person:
    # 构造方法：初始化属性
    def __init__(self, name, age):
        self.name = name        # 公有属性
        self.__age = age        # 私有属性（外部无法直接访问）

    # 公有方法：获取私有属性
    def get_age(self):
        return self.__age

    # 普通方法
    def show_info(self):
        print(f"姓名：{self.name}，年龄：{self.__age}")

# 实例化对象
p1 = Person("张三", 22)
p1.show_info()
print("通过方法获取私有年龄：", p1.get_age())

# ========== 2. 继承（工具类继承实体类） ==========
class PersonUtil(Person):
    # 子类新增方法
    def print_name(self):
        print(f"提取姓名：{self.name}")

# 子类实例
util = PersonUtil("李四", 25)
util.show_info()
util.print_name()