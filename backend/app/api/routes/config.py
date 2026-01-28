"""
配置管理 API 路由
"""
from fastapi import APIRouter, HTTPException, status
from typing import Optional
from loguru import logger

from ...models.schemas import ConfigUpdateRequest, ConfigResponse
from ...config import Settings, app_config
from ...services.transcription_service import TranscriptionService
from ...services.analysis_service import AnalysisService

router = APIRouter(prefix="/api/config", tags=["config"])

# 全局服务实例（实际使用时应该通过依赖注入）
transcription_service: Optional[TranscriptionService] = None
analysis_service: Optional[AnalysisService] = None

settings = Settings()


@router.get("/")
async def get_config() -> dict:
    """
    获取完整配置
    """
    try:
        return app_config.model_dump()
    except Exception as e:
        logger.error(f"Error getting config: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.put("/")
async def update_config(request: ConfigUpdateRequest) -> ConfigResponse:
    """
    更新配置
    """
    try:
        # 更新配置
        if request.llm:
            app_config.llm.update(request.llm)
            # 如果分析服务正在运行，更新其配置
            if analysis_service:
                analysis_service.update_llm_config(**request.llm)

        if request.stt:
            app_config.stt.update(request.stt)
            # 如果转写服务正在运行，更新其配置
            if transcription_service:
                transcription_service.update_config(**request.stt)

        if request.scenario:
            app_config.scenario.update(request.scenario)
            if analysis_service:
                analysis_service.update_scenario(request.scenario)

        if request.analysis_prompt is not None:
            app_config.analysis_prompt = request.analysis_prompt
            if analysis_service:
                analysis_service.update_analysis_prompt(request.analysis_prompt)

        if request.audio:
            app_config.audio.update(request.audio)

        # 保存配置
        settings.save_config(app_config)

        return ConfigResponse(
            success=True,
            message="Configuration updated successfully",
            config=app_config.model_dump()
        )

    except Exception as e:
        logger.error(f"Error updating config: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/llm")
async def get_llm_config() -> dict:
    """
    获取 LLM 配置
    """
    try:
        return app_config.llm.model_dump()
    except Exception as e:
        logger.error(f"Error getting LLM config: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.put("/llm")
async def update_llm_config(config: dict) -> ConfigResponse:
    """
    更新 LLM 配置
    """
    try:
        app_config.llm.update(config)

        if analysis_service:
            analysis_service.update_llm_config(**config)

        settings.save_config(app_config)

        return ConfigResponse(
            success=True,
            message="LLM configuration updated",
            config=app_config.llm.model_dump()
        )

    except Exception as e:
        logger.error(f"Error updating LLM config: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/stt")
async def get_stt_config() -> dict:
    """
    获取 STT 配置
    """
    try:
        return app_config.stt.model_dump()
    except Exception as e:
        logger.error(f"Error getting STT config: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.put("/stt")
async def update_stt_config(config: dict) -> ConfigResponse:
    """
    更新 STT 配置
    """
    try:
        app_config.stt.update(config)

        if transcription_service:
            transcription_service.update_config(**config)

        settings.save_config(app_config)

        return ConfigResponse(
            success=True,
            message="STT configuration updated",
            config=app_config.stt.model_dump()
        )

    except Exception as e:
        logger.error(f"Error updating STT config: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/scenario")
async def get_scenario_config() -> dict:
    """
    获取场景配置
    """
    try:
        return app_config.scenario.model_dump()
    except Exception as e:
        logger.error(f"Error getting scenario config: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.put("/scenario")
async def update_scenario_config(config: dict) -> ConfigResponse:
    """
    更新场景配置
    """
    try:
        app_config.scenario.update(config)

        if analysis_service:
            analysis_service.update_scenario(config)

        settings.save_config(app_config)

        return ConfigResponse(
            success=True,
            message="Scenario configuration updated",
            config=app_config.scenario.model_dump()
        )

    except Exception as e:
        logger.error(f"Error updating scenario config: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )