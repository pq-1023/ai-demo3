# 统一LLM客户端：封装Ollama/云端API、普通chat、chat_stream流式方法
import json
import requests
from typing import List, Dict, Generator, Tuple
from config.settings import OLLAMA_BASE_URL


class LlmClient:
    """
    统一LLM客户端
    支持：普通一次性输出 / 流式输出
    扩展：后续可兼容OpenAI云端API
    """
    def __init__(self, model_name: str):
        self.url = OLLAMA_BASE_URL
        self.model_name = model_name
        self.timeout = 60

    def switch_model(self, model_name: str):
        """动态切换模型"""
        self.model_name = model_name

    def chat(self, messages: List[Dict], temperature: float = 0.2) -> Tuple[bool, str]:
        """非流式：一次性返回完整回答"""
        body = {
            "model": self.model_name,
            "messages": messages,
            "stream": False,
            "temperature": temperature
        }
        try:
            resp = requests.post(self.url, json=body, timeout=self.timeout)
            resp.raise_for_status()
            data = resp.json()
            return True, data["message"]["content"].strip()
        except requests.exceptions.ConnectionError:
            return False, "【错误】Ollama服务未启动"
        except Exception as e:
            return False, f"【请求异常】{str(e)}"

    def chat_stream(self, messages: List[Dict], temperature: float = 0.2) -> Generator[str, None, None]:
        """流式输出生成器，逐段返回文本"""
        body = {
            "model": self.model_name,
            "messages": messages,
            "stream": True,
            "temperature": temperature
        }
        try:
            resp = requests.post(self.url, json=body, timeout=self.timeout, stream=True)
            resp.raise_for_status()
            for line in resp.iter_lines(decode_unicode=True):
                if not line:
                    continue
                chunk = json.loads(line)
                content = chunk["message"]["content"]
                yield content
                if chunk.get("done", False):
                    break
        except requests.exceptions.ConnectionError:
            yield "【错误】Ollama服务未启动"
        except Exception as e:
            yield f"【请求异常】{str(e)}"