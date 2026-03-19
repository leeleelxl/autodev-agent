"""
LLM 模块

支持多个 LLM 提供商的统一接口
- 原生客户端: BaseLLMClient, KimiClient, ClaudeClient, QwenClient
- LangChain 适配: create_langchain_llm (用于 ReAct Agent)
"""

from .base_client import BaseLLMClient, LLMMessage, LLMResponse, LLMProvider
from .claude_client import ClaudeClient
from .kimi_client import KimiClient
from .qwen_client import QwenClient
from .factory import LLMFactory
from .langchain_adapter import create_langchain_llm

__all__ = [
    "BaseLLMClient",
    "LLMMessage",
    "LLMResponse",
    "LLMProvider",
    "ClaudeClient",
    "KimiClient",
    "QwenClient",
    "LLMFactory",
    "create_langchain_llm",
]
