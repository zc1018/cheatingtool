"""
WebSocket 连接管理器
管理所有 WebSocket 连接和消息广播
"""
from fastapi import WebSocket
from typing import List, Set
from loguru import logger


class ConnectionManager:
    """WebSocket 连接管理器"""

    def __init__(self):
        # 活跃的 WebSocket 连接
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket) -> None:
        """
        接受新的 WebSocket 连接

        Args:
            websocket: WebSocket 连接对象
        """
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket connected. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket) -> None:
        """
        断开 WebSocket 连接

        Args:
            websocket: WebSocket 连接对象
        """
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logger.info(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")

    async def send_personal_message(self, message: dict, websocket: WebSocket) -> None:
        """
        发送个人消息

        Args:
            message: 消息内容
            websocket: 目标 WebSocket 连接
        """
        try:
            import json
            await websocket.send_json(message)
        except Exception as e:
            logger.error(f"Error sending personal message: {e}")

    async def broadcast(self, message: dict) -> None:
        """
        广播消息到所有连接

        Args:
            message: 消息内容
        """
        import json

        # 需要移除断开的连接
        disconnected = []

        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error broadcasting to connection: {e}")
                disconnected.append(connection)

        # 移除断开的连接
        for connection in disconnected:
            self.disconnect(connection)

    async def broadcast_transcription(self, text: str, is_final: bool, speaker: str) -> None:
        """
        广播转写结果

        Args:
            text: 转写文本
            is_final: 是否为最终结果
            speaker: 说话人
        """
        from ...models.schemas import WSTranscriptionMessage

        message = WSTranscriptionMessage(
            text=text,
            is_final=is_final,
            speaker=speaker,
        )

        await self.broadcast(message.model_dump())

    async def broadcast_analysis(self, intent: str, thoughts: str, real_need: str, suggested_reply: str) -> None:
        """
        广播分析结果

        Args:
            intent: 对方意图
            thoughts: AI 思考过程
            real_need: 真实需求
            suggested_reply: 建议回复
        """
        from ...models.schemas import WSAnalysisMessage

        message = WSAnalysisMessage(
            intent=intent,
            thoughts=thoughts,
            real_need=real_need,
            suggested_reply=suggested_reply,
        )

        await self.broadcast(message.model_dump())

    async def broadcast_error(self, message: str, code: str = None) -> None:
        """
        广播错误消息

        Args:
            message: 错误消息
            code: 错误代码
        """
        from ...models.schemas import WSErrorMessage

        error_msg = WSErrorMessage(
            message=message,
            code=code,
        )

        await self.broadcast(error_msg.model_dump())

    def get_connection_count(self) -> int:
        """
        获取当前连接数

        Returns:
            连接数量
        """
        return len(self.active_connections)

    def get_connection_ids(self) -> Set[int]:
        """
        获取所有连接的 ID

        Returns:
            连接 ID 集合
        """
        return {id(conn) for conn in self.active_connections}


# 全局连接管理器实例
manager = ConnectionManager()