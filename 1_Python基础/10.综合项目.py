# ========== 10.综合项目 ==========
import json
import logging
import requests
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from configparser import ConfigParser
from pathlib import Path

# ---------------------- 1.日志初始化（Day8 logging） ----------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# ---------------------- 2.读取ini配置（Day8 configparser） ----------------------
cfg = ConfigParser()
cfg.read("config.ini", encoding="utf-8")
api_url = cfg.get("API", "url")
req_timeout = cfg.getint("API", "timeout")
thread_num = cfg.getint("THREAD", "max_workers")#线程池最大并发数
# 接口地址、超时、线程数写在配置，不用改源代码（解耦，不硬编码）

# ---------------------- 3.单条数据处理任务 ----------------------
def handle_data(item):
    try:
        # 接口请求，参数拼接到url
        resp = requests.get(api_url, params=item, timeout=req_timeout)
        # params自动把字典拼接到url参数
        item["status"] = resp.status_code
        item["result"] = "请求成功"
        item["deal_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S") # Day8 datetime
        return item
    except Exception as e:
        logging.error(f'id:{item["id"]} 请求异常：{str(e)}')
        item["result"] = "请求失败"
        item["deal_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return item
    # 成功 / 失败都新增：status、result、deal_time三个字段

# ---------------------- 4.程序入口 ----------------------
if __name__ == "__main__":
    start_time = datetime.now()
    logging.info("脚本开始执行")

    # 读取本地json数据
    input_path = Path("input.json")
    with open(input_path, "r", encoding="utf-8") as f:
        data_list = json.load(f)
    logging.info(f"读取到{len(data_list)}条待处理数据")

    # 多线程并发处理（Day9 线程池）
    with ThreadPoolExecutor(max_workers=thread_num) as pool:
        result_list = list(pool.map(handle_data, data_list))

    # 结果写入新json
    output_path = Path("output.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result_list, f, ensure_ascii=False, indent=2)

    # 统计耗时
    cost_sec = (datetime.now() - start_time).total_seconds()
    logging.info(f"处理完毕，耗时{cost_sec:.2f}秒，结果存入output.json")