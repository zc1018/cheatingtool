"""
配置管理模块
支持从环境变量和 JSON 文件加载配置
"""
import json
from pathlib import Path
from typing import Optional, Literal
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class LLMConfig(BaseModel):
    """LLM 配置"""
    provider: Literal["openai", "anthropic", "ollama", "kimi", "glm", "custom"] = "kimi"
    api_key: Optional[str] = "sk-80qS7TQ0FoYKUM2zWkD5VTJN1a63xlbkbKOog1AWaWJGNmkD"
    base_url: Optional[str] = None
    model: str = "kimi-k2.5"
    temperature: float = 0.7
    max_tokens: int = 2000


class STTConfig(BaseModel):
    """STT 配置"""
    provider: Literal["elevenlabs", "qwen"] = "elevenlabs"
    api_key: Optional[str] = None
    language: str = "zh"
    model: Optional[str] = None


class ScenarioConfig(BaseModel):
    """场景配置"""
    name: str = "通用对话"
    ai_role: str = "你是一个专业的对话助手"
    user_goal: str = "进行有效的沟通"
    context: str = ""


class AudioConfig(BaseModel):
    """音频配置"""
    sample_rate: int = 16000
    channels: int = 1
    chunk_duration: float = 1.0  # 秒
    buffer_size: int = 10  # 缓冲区大小（秒）


class AppConfig(BaseModel):
    """应用配置"""
    llm: LLMConfig = Field(default_factory=LLMConfig)
    stt: STTConfig = Field(default_factory=STTConfig)
    scenario: ScenarioConfig = Field(default_factory=ScenarioConfig)
    audio: AudioConfig = Field(default_factory=AudioConfig)
    analysis_prompt: str = "基于对话内容，分析对方的：\n1. 真实目的\n2. 潜在顾虑\n3. 决策因素\n并给出建议回复"


class Settings(BaseSettings):
    """全局设置"""
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )

    # 数据目录
    data_dir: Path = Path(__file__).parent.parent / "data"
    config_file: Path = data_dir / "config.json"

    def load_config(self) -> AppConfig:
        """从 JSON 文件加载配置"""
        if self.config_file.exists():
            with open(self.config_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                return AppConfig(**data)
        return AppConfig()

    def save_config(self, config: AppConfig) -> None:
        """保存配置到 JSON 文件"""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        with open(self.config_file, "w", encoding="utf-8") as f:
            json.dump(config.model_dump(), f, ensure_ascii=False, indent=2)


# 全局设置实例
settings = Settings()

# 加载应用配置
app_config = settings.load_config()
