"""
音频服务
管理音频捕获和缓冲
"""
import asyncio
from typing import Optional
from loguru import logger

from ..core.audio.capture import AudioCapture
from ..core.audio.buffer import AudioBuffer


class AudioService:
    """音频服务"""

    def __init__(
        self,
        sample_rate: int = 16000,
        channels: int = 1,
        buffer_duration: float = 10.0,
        chunk_duration: float = 1.0,
    ):
        """
        初始化音频服务

        Args:
            sample_rate: 采样率
            channels: 声道数
            buffer_duration: 缓冲区时长
            chunk_duration: 音频块时长
        """
        self.sample_rate = sample_rate
        self.channels = channels

        # 音频捕获器
        self.capture: Optional[AudioCapture] = None

        # 音频缓冲区
        self.buffer = AudioBuffer(
            sample_rate=sample_rate,
            channels=channels,
            buffer_duration=buffer_duration,
            chunk_duration=chunk_duration,
        )

        self.is_running = False

    async def start(self) -> bool:
        """
        开始音频捕获

        Returns:
            是否成功启动
        """
        if self.is_running:
            logger.warning("Audio service already running")
            return False

        try:
            # 创建音频捕获器
            self.capture = AudioCapture(
                sample_rate=self.sample_rate,
                channels=self.channels,
            )

            # 设置音频回调
            self.capture.set_callback(self._on_audio_data)

            # 启动捕获
            success = await self.capture.start()
            if success:
                self.is_running = True
                logger.info("Audio service started")
            return success

        except Exception as e:
            logger.error(f"Failed to start audio service: {e}")
            return False

    async def stop(self) -> bool:
        """
        停止音频捕获

        Returns:
            是否成功停止
        """
        if not self.is_running:
            logger.warning("Audio service not running")
            return False

        try:
            if self.capture:
                await self.capture.stop()
                self.capture = None

            self.is_running = False
            logger.info("Audio service stopped")
            return True

        except Exception as e:
            logger.error(f"Failed to stop audio service: {e}")
            return False

    def _on_audio_data(self, audio_data):
        """
        音频数据回调

        Args:
            audio_data: 音频数据
        """
        try:
            # 将音频数据写入缓冲区
            # 注意：这里需要将 audio_data 转换为 numpy array
            # 具体实现取决于 AudioCapture 返回的数据格式
            import numpy as np

            # 假设 audio_data 是 AudioBufferList 格式
            # 需要转换为 numpy array
            # 这里是简化实现，实际需要根据 macOS API 返回的格式处理
            if isinstance(audio_data, np.ndarray):
                asyncio.create_task(self.buffer.write(audio_data))
            else:
                logger.warning("Unsupported audio data format")

        except Exception as e:
            logger.error(f"Error processing audio data: {e}")

    def get_audio_stream(self):
        """
        获取音频流

        Returns:
            音频数据流
        """
        return self.buffer.stream_chunks()

    def get_status(self) -> dict:
        """
        获取服务状态

        Returns:
            状态字典
        """
        status = {
            "is_running": self.is_running,
            "sample_rate": self.sample_rate,
            "channels": self.channels,
            "buffer_level": self.buffer.get_buffer_level(),
            "available_duration": self.buffer.get_available_duration(),
        }

        if self.capture:
            status.update(self.capture.get_status())

        return status

    async def clear_buffer(self) -> None:
        """清空音频缓冲区"""
        await self.buffer.clear()
        logger.info("Audio buffer cleared")