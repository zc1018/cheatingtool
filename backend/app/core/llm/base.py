"""
LLM (Large Language Model) 抽象基类
定义 LLM 服务的统一接口
"""
from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any, AsyncIterator
from loguru import logger


class Message:
    """对话消息"""

    def __init__(self, role: str, content: str):
        """
        初始化消息

        Args:
            role: 角色 (system, user, assistant)
            content: 消息内容
        """
        self.role = role
        self.content = content

    def to_dict(self) -> Dict[str, str]:
        """转换为字典"""
        return {"role": self.role, "content": self.content}

    def __repr__(self):
        return f"Message(role='{self.role}', content='{self.content[:50]}...')"


class LLMResponse:
    """LLM 响应"""

    def __init__(
        self,
        content: str,
        model: str,
        usage: Optional[Dict[str, int]] = None,
        finish_reason: Optional[str] = None,
    ):
        """
        初始化响应

        Args:
            content: 响应内容
            model: 使用的模型
            usage: Token 使用情况
            finish_reason: 完成原因
        """
        self.content = content
        self.model = model
        self.usage = usage or {}
        self.finish_reason = finish_reason

    def __repr__(self):
        return f"LLMResponse(content='{self.content[:50]}...', model='{self.model}')"


class BaseLLM(ABC):
    """LLM 服务抽象基类"""

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: str = "gpt-4o",
        temperature: float = 0.7,
        max_tokens: int = 2000,
    ):
        """
        初始化 LLM 服务

        Args:
            api_key: API 密钥
            base_url: API 基础 URL
            model: 模型名称
            temperature: 温度参数 (0.0-2.0)
            max_tokens: 最大 token 数
        """
        self.api_key = api_key
        self.base_url = base_url
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens

    @abstractmethod
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
            temperature: 温度参数（覆盖默认值）
            max_tokens: 最大 token 数（覆盖默认值）

        Returns:
            LLM 响应
        """
        pass

    @abstractmethod
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
            temperature: 温度参数（覆盖默认值）
            max_tokens: 最大 token 数（覆盖默认值）

        Yields:
            响应内容片段
        """
        pass

    def validate_config(self) -> bool:
        """
        验证配置

        Returns:
            配置是否有效
        """
        if not self.api_key:
            logger.error(f"{self.__class__.__name__}: API key is required")
            return False
        if not self.model:
            logger.error(f"{self.__class__.__name__}: Model is required")
            return False
        return True

    def create_message(self, role: str, content: str) -> Message:
        """
        创建消息

        Args:
            role: 角色
            content: 内容

        Returns:
            消息对象
        """
        return Message(role=role, content=content)

    def create_system_message(self, content: str) -> Message:
        """创建系统消息"""
        return self.create_message("system", content)

    def create_user_message(self, content: str) -> Message:
        """创建用户消息"""
        return self.create_message("user", content)

    def create_assistant_message(self, content: str) -> Message:
        """创建助手消息"""
        return self.create_message("assistant", content)