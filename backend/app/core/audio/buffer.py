"""
音频缓冲模块
提供环形缓冲区和流式音频块生成
"""
import asyncio
import numpy as np
from collections import deque
from typing import Optional, AsyncIterator
from loguru import logger


class AudioBuffer:
    """音频环形缓冲区"""

    def __init__(
        self,
        sample_rate: int = 16000,
        channels: int = 1,
        buffer_duration: float = 10.0,
        chunk_duration: float = 1.0,
    ):
        """
        初始化音频缓冲区

        Args:
            sample_rate: 采样率
            channels: 声道数
            buffer_duration: 缓冲区时长（秒）
            chunk_duration: 音频块时长（秒）
        """
        self.sample_rate = sample_rate
        self.channels = channels
        self.buffer_duration = buffer_duration
        self.chunk_duration = chunk_duration

        # 计算缓冲区大小
        self.buffer_size = int(sample_rate * buffer_duration)
        self.chunk_size = int(sample_rate * chunk_duration)

        # 环形缓冲区
        self.buffer = deque(maxlen=self.buffer_size)

        # 同步锁
        self.lock = asyncio.Lock()

        # 新数据事件
        self.new_data_event = asyncio.Event()

    async def write(self, data: np.ndarray) -> None:
        """
        写入音频数据

        Args:
            data: 音频数据 (numpy array)
        """
        async with self.lock:
            # 将数据添加到缓冲区
            for sample in data.flatten():
                self.buffer.append(sample)

            # 通知有新数据
            self.new_data_event.set()

    async def read_chunk(self) -> Optional[np.ndarray]:
        """
        读取一个音频块

        Returns:
            音频数据块，如果缓冲区数据不足则返回 None
        """
        async with self.lock:
            if len(self.buffer) < self.chunk_size:
                return None

            # 读取一个块
            chunk = np.array([self.buffer.popleft() for _ in range(self.chunk_size)])
            return chunk.reshape(-1, self.channels)

    async def stream_chunks(self) -> AsyncIterator[np.ndarray]:
        """
        流式生成音频块

        Yields:
            音频数据块
        """
        while True:
            # 等待新数据
            await self.new_data_event.wait()

            # 读取所有可用的块
            while True:
                chunk = await self.read_chunk()
                if chunk is None:
                    break
                yield chunk

            # 重置事件
            self.new_data_event.clear()

    async def clear(self) -> None:
        """清空缓冲区"""
        async with self.lock:
            self.buffer.clear()
            logger.debug("Audio buffer cleared")

    def get_buffer_level(self) -> float:
        """
        获取缓冲区填充率

        Returns:
            填充率 (0.0 - 1.0)
        """
        return len(self.buffer) / self.buffer_size

    def get_available_duration(self) -> float:
        """
        获取缓冲区中可用的音频时长

        Returns:
            时长（秒）
        """
        return len(self.buffer) / self.sample_rate


class AudioProcessor:
    """音频预处理器"""

    @staticmethod
    def normalize(data: np.ndarray) -> np.ndarray:
        """
        归一化音频数据

        Args:
            data: 音频数据

        Returns:
            归一化后的数据
        """
        max_val = np.abs(data).max()
        if max_val > 0:
            return data / max_val
        return data

    @staticmethod
    def resample(
        data: np.ndarray, orig_sr: int, target_sr: int
    ) -> np.ndarray:
        """
        重采样音频数据

        Args:
            data: 音频数据
            orig_sr: 原始采样率
            target_sr: 目标采样率

        Returns:
            重采样后的数据
        """
        if orig_sr == target_sr:
            return data

        # 简单的线性插值重采样
        duration = len(data) / orig_sr
        target_length = int(duration * target_sr)
        indices = np.linspace(0, len(data) - 1, target_length)
        return np.interp(indices, np.arange(len(data)), data)

    @staticmethod
    def to_mono(data: np.ndarray) -> np.ndarray:
        """
        转换为单声道

        Args:
            data: 音频数据 (可能是多声道)

        Returns:
            单声道数据
        """
        if data.ndim == 1:
            return data
        return data.mean(axis=1)

    @staticmethod
    def apply_gain(data: np.ndarray, gain_db: float) -> np.ndarray:
        """
        应用增益

        Args:
            data: 音频数据
            gain_db: 增益（分贝）

        Returns:
            应用增益后的数据
        """
        gain_linear = 10 ** (gain_db / 20)
        return data * gain_linear