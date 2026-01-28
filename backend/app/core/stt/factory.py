"""
STT 工厂模块
根据配置创建对应的 STT 客户端实例
"""
from typing import Optional
from loguru import logger

from .base import BaseSTT
from .elevenlabs import ElevenLabsSTT
from .qwen import QwenAudioSTT


class STTFactory:
    """STT 客户端工厂"""

    @staticmethod
    def create(
        provider: str,
        api_key: str,
        language: str = "zh",
        model: Optional[str] = None,
    ) -> BaseSTT:
        """
        创建 STT 客户端

        Args:
            provider: STT 提供商 (elevenlabs, qwen)
            api_key: API 密钥
            language: 语言代码
            model: 模型名称

        Returns:
            STT 客户端实例

        Raises:
            ValueError: 不支持的提供商
        """
        provider = provider.lower()

        if provider == "elevenlabs":
            model = model or "eleven_multilingual_v2"
            logger.info(f"Creating ElevenLabs STT client with model: {model}")
            return ElevenLabsSTT(
                api_key=api_key,
                language=language,
                model=model,
            )

        elif provider == "qwen":
            model = model or "qwen-audio-turbo"
            logger.info(f"Creating Qwen-Audio STT client with model: {model}")
            return QwenAudioSTT(
                api_key=api_key,
                language=language,
                model=model,
            )

        else:
            raise ValueError(
                f"Unsupported STT provider: {provider}. "
                f"Supported providers: elevenlabs, qwen"
            )

    @staticmethod
    def get_supported_providers() -> list[str]:
        """
        获取支持的 STT 提供商列表

        Returns:
            提供商列表
        """
        return ["elevenlabs", "qwen"]

    @staticmethod
    def get_default_model(provider: str) -> str:
        """
        获取提供商的默认模型

        Args:
            provider: STT 提供商

        Returns:
            默认模型名称
        """
        defaults = {
            "elevenlabs": "eleven_multilingual_v2",
            "qwen": "qwen-audio-turbo",
        }
        return defaults.get(provider.lower(), "")