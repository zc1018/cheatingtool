"""
音频控制 API 路由
"""
from fastapi import APIRouter, HTTPException, status
from loguru import logger

from ...models.schemas import AudioControlRequest, AudioControlResponse, AudioStatus
from ...services.audio_service import AudioService

router = APIRouter(prefix="/api/audio", tags=["audio"])

# 全局音频服务实例（实际使用时应该通过依赖注入）
audio_service: AudioService = None


@router.post("/start", response_model=AudioControlResponse)
async def start_audio_capture():
    """
    开始音频捕获
    """
    try:
        if not audio_service:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Audio service not initialized"
            )

        success = await audio_service.start()

        if success:
            return AudioControlResponse(
                success=True,
                message="Audio capture started",
                status=AudioStatus(**audio_service.get_status())
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to start audio capture"
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error starting audio capture: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/stop", response_model=AudioControlResponse)
async def stop_audio_capture():
    """
    停止音频捕获
    """
    try:
        if not audio_service:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Audio service not initialized"
            )

        success = await audio_service.stop()

        if success:
            return AudioControlResponse(
                success=True,
                message="Audio capture stopped",
                status=AudioStatus(**audio_service.get_status())
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to stop audio capture"
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error stopping audio capture: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/status", response_model=AudioStatus)
async def get_audio_status():
    """
    获取音频捕获状态
    """
    try:
        if not audio_service:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Audio service not initialized"
            )

        status_data = audio_service.get_status()
        return AudioStatus(**status_data)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting audio status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/control", response_model=AudioControlResponse)
async def control_audio(request: AudioControlRequest):
    """
    音频控制（统一的控制接口）
    """
    try:
        if not audio_service:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Audio service not initialized"
            )

        if request.action == "start":
            success = await audio_service.start()
            message = "Audio capture started"
        elif request.action == "stop":
            success = await audio_service.stop()
            message = "Audio capture stopped"
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unknown action: {request.action}"
            )

        if success:
            return AudioControlResponse(
                success=True,
                message=message,
                status=AudioStatus(**audio_service.get_status())
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to execute action: {request.action}"
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error controlling audio: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )