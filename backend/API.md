# macOS AI 实时语音助手 - API 文档

## 概述

本文档描述了 macOS AI 实时语音助手后端的所有 API 端点。

**基础 URL**: `http://localhost:8000`

## 目录

- [REST API](#rest-api)
  - [音频控制](#音频控制)
  - [配置管理](#配置管理)
  - [LLM 管理](#llm-管理)
  - [Prompt 模板](#prompt-模板)
  - [系统状态](#系统状态)
- [WebSocket API](#websocket-api)
- [数据模型](#数据模型)
- [错误处理](#错误处理)

---

## REST API

### 音频控制

#### 开始音频捕获

**端点**: `POST /api/audio/start`

**描述**: 启动系统音频捕获

**响应**:
```json
{
  "success": true,
  "message": "Audio capture started",
  "status": {
    "is_capturing": true,
    "sample_rate": 16000,
    "channels": 1,
    "duration": 0.0
  }
}
```

**错误响应**:
```json
{
  "detail": "Failed to start audio capture"
}
```

#### 停止音频捕获

**端点**: `POST /api/audio/stop`

**描述**: 停止系统音频捕获

**响应**:
```json
{
  "success": true,
  "message": "Audio capture stopped",
  "status": {
    "is_capturing": false,
    "sample_rate": 16000,
    "channels": 1,
    "duration": 120.5
  }
}
```

#### 获取音频状态

**端点**: `GET /api/audio/status`

**描述**: 获取当前音频捕获状态

**响应**:
```json
{
  "is_capturing": true,
  "sample_rate": 16000,
  "channels": 1,
  "duration": 120.5
}
```

#### 音频控制（统一接口）

**端点**: `POST /api/audio/control`

**描述**: 统一的音频控制接口

**请求体**:
```json
{
  "action": "start" | "stop"
}
```

**响应**: 同开始/停止音频捕获

---

### 配置管理

#### 获取完整配置

**端点**: `GET /api/config/`

**描述**: 获取所有配置信息

**响应**:
```json
{
  "llm": {
    "provider": "openai",
    "api_key": "sk-***",
    "base_url": null,
    "model": "gpt-4o",
    "temperature": 0.7,
    "max_tokens": 2000
  },
  "stt": {
    "provider": "elevenlabs",
    "api_key": "***",
    "language": "zh",
    "model": "eleven_multilingual_v2"
  },
  "scenario": {
    "name": "销售谈判",
    "ai_role": "你是一个专业的销售顾问助手",
    "user_goal": "成功签下这个客户",
    "context": "我是一家软件公司的销售"
  },
  "audio": {
    "sample_rate": 16000,
    "channels": 1,
    "chunk_duration": 1.0,
    "buffer_size": 10
  },
  "analysis_prompt": "基于对话内容，分析对方的：\n1. 真实目的\n2. 潜在顾虑\n3. 决策因素\n并给出建议回复"
}
```

#### 更新配置

**端点**: `PUT /api/config/`

**描述**: 更新配置（支持部分更新）

**请求体**:
```json
{
  "llm": {
    "model": "gpt-4o-mini",
    "temperature": 0.5
  },
  "scenario": {
    "name": "技术面试"
  }
}
```

**响应**:
```json
{
  "success": true,
  "message": "Configuration updated successfully",
  "config": { /* 完整配置 */ }
}
```

#### 获取 LLM 配置

**端点**: `GET /api/config/llm`

**响应**:
```json
{
  "provider": "openai",
  "api_key": "sk-***",
  "model": "gpt-4o",
  "temperature": 0.7,
  "max_tokens": 2000
}
```

#### 更新 LLM 配置

**端点**: `PUT /api/config/llm`

**请求体**: 同获取 LLM 配置的响应格式

#### 获取 STT 配置

**端点**: `GET /api/config/stt`

**响应**:
```json
{
  "provider": "elevenlabs",
  "api_key": "***",
  "language": "zh",
  "model": "eleven_multilingual_v2"
}
```

#### 更新 STT 配置

**端点**: `PUT /api/config/stt`

**请求体**: 同获取 STT 配置的响应格式

#### 获取场景配置

**端点**: `GET /api/config/scenario`

**响应**:
```json
{
  "name": "销售谈判",
  "ai_role": "你是一个专业的销售顾问助手",
  "user_goal": "成功签下这个客户",
  "context": "我是一家软件公司的销售"
}
```

#### 更新场景配置

**端点**: `PUT /api/config/scenario`

**请求体**: 同获取场景配置的响应格式

---

### LLM 管理

#### 获取支持的 LLM 提供商

**端点**: `GET /api/llm/providers`

**响应**:
```json
["openai", "anthropic", "ollama"]
```

#### 获取提供商信息

**端点**: `GET /api/llm/providers/{provider}`

**响应**:
```json
{
  "provider": "openai",
  "name": "OpenAI",
  "default_model": "gpt-4o",
  "available_models": [
    "gpt-4o",
    "gpt-4o-mini",
    "gpt-4-turbo",
    "gpt-3.5-turbo"
  ]
}
```

#### 获取提供商的模型列表

**端点**: `GET /api/llm/models/{provider}`

**响应**:
```json
["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-3.5-turbo"]
```

#### 测试 LLM 连接

**端点**: `POST /api/llm/test`

**请求体**:
```json
{
  "provider": "openai",
  "api_key": "sk-xxx",
  "model": "gpt-4o",
  "prompt": "Hello, this is a test."
}
```

**响应**:
```json
{
  "success": true,
  "provider": "openai",
  "model": "gpt-4o",
  "response": "Hello! How can I help you today?",
  "usage": {
    "prompt_tokens": 5,
    "completion_tokens": 7,
    "total_tokens": 12
  }
}
```

---

### Prompt 模板

#### 获取 Prompt 列表

**端点**: `GET /api/prompts/`

**查询参数**:
- `category` (可选): 按分类筛选
- `limit` (可选): 限制返回数量，默认 50

**响应**:
```json
{
  "prompts": [
    {
      "id": "20240128120000",
      "name": "销售谈判分析",
      "content": "分析销售对话...",
      "category": "sales",
      "created_at": "2024-01-28T12:00:00",
      "updated_at": "2024-01-28T12:00:00"
    }
  ],
  "total": 1
}
```

#### 获取单个 Prompt

**端点**: `GET /api/prompts/{prompt_id}`

**响应**: 同列表中的单个 prompt 对象

#### 创建 Prompt

**端点**: `POST /api/prompts/`

**请求体**:
```json
{
  "name": "销售谈判分析",
  "content": "分析销售对话中的关键点...",
  "category": "sales"
}
```

**响应**: 创建的 prompt 对象

#### 更新 Prompt

**端点**: `PUT /api/prompts/{prompt_id}`

**请求体**:
```json
{
  "name": "更新的名称",
  "content": "更新的内容",
  "category": "sales"
}
```

**响应**: 更新后的 prompt 对象

#### 删除 Prompt

**端点**: `DELETE /api/prompts/{prompt_id}`

**响应**:
```json
{
  "success": true,
  "message": "Prompt deleted"
}
```

---

### 系统状态

#### 根路径

**端点**: `GET /`

**响应**:
```json
{
  "name": "macOS AI Voice Assistant Backend",
  "version": "1.0.0",
  "status": "running"
}
```

#### 健康检查

**端点**: `GET /health`

**响应**:
```json
{
  "status": "healthy",
  "services": {
    "audio": {
      "is_running": true,
      "sample_rate": 16000,
      "channels": 1,
      "buffer_level": 0.5,
      "available_duration": 5.0
    },
    "transcription": {
      "is_running": true,
      "provider": "elevenlabs",
      "language": "zh",
      "model": "eleven_multilingual_v2",
      "is_connected": true
    },
    "analysis": {
      "is_running": true,
      "llm_provider": "openai",
      "llm_model": "gpt-4o",
      "scenario": "销售谈判",
      "conversation_turns": 10
    }
  },
  "websocket_connections": 2
}
```

---

## WebSocket API

### 连接端点

**端点**: `ws://localhost:8000/ws/stream`

**描述**: 实时推送转写结果和分析建议

### 消息类型

#### 1. 控制命令（客户端 -> 服务端）

```json
{
  "type": "command",
  "action": "start" | "stop" | "status"
}
```

#### 2. 转写结果（服务端 -> 客户端）

```json
{
  "type": "transcription",
  "text": "你好，请问有什么可以帮助你的？",
  "is_final": true,
  "speaker": "other"
}
```

#### 3. 分析结果（服务端 -> 客户端）

```json
{
  "type": "analysis",
  "intent": "对方想了解产品价格",
  "thoughts": "对方可能在比较多家供应商，关注性价比",
  "real_need": "寻找性价比高的解决方案",
  "suggested_reply": "我们的产品在同类中性价比很高，我可以给您详细介绍一下..."
}
```

#### 4. 错误消息（服务端 -> 客户端）

```json
{
  "type": "error",
  "message": "转写服务连接失败",
  "code": "TRANSCRIPTION_ERROR"
}
```

#### 5. 状态信息（服务端 -> 客户端）

```json
{
  "type": "status",
  "data": {
    "audio": { /* 音频服务状态 */ },
    "transcription": { /* 转写服务状态 */ },
    "analysis": { /* 分析服务状态 */ },
    "connections": 2
  }
}
```

#### 6. 信息消息（服务端 -> 客户端）

```json
{
  "type": "info",
  "message": "Services started"
}
```

### 使用示例

#### JavaScript (浏览器)

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/stream');

ws.onopen = () => {
  console.log('WebSocket connected');

  // 发送启动命令
  ws.send(JSON.stringify({
    type: 'command',
    action: 'start'
  }));
};

ws.onmessage = (event) => {
  const message = JSON.parse(event.data);

  switch (message.type) {
    case 'transcription':
      console.log('转写结果:', message.text);
      break;
    case 'analysis':
      console.log('分析结果:', message);
      break;
    case 'error':
      console.error('错误:', message.message);
      break;
  }
};

ws.onerror = (error) => {
  console.error('WebSocket error:', error);
};

ws.onclose = () => {
  console.log('WebSocket disconnected');
};

// 停止服务
function stop() {
  ws.send(JSON.stringify({
    type: 'command',
    action: 'stop'
  }));
}
```

#### Python

```python
import asyncio
import websockets
import json

async def websocket_client():
    uri = "ws://localhost:8000/ws/stream"

    async with websockets.connect(uri) as websocket:
        # 发送启动命令
        await websocket.send(json.dumps({
            "type": "command",
            "action": "start"
        }))

        # 接收消息
        while True:
            message = await websocket.recv()
            data = json.loads(message)

            if data['type'] == 'transcription':
                print(f"转写: {data['text']}")
            elif data['type'] == 'analysis':
                print(f"分析: {data}")
            elif data['type'] == 'error':
                print(f"错误: {data['message']}")

asyncio.run(websocket_client())
```

---

## 数据模型

### AudioStatus

```typescript
{
  is_capturing: boolean;
  sample_rate: number;
  channels: number;
  duration: number;
}
```

### TranscriptionResult

```typescript
{
  text: string;
  is_final: boolean;
  speaker: "user" | "other" | "unknown";
  timestamp: string;
  confidence?: number;
}
```

### AnalysisResult

```typescript
{
  intent: string;
  thoughts: string;
  real_need: string;
  suggested_reply: string;
  timestamp: string;
}
```

### PromptTemplate

```typescript
{
  id: string;
  name: string;
  content: string;
  category: string;
  created_at: string;
  updated_at: string;
}
```

---

## 错误处理

所有错误响应遵循以下格式：

```json
{
  "detail": "错误描述信息"
}
```

### HTTP 状态码

- `200 OK`: 请求成功
- `201 Created`: 资源创建成功
- `400 Bad Request`: 请求参数错误
- `404 Not Found`: 资源不存在
- `500 Internal Server Error`: 服务器内部错误
- `503 Service Unavailable`: 服务不可用

---

## 认证

当前版本不包含认证机制。在生产环境中，建议添加：

- API 密钥认证
- JWT Token 认证
- WebSocket 连接认证

---

## 速率限制

当前版本没有速率限制。建议在生产环境中添加：

- 请求频率限制
- WebSocket 连接数限制
- API 调用配额

---

## 附录

### 支持的 LLM 提供商

| 提供商 | 模型 |
|--------|------|
| OpenAI | gpt-4o, gpt-4o-mini, gpt-4-turbo, gpt-3.5-turbo |
| Anthropic | claude-3-5-sonnet, claude-3-opus, claude-3-sonnet, claude-3-haiku |
| Ollama | llama2, llama3, mistral, qwen, gemma |

### 支持的 STT 提供商

| 提供商 | 模型 |
|--------|------|
| ElevenLabs | eleven_multilingual_v2 |
| Qwen | qwen-audio-turbo |

---

**最后更新**: 2026-01-28
**版本**: 1.0.0
