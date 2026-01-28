"""
LLM 配置和管理 API 路由
"""
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional
from loguru import logger

from ...core.llm.factory import LLMFactory

router = APIRouter(prefix="/api/llm", tags=["llm"])


class ProviderInfo(BaseModel):
    """提供商信息"""
    provider: str
    name: str
    default_model: str
    available_models: List[str]


@router.get("/providers")
async def get_supported_providers() -> List[str]:
    """
    获取支持的 LLM 提供商列表
    """
    try:
        return LLMFactory.get_supported_providers()
    except Exception as e:
        logger.error(f"Error getting providers: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/providers/{provider}")
async def get_provider_info(provider: str) -> ProviderInfo:
    """
    获取特定提供商的详细信息
    """
    try:
        supported = LLMFactory.get_supported_providers()
        if provider not in supported:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Provider '{provider}' not supported"
            )

        provider_names = {
            "openai": "OpenAI",
            "anthropic": "Anthropic",
            "ollama": "Ollama (Local)",
        }

        return ProviderInfo(
            provider=provider,
            name=provider_names.get(provider, provider),
            default_model=LLMFactory.get_default_model(provider),
            available_models=LLMFactory.get_available_models(provider),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting provider info: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/models/{provider}")
async def get_provider_models(provider: str) -> List[str]:
    """
    获取提供商的可用模型列表
    """
    try:
        supported = LLMFactory.get_supported_providers()
        if provider not in supported:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Provider '{provider}' not supported"
            )

        models = LLMFactory.get_available_models(provider)
        return models

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting models: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


class TestRequest(BaseModel):
    """测试请求"""
    provider: str
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    model: Optional[str] = None
    prompt: str = "Hello, this is a test."


@router.post("/test")
async def test_llm_connection(request: TestRequest):
    """
    测试 LLM 连接
    """
    try:
        from ...core.llm.base import Message

        # 创建测试客户端
        client = LLMFactory.create(
            provider=request.provider,
            api_key=request.api_key,
            base_url=request.base_url,
            model=request.model or LLMFactory.get_default_model(request.provider),
        )

        # 发送测试消息
        messages = [Message(role="user", content=request.prompt)]
        response = await client.chat(messages)

        return {
            "success": True,
            "provider": request.provider,
            "model": response.model,
            "response": response.content[:200],  # 只返回前200个字符
            "usage": response.usage,
        }

    except Exception as e:
        logger.error(f"Error testing LLM: {e}")
        return {
            "success": False,
            "error": str(e),
        }