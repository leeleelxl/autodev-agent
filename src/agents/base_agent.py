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
