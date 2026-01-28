"""
转写服务
管理语音转文字
"""
import asyncio
from typing import Optional, AsyncIterator
from loguru import logger

from ..core.stt.base import BaseSTT, STTResult
from ..core.stt.factory import STTFactory


class TranscriptionService:
    """转写服务"""

    def __init__(
        self,
        provider: str = "elevenlabs",
        api_key: Optional[str] = None,
        language: str = "zh",
        model: Optional[str] = None,
    ):
        """
        初始化转写服务

        Args:
            provider: STT 提供商
            api_key: API 密钥
            language: 语言代码
            model: 模型名称
        """
        self.provider = provider
        self.api_key = api_key
        self.language = language
        self.model = model

        self.stt_client: Optional[BaseSTT] = None
        self.is_running = False

    async def start(self) -> bool:
        """
        启动转写服务

        Returns:
            是否成功启动
        """
        if self.is_running:
            logger.warning("Transcription service already running")
            return False

        try:
            # 创建 STT 客户端
            self.stt_client = STTFactory.create(
                provider=self.provider,
                api_key=self.api_key,
                language=self.language,
                model=self.model,
            )

            # 连接到 STT 服务
            success = await self.stt_client.connect()
            if success:
                self.is_running = True
                logger.info(f"Transcription service started with {self.provider}")
            return success

        except Exception as e:
            logger.error(f"Failed to start transcription service: {e}")
            return False

    async def stop(self) -> bool:
        """
        停止转写服务

        Returns:
            是否成功停止
        """
        if not self.is_running:
            logger.warning("Transcription service not running")
            return False

        try:
            if self.stt_client:
                await self.stt_client.disconnect()
                self.stt_client = None

            self.is_running = False
            logger.info("Transcription service stopped")
            return True

        except Exception as e:
            logger.error(f"Failed to stop transcription service: {e}")
            return False

    async def transcribe_stream(
        self, audio_stream: AsyncIterator
    ) -> AsyncIterator[STTResult]:
        """
        流式转写音频

        Args:
            audio_stream: 音频数据流

        Yields:
            转写结果
        """
        if not self.is_running or not self.stt_client:
            logger.error("Transcription service not running")
            return

        try:
            async for result in self.stt_client.transcribe_stream(audio_stream):
                yield result

        except Exception as e:
            logger.error(f"Error in transcription stream: {e}")

    async def transcribe_file(self, audio_file: str) -> Optional[STTResult]:
        """
        转写音频文件

        Args:
            audio_file: 音频文件路径

        Returns:
            转写结果
        """
        if not self.stt_client:
            logger.error("STT client not initialized")
            return None

        try:
            result = await self.stt_client.transcribe_file(audio_file)
            return result

        except Exception as e:
            logger.error(f"Error transcribing file: {e}")
            return None

    def update_config(
        self,
        provider: Optional[str] = None,
        api_key: Optional[str] = None,
        language: Optional[str] = None,
        model: Optional[str] = None,
    ) -> None:
        """
        更新配置

        Args:
            provider: STT 提供商
            api_key: API 密钥
            language: 语言代码
            model: 模型名称
        """
        if provider:
            self.provider = provider
        if api_key:
            self.api_key = api_key
        if language:
            self.language = language
        if model:
            self.model = model

        logger.info(f"Transcription config updated: {self.provider}")

    def get_status(self) -> dict:
        """
        获取服务状态

        Returns:
            状态字典
        """
        return {
            "is_running": self.is_running,
            "provider": self.provider,
            "language": self.language,
            "model": self.model,
            "is_connected": self.stt_client.is_connected if self.stt_client else False,
        }