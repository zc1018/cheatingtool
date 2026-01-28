"""
建议生成器
分析对方意图并生成回复建议
"""
from typing import Optional
from loguru import logger

from ..llm.base import BaseLLM, Message
from .conversation import ConversationAnalyzer


class SuggestionGenerator:
    """建议生成器"""

    def __init__(
        self,
        llm_client: BaseLLM,
        scenario_config: Optional[dict] = None,
        analysis_prompt: Optional[str] = None,
    ):
        """
        初始化建议生成器

        Args:
            llm_client: LLM 客户端
            scenario_config: 场景配置
            analysis_prompt: 分析提示词
        """
        self.llm_client = llm_client
        self.scenario_config = scenario_config or {}
        self.analysis_prompt = analysis_prompt or self._default_analysis_prompt()

    def _default_analysis_prompt(self) -> str:
        """默认分析提示词"""
        return """基于对话内容，分析对方的：
1. 真实目的
2. 潜在顾虑
3. 决策因素
并给出建议回复"""

    async def generate_suggestion(
        self,
        conversation_analyzer: ConversationAnalyzer,
        context_turns: int = 5,
    ) -> dict:
        """
        生成回复建议

        Args:
            conversation_analyzer: 对话分析器
            context_turns: 使用的上下文轮次数

        Returns:
            建议字典，包含 intent, thoughts, real_need, suggested_reply
        """
        try:
            # 获取对话上下文
            context = conversation_analyzer.get_context_text(context_turns)

            if not context:
                logger.warning("No conversation context available")
                return self._empty_suggestion()

            # 构建分析提示
            messages = self._build_analysis_messages(context)

            # 调用 LLM 生成分析
            response = await self.llm_client.chat(messages)

            # 解析响应
            suggestion = self._parse_response(response.content)

            logger.info(f"Generated suggestion: {suggestion['intent'][:50]}...")
            return suggestion

        except Exception as e:
            logger.error(f"Error generating suggestion: {e}")
            return self._empty_suggestion()

    def _build_analysis_messages(self, context: str) -> list[Message]:
        """
        构建分析消息

        Args:
            context: 对话上下文

        Returns:
            消息列表
        """
        messages = []

        # 系统消息：设置角色和场景
        system_content = self._build_system_prompt()
        messages.append(Message(role="system", content=system_content))

        # 用户消息：对话上下文和分析要求
        user_content = f"""当前对话内容：
{context}

{self.analysis_prompt}

请以 JSON 格式返回分析结果：
{{
  "intent": "对方的意图",
  "thoughts": "你的思考过程",
  "real_need": "对方的真实需求",
  "suggested_reply": "建议的回复内容"
}}"""

        messages.append(Message(role="user", content=user_content))

        return messages

    def _build_system_prompt(self) -> str:
        """
        构建系统提示词

        Returns:
            系统提示词
        """
        ai_role = self.scenario_config.get("ai_role", "你是一个专业的对话助手")
        user_goal = self.scenario_config.get("user_goal", "进行有效的沟通")
        context = self.scenario_config.get("context", "")

        prompt = f"""{ai_role}

用户目标：{user_goal}"""

        if context:
            prompt += f"\n\n场景背景：{context}"

        prompt += """

你的任务是分析对话，理解对方的真实意图和需求，并为用户提供有效的回复建议。"""

        return prompt

    def _parse_response(self, content: str) -> dict:
        """
        解析 LLM 响应

        Args:
            content: 响应内容

        Returns:
            解析后的建议字典
        """
        try:
            import json
            import re

            # 尝试提取 JSON
            json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', content, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                data = json.loads(json_str)
                return {
                    "intent": data.get("intent", ""),
                    "thoughts": data.get("thoughts", ""),
                    "real_need": data.get("real_need", ""),
                    "suggested_reply": data.get("suggested_reply", ""),
                }

            # 如果无法解析 JSON，尝试从文本中提取
            return self._extract_from_text(content)

        except Exception as e:
            logger.error(f"Error parsing response: {e}")
            return self._empty_suggestion()

    def _extract_from_text(self, content: str) -> dict:
        """
        从文本中提取建议信息

        Args:
            content: 文本内容

        Returns:
            建议字典
        """
        # 简单的文本提取逻辑
        lines = content.split("\n")
        result = {
            "intent": "",
            "thoughts": "",
            "real_need": "",
            "suggested_reply": "",
        }

        current_key = None
        for line in lines:
            line = line.strip()
            if "意图" in line or "intent" in line.lower():
                current_key = "intent"
            elif "思考" in line or "thought" in line.lower():
                current_key = "thoughts"
            elif "需求" in line or "need" in line.lower():
                current_key = "real_need"
            elif "建议" in line or "reply" in line.lower() or "回复" in line:
                current_key = "suggested_reply"
            elif current_key and line:
                result[current_key] += line + " "

        return result

    def _empty_suggestion(self) -> dict:
        """
        返回空建议

        Returns:
            空建议字典
        """
        return {
            "intent": "无法分析",
            "thoughts": "对话上下文不足",
            "real_need": "需要更多信息",
            "suggested_reply": "请继续对话以获取更多信息",
        }

    def update_scenario(self, scenario_config: dict) -> None:
        """
        更新场景配置

        Args:
            scenario_config: 新的场景配置
        """
        self.scenario_config = scenario_config
        logger.info(f"Updated scenario: {scenario_config.get('name', 'Unknown')}")

    def update_analysis_prompt(self, prompt: str) -> None:
        """
        更新分析提示词

        Args:
            prompt: 新的提示词
        """
        self.analysis_prompt = prompt
        logger.info("Updated analysis prompt")