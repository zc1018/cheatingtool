"""
ElevenLabs STT 客户端
使用 ElevenLabs WebSocket API 进行实时语音转写
"""
import asyncio
import json
from typing import AsyncIterator, Optional
import numpy as np
import websockets
from loguru import logger

from .base import BaseSTT, STTResult


class ElevenLabsSTT(BaseSTT):
    """ElevenLabs 语音转文字客户端"""

    def __init__(
        self,
        api_key: str,
        language: str = "zh",
        model: str = "eleven_multilingual_v2",
    ):
        """
        初始化 ElevenLabs STT 客户端

        Args:
            api_key: ElevenLabs API 密钥
            language: 语言代码
            model: 模型名称
        """
        super().__init__(api_key=api_key, language=language, model=model)
        self.ws_url = f"wss://api.elevenlabs.io/v1/speech-to-text/{model}"
        self.websocket: Optional[websockets.WebSocketClientProtocol] = None

    async def connect(self) -> bool:
        """连接到 ElevenLabs WebSocket"""
        if not self.validate_config():
            return False

        try:
            headers = {
                "xi-api-key": self.api_key,
            }

            self.websocket = await websockets.connect(
                self.ws_url,
                extra_headers=headers,
            )

            self.is_connected = True
            logger.info("Connected to ElevenLabs STT service")
            return True

        except Exception as e:
            logger.error(f"Failed to connect to ElevenLabs: {e}")
            return False

    async def disconnect(self) -> None:
        """断开连接"""
        if self.websocket:
            await self.websocket.close()
            self.websocket = None
        self.is_connected = False
        logger.info("Disconnected from ElevenLabs STT service")

    async def transcribe_stream(
        self, audio_stream: AsyncIterator[np.ndarray]
    ) -> AsyncIterator[STTResult]:
        """
        流式转写音频

        Args:
            audio_stream: 音频数据流 (16kHz, 16-bit PCM)

        Yields:
            转写结果
        """
        if not self.is_connected:
            await self.connect()

        if not self.websocket:
            logger.error("WebSocket not connected")
            return

        try:
            # 启动发送任务
            send_task = asyncio.create_task(
                self._send_audio(audio_stream)
            )

            # 接收转写结果
            async for result in self._receive_transcriptions():
                yield result

            # 等待发送任务完成
            await send_task

        except Exception as e:
            logger.error(f"Error in transcribe_stream: {e}")
        finally:
            await self.disconnect()

    async def _send_audio(self, audio_stream: AsyncIterator[np.ndarray]) -> None:
        """发送音频数据到 WebSocket"""
        try:
            async for audio_chunk in audio_stream:
                if not self.websocket:
                    break

                # 转换为 16-bit PCM bytes
                audio_bytes = (audio_chunk * 32767).astype(np.int16).tobytes()

                # 发送音频数据
                await self.websocket.send(audio_bytes)

            # 发送结束信号
            if self.websocket:
                await self.websocket.send(json.dumps({"type": "end"}))

        except Exception as e:
            logger.error(f"Error sending audio: {e}")

    async def _receive_transcriptions(self) -> AsyncIterator[STTResult]:
        """接收转写结果"""
        try:
            while self.websocket:
                message = await self.websocket.recv()

                if isinstance(message, str):
                    data = json.loads(message)

                    # 解析转写结果
                    if "text" in data:
                        yield STTResult(
                            text=data["text"],
                            is_final=data.get("is_final", False),
                            confidence=data.get("confidence"),
                            language=data.get("language", self.language),
                        )

        except websockets.exceptions.ConnectionClosed:
            logger.info("WebSocket connection closed")
        except Exception as e:
            logger.error(f"Error receiving transcriptions: {e}")

    async def transcribe_file(self, audio_file: str) -> STTResult:
        """
        转写音频文件

        Args:
            audio_file: 音频文件路径

        Returns:
            转写结果
        """
        # ElevenLabs 主要用于流式转写
        # 文件转写可以通过读取文件并流式发送实现
        raise NotImplementedError(
            "File transcription not implemented for ElevenLabs. Use transcribe_stream instead."
        )