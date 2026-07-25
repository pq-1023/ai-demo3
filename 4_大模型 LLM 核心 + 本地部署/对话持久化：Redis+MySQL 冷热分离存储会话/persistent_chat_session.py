import json
import uuid
import requests
import redis
import pymysql
from typing import Optional, Tuple, List, Dict
# ---------------------- 1. Ollama客户端（沿用之前） ----------------------
class OllamaClient:
    def __init__(self, model_name: str):
        self.url = "http://127.0.0.1:11434/api/chat"
        self.model_name = model_name
        self.timeout = 60

    def chat(self, messages: List[Dict], temperature: float = 0.7) -> Tuple[bool, str]:
        body = {
            "model": self.model_name,
            "messages": messages,
            "temperature": temperature,
            "stream": False
        }
        try:
            resp = requests.post(self.url, json=body, timeout=self.timeout)
            resp.raise_for_status()
            data = resp.json()
        except requests.exceptions.ConnectionError:
            return False, "Ollama未启动"
        except Exception as e:
            return False, f"请求异常:{str(e)}"
        try:
            content = data["message"]["content"].strip()
            return True, content
        except Exception as e:
            return False, f"解析失败:{str(e)}"


# ---------------------- 2. Redis工具类：缓存会话热数据 ----------------------
class RedisChatCache:
    def __init__(self):
        # 连接本地redis
        self.r = redis.Redis(
            host="127.0.0.1",
            port=6379,
            db=2,
            decode_responses=True  # Redis 默认返回 bytes 字节串；开启后直接返回字符串，不用手动decode()
        )
        self.TTL_SECONDS = 3600 * 2  # 会话缓存2小时过期
        self.KEY_PREFIX = "chat:session:"  # Redis 键前缀，用来区分业务数据，防止 key 冲突

    def _get_key(self, session_id: str):
        return self.KEY_PREFIX + session_id  # 内部私有方法，自动拼接完整 Redis key

    # 写入完整消息列表
    def set_messages(self, session_id: str, messages: List[Dict]):
        key = self._get_key(session_id)
        # json.dumps()：Python 列表字典 → JSON 字符串（Redis 只能存字符串）
        # ensure_ascii=False：保证中文不会被转义
        data = json.dumps(messages, ensure_ascii=False)
        self.r.setex(key, self.TTL_SECONDS, data)  # setex(key,过期时间,值)：写入同时设置过期时间

    # 读取消息列表
    def get_messages(self, session_id: str) -> Optional[List[Dict]]:
        key = self._get_key(session_id)
        raw = self.r.get(key)  # self.r.get(key) 获取字符串
        if raw is None:  # 拿到None代表缓存不存在（缓存失效）
            return None
        return json.loads(raw)  # json.loads()：字符串转回 Python 消息列表

    # 删除指定会话缓存，代码里暂时没有调用，预留扩展。
    def delete(self, session_id: str):
        self.r.delete(self._get_key(session_id))

# ---------------------- 3. MySQL持久化工具类 ----------------------
class MysqlChatStore:
    def __init__(self):
        self.conn = pymysql.connect(
            host="127.0.0.1",
            port=3306,
            user="root",
            password="123456",
            database="llm_chat",
            charset="utf8mb4"
        )

    def create_session(self, session_id: str, user_id: str):
        """创建会话元数据"""
        cur = self.conn.cursor()  # 创建游标 cursor，所有 SQL 语句都靠游标执行，可以理解成 “执行 SQL 的工具”。
        sql = """INSERT IGNORE INTO chat_session(session_id,user_id) VALUES(%s,%s)  """
        # %s 是 pymysql 的占位符，不是字符串格式化！防止 SQL 注入
        cur.execute(sql, (session_id, user_id))  # cur.execute(sql, (session_id, user_id))把两个参数传入 SQL，执行插入。
        self.conn.commit()  # MySQL 默认事务模式，不 commit，数据不会真正写入硬盘。
        # 执行时机：新建会话的时候调用，往 chat_session 表插入一行会话信息。

    def add_message(self, session_id: str, role: str, content: str):
        """新增一条消息记录"""
        cur = self.conn.cursor()
        sql = """INSERT INTO chat_message(session_id,role,content) VALUES(%s,%s,%s)"""
        cur.execute(sql, (session_id, role, content))
        self.conn.commit()

    def load_all_messages(self, session_id: str) -> List[Dict]:
        """从数据库加载该会话全部历史消息（缓存失效时使用）"""
        cur = self.conn.cursor(pymysql.cursors.DictCursor)
        sql = """SELECT role,content FROM chat_message WHERE session_id=%s ORDER BY create_time ASC"""
        cur.execute(sql, (session_id,))
        rows = cur.fetchall()
        msgs = [{"role": r["role"], "content": r["content"]} for r in rows]
        return msgs

    def close(self):
        self.conn.close()


# ---------------------- 4. 持久化会话管理器【核心】 ----------------------
class PersistentChatSession:
    def __init__(
            self,
            ollama_client: OllamaClient,#调用大模型的客户端
            redis_cache: RedisChatCache,
            mysql_store: MysqlChatStore,
            user_id: str,
            session_id: Optional[str] = None,
            max_turn: int = 4
    ):
        self.client = ollama_client
        self.cache = redis_cache
        self.db = mysql_store
        self.user_id = user_id
        self.max_turn = max_turn

        # 没有传入session_id → 创建全新会话
        if session_id is None:
            self.session_id = str(uuid.uuid4())
            self.db.create_session(self.session_id, self.user_id) #self.db.create_session() → 在 MySQL chat_session 表插入这条会话元数据
            # 初始化系统提示词
            self.messages = [
                {"role": "system", "content": "你是简洁清晰的AI助手。"}
            ]
            self.cache.set_messages(self.session_id, self.messages)
        else:
            self.session_id = session_id
            # 优先读取Redis缓存
            self.messages = self.cache.get_messages(self.session_id)
            if self.messages is None:
                # 缓存失效，从MySQL加载历史消息
                print("缓存未命中，从MySQL加载会话历史")
                self.messages = self.db.load_all_messages(self.session_id)
                if not self.messages:
                    # 数据库也无记录，新建
                    self.messages = [{"role": "system", "content": "你是简洁清晰的AI助手。"}]
                # 回填Redis缓存
                self.cache.set_messages(self.session_id, self.messages)

    def _truncate_history(self):
        """上下文截断，沿用Day35逻辑"""
        while (len(self.messages) - 1) // 2 > self.max_turn:
            del self.messages[1]
            del self.messages[1]

    def send(self, user_text: str) -> Tuple[bool, str]:
        # 1.追加用户消息
        self.messages.append({"role": "user", "content": user_text})
        self._truncate_history()
        # 2.调用模型
        ok, reply = self.client.chat(self.messages)
        if ok:
            self.messages.append({"role": "assistant", "content": reply})
            # ===== 双写：更新Redis + 写入MySQL =====
            self.cache.set_messages(self.session_id, self.messages)
            self.db.add_message(self.session_id, "user", user_text)
            self.db.add_message(self.session_id, "assistant", reply)
        return ok, reply


# ---------------------- 程序入口测试 ----------------------
if __name__ == "__main__":
    # 初始化底层组件
    ollama = OllamaClient("qwen2.5:3b-instruct-q4_K_M")
    redis_cache = RedisChatCache()
    mysql_db = MysqlChatStore()

    # ========== 关键演示 ==========
    # 第一次运行：不传入session_id，自动新建会话
    session = PersistentChatSession(
        ollama_client=ollama,
        redis_cache=redis_cache,
        mysql_store=mysql_db,
        user_id="user_001"
    )
    print(f"当前会话ID：{session.session_id}")
    sid = session.session_id

    print("====开始对话，输入exit退出====")
    while True:
        inp = input("你：")
        if inp.lower() == "exit":
            break
        success, ans = session.send(inp)
        if success:
            print(f"AI：{ans}\n")
        else:
            print(f"错误：{ans}\n")

    mysql_db.close()

    """
    【重启程序测试持久化】
    把上面代码注释，启用下面代码，填入刚才打印的session_id
    程序重启后，依然可以读取历史对话！
    session = PersistentChatSession(
        ollama_client=ollama,
        redis_cache=redis_cache,
        mysql_store=redis_cache,
        mysql_store=mysql_db,
        user_id="user_001",
        session_id="复制刚才输出的sid"
    )
    """
