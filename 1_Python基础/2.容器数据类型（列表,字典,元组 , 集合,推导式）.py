# ========== 2.容器数据类型（列表 / 字典 / 元组 / 集合 / 推导式） ==========/

# list 列表 → 对应 ArrayList，有序、可增删改查、允许重复
# dict 字典 → 对应 HashMap，键值对结构，AI 数据处理最常用
# tuple 元组 → 不可变列表，定义后不能修改
# set 集合 → 无序、自动去重，对应 HashSet
# 列表 / 字典推导式：Python 语法糖，快速生成容器，简化循环

# ========== 1. 列表 list ==========
arr = [10, 20, 30, "AI脚本"]
# 增
arr.append(40)
# 删
arr.remove(20)
# 改
arr[0] = 100
# 查
print("列表查询：", arr[1])
print("列表全部：", arr)

# ========== 2. 字典 dict（重点） ==========
# 基础字典
user = {"username": "test", "age": 22}
# 增
user["gender"] = "男"
# 删
del user["age"]
# 改
user["username"] = "ai_dev"
# 查
print("username：", user["username"])
print(user)
print("-----遍历每一组键值对-----")
for key, value in user.items():
    print(f"{key} = {value}")

# 字典嵌套（AI接口返回、结构化数据高频用法）
res_data = {
    "code": 200,
    "msg": "请求成功",
    "data": [
        {"id": 1, "title": "数据1"},
        {"id": 2, "title": "数据2"}
    ]
}
# 多层取值
print("嵌套字典取值：", res_data["data"][0]["title"])

# ========== 3. 元组 tuple 不可变 ==========
t = (1, 2, 3)
print("元组：", t)
# t[0] = 10  报错：元组不允许修改

# ========== 4. 集合 set 自动去重 ==========
s = {1, 1, 2, 2, 3}
print("集合去重：", s)

# ========== 5. 推导式（语法糖） ==========
# 列表推导式：快速生成 0~9 列表
new_list = [x for x in range(10)]
print("列表推导式：", new_list)

# 带条件推导式：只保留偶数
even_list = [x for x in range(10) if x % 2 == 0]
print("条件推导式：", even_list)