# ========== 7. 网络请求 requests ==========

# requests：Python 第三方 HTTP 请求库，AI 对接大模型 API 必用（调用文心、通义、OpenAI 接口全靠它），替代繁琐原生urllib
# GET：查询数据、参数拼在 URL 后面（接口查数据）
# POST：提交数据、放请求体（AI 传提示词 prompt 基本全用 POST）

# 四个高频参数（AI 接口标配）
# url：接口地址
# params：GET 专用，拼接 URL 查询参数
# json：POST 专用，传 JSON 格式请求体（大模型 prompt、入参都放这里）
# headers：请求头，AI 接口必填Authorization: Bearer 密钥token

# resp.status_code：状态码，200=请求成功
# resp.json()：自动把返回 JSON 字符串 → Python 字典（AI 返回结构化数据首选）
# resp.text：原始文本（非 JSON 接口用）
import requests

# 公开免费测试API（可直接调用）
url = "https://httpbin.org/get"

# ========== 1. GET 请求 + 带参数 ==========
params = {"name": "AI", "age": 22}
resp = requests.get(url, params=params)

print("状态码：", resp.status_code)
# 解析JSON数据（字典）
result = resp.json()
print("接口返回数据：", result["args"])

# ========== 2. POST 请求 ==========
post_url = "https://httpbin.org/post"
json_body = {"title": "测试数据", "content": "Python请求"}
resp2 = requests.post(post_url, json=json_body)
print("\nPOST返回：", resp2.json()["json"])
