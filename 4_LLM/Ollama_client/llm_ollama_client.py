import requests
from typing import Optional, Tuple
class OllamaClient:
    """本地Ollama统一调用客户端"""
    def __init__(self, model_name: str):
        self.url = "http://127.0.0.1:11434/api/chat"
        self.model_name = model_name
        self.timeout = 60

    def chat(
        self,
        prompt: str,
        temperature: Optional[float] = 0.7
    ) -> Tuple[bool, str]:
        """
        单轮对话
        :param prompt: 用户提问
        :param temperature: 随机性 0~1
        :return: (成功标记, 回答文本/错误信息)
        """
        body = {
            "model": self.model_name,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": temperature,
            "stream": False
        }

        try:
            resp = requests.post(
                url=self.url,
                json=body,
                timeout=self.timeout
            )
            resp.raise_for_status()
            data = resp.json()
        except requests.exceptions.Timeout:
            return False, "请求超时，请检查Ollama是否正常运行"
        except requests.exceptions.ConnectionError:
            return False, "连接失败！确认Ollama后台已经启动"
        except Exception as e:
            return False, f"网络请求异常：{str(e)}"

        # 解析返回结果
        try:
            content = data["message"]["content"].strip()
            return True, content
        except Exception as e:
            return False, f"返回数据解析失败：{str(e)}，原始响应：{data}"


if __name__ == "__main__":
    # 实例化客户端，填入你本地模型名称
    client = OllamaClient(model_name="qwen2.5:3b-instruct-q4_K_M")

    question = "你好"
    ok, result = client.chat(question, temperature=0.6)

    if ok:
        print("====模型回答====")
        print(result)
    else:
        print("调用失败：", result)

# 交互式持续提问（追加到main下方测试）
if __name__ == "__main__":
    client = OllamaClient(model_name="qwen2.5:3b-instruct-q4_K_M")
    print("输入问题进行提问，输入 exit 退出\n")
    while True:
        user_input = input("你：")
        if user_input.strip().lower() == "exit":
            break
        success, ans = client.chat(user_input)
        if success:
            print("AI：", ans, "\n")
        else:
            print("错误：", ans, "\n")