# 配置层：所有配置：数据库地址、redis地址、模型默认参数、TTL、最大轮数
# ====================== 全局配置文件 ======================
# MySQL配置
MYSQL_HOST = "127.0.0.1"
MYSQL_PORT = 3306
MYSQL_USER = "root"
MYSQL_PASSWORD = "123456"  # 修改为你自己mysql密码
MYSQL_DB = "llm_chat"

# Redis配置
REDIS_HOST = "127.0.0.1"
REDIS_PORT = 6379
REDIS_DB = 0
REDIS_TTL = 3600 * 2
REDIS_KEY_PREFIX = "chat:session:"

# LLM大模型基础配置
DEFAULT_MODEL = "qwen2.5:3b-instruct-q4_K_M"
OLLAMA_BASE_URL = "http://127.0.0.1:11434/api/chat"
TEMPERATURE = 0.2  # 低温抑制幻觉
MAX_TURN = 4       # 最大保留对话轮数

# 防幻觉系统提示词
SYSTEM_PROMPT = """你是简洁清晰的AI助手。
重要规则：
1. 如果问题你没有确切答案，不要编造内容，直接告知你无法回答；
2. 禁止虚构数据、人名、文献、事件；
3. 回答严格基于已有对话内容，不能凭空猜测；
4. 语言简洁，不要输出无关冗余文字。
"""