"""
Anthropic LLM 客户端
支持 Claude API
"""
from typing import List, Optional, AsyncIterator
from loguru import logger

try:
    from anthropic import AsyncAnthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    logger.warning("anthropic package not available")
    ANTHROPIC_AVAILABLE = False

from .base import BaseLLM, Message, LLMResponse


class AnthropicClient(BaseLLM):
    """Anthropic Claude LLM 客户端"""

    def __init__(
        self,
        api_key: str,
        base_url: Optional[str] = None,
        model: str = "claude-3-5-sonnet-20241022",
        temperature: float = 0.7,
        max_tokens: int = 2000,
    ):
        """
        初始化 Anthropic 客户端

        Args:
            api_key: Anthropic API 密钥
            base_url: API 基础 URL
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

        if not ANTHROPIC_AVAILABLE:
            raise RuntimeError("anthropic package not available")

        # 创建客户端
        client_kwargs = {"api_key": self.api_key}
        if self.base_url:
            client_kwargs["base_url"] = self.base_url

        self.client = AsyncAnthropic(**client_kwargs)

    def _convert_messages(self, messages: List[Message]) -> tuple[str, List[dict]]:
        """
        转换消息格式为 Anthropic 格式
        Anthropic 要求 system 消息单独传递

        Args:
            messages: 消息列表

        Returns:
            (system_prompt, anthropic_messages)
        """
        system_prompt = ""
        anthropic_messages = []

        for msg in messages:
            if msg.role == "system":
                system_prompt = msg.content
            else:
                anthropic_messages.append({
                    "role": msg.role,
                    "content": msg.content
                })

        return system_prompt, anthropic_messages

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
            system_prompt, anthropic_messages = self._convert_messages(messages)

            # 构建请求参数
            request_params = {
                "model": self.model,
                "messages": anthropic_messages,
                "temperature": temperature or self.temperature,
                "max_tokens": max_tokens or self.max_tokens,
            }

            if system_prompt:
                request_params["system"] = system_prompt

            # 调用 API
            response = await self.client.messages.create(**request_params)

            # 解析响应
            content = ""
            if response.content:
                content = response.content[0].text if response.content else ""

            return LLMResponse(
                content=content,
                model=response.model,
                usage={
                    "prompt_tokens": response.usage.input_tokens,
                    "completion_tokens": response.usage.output_tokens,
                    "total_tokens": response.usage.input_tokens + response.usage.output_tokens,
                },
                finish_reason=response.stop_reason,
            )

        except Exception as e:
            logger.error(f"Anthropic API error: {e}")
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
            system_prompt, anthropic_messages = self._convert_messages(messages)

            # 构建请求参数
            request_params = {
                "model": self.model,
                "messages": anthropic_messages,
                "temperature": temperature or self.temperature,
                "max_tokens": max_tokens or self.max_tokens,
            }

            if system_prompt:
                request_params["system"] = system_prompt

            # 调用流式 API
            async with self.client.messages.stream(**request_params) as stream:
                async for text in stream.text_stream:
                    yield text

        except Exception as e:
            logger.error(f"Anthropic streaming error: {e}")
            raise