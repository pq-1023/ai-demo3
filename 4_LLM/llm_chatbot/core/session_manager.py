# PersistentChatSession 会话管理器（业务核心）
import uuid
from typing import Optional, Tuple, List, Dict, Generator
from core.llm_client import LlmClient
from storage.redis_cache import RedisChatCache
from storage.mysql_store import MysqlChatStore
from config.settings import MAX_TURN, SYSTEM_PROMPT


class PersistentChatSession:
    """持久化会话管理器：冷热分离、多轮对话、流式支持"""
    def __init__(
            self,
            llm_client: LlmClient,
            redis_cache: RedisChatCache,
            mysql_store: MysqlChatStore,
            user_id: str,
            session_id: Optional[str] = None
    ):
        self.client = llm_client
        self.cache = redis_cache
        self.db = mysql_store
        self.user_id = user_id
        self.max_turn = MAX_TURN
        self.messages: List[Dict] = []

        if session_id is None:
            # 创建全新会话
            self.session_id = str(uuid.uuid4())
            self.db.create_session(self.session_id, self.user_id)
            self.messages = [{"role": "system", "content": SYSTEM_PROMPT}]
            self.cache.set_messages(self.session_id, self.messages)
        else:
            # 加载已有会话，优先读取Redis
            self.session_id = session_id
            self.messages = self.cache.get_messages(self.session_id)
            if self.messages is None:
                print("缓存未命中，从MySQL加载会话历史")
                self.messages = self.db.load_all_messages(self.session_id)
                if not self.messages:
                    self.messages = [{"role": "system", "content": SYSTEM_PROMPT}]
                self.cache.set_messages(self.session_id, self.messages)

    def _truncate_history(self):
        """滑动窗口上下文截断，防止token超限"""
        while (len(self.messages) - 1) // 2 > self.max_turn:
            del self.messages[1]
            del self.messages[1]

    def send(self, user_text: str) -> Tuple[bool, str]:
        """普通对话，一次性返回完整结果"""
        self.messages.append({"role": "user", "content": user_text})
        ok, reply = self.client.chat(self.messages)
        if ok:
            self.messages.append({"role": "assistant", "content": reply})
            self._truncate_history()  # 修复：在助手回复添加后再截断
            self.cache.set_messages(self.session_id, self.messages)
            self.db.add_message(self.session_id, "user", user_text)
            self.db.add_message(self.session_id, "assistant", reply)
        return ok, reply

    def stream_send(self, user_text: str) -> Generator[str, None, None]:
        """流式对话生成器，打字机效果"""
        self.messages.append({"role": "user", "content": user_text})
        full_reply = ""
        for piece in self.client.chat_stream(self.messages):
            yield piece
            full_reply += piece
        # 全部接收完成后统一持久化
        self.messages.append({"role": "assistant", "content": full_reply})
        self._truncate_history()  # 修复：在助手回复添加后再截断
        self.cache.set_messages(self.session_id, self.messages)
        self.db.add_message(self.session_id, "user", user_text)
        self.db.add_message(self.session_id, "assistant", full_reply)