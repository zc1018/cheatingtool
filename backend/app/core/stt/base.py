"""
STT (Speech-to-Text) 抽象基类
定义语音转文字服务的统一接口
"""
from abc import ABC, abstractmethod
from typing import AsyncIterator, Optional
import numpy as np
from loguru import logger


class STTResult:
    """STT 转写结果"""

    def __init__(
        self,
        text: str,
        is_final: bool = False,
        confidence: Optional[float] = None,
        language: Optional[str] = None,
    ):
        self.text = text
        self.is_final = is_final
        self.confidence = confidence
        self.language = language

    def __repr__(self):
        return f"STTResult(text='{self.text}', is_final={self.is_final}, confidence={self.confidence})"


class BaseSTT(ABC):
    """STT 服务抽象基类"""

    def __init__(
        self,
        api_key: Optional[str] = None,
        language: str = "zh",
        model: Optional[str] = None,
    ):
        """
        初始化 STT 服务

        Args:
            api_key: API 密钥
            language: 语言代码 (zh, en, etc.)
            model: 模型名称
        """
        self.api_key = api_key
        self.language = language
        self.model = model
        self.is_connected = False

    @abstractmethod
    async def connect(self) -> bool:
        """
        连接到 STT 服务

        Returns:
            是否连接成功
        """
        pass

    @abstractmethod
    async def disconnect(self) -> None:
        """断开连接"""
        pass

    @abstractmethod
    async def transcribe_stream(
        self, audio_stream: AsyncIterator[np.ndarray]
    ) -> AsyncIterator[STTResult]:
        """
        流式转写音频

        Args:
            audio_stream: 音频数据流

        Yields:
            转写结果
        """
        pass

    @abstractmethod
    async def transcribe_file(self, audio_file: str) -> STTResult:
        """
        转写音频文件

        Args:
            audio_file: 音频文件路径

        Returns:
            转写结果
        """
        pass

    async def __aenter__(self):
        """异步上下文管理器入口"""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器退出"""
        await self.disconnect()

    def validate_config(self) -> bool:
        """
        验证配置

        Returns:
            配置是否有效
        """
        if not self.api_key:
            logger.error(f"{self.__class__.__name__}: API key is required")
            return False
        return True