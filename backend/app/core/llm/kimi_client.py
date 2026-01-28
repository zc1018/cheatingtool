"""
Kimi LLM 客户端
支持月之暗面 Kimi API
"""
from typing import Optional
from loguru import logger

try:
    from openai import AsyncOpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    logger.warning("openai package not available")
    OPENAI_AVAILABLE = False

from .base import BaseLLM, Message, LLMResponse


class KimiClient(BaseLLM):
    """月之暗面 Kimi LLM 客户端"""

    def __init__(
        self,
        api_key: str,
        base_url: Optional[str] = None,
        model: str = "moonshot-v1-8k",
        temperature: float = 0.7,
        max_tokens: int = 2000,
    ):
        """
        初始化 Kimi 客户端

        Args:
            api_key: Kimi API 密钥
            base_url: API 基础 URL（默认为 Kimi 官方端点）
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

        if not OPENAI_AVAILABLE:
            raise RuntimeError("openai package not available")

        # Kimi 使用兼容 OpenAI 的 API
        self.client = AsyncOpenAI(
            api_key=self.api_key,
            base_url=self.base_url or "https://api.moonshot.cn/v1",
        )

    async def chat(
        self,
        messages: list,
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
            openai_messages = [msg.to_dict() for msg in messages]

            # 调用 API
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=openai_messages,
                temperature=temperature or self.temperature,
                max_tokens=max_tokens or self.max_tokens,
            )

            # 解析响应
            choice = response.choices[0]
            return LLMResponse(
                content=choice.message.content or "",
                model=response.model,
                usage={
                    "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
                    "completion_tokens": response.usage.completion_tokens if response.usage else 0,
                    "total_tokens": response.usage.total_tokens if response.usage else 0,
                },
                finish_reason=choice.finish_reason,
            )

        except Exception as e:
            logger.error(f"Kimi API error: {e}")
            raise

    async def chat_stream(
        self,
        messages: list,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ):
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
            openai_messages = [msg.to_dict() for msg in messages]

            # 调用流式 API
            stream = await self.client.chat.completions.create(
                model=self.model,
                messages=openai_messages,
                temperature=temperature or self.temperature,
                max_tokens=max_tokens or self.max_tokens,
                stream=True,
            )

            # 流式返回内容
            async for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content

        except Exception as e:
            logger.error(f"Kimi streaming error: {e}")
            raise
