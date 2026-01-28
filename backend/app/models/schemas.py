"""
Pydantic 数据模型
定义所有 API 请求/响应模型和内部数据结构
"""
from datetime import datetime
from typing import Optional, Literal, List
from pydantic import BaseModel, Field


# ============ 音频相关 ============

class AudioStatus(BaseModel):
    """音频捕获状态"""
    is_capturing: bool = False
    sample_rate: int = 16000
    channels: int = 1
    duration: float = 0.0  # 已捕获时长（秒）


class AudioControlRequest(BaseModel):
    """音频控制请求"""
    action: Literal["start", "stop", "pause", "resume"]


class AudioControlResponse(BaseModel):
    """音频控制响应"""
    success: bool
    message: str
    status: Optional[AudioStatus] = None


# ============ 转写相关 ============

class TranscriptionResult(BaseModel):
    """转写结果"""
    text: str
    is_final: bool = False
    speaker: Literal["user", "other", "unknown"] = "unknown"
    timestamp: datetime = Field(default_factory=datetime.now)
    confidence: Optional[float] = None


# ============ 分析相关 ============

class AnalysisResult(BaseModel):
    """AI 分析结果"""
    intent: str  # 对方意图
    thoughts: str  # AI 的思考过程
    real_need: str  # 真实需求
    suggested_reply: str  # 建议回复
    timestamp: datetime = Field(default_factory=datetime.now)


# ============ WebSocket 消息 ============

class WSMessage(BaseModel):
    """WebSocket 消息基类"""
    type: str


class WSTranscriptionMessage(WSMessage):
    """转写消息"""
    type: Literal["transcription"] = Field(default="transcription")
    text: str
    is_final: bool
    speaker: Literal["user", "other", "unknown"]


class WSAnalysisMessage(WSMessage):
    """分析消息"""
    type: Literal["analysis"] = Field(default="analysis")
    intent: str
    thoughts: str
    real_need: str
    suggested_reply: str


class WSCommandMessage(WSMessage):
    """控制命令消息"""
    type: Literal["command"] = Field(default="command")
    action: Literal["start", "stop", "pause"]


class WSErrorMessage(WSMessage):
    """错误消息"""
    type: Literal["error"] = Field(default="error")
    message: str
    code: Optional[str] = None


# ============ 配置相关 ============

class ConfigUpdateRequest(BaseModel):
    """配置更新请求"""
    llm: Optional[dict] = None
    stt: Optional[dict] = None
    scenario: Optional[dict] = None
    audio: Optional[dict] = None
    analysis_prompt: Optional[str] = None


class ConfigResponse(BaseModel):
    """配置响应"""
    success: bool
    message: str
    config: Optional[dict] = None


# ============ Prompt 模板相关 ============

class PromptTemplate(BaseModel):
    """Prompt 模板"""
    id: str
    name: str
    content: str
    category: str = "general"
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class PromptCreateRequest(BaseModel):
    """创建 Prompt 请求"""
    name: str
    content: str
    category: str = "general"


class PromptUpdateRequest(BaseModel):
    """更新 Prompt 请求"""
    name: Optional[str] = None
    content: Optional[str] = None
    category: Optional[str] = None


class PromptListResponse(BaseModel):
    """Prompt 列表响应"""
    prompts: List[PromptTemplate]
    total: int


# ============ 会话相关 ============

class ConversationMessage(BaseModel):
    """对话消息"""
    speaker: Literal["user", "other"]
    text: str
    timestamp: datetime = Field(default_factory=datetime.now)


class Session(BaseModel):
    """会话"""
    id: str
    name: str
    messages: List[ConversationMessage] = []
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
