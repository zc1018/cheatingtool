# macOS AI 实时语音助手

一个强大的 macOS 桌面工具，实时监听系统音频，通过 AI 分析对话内容，为用户提供实时建议和回复。

## 项目简介

本应用专为需要实时沟通辅助的场景设计（如销售谈判、客服、技术面试等），通过语音识别和 AI 分析，帮助用户：

- 🎤 **实时转写**: 自动转写系统音频中的对话
- 🧠 **AI 分析**: 分析对方的真实意图、潜在顾虑和需求
- 💬 **建议回复**: 智能生成针对性的回复建议
- 🎯 **场景适配**: 支持自定义场景和分析策略

## 技术栈

### 后端
- **框架**: FastAPI (Python 3.10+)
- **音频捕获**: ScreenCaptureKit (PyObjC)
- **语音转文字**: ElevenLabs / 通义千问 Qwen-Audio
- **AI 分析**: OpenAI GPT-4 / Anthropic Claude / Ollama
- **实时通信**: WebSocket
- **数据存储**: JSON / SQLite

### 前端
- **框架**: Electron + React 18
- **UI 库**: shadcn/ui + TailwindCSS
- **状态管理**: Zustand
- **音频可视化**: Wavesurfer.js

## 项目结构

```
cheatingtool/
├── backend/                  # 后端代码
│   ├── app/
│   │   ├── main.py          # FastAPI 入口
│   │   ├── config.py        # 配置管理
│   │   ├── api/             # REST API 和 WebSocket
│   │   ├── core/            # 核心模块（音频、STT、LLM、分析）
│   │   ├── models/          # 数据模型
│   │   └── services/        # 业务服务层
│   ├── data/                # 数据目录
│   ├── requirements.txt     # Python 依赖
│   └── API.md              # API 文档
├── frontend/                # 前端代码
│   └── 开发计划.md          # 前端开发计划
└── README.md               # 本文件
```

## 核心功能

### 1. 音频捕获
- 使用 ScreenCaptureKit 捕获 macOS 系统音频
- 支持所有应用程序的音频输出
- 实时音频缓冲和流式处理

### 2. 语音转文字 (STT)
- **ElevenLabs**: WebSocket 实时转写，支持多语言
- **Qwen-Audio**: 阿里云 DashScope API，适合中文
- 可切换不同的 STT 提供商

### 3. AI 分析
- **OpenAI**: GPT-4o, GPT-4 Turbo
- **Anthropic**: Claude 3.5 Sonnet, Claude 3 Opus
- **Ollama**: 本地开源模型（Llama, Mistral 等）
- 实时分析对话意图、需求和建议回复

### 4. 对话管理
- 维护完整的对话历史
- 识别说话人（用户/对方）
- 对话统计和分析

## 快速开始

### 环境要求

- macOS 12.3+
- Python 3.10+
- Node.js 18+ (前端开发)

### 后端设置

```bash
# 1. 进入后端目录
cd backend

# 2. 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 配置环境变量（可选）
cp .env.example .env
# 编辑 .env 文件，添加 API keys

# 5. 启动服务
uvicorn app.main:app --reload
```

后端服务将在 `http://localhost:8000` 启动。

### 前端设置

前端开发正在进行中，详细计划请查看 `frontend/开发计划.md`。

## 配置说明

### API Keys 配置

在 `backend/data/config.json` 中配置：

```json
{
  "llm": {
    "provider": "openai",
    "api_key": "sk-your-openai-key",
    "model": "gpt-4o",
    "temperature": 0.7
  },
  "stt": {
    "provider": "elevenlabs",
    "api_key": "your-elevenlabs-key",
    "language": "zh"
  }
}
```

或通过 API 更新配置：

```bash
curl -X PUT http://localhost:8000/api/config/llm \
  -H "Content-Type: application/json" \
  -d '{"provider": "openai", "model": "gpt-4o", "api_key": "sk-xxx"}'
```

### 场景配置

自定义场景以优化分析效果：

```json
{
  "scenario": {
    "name": "销售谈判",
    "ai_role": "你是一个专业的销售顾问助手",
    "user_goal": "成功签下这个客户",
    "context": "我是一家软件公司的销售，正在演示产品"
  }
}
```

## API 使用

### REST API

```bash
# 健康检查
curl http://localhost:8000/health

# 开始音频捕获
curl -X POST http://localhost:8000/api/audio/start

# 获取配置
curl http://localhost:8000/api/config/

# 更新配置
curl -X PUT http://localhost:8000/api/config/ \
  -H "Content-Type: application/json" \
  -d '{"llm": {"model": "gpt-4o-mini"}}'
```

### WebSocket

连接到实时流：

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/stream');

ws.onmessage = (event) => {
  const message = JSON.parse(event.data);

  if (message.type === 'transcription') {
    console.log('转写:', message.text);
  }

  if (message.type === 'analysis') {
    console.log('分析:', message);
  }
};
```

详细 API 文档请查看 [`backend/API.md`](backend/API.md)。

## 开发说明

### 后端开发（Claude Code）

后端开发由 Claude Code 负责，直接在 `backend/` 目录中开发：

```bash
cd backend
# 编辑代码
# 运行测试
# 提交代码
```

### 前端开发（Gemini 3）

前端开发由 Gemini 3 负责，在 Antigravity 环境中根据 `frontend/开发计划.md` 进行开发。

详细分工请查看项目的 CLAUDE.md 文件。

## 常见问题

### 1. macOS 音频捕获权限问题

首次运行时，需要授予屏幕录制权限：

1. 打开"系统设置" → "隐私与安全性"
2. 找到"屏幕录制"
3. 添加 Python 或终端应用

### 2. API Key 无效

确保：
- API Key 格式正确
- 账户有足够的配额
- 网络连接正常

### 3. 音频捕获无声音

检查：
- 系统音频输出是否正常
- 是否有应用程序正在播放音频
- ScreenCaptureKit 权限是否已授予

## 许可证

本项目仅用于学习和研究目的。使用时请遵守相关服务的使用条款。

## 贡献

欢迎提交 Issue 和 Pull Request！

## 致谢

- [FastAPI](https://fastapi.tiangolo.com/) - 现代化的 Python Web 框架
- [OpenAI](https://openai.com/) - GPT-4 API
- [Anthropic](https://www.anthropic.com/) - Claude API
- [ElevenLabs](https://elevenlabs.io/) - 语音转文字 API
- [阿里云](https://www.aliyun.com/) - DashScope API

---

**最后更新**: 2026-01-28
**版本**: 1.0.0
