"""
LLM Factory - 创建 LLM 客户端
"""

from typing import Optional
from .base_client import BaseLLMClient, LLMProvider
from .claude_client import ClaudeClient
from .kimi_client import KimiClient
from .qwen_client import QwenClient


class LLMFactory:
    """LLM 客户端工厂"""

    # 默认模型配置
    DEFAULT_MODELS = {
        LLMProvider.ANTHROPIC: "claude-3-5-sonnet-20241022",
        LLMProvider.MOONSHOT: "moonshot-v1-8k",
        LLMProvider.QWEN: "qwen-max",
    }

    @staticmethod
    def create_client(
        provider: LLMProvider,
        api_key: str,
        model: Optional[str] = None
    ) -> BaseLLMClient:
        """
        创建 LLM 客户端

        Args:
            provider: LLM 提供商
            api_key: API Key
            model: 模型名称（可选，使用默认模型）

        Returns:
            LLM 客户端实例
        """
        if model is None:
            model = LLMFactory.DEFAULT_MODELS[provider]

        if provider == LLMProvider.ANTHROPIC:
            return ClaudeClient(api_key, model)
        elif provider == LLMProvider.MOONSHOT:
            return KimiClient(api_key, model)
        elif provider == LLMProvider.QWEN:
            return QwenClient(api_key, model)
        else:
            raise ValueError(f"不支持的 LLM 提供商: {provider}")

    @staticmethod
    def get_available_providers() -> list:
        """获取所有可用的提供商"""
        return list(LLMProvider)

    @staticmethod
    def get_default_model(provider: LLMProvider) -> str:
        """获取提供商的默认模型"""
        return LLMFactory.DEFAULT_MODELS[provider]
