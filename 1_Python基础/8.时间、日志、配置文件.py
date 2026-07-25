# ========== 8. 时间、日志、配置文件 ==========

# datetime：处理日期、时间戳、时间格式化
# logging：标准日志库，分级打印日志（INFO/ERROR），替代 print 做正式脚本
# configparser：读取 ini 配置文件，把接口地址、密钥等抽离配置，硬编码解耦

import logging
from datetime import datetime
from configparser import ConfigParser

# ========== 1. 日志配置 ==========
logging.basicConfig(
    # level：日志输出等级，INFO及以上才打印
    level=logging.INFO,
    # format：日志输出格式：时间-级别-日志内容
    format="%(asctime)s - %(levelname)s - %(message)s",
    # datefmt：自定义时间格式
    datefmt="%Y-%m-%d %H:%M:%S"
)
# 不同级别日志输出
logging.debug("调试信息，level=INFO时不输出")
logging.info("程序启动")
logging.warning("普通警告信息")
logging.error("错误示例")

# ========== 2. 时间处理 ==========
now = datetime.now()
# strftime：时间对象→格式化字符串
now_str = now.strftime("%Y-%m-%d %H:%M:%S")
print("当前格式化时间：", now_str)
# 拓展：时间转时间戳
timestamp = now.timestamp()
print("当前时间戳：", timestamp)

# ========== 3. 读取 ini 配置文件 ==========
cfg = ConfigParser()
# 加载配置文件，utf-8防止中文乱码
cfg.read("config.ini", encoding="utf-8")
# 读取配置项
# get(区块名, key) 读取字符串
api_url = cfg.get("API", "url")
app_name = cfg.get("APP", "name")
# getint：读取数字类型配置
timeout = cfg.getint("API", "timeout")
version = cfg.get("APP", "version")
print("读取配置-接口地址：", api_url)
print("读取配置-应用名：", app_name)
print("读取配置-超时时间：", timeout, type(timeout))