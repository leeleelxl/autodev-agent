"""
LLM Provider 抽象层

支持多个 LLM 提供商：Claude, Kimi, Qwen
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from enum import Enum


class LLMProvider(str, Enum):
    """LLM 提供商"""
    ANTHROPIC = "anthropic"
    MOONSHOT = "moonshot"  # Kimi
    QWEN = "qwen"


class LLMMessage:
    """统一的消息格式"""
    def __init__(self, role: str, content: str):
        self.role = role
        self.content = content


class LLMResponse:
    """统一的响应格式"""
    def __init__(self, content: str, model: str, usage: Optional[Dict[str, int]] = None):
        self.content = content
        self.model = model
        self.usage = usage or {}


class BaseLLMClient(ABC):
    """LLM 客户端基类"""

    def __init__(self, api_key: str, model: str):
        self.api_key = api_key
        self.model = model

    @abstractmethod
    async def chat(
        self,
        messages: List[LLMMessage],
        temperature: float = 0.7,
        max_tokens: int = 4096,
        **kwargs
    ) -> LLMResponse:
        """发送聊天请求"""
        pass

    @abstractmethod
    def get_provider(self) -> LLMProvider:
        """获取提供商类型"""
        pass
