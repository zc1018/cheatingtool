"""
LLM 工厂模块
根据配置创建对应的 LLM 客户端实例
"""
from typing import Optional
from loguru import logger

from .base import BaseLLM
from .openai_client import OpenAIClient
from .anthropic_client import AnthropicClient
from .ollama_client import OllamaClient
from .kimi_client import KimiClient
from .glm_client import GLMClient


class LLMFactory:
    """LLM 客户端工厂"""

    @staticmethod
    def create(
        provider: str,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
    ) -> BaseLLM:
        """
        创建 LLM 客户端

        Args:
            provider: LLM 提供商 (openai, anthropic, ollama, kimi, glm, custom)
            api_key: API 密钥
            base_url: API 基础 URL
            model: 模型名称
            temperature: 温度参数
            max_tokens: 最大 token 数

        Returns:
            LLM 客户端实例

        Raises:
            ValueError: 不支持的提供商或缺少必需参数
        """
        provider = provider.lower()

        if provider == "openai":
            if not api_key:
                raise ValueError("OpenAI requires api_key")
            model = model or "gpt-4o"
            logger.info(f"Creating OpenAI client with model: {model}")
            return OpenAIClient(
                api_key=api_key,
                base_url=base_url,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
            )

        elif provider == "anthropic":
            if not api_key:
                raise ValueError("Anthropic requires api_key")
            model = model or "claude-3-5-sonnet-20241022"
            logger.info(f"Creating Anthropic client with model: {model}")
            return AnthropicClient(
                api_key=api_key,
                base_url=base_url,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
            )

        elif provider == "ollama":
            base_url = base_url or "http://localhost:11434"
            model = model or "llama2"
            logger.info(f"Creating Ollama client with model: {model}")
            return OllamaClient(
                api_key=api_key,
                base_url=base_url,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
            )

        elif provider == "kimi":
            if not api_key:
                raise ValueError("Kimi requires api_key")
            model = model or "moonshot-v1-8k"
            logger.info(f"Creating Kimi client with model: {model}")
            return KimiClient(
                api_key=api_key,
                base_url=base_url,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
            )

        elif provider == "glm":
            if not api_key:
                raise ValueError("GLM requires api_key")
            model = model or "glm-4"
            logger.info(f"Creating GLM client with model: {model}")
            return GLMClient(
                api_key=api_key,
                base_url=base_url,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
            )

        elif provider == "custom":
            if not api_key:
                raise ValueError("Custom API requires api_key")
            if not base_url:
                raise ValueError("Custom API requires base_url")
            model = model or "custom-model"
            logger.info(f"Creating custom API client with base_url: {base_url}")
            # 使用 OpenAI 客户端连接自定义 API
            return OpenAIClient(
                api_key=api_key,
                base_url=base_url,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
            )

        else:
            raise ValueError(
                f"Unsupported LLM provider: {provider}. "
                f"Supported providers: openai, anthropic, ollama, kimi, glm, custom"
            )

    @staticmethod
    def get_supported_providers() -> list[str]:
        """
        获取支持的 LLM 提供商列表

        Returns:
            提供商列表
        """
        return ["openai", "anthropic", "ollama", "kimi", "glm", "custom"]

    @staticmethod
    def get_default_model(provider: str) -> str:
        """
        获取提供商的默认模型

        Args:
            provider: LLM 提供商

        Returns:
            默认模型名称
        """
        defaults = {
            "openai": "gpt-4o",
            "anthropic": "claude-3-5-sonnet-20241022",
            "ollama": "llama2",
            "kimi": "moonshot-v1-8k",
            "glm": "glm-4",
            "custom": "custom-model",
        }
        return defaults.get(provider.lower(), "")

    @staticmethod
    def get_available_models(provider: str) -> list[str]:
        """
        获取提供商的可用模型列表

        Args:
            provider: LLM 提供商

        Returns:
            模型列表
        """
        models = {
            "openai": [
                "gpt-4o",
                "gpt-4o-mini",
                "gpt-4-turbo",
                "gpt-3.5-turbo",
            ],
            "anthropic": [
                "claude-3-5-sonnet-20241022",
                "claude-3-opus-20240229",
                "claude-3-sonnet-20240229",
                "claude-3-haiku-20240307",
            ],
            "ollama": [
                "llama2",
                "llama3",
                "mistral",
                "qwen",
                "gemma",
            ],
            "kimi": [
                "moonshot-v1-8k",
                "moonshot-v1-32k",
                "moonshot-v1-128k",
            ],
            "glm": [
                "glm-4",
                "glm-4-0520",
                "glm-4-air",
                "glm-4-flash",
                "glm-3-turbo",
            ],
            "custom": [],  # 用户自定义
        }
        return models.get(provider.lower(), [])