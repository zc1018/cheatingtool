"""
Ollama LLM 客户端
支持本地 Ollama 模型
"""
from typing import List, Optional, AsyncIterator
import httpx
from loguru import logger

from .base import BaseLLM, Message, LLMResponse


class OllamaClient(BaseLLM):
    """Ollama 本地 LLM 客户端"""

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "http://localhost:11434",
        model: str = "llama2",
        temperature: float = 0.7,
        max_tokens: int = 2000,
    ):
        """
        初始化 Ollama 客户端

        Args:
            api_key: API 密钥（Ollama 不需要，保留用于接口一致性）
            base_url: Ollama 服务地址
            model: 模型名称
            temperature: 温度参数
            max_tokens: 最大 token 数
        """
        super().__init__(
            api_key=api_key,
            base_url=base_url,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        self.client = httpx.AsyncClient(timeout=60.0)

    def validate_config(self) -> bool:
        """
        验证配置
        Ollama 不需要 API key

        Returns:
            配置是否有效
        """
        if not self.model:
            logger.error("Ollama: Model is required")
            return False
        if not self.base_url:
            logger.error("Ollama: Base URL is required")
            return False
        return True

    async def chat(
        self,
        messages: List[Message],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> LLMResponse:
        """
        对话补全

        Args:
            messages: 消息列表
            temperature: 温度参数
            max_tokens: 最大 token 数

        Returns:
            LLM 响应
        """
        if not self.validate_config():
            raise ValueError("Invalid configuration")

        try:
            # 转换消息格式
            ollama_messages = [msg.to_dict() for msg in messages]

            # 构建请求
            request_data = {
                "model": self.model,
                "messages": ollama_messages,
                "stream": False,
                "options": {
                    "temperature": temperature or self.temperature,
                    "num_predict": max_tokens or self.max_tokens,
                }
            }

            # 调用 API
            response = await self.client.post(
                f"{self.base_url}/api/chat",
                json=request_data,
            )
            response.raise_for_status()

            # 解析响应
            data = response.json()
            return LLMResponse(
                content=data.get("message", {}).get("content", ""),
                model=data.get("model", self.model),
                usage={
                    "prompt_tokens": data.get("prompt_eval_count", 0),
                    "completion_tokens": data.get("eval_count", 0),
                    "total_tokens": data.get("prompt_eval_count", 0) + data.get("eval_count", 0),
                },
                finish_reason=data.get("done_reason", "stop"),
            )

        except httpx.HTTPError as e:
            logger.error(f"Ollama HTTP error: {e}")
            raise
        except Exception as e:
            logger.error(f"Ollama API error: {e}")
            raise

    async def chat_stream(
        self,
        messages: List[Message],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> AsyncIterator[str]:
        """
        流式对话补全

        Args:
            messages: 消息列表
            temperature: 温度参数
            max_tokens: 最大 token 数

        Yields:
            响应内容片段
        """
        if not self.validate_config():
            raise ValueError("Invalid configuration")

        try:
            # 转换消息格式
            ollama_messages = [msg.to_dict() for msg in messages]

            # 构建请求
            request_data = {
                "model": self.model,
                "messages": ollama_messages,
                "stream": True,
                "options": {
                    "temperature": temperature or self.temperature,
                    "num_predict": max_tokens or self.max_tokens,
                }
            }

            # 调用流式 API
            async with self.client.stream(
                "POST",
                f"{self.base_url}/api/chat",
                json=request_data,
            ) as response:
                response.raise_for_status()

                # 流式读取响应
                async for line in response.aiter_lines():
                    if line.strip():
                        try:
                            import json
                            data = json.loads(line)
                            if "message" in data and "content" in data["message"]:
                                content = data["message"]["content"]
                                if content:
                                    yield content
                        except json.JSONDecodeError:
                            continue

        except httpx.HTTPError as e:
            logger.error(f"Ollama streaming HTTP error: {e}")
            raise
        except Exception as e:
            logger.error(f"Ollama streaming error: {e}")
            raise

    async def close(self):
        """关闭客户端"""
        await self.client.aclose()