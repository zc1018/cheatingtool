"""
Qwen-Audio STT 客户端
使用阿里云 DashScope API 进行音频转写
"""
import asyncio
import base64
from typing import AsyncIterator, Optional
import numpy as np
import soundfile as sf
from pathlib import Path
from loguru import logger

try:
    from dashscope import MultiModalConversation
    DASHSCOPE_AVAILABLE = True
except ImportError:
    logger.warning("dashscope not available, Qwen STT will not work")
    DASHSCOPE_AVAILABLE = False

from .base import BaseSTT, STTResult


class QwenAudioSTT(BaseSTT):
    """通义千问 Qwen-Audio 语音转文字客户端"""

    def __init__(
        self,
        api_key: str,
        language: str = "zh",
        model: str = "qwen-audio-turbo",
    ):
        """
        初始化 Qwen-Audio STT 客户端

        Args:
            api_key: 阿里云 DashScope API 密钥
            language: 语言代码
            model: 模型名称
        """
        super().__init__(api_key=api_key, language=language, model=model)

        if not DASHSCOPE_AVAILABLE:
            raise RuntimeError("dashscope package not available")

    async def connect(self) -> bool:
        """连接到 Qwen-Audio 服务"""
        if not self.validate_config():
            return False

        # DashScope 不需要显式连接
        self.is_connected = True
        logger.info("Qwen-Audio STT service ready")
        return True

    async def disconnect(self) -> None:
        """断开连接"""
        self.is_connected = False
        logger.info("Qwen-Audio STT service disconnected")

    async def transcribe_stream(
        self, audio_stream: AsyncIterator[np.ndarray]
    ) -> AsyncIterator[STTResult]:
        """
        流式转写音频
        注意：Qwen-Audio 不支持真正的流式转写，这里实现为批量转写

        Args:
            audio_stream: 音频数据流

        Yields:
            转写结果
        """
        if not self.is_connected:
            await self.connect()

        # 收集音频数据
        audio_chunks = []
        async for chunk in audio_stream:
            audio_chunks.append(chunk)

        if not audio_chunks:
            return

        # 合并音频数据
        audio_data = np.concatenate(audio_chunks)

        # 保存为临时文件
        temp_file = Path("/tmp/qwen_audio_temp.wav")
        sf.write(temp_file, audio_data, 16000)

        try:
            # 转写音频文件
            result = await self.transcribe_file(str(temp_file))
            yield result
        finally:
            # 清理临时文件
            if temp_file.exists():
                temp_file.unlink()

    async def transcribe_file(self, audio_file: str) -> STTResult:
        """
        转写音频文件

        Args:
            audio_file: 音频文件路径

        Returns:
            转写结果
        """
        if not self.is_connected:
            await self.connect()

        try:
            # 读取音频文件并转换为 base64
            with open(audio_file, "rb") as f:
                audio_bytes = f.read()
            audio_base64 = base64.b64encode(audio_bytes).decode("utf-8")

            # 构建请求
            messages = [
                {
                    "role": "user",
                    "content": [
                        {
                            "audio": f"data:audio/wav;base64,{audio_base64}"
                        },
                        {
                            "text": "请将这段音频转写为文字。"
                        }
                    ]
                }
            ]

            # 调用 API
            response = await asyncio.to_thread(
                MultiModalConversation.call,
                model=self.model,
                messages=messages,
                api_key=self.api_key,
            )

            # 解析响应
            if response.status_code == 200:
                text = response.output.choices[0].message.content[0]["text"]
                return STTResult(
                    text=text,
                    is_final=True,
                    confidence=1.0,
                    language=self.language,
                )
            else:
                logger.error(f"Qwen-Audio API error: {response.message}")
                return STTResult(
                    text="",
                    is_final=True,
                    confidence=0.0,
                )

        except Exception as e:
            logger.error(f"Error transcribing file: {e}")
            return STTResult(
                text="",
                is_final=True,
                confidence=0.0,
            )