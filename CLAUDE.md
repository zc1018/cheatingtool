# macOS AI 实时语音助手 - 项目开发规范

## 项目概述

构建一个 macOS 桌面工具，实时监听系统音频，通过 AI 分析对话内容，为用户提供实时建议。

**技术栈**:
- 后端: FastAPI + Python 3.10+
- 前端: Electron + React 18
- 音频: ScreenCaptureKit (PyObjC)
- AI: OpenAI / Anthropic / Ollama

---

## 开发分工

### 后端开发（Claude Code）
- **工作目录**: `backend/`
- **开发方式**: 直接实现所有 Python 代码
- **职责**:
  - API 接口设计与实现
  - 音频捕获和处理
  - STT 和 LLM 集成
  - WebSocket 实时通信

### 前端开发（Gemini 3）
- **工作目录**: `frontend/`
- **开发方式**: 仅生成开发计划，不编写代码
- **职责**:
  - 根据 Claude Code 生成的计划实现前端
  - 在 Antigravity 环境中开发

---

## 项目架构经验

### 1. 模块化设计
```
backend/app/
├── core/          # 核心功能模块
│   ├── audio/     # 音频捕获、缓冲、处理
│   ├── stt/       # 语音转文字（基类 + 工厂）
│   ├── llm/       # LLM 客户端（基类 + 工厂）
│   └── analysis/  # 对话分析、建议生成
├── services/      # 业务服务层
│   ├── audio_service.py
│   ├── transcription_service.py
│   └── analysis_service.py
├── api/           # API 层
│   ├── routes/    # REST API
│   └── websocket/ # WebSocket 处理
└── models/        # Pydantic 数据模型
```

**关键原则**:
- 每个核心模块都有抽象基类 + 工厂模式
- 服务层整合核心模块，提供业务逻辑
- API 层只处理 HTTP/WebSocket 协议

### 2. 工厂模式的应用

用于支持多种提供商：

```python
# STT 工厂
class STTFactory:
    @staticmethod
    def create(provider: str, **kwargs) -> BaseSTT:
        if provider == "elevenlabs":
            return ElevenLabsSTT(**kwargs)
        elif provider == "qwen":
            return QwenAudioSTT(**kwargs)

# LLM 工厂
class LLMFactory:
    @staticmethod
    def create(provider: str, **kwargs) -> BaseLLM:
        if provider == "openai":
            return OpenAIClient(**kwargs)
        elif provider == "anthropic":
            return AnthropicClient(**kwargs)
        elif provider == "ollama":
            return OllamaClient(**kwargs)
```

**好处**:
- 易于扩展新的提供商
- 统一的接口，降低耦合
- 配置驱动的切换

### 3. 异步流式处理

音频转写流：

```python
async def transcribe_stream(
    self, audio_stream: AsyncIterator[np.ndarray]
) -> AsyncIterator[STTResult]:
    async for chunk in audio_stream:
        # 处理音频块
        result = await self.stt_client.transcribe(chunk)
        yield result
```

**关键点**:
- 使用 `AsyncIterator` 处理流式数据
- 避免阻塞操作，保持高并发
- 正确处理异步生成器

### 4. WebSocket 实时推送

消息类型设计：

```python
# 转写结果
{"type": "transcription", "text": "...", "is_final": true}

# AI 分析
{"type": "analysis", "intent": "...", "suggested_reply": "..."}

# 错误消息
{"type": "error", "message": "...", "code": "..."}
```

**最佳实践**:
- 统一的消息格式（type 字段）
- 连接管理器管理多个客户端
- 错误处理和重连机制

---

## 常见问题解决方案

### PyObjC 类型警告

**问题**: PyObjC 调用 macOS API 时出现大量类型警告

**解决**: 这些警告是正常的，不影响运行
```python
# 不需要修复这些类型警告
# PyObjC 的动态特性导致静态类型检查不准确
```

### Pydantic 配置更新

**问题**: Pydantic v2 的模型没有 `update()` 方法

**解决**:
```python
# 错误方式
config.llm.update(new_config)

# 正确方式
config.llm = config.llm.model_copy(update=new_config)
```

### WebSocket 连接管理

**问题**: 多个客户端同时连接需要管理

**解决**: 使用连接管理器
```python
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            await connection.send_json(message)
```

---

## 开发流程经验

### 1. 使用 executing-plans 技能

- 将大任务分解为小批次（每批 3 个任务）
- 每批完成后报告进度
- 使用 TodoWrite 追踪任务状态

### 2. 完整的文档

后端完成后必须提供：
- ✅ API 文档（`backend/API.md`）
- ✅ 前端开发计划（`frontend/开发计划.md`）
- ✅ 项目 README（根目录）

### 3. Git 提交规范

```bash
# 详细的 commit message
git commit -m "feat: 完成 macOS AI 实时语音助手后端实现

## 核心功能
- ✅ 音频捕获模块（ScreenCaptureKit）
- ✅ STT 模块（ElevenLabs + Qwen-Audio）
...

Co-Authored-By: Claude (GLM-4.7) <noreply@anthropic.com>"
```

---

## 技术要点

### macOS 音频捕获

需要 macOS 12.3+ 和屏幕录制权限：

```python
from AVFoundation import AVCaptureSession, AVCaptureDevice
from CoreMedia import CMSampleBufferGetAudioBufferListWithRetainedBlockBuffer

# 创建捕获会话
session = AVCaptureSession.alloc().init()
device = AVCaptureDevice.defaultDeviceWithMediaType_(AVMediaTypeAudio)
```

### STT 集成

**ElevenLabs** (实时):
```python
# WebSocket 连接
ws_url = "wss://api.elevenlabs.io/v1/speech-to-text/eleven_multilingual_v2"
websocket = await websockets.connect(ws_url, headers={"xi-api-key": api_key})
```

**Qwen-Audio** (批量):
```python
# HTTP API
from dashscope import MultiModalConversation
response = MultiModalConversation.call(model="qwen-audio-turbo", messages=[...])
```

### LLM 集成

统一的异步接口：

```python
# OpenAI
from openai import AsyncOpenAI
client = AsyncOpenAI(api_key=...)
response = await client.chat.completions.create(...)

# Anthropic
from anthropic import AsyncAnthropic
client = AsyncAnthropic(api_key=...)
response = await client.messages.create(...)

# Ollama (本地)
import httpx
response = await httpx.post("http://localhost:11434/api/chat", json=...)
```

---

## 性能优化建议

### 1. 音频缓冲

使用环形缓冲区避免内存溢出：

```python
from collections import deque
buffer = deque(maxlen=sample_rate * buffer_duration)
```

### 2. 流式处理

不要等待完整音频再转写：

```python
async def stream_chunks():
    while True:
        chunk = await read_chunk()
        if chunk:
            yield chunk  # 实时处理
```

### 3. 异步 I/O

所有网络和文件操作使用异步：

```python
# 错误（阻塞）
with open(file) as f:
    data = f.read()

# 正确（异步）
import aiofiles
async with aiofiles.open(file) as f:
    data = await f.read()
```

---

## 测试策略

### 1. 单元测试

```python
# 测试工厂模式
def test_stt_factory():
    client = STTFactory.create("elevenlabs", api_key="test")
    assert isinstance(client, ElevenLabsSTT)

# 测试配置
def test_config():
    config = AppConfig()
    assert config.llm.provider == "openai"
```

### 2. 集成测试

使用测试音频文件验证完整流程。

### 3. 手动测试

```bash
# 启动服务
uvicorn app.main:app --reload

# 访问 API 文档
open http://localhost:8000/docs
```

---

## 部署注意事项

### 1. macOS 权限

首次运行需要授予：
- 屏幕录制权限
- 麦克风访问权限（如果使用）

### 2. 环境变量

```bash
# .env 文件
OPENAI_API_KEY=sk-xxx
ANTHROPIC_API_KEY=sk-ant-xxx
ELEVENLABS_API_KEY=xxx
```

### 3. 依赖安装

```bash
# 系统依赖
brew install python@3.10

# Python 依赖
pip install -r requirements.txt
```

---

## 扩展建议

### 1. 添加新的 STT 提供商

1. 在 `core/stt/` 创建新文件
2. 继承 `BaseSTT`
3. 在 `STTFactory.create()` 添加 case

### 2. 添加新的 LLM 提供商

1. 在 `core/llm/` 创建新文件
2. 继承 `BaseLLM`
3. 在 `LLMFactory.create()` 添加 case

### 3. 添加新的 REST API 端点

1. 在 `api/routes/` 创建新文件
2. 使用 FastAPI 路由装饰器
3. 在 `main.py` 注册路由

---

## 相关资源

- [FastAPI 文档](https://fastapi.tiangolo.com/)
- [PyObjC 文档](https://pyobjc.readthedocs.io/)
- [WebSockets in Python](https://websockets.readthedocs.io/)
- [ElevenLabs API](https://docs.elevenlabs.io/)
- [OpenAI API](https://platform.openai.com/docs)

---

**最后更新**: 2026-01-28
**维护者**: Claude Code
