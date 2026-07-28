# 程序入口、控制台交互# 部署文档（Day42完善）
from core.llm_client import LlmClient
from core.session_manager import PersistentChatSession
from storage.redis_cache import RedisChatCache
from storage.mysql_store import MysqlChatStore
from config.settings import DEFAULT_MODEL


def print_help():
    help_text = """
========== 指令说明 ==========
/new          创建全新会话
/load sid     加载指定历史会话
/model name   切换模型，例 /model qwen2.5:7b
exit          退出程序
==============================
"""
    print(help_text)


if __name__ == "__main__":
    # 初始化底层工具
    redis_cache = RedisChatCache()
    mysql_db = MysqlChatStore()
    llm_client = LlmClient(DEFAULT_MODEL)

    # 新建默认会话
    session = PersistentChatSession(
        llm_client=llm_client,
        redis_cache=redis_cache,
        mysql_store=mysql_db,
        user_id="user_001"
    )
    print(f"✅ 会话ID：{session.session_id}（保存ID用于后续恢复）")
    print_help()

    try:
        while True:
            user_input = input("\n你：").strip()
            if not user_input:
                continue

            # 指令处理
            if user_input.lower() == "exit":
                print("程序退出")
                break
            elif user_input == "/new":
                session = PersistentChatSession(
                    llm_client=llm_client,
                    redis_cache=redis_cache,
                    mysql_store=mysql_db,
                    user_id="user_001"
                )
                print(f"✅ 创建新会话，ID：{session.session_id}")
                continue
            elif user_input.startswith("/load "):
                sid = user_input.replace("/load ", "").strip()
                session = PersistentChatSession(
                    llm_client=llm_client,
                    redis_cache=redis_cache,
                    mysql_store=mysql_db,
                    user_id="user_001",
                    session_id=sid
                )
                print(f"✅ 成功加载会话：{session.session_id}")
                continue
            elif user_input.startswith("/model "):
                model_name = user_input.replace("/model ", "").strip()
                llm_client.switch_model(model_name)
                print(f"✅ 已切换模型：{model_name}")
                continue

            # 正常流式对话
            print("AI：", end="", flush=True)
            for chunk in session.stream_send(user_input):
                print(chunk, end="", flush=True)
            print()
    finally:
        mysql_db.close()