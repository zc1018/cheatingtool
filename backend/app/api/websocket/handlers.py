"""
WebSocket 处理器
处理 WebSocket 连接和消息
"""
import asyncio
import json
from fastapi import WebSocket, WebSocketDisconnect
from typing import Optional
from loguru import logger

from .manager import manager
from ...services.audio_service import AudioService
from ...services.transcription_service import TranscriptionService
from ...services.analysis_service import AnalysisService
from ...models.schemas import WSCommandMessage


async def handle_websocket_connection(
    websocket: WebSocket,
    audio_service: Optional[AudioService] = None,
    transcription_service: Optional[TranscriptionService] = None,
    analysis_service: Optional[AnalysisService] = None,
):
    """
    处理 WebSocket 连接

    Args:
        websocket: WebSocket 连接
        audio_service: 音频服务
        transcription_service: 转写服务
        analysis_service: 分析服务
    """
    await manager.connect(websocket)

    try:
        while True:
            # 接收消息
            data = await websocket.receive_text()
            message = json.loads(data)

            # 处理不同类型的消息
            message_type = message.get("type")

            if message_type == "command":
                await handle_command(websocket, message, audio_service, transcription_service, analysis_service)
            else:
                logger.warning(f"Unknown message type: {message_type}")
                await manager.send_personal_message(
                    {"type": "error", "message": f"Unknown message type: {message_type}"},
                    websocket
                )

    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info("WebSocket disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)
        try:
            await manager.send_personal_message(
                {"type": "error", "message": str(e)},
                websocket
            )
        except:
            pass


async def handle_command(
    websocket: WebSocket,
    message: dict,
    audio_service: Optional[AudioService],
    transcription_service: Optional[TranscriptionService],
    analysis_service: Optional[AnalysisService],
):
    """
    处理控制命令

    Args:
        websocket: WebSocket 连接
        message: 消息内容
        audio_service: 音频服务
        transcription_service: 转写服务
        analysis_service: 分析服务
    """
    try:
        action = message.get("action")

        if action == "start":
            await handle_start_command(audio_service, transcription_service, analysis_service)
            await manager.send_personal_message(
                {"type": "info", "message": "Services started"},
                websocket
            )

        elif action == "stop":
            await handle_stop_command(audio_service, transcription_service, analysis_service)
            await manager.send_personal_message(
                {"type": "info", "message": "Services stopped"},
                websocket
            )

        elif action == "status":
            status_data = get_services_status(audio_service, transcription_service, analysis_service)
            await manager.send_personal_message(
                {"type": "status", "data": status_data},
                websocket
            )

        else:
            await manager.send_personal_message(
                {"type": "error", "message": f"Unknown action: {action}"},
                websocket
            )

    except Exception as e:
        logger.error(f"Error handling command: {e}")
        await manager.send_personal_message(
            {"type": "error", "message": str(e)},
            websocket
        )


async def handle_start_command(
    audio_service: Optional[AudioService],
    transcription_service: Optional[TranscriptionService],
    analysis_service: Optional[AnalysisService],
):
    """
    处理启动命令

    Args:
        audio_service: 音频服务
        transcription_service: 转写服务
        analysis_service: 分析服务
    """
    logger.info("Starting all services...")

    # 启动音频服务
    if audio_service:
        await audio_service.start()

    # 启动转写服务
    if transcription_service:
        await transcription_service.start()

    # 启动分析服务
    if analysis_service:
        await analysis_service.start()

    logger.info("All services started")


async def handle_stop_command(
    audio_service: Optional[AudioService],
    transcription_service: Optional[TranscriptionService],
    analysis_service: Optional[AnalysisService],
):
    """
    处理停止命令

    Args:
        audio_service: 音频服务
        transcription_service: 转写服务
        analysis_service: 分析服务
    """
    logger.info("Stopping all services...")

    # 停止音频服务
    if audio_service:
        await audio_service.stop()

    # 停止转写服务
    if transcription_service:
        await transcription_service.stop()

    # 停止分析服务
    if analysis_service:
        await analysis_service.stop()

    logger.info("All services stopped")


def get_services_status(
    audio_service: Optional[AudioService],
    transcription_service: Optional[TranscriptionService],
    analysis_service: Optional[AnalysisService],
) -> dict:
    """
    获取所有服务的状态

    Args:
        audio_service: 音频服务
        transcription_service: 转写服务
        analysis_service: 分析服务

    Returns:
        状态字典
    """
    return {
        "audio": audio_service.get_status() if audio_service else None,
        "transcription": transcription_service.get_status() if transcription_service else None,
        "analysis": analysis_service.get_status() if analysis_service else None,
        "connections": manager.get_connection_count(),
    }


async def stream_transcription_results(transcription_service: TranscriptionService):
    """
    流式推送转写结果

    Args:
        transcription_service: 转写服务
    """
    try:
        if not audio_service:
            logger.error("Audio service not available")
            return

        # 获取音频流
        audio_stream = audio_service.get_audio_stream()

        # 流式转写
        async for result in transcription_service.transcribe_stream(audio_stream):
            # 广播转写结果
            await manager.broadcast_transcription(
                text=result.text,
                is_final=result.is_final,
                speaker="other",  # 默认为对方，可以后续优化
            )

            # 如果是最终结果，添加到对话分析器
            if result.is_final and analysis_service:
                analysis_service.add_conversation_turn(
                    text=result.text,
                    speaker="other",
                    confidence=result.confidence or 1.0
                )

                # 生成建议
                suggestion = await analysis_service.generate_suggestion()
                if suggestion:
                    await manager.broadcast_analysis(**suggestion)

    except Exception as e:
        logger.error(f"Error streaming transcription: {e}")
        await manager.broadcast_error(f"Transcription error: {str(e)}")