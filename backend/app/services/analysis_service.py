"""
分析服务
管理对话分析和建议生成
"""
import asyncio
from typing import Optional
from loguru import logger

from ..core.llm.base import BaseLLM
from ..core.llm.factory import LLMFactory
from ..core.analysis.conversation import ConversationAnalyzer
from ..core.analysis.suggestions import SuggestionGenerator


class AnalysisService:
    """分析服务"""

    def __init__(
        self,
        llm_provider: str = "openai",
        llm_api_key: Optional[str] = None,
        llm_base_url: Optional[str] = None,
        llm_model: Optional[str] = None,
        llm_temperature: float = 0.7,
        llm_max_tokens: int = 2000,
        scenario_config: Optional[dict] = None,
        analysis_prompt: Optional[str] = None,
    ):
        """
        初始化分析服务

        Args:
            llm_provider: LLM 提供商
            llm_api_key: LLM API 密钥
            llm_base_url: LLM API 基础 URL
            llm_model: LLM 模型名称
            llm_temperature: LLM 温度参数
            llm_max_tokens: LLM 最大 token 数
            scenario_config: 场景配置
            analysis_prompt: 分析提示词
        """
        self.llm_provider = llm_provider
        self.llm_api_key = llm_api_key
        self.llm_base_url = llm_base_url
        self.llm_model = llm_model
        self.llm_temperature = llm_temperature
        self.llm_max_tokens = llm_max_tokens

        self.scenario_config = scenario_config or {}
        self.analysis_prompt = analysis_prompt

        self.llm_client: Optional[BaseLLM] = None
        self.conversation_analyzer = ConversationAnalyzer()
        self.suggestion_generator: Optional[SuggestionGenerator] = None
        self.is_running = False

    async def start(self) -> bool:
        """
        启动分析服务

        Returns:
            是否成功启动
        """
        if self.is_running:
            logger.warning("Analysis service already running")
            return False

        try:
            # 创建 LLM 客户端
            self.llm_client = LLMFactory.create(
                provider=self.llm_provider,
                api_key=self.llm_api_key,
                base_url=self.llm_base_url,
                model=self.llm_model,
                temperature=self.llm_temperature,
                max_tokens=self.llm_max_tokens,
            )

            # 创建建议生成器
            self.suggestion_generator = SuggestionGenerator(
                llm_client=self.llm_client,
                scenario_config=self.scenario_config,
                analysis_prompt=self.analysis_prompt,
            )

            self.is_running = True
            logger.info(f"Analysis service started with {self.llm_provider}")
            return True

        except Exception as e:
            logger.error(f"Failed to start analysis service: {e}")
            return False

    async def stop(self) -> bool:
        """
        停止分析服务

        Returns:
            是否成功停止
        """
        if not self.is_running:
            logger.warning("Analysis service not running")
            return False

        try:
            self.llm_client = None
            self.suggestion_generator = None
            self.is_running = False
            logger.info("Analysis service stopped")
            return True

        except Exception as e:
            logger.error(f"Failed to stop analysis service: {e}")
            return False

    def add_conversation_turn(
        self,
        text: str,
        speaker: Optional[str] = None,
        confidence: float = 1.0
    ) -> None:
        """
        添加对话轮次

        Args:
            text: 对话内容
            speaker: 说话人
            confidence: 置信度
        """
        if not self.is_running:
            logger.warning("Analysis service not running")
            return

        self.conversation_analyzer.add_turn(text, speaker, confidence)
        logger.debug(f"Added conversation turn: {text[:50]}...")

    async def generate_suggestion(self, context_turns: int = 5) -> Optional[dict]:
        """
        生成回复建议

        Args:
            context_turns: 使用的上下文轮次数

        Returns:
            建议字典
        """
        if not self.is_running or not self.suggestion_generator:
            logger.error("Analysis service not running")
            return None

        try:
            suggestion = await self.suggestion_generator.generate_suggestion(
                conversation_analyzer=self.conversation_analyzer,
                context_turns=context_turns,
            )
            return suggestion

        except Exception as e:
            logger.error(f"Error generating suggestion: {e}")
            return None

    def get_conversation_history(self, n: int = 10) -> list:
        """
        获取对话历史

        Args:
            n: 获取的轮次数

        Returns:
            对话历史列表
        """
        return self.conversation_analyzer.export_history()[-n:]

    def get_conversation_statistics(self) -> dict:
        """
        获取对话统计信息

        Returns:
            统计信息字典
        """
        return self.conversation_analyzer.get_statistics()

    def clear_conversation(self) -> None:
        """清空对话历史"""
        self.conversation_analyzer.clear()
        logger.info("Conversation history cleared")

    def update_scenario(self, scenario_config: dict) -> None:
        """
        更新场景配置

        Args:
            scenario_config: 新的场景配置
        """
        self.scenario_config = scenario_config
        if self.suggestion_generator:
            self.suggestion_generator.update_scenario(scenario_config)
        logger.info(f"Scenario updated: {scenario_config.get('name', 'Unknown')}")

    def update_analysis_prompt(self, prompt: str) -> None:
        """
        更新分析提示词

        Args:
            prompt: 新的提示词
        """
        self.analysis_prompt = prompt
        if self.suggestion_generator:
            self.suggestion_generator.update_analysis_prompt(prompt)
        logger.info("Analysis prompt updated")

    def update_llm_config(
        self,
        provider: Optional[str] = None,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> None:
        """
        更新 LLM 配置

        Args:
            provider: LLM 提供商
            api_key: API 密钥
            model: 模型名称
            temperature: 温度参数
            max_tokens: 最大 token 数
        """
        need_restart = False

        if provider and provider != self.llm_provider:
            self.llm_provider = provider
            need_restart = True

        if api_key:
            self.llm_api_key = api_key

        if model:
            self.llm_model = model

        if temperature is not None:
            self.llm_temperature = temperature

        if max_tokens is not None:
            self.llm_max_tokens = max_tokens

        if need_restart:
            logger.info("LLM config changed, restarting analysis service")
            asyncio.create_task(self._restart())

    async def _restart(self) -> None:
        """重启服务"""
        await self.stop()
        await self.start()

    def get_status(self) -> dict:
        """
        获取服务状态

        Returns:
            状态字典
        """
        return {
            "is_running": self.is_running,
            "llm_provider": self.llm_provider,
            "llm_model": self.llm_model,
            "scenario": self.scenario_config.get("name", "Unknown"),
            "conversation_turns": len(self.conversation_analyzer.conversation_history),
        }