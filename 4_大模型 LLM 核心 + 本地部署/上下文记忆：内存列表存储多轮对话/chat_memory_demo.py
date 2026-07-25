import requests
from typing import Optional, Tuple, List, Dict
#
# Ollama底层调用客户端
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
            return False, "连接失败，请确认Ollama已启动"
        except requests.exceptions.Timeout:
            return False, "请求超时"
        except Exception as e:
            return False, f"请求异常：{str(e)}"

        try:
            content = data["message"]["content"].strip()
            return True, content
        except Exception as e:
            return False, f"解析失败：{str(e)}"


# 多轮对话管理器（上下文记忆 + 自动截断）
class ChatSession:
    def __init__(self, client: OllamaClient, max_turn: int = 6):
        """
        :param client: ollama调用实例
        :param max_turn: 最大保留多少轮问答（一轮=user+assistant）
        """
        self.client = client
        self.max_turn = max_turn
        # 消息列表，存放完整对话上下文
        self.messages: List[Dict] = [
            {"role": "system", "content": "你是乐于助人的AI助手，回答简洁清晰。"}
        ]

    def _truncate_history(self):
        """
        上下文截断：超出最大轮数，删除最早的对话
        system消息永远保留，只删除后面user+assistant成对消息
        """
        # system消息占1条，剩下都是成对对话
        while (len(self.messages) - 1) // 2 > self.max_turn:
            # 删掉最靠前的一组 user + assistant（两条）
            del self.messages[1]
            del self.messages[1]

    def send(self, user_text: str) -> Tuple[bool, str]:
        # 1. 用户消息加入上下文
        self.messages.append({"role": "user", "content": user_text})

        # 2. 检查并截断超长历史
        self._truncate_history()

        # 3. 请求模型
        ok, reply = self.client.chat(self.messages)

        if ok:
            # 成功，把模型回复存入上下文
            self.messages.append({"role": "assistant", "content": reply})

        return ok, reply


if __name__ == "__main__":
    # 初始化
    ollama_client = OllamaClient(model_name="qwen2.5:3b-instruct-q4_K_M")
    session = ChatSession(client=ollama_client, max_turn=4)

    print("=== 多轮对话机器人 | 输入 exit 退出 ===")
    while True:
        user_input = input("你：")
        if user_input.strip().lower() == "exit":
            print("对话结束")
            break
        success, answer = session.send(user_input)
        if success:
            print(f"AI：{answer}\n")
        else:
            print(f"错误：{answer}\n")