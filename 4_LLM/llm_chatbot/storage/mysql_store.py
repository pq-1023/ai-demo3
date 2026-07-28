# MysqlChatStore MySQL持久化工具
import pymysql
from typing import List, Dict
from config.settings import MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DB


class MysqlChatStore:
    """MySQL持久化存储层"""
    def __init__(self):
        self.conn = pymysql.connect(
            host=MYSQL_HOST,
            port=MYSQL_PORT,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DB,
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