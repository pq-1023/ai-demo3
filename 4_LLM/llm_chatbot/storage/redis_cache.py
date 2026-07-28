# RedisChatCache 会话缓存工具
import json
import redis
from typing import List, Dict, Optional
from config.settings import REDIS_HOST, REDIS_PORT, REDIS_DB, REDIS_TTL, REDIS_KEY_PREFIX


class RedisChatCache:
    """Redis会话缓存工具，冷热分离缓存层"""
    def __init__(self):
        self.r = redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            db=REDIS_DB,
            decode_responses=True
        )
        self.TTL_SECONDS = REDIS_TTL
        self.KEY_PREFIX = REDIS_KEY_PREFIX

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