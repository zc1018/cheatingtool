"""
音频捕获模块
使用 macOS ScreenCaptureKit 捕获系统音频
需要 macOS 12.3+ 和屏幕录制权限
"""
import asyncio
from typing import Optional, Callable
from loguru import logger

try:
    import objc
    from Foundation import NSObject
    from AVFoundation import (
        AVCaptureSession,
        AVCaptureDevice,
        AVMediaTypeAudio,
        AVCaptureDeviceInput,
        AVCaptureAudioDataOutput,
    )
    from CoreMedia import CMSampleBufferGetAudioBufferListWithRetainedBlockBuffer
    MACOS_AUDIO_AVAILABLE = True
except ImportError:
    logger.warning("PyObjC not available, audio capture will not work")
    MACOS_AUDIO_AVAILABLE = False


class AudioCaptureDelegate(NSObject):
    """音频捕获代理"""

    def initWithCallback_(self, callback):
        """初始化"""
        self = objc.super(AudioCaptureDelegate, self).init()
        if self is None:
            return None
        self.callback = callback
        return self

    def captureOutput_didOutputSampleBuffer_fromConnection_(
        self, output, sample_buffer, connection
    ):
        """捕获音频数据回调"""
        try:
            # 从 CMSampleBuffer 提取音频数据
            audio_buffer_list = CMSampleBufferGetAudioBufferListWithRetainedBlockBuffer(
                sample_buffer, None, None
            )
            if audio_buffer_list and self.callback:
                self.callback(audio_buffer_list)
        except Exception as e:
            logger.error(f"Error processing audio buffer: {e}")


class AudioCapture:
    """音频捕获器"""

    def __init__(self, sample_rate: int = 16000, channels: int = 1):
        """
        初始化音频捕获器

        Args:
            sample_rate: 采样率
            channels: 声道数
        """
        self.sample_rate = sample_rate
        self.channels = channels
        self.is_capturing = False
        self.session: Optional[object] = None
        self.delegate: Optional[object] = None
        self.audio_callback: Optional[Callable] = None

        if not MACOS_AUDIO_AVAILABLE:
            raise RuntimeError("PyObjC not available, cannot capture audio")

    def set_callback(self, callback: Callable):
        """设置音频数据回调"""
        self.audio_callback = callback

    async def start(self) -> bool:
        """开始捕获音频"""
        if self.is_capturing:
            logger.warning("Audio capture already started")
            return False

        try:
            # 创建捕获会话
            self.session = AVCaptureSession.alloc().init()

            # 获取默认音频设备
            device = AVCaptureDevice.defaultDeviceWithMediaType_(AVMediaTypeAudio)
            if not device:
                logger.error("No audio device found")
                return False

            # 创建输入
            device_input = AVCaptureDeviceInput.deviceInputWithDevice_error_(
                device, None
            )
            if not device_input:
                logger.error("Failed to create audio input")
                return False

            # 添加输入到会话
            if self.session.canAddInput_(device_input):
                self.session.addInput_(device_input)
            else:
                logger.error("Cannot add audio input to session")
                return False

            # 创建输出
            audio_output = AVCaptureAudioDataOutput.alloc().init()

            # 创建代理
            self.delegate = AudioCaptureDelegate.alloc().initWithCallback_(
                self._handle_audio_data
            )

            # 设置输出代理
            from dispatch import dispatch_get_global_queue, DISPATCH_QUEUE_PRIORITY_DEFAULT
            queue = dispatch_get_global_queue(DISPATCH_QUEUE_PRIORITY_DEFAULT, 0)
            audio_output.setSampleBufferDelegate_queue_(self.delegate, queue)

            # 添加输出到会话
            if self.session.canAddOutput_(audio_output):
                self.session.addOutput_(audio_output)
            else:
                logger.error("Cannot add audio output to session")
                return False

            # 开始捕获
            self.session.startRunning()
            self.is_capturing = True
            logger.info("Audio capture started")
            return True

        except Exception as e:
            logger.error(f"Failed to start audio capture: {e}")
            return False

    def _handle_audio_data(self, audio_buffer_list):
        """处理音频数据"""
        if self.audio_callback:
            try:
                self.audio_callback(audio_buffer_list)
            except Exception as e:
                logger.error(f"Error in audio callback: {e}")

    async def stop(self) -> bool:
        """停止捕获音频"""
        if not self.is_capturing:
            logger.warning("Audio capture not started")
            return False

        try:
            if self.session:
                self.session.stopRunning()
            self.is_capturing = False
            logger.info("Audio capture stopped")
            return True
        except Exception as e:
            logger.error(f"Failed to stop audio capture: {e}")
            return False

    def get_status(self) -> dict:
        """获取捕获状态"""
        return {
            "is_capturing": self.is_capturing,
            "sample_rate": self.sample_rate,
            "channels": self.channels,
        }
