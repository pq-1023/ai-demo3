# ========== 9. 并发基础 - 多线程 & 线程池 ==========

# 多线程：同一进程内多个任务并发执行，适合网络 IO 请求（接口调用、爬虫）
# ThreadPoolExecutor 线程池：统一管理线程
# 预先创建指定数量线程，复用线程，不用反复新建销毁
# with语句自动关闭线程池，不用手动 shutdown
# map：批量传参、自动分配任务，写法最简
from concurrent.futures import ThreadPoolExecutor
import requests

# 单个任务：访问链接
def request_url(url):
    resp = requests.get(url, timeout=5)
    print(f"请求 {url} 完成，状态码：{resp.status_code}")

# 测试地址
url_list = [
    "https://www.baidu.com",
    "https://www.baidu.com",
    "https://www.baidu.com"
]

# 创建线程池，最大并发数3
# 必须加 if __name__ == '__main__'：windows系统多进程/线程规范写法
if __name__ == "__main__":
    # max_workers：最大并发线程数
    with ThreadPoolExecutor(max_workers=3) as pool:
        # map(任务函数, 参数可迭代对象)，自动遍历列表分配任务
        pool.map(request_url, url_list)
    print("所有并发任务执行完毕")