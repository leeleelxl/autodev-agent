"""
Base Agent 抽象类

所有 agent 的基类，定义统一接口
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


class AgentConfig(BaseModel):
    """Agent 配置"""
    name: str
    role: str
    provider: str = "anthropic"  # anthropic, moonshot, qwen
    model: str = "claude-3-5-sonnet-20241022"
    temperature: float = 0.7
    max_tokens: int = 4096


class Message(BaseModel):
    """消息格式"""
    role: str  # system, user, assistant
    content: str
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)


class AgentResponse(BaseModel):
    """Agent 响应"""
    content: str
    reasoning: Optional[str] = None
    actions: List[Dict[str, Any]] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class BaseAgent(ABC):
    """Agent 基类"""

    def __init__(self, config: AgentConfig):
        self.config = config
        self.memory: List[Message] = []
        self.llm_client = None
        self.memory_manager = None

    def set_memory_manager(self, memory_manager):
        """设置记忆管理器"""
        self.memory_manager = memory_manager

    def set_llm_client(self, client):
        """设置 LLM 客户端"""
        from ..llm import BaseLLMClient
        self.llm_client = client

    async def _call_llm(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """
        调用 LLM

        Args:
            messages: 消息列表
            **kwargs: 其他参数

        Returns:
            LLM 响应内容
        """
        if not self.llm_client:
            raise ValueError("LLM 客户端未设置，请先调用 set_llm_client()")

        from ..llm import LLMMessage

        llm_messages = [LLMMessage(role=m["role"], content=m["content"]) for m in messages]

        response = await self.llm_client.chat(
            messages=llm_messages,
            temperature=kwargs.get("temperature", self.config.temperature),
            max_tokens=kwargs.get("max_tokens", self.config.max_tokens)
        )

        return response.content

    @abstractmethod
    async def process(self, task: str, context: Optional[Dict[str, Any]] = None) -> AgentResponse:
        """
        处理任务

        Args:
            task: 任务描述
            context: 上下文信息

        Returns:
            AgentResponse: agent 响应
        """
        pass

    def add_message(self, message: Message):
        """添加消息到记忆"""
        self.memory.append(message)

    def clear_memory(self):
        """清空记忆"""
        self.memory.clear()

    def get_memory(self) -> List[Message]:
        """获取记忆"""
        return self.memory
