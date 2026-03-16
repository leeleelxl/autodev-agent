"""
工具集 - Agent 可用的工具
"""

from abc import ABC, abstractmethod
from typing import Any, Dict
from pydantic import BaseModel


class ToolResult(BaseModel):
    """工具执行结果"""
    success: bool
    output: Any
    error: str = ""


class BaseTool(ABC):
    """工具基类"""

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

    @abstractmethod
    async def execute(self, **kwargs) -> ToolResult:
        """执行工具"""
        pass
