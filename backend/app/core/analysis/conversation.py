"""
对话分析器
维护对话上下文和识别说话人
"""
from datetime import datetime
from typing import List, Optional, Literal
from dataclasses import dataclass
from loguru import logger


@dataclass
class ConversationTurn:
    """对话轮次"""
    speaker: Literal["user", "other"]
    text: str
    timestamp: datetime
    confidence: float = 1.0

    def __repr__(self):
        return f"[{self.speaker}] {self.text[:50]}..."


class ConversationAnalyzer:
    """对话分析器"""

    def __init__(self, max_history: int = 20):
        """
        初始化对话分析器

        Args:
            max_history: 保留的最大对话轮次数
        """
        self.max_history = max_history
        self.conversation_history: List[ConversationTurn] = []
        self.current_speaker: Optional[Literal["user", "other"]] = None
        self.speaker_patterns: dict = {
            "user": [],
            "other": []
        }

    def add_turn(
        self,
        text: str,
        speaker: Optional[Literal["user", "other"]] = None,
        confidence: float = 1.0
    ) -> ConversationTurn:
        """
        添加对话轮次

        Args:
            text: 对话内容
            speaker: 说话人（如果为 None，则自动识别）
            confidence: 置信度

        Returns:
            对话轮次对象
        """
        # 如果没有指定说话人，尝试识别
        if speaker is None:
            speaker = self._identify_speaker(text)

        # 创建对话轮次
        turn = ConversationTurn(
            speaker=speaker,
            text=text,
            timestamp=datetime.now(),
            confidence=confidence
        )

        # 添加到历史记录
        self.conversation_history.append(turn)

        # 限制历史记录长度
        if len(self.conversation_history) > self.max_history:
            self.conversation_history.pop(0)

        # 更新当前说话人
        self.current_speaker = speaker

        logger.debug(f"Added conversation turn: {turn}")
        return turn

    def _identify_speaker(self, text: str) -> Literal["user", "other"]:
        """
        识别说话人
        简单实现：基于轮流说话的假设

        Args:
            text: 对话内容

        Returns:
            说话人标识
        """
        # 如果没有历史记录，默认为对方
        if not self.conversation_history:
            return "other"

        # 基于轮流说话的假设
        last_speaker = self.conversation_history[-1].speaker
        return "user" if last_speaker == "other" else "other"

    def get_recent_history(self, n: int = 5) -> List[ConversationTurn]:
        """
        获取最近的对话历史

        Args:
            n: 获取的轮次数

        Returns:
            对话轮次列表
        """
        return self.conversation_history[-n:]

    def get_context_text(self, n: int = 5) -> str:
        """
        获取对话上下文文本

        Args:
            n: 获取的轮次数

        Returns:
            格式化的对话文本
        """
        recent = self.get_recent_history(n)
        lines = []
        for turn in recent:
            speaker_label = "我" if turn.speaker == "user" else "对方"
            lines.append(f"{speaker_label}: {turn.text}")
        return "\n".join(lines)

    def get_speaker_turns(self, speaker: Literal["user", "other"]) -> List[ConversationTurn]:
        """
        获取特定说话人的所有轮次

        Args:
            speaker: 说话人标识

        Returns:
            对话轮次列表
        """
        return [turn for turn in self.conversation_history if turn.speaker == speaker]

    def get_last_turn(self) -> Optional[ConversationTurn]:
        """
        获取最后一个对话轮次

        Returns:
            对话轮次对象，如果没有则返回 None
        """
        return self.conversation_history[-1] if self.conversation_history else None

    def clear(self) -> None:
        """清空对话历史"""
        self.conversation_history.clear()
        self.current_speaker = None
        logger.info("Conversation history cleared")

    def get_statistics(self) -> dict:
        """
        获取对话统计信息

        Returns:
            统计信息字典
        """
        user_turns = self.get_speaker_turns("user")
        other_turns = self.get_speaker_turns("other")

        return {
            "total_turns": len(self.conversation_history),
            "user_turns": len(user_turns),
            "other_turns": len(other_turns),
            "current_speaker": self.current_speaker,
            "duration": self._calculate_duration(),
        }

    def _calculate_duration(self) -> float:
        """
        计算对话持续时间（秒）

        Returns:
            持续时间
        """
        if len(self.conversation_history) < 2:
            return 0.0

        first = self.conversation_history[0].timestamp
        last = self.conversation_history[-1].timestamp
        return (last - first).total_seconds()

    def export_history(self) -> List[dict]:
        """
        导出对话历史

        Returns:
            对话历史列表（字典格式）
        """
        return [
            {
                "speaker": turn.speaker,
                "text": turn.text,
                "timestamp": turn.timestamp.isoformat(),
                "confidence": turn.confidence,
            }
            for turn in self.conversation_history
        ]