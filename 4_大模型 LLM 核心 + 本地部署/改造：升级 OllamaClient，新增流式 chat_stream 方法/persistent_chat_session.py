import json
import uuid
import requests
import redis
import pymysql
from typing import Optional, Tuple, List, Dict, Generator
# ---------------------- 1. OllamaClient 同时支持普通/流式调用 ----------------------
class OllamaClient:
    def __init__(self, model_name: str):
        self.url = "http://127.0.0.1:11434/api/chat"
        self.model_name = model_name
        self.timeout = 60

    def chat(self, messages: List[Dict], temperature: float = 0.7) -> Tuple[bool, str]:
        """非流式：一次性完整返回"""
        body = {
            "model": self.model_name,
            "messages": messages,
            "stream": False
        }
        try:
            resp = requests.post(self.url, json=body, timeout=self.timeout)
            resp.raise_for_status()
            data = resp.json()
            return True, data["message"]["content"].strip()
        except requests.exceptions.ConnectionError:
            return False, "Ollama未启动"
        except Exception as e:
            return False, f"请求异常:{str(e)}"

    def chat_stream(self, messages: List[Dict], temperature: float = 0.7) -> Generator[str, None, None]:
        """Day37 流式生成器"""
        body = {
            "model": self.model_name,
            "messages": messages,
            "stream": True,
            "temperature": temperature
        }

        try:
            resp = requests.post(self.url, json=body, timeout=self.timeout, stream=True)
            resp.raise_for_status()
            # 逐行迭代接收分片
            # iter_lines()：持续读取响应流里面一行一行的数据；
            # decode_unicode=True 直接返回字符串，不用处理字节。
            for line in resp.iter_lines(decode_unicode=True):
                if not line:
                    continue
                chunk = json.loads(line)# 把一行文本 → 转为字典对象，这就是单条分片数据。
                content = chunk["message"]["content"]
                yield content# 吐出片段，外部循环打印
                if chunk.get("done", False):
                    break
        except requests.exceptions.ConnectionError:
            yield "【错误】Ollama未启动"
        except Exception as e:
            yield f"【请求异常】{str(e)}"


# ---------------------- 2. Redis工具类（冷热缓存） ----------------------
class RedisChatCache:
    def __init__(self):
        self.r = redis.Redis(
            host="127.0.0.1",
            port=6379,
            db=2,
            decode_responses=True
        )
        self.TTL_SECONDS = 3600 * 2
        self.KEY_PREFIX = "chat:session:"

    def _get_key(self, session_id: str):
        return self.KEY_PREFIX + session_id

    def set_messages(self, session_id: str, messages: List[Dict]):
        key = self._get_key(session_id)
        data = json.dumps(messages, ensure_ascii=False)
        self.r.setex(key, self.TTL_SECONDS, data)

    def get_messages(self, session_id: str) -> Optional[List[Dict]]:
        raw = self.r.get(self._get_key(session_id))
        if raw is None:
            return None
        return json.loads(raw)

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
        cur = self.conn.cursor()
        sql = "INSERT IGNORE INTO chat_session(session_id,user_id) VALUES(%s,%s)"
        cur.execute(sql, (session_id, user_id))
        self.conn.commit()

    def add_message(self, session_id: str, role: str, content: str):
        cur = self.conn.cursor()
        sql = "INSERT INTO chat_message(session_id,role,content) VALUES(%s,%s,%s)"
        cur.execute(sql, (session_id, role, content))
        self.conn.commit()

    def load_all_messages(self, session_id: str) -> List[Dict]:
        cur = self.conn.cursor(pymysql.cursors.DictCursor)
        sql = """
        SELECT role,content FROM chat_message WHERE session_id=%s ORDER BY create_time ASC
        """
        cur.execute(sql, (session_id,))
        rows = cur.fetchall()
        msgs = [{"role": r["role"], "content": r["content"]} for r in rows]
        return msgs

    def close(self):
        self.conn.close()


# ---------------------- 4. 持久化会话管理器【核心：新增stream_send流式方法】 ----------------------
class PersistentChatSession:
    def __init__(
            self,
            ollama_client: OllamaClient,
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

        if session_id is None:
            self.session_id = str(uuid.uuid4())
            self.db.create_session(self.session_id, self.user_id)
            self.messages = [{"role": "system", "content": "你是简洁清晰的AI助手。"}]
            self.cache.set_messages(self.session_id, self.messages)
        else:
            self.session_id = session_id
            self.messages = self.cache.get_messages(self.session_id)
            if self.messages is None:
                print("缓存未命中，从MySQL加载会话历史")
                self.messages = self.db.load_all_messages(self.session_id)
                if not self.messages:
                    self.messages = [{"role": "system", "content": "你是简洁清晰的AI助手。"}]
                self.cache.set_messages(self.session_id, self.messages)

    def _truncate_history(self):
        while (len(self.messages) - 1) // 2 > self.max_turn:
            del self.messages[1]
            del self.messages[1]

    # 原有：一次性对话（非流式）
    def send(self, user_text: str) -> Tuple[bool, str]:
        self.messages.append({"role": "user", "content": user_text})
        self._truncate_history()
        ok, reply = self.client.chat(self.messages)
        if ok:
            self.messages.append({"role": "assistant", "content": reply})
            self.cache.set_messages(self.session_id, self.messages)
            self.db.add_message(self.session_id, "user", user_text)
            self.db.add_message(self.session_id, "assistant", reply)
        return ok, reply

    # ===================== Day37 新增：流式对话生成器 =====================
    def stream_send(self, user_text: str) -> Generator[str, None, None]:
        """
        流式聊天，逐段yield文字
        ⚠重要：等全部内容接收完毕，才统一持久化
        """
        self.messages.append({"role": "user", "content": user_text})
        self._truncate_history()

        full_reply = ""
        # 循环接收流式片段，向外吐出（打字机效果）
        for piece in self.client.chat_stream(self.messages):
            yield piece
            full_reply += piece

        # 模型生成全部结束后，持久化操作
        self.messages.append({"role": "assistant", "content": full_reply})
        self.cache.set_messages(self.session_id, self.messages)
        self.db.add_message(self.session_id, "user", user_text)
        self.db.add_message(self.session_id, "assistant", full_reply)


# ---------------------- 主程序：流式聊天测试入口 ----------------------
if __name__ == "__main__":
    ollama = OllamaClient("qwen2.5:3b-instruct-q4_K_M")
    redis_cache = RedisChatCache()
    mysql_db = MysqlChatStore()

    # 新建会话
    session = PersistentChatSession(
        ollama_client=ollama,
        redis_cache=redis_cache,
        mysql_store=mysql_db,
        user_id="user_001"
    )
    print(f"✅当前会话ID = {session.session_id}，请保存用于重启恢复！")

    print("====流式聊天 | exit退出 ====")
    while True:
        text = input("\n你：")
        if text.lower() == "exit":
            break

        print("AI：", end="", flush=True)
        # 调用流式方法，循环打印片段
        for chunk in session.stream_send(text):
            print(chunk, end="", flush=True)
        print()

    mysql_db.close()
    """
    # 重启加载历史会话【正确模板】
    session = PersistentChatSession(
        ollama_client=ollama,
        redis_cache=redis_cache,
        mysql_store=mysql_db,
        user_id="user_001",
        session_id="粘贴你控制台打印的sid"
    )
    """


