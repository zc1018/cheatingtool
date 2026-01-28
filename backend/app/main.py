"""
FastAPI 应用入口
"""
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from loguru import logger
import sys

from .config import settings, app_config
from .api.routes import audio, config, llm, prompts
from .api.websocket import handlers
from .api.websocket.manager import manager
from .services.audio_service import AudioService
from .services.transcription_service import TranscriptionService
from .services.analysis_service import AnalysisService


# 配置日志
logger.remove()
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="INFO",
)

# 全局服务实例
audio_service: AudioService = None
transcription_service: TranscriptionService = None
analysis_service: AnalysisService = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动
    logger.info("Starting macOS AI Voice Assistant Backend...")

    # 初始化服务
    global audio_service, transcription_service, analysis_service

    try:
        # 创建音频服务
        audio_service = AudioService(
            sample_rate=app_config.audio.sample_rate,
            channels=app_config.audio.channels,
            buffer_duration=app_config.audio.buffer_size,
        )

        # 创建转写服务
        transcription_service = TranscriptionService(
            provider=app_config.stt.provider,
            api_key=app_config.stt.api_key,
            language=app_config.stt.language,
            model=app_config.stt.model,
        )

        # 创建分析服务
        analysis_service = AnalysisService(
            llm_provider=app_config.llm.provider,
            llm_api_key=app_config.llm.api_key,
            llm_base_url=app_config.llm.base_url,
            llm_model=app_config.llm.model,
            llm_temperature=app_config.llm.temperature,
            llm_max_tokens=app_config.llm.max_tokens,
            scenario_config=app_config.scenario.model_dump(),
            analysis_prompt=app_config.analysis_prompt,
        )

        # 注入服务到路由
        audio.audio_service = audio_service
        config.transcription_service = transcription_service
        config.analysis_service = analysis_service

        logger.info("All services initialized")

    except Exception as e:
        logger.error(f"Error initializing services: {e}")

    yield

    # 关闭
    logger.info("Shutting down services...")

    try:
        if audio_service:
            await audio_service.stop()
        if transcription_service:
            await transcription_service.stop()
        if analysis_service:
            await analysis_service.stop()

        logger.info("All services stopped")
    except Exception as e:
        logger.error(f"Error stopping services: {e}")


# 创建 FastAPI 应用
app = FastAPI(
    title="macOS AI Voice Assistant Backend",
    description="实时语音助手后端 API",
    version="1.0.0",
    lifespan=lifespan,
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该限制具体的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 注册路由
app.include_router(audio.router)
app.include_router(config.router)
app.include_router(llm.router)
app.include_router(prompts.router)


# 根路径
@app.get("/")
async def root():
    """根路径"""
    return {
        "name": "macOS AI Voice Assistant Backend",
        "version": "1.0.0",
        "status": "running",
    }


# 健康检查
@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "services": {
            "audio": audio_service.get_status() if audio_service else None,
            "transcription": transcription_service.get_status() if transcription_service else None,
            "analysis": analysis_service.get_status() if analysis_service else None,
        },
        "websocket_connections": manager.get_connection_count(),
    }


# WebSocket 端点
@app.websocket("/ws/stream")
async def websocket_stream(websocket: WebSocket):
    """
    WebSocket 流端点
    用于实时推送转写结果和分析建议
    """
    await handlers.handle_websocket_connection(
        websocket=websocket,
        audio_service=audio_service,
        transcription_service=transcription_service,
        analysis_service=analysis_service,
    )


# 全局异常处理
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """全局异常处理器"""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc)},
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )