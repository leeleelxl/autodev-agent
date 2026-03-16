"""
Memory 系统 - 基础接口
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from datetime import datetime


class MemoryEntry(BaseModel):
    """记忆条目"""
    id: str
    content: str
    metadata: Dict[str, Any]
    timestamp: datetime
    embedding: Optional[List[float]] = None


class BaseMemory(ABC):
    """记忆系统基类"""

    @abstractmethod
    async def add(self, content: str, metadata: Dict[str, Any]) -> str:
        """添加记忆"""
        pass

    @abstractmethod
    async def search(self, query: str, top_k: int = 5) -> List[MemoryEntry]:
        """搜索相关记忆"""
        pass

    @abstractmethod
    async def get(self, memory_id: str) -> Optional[MemoryEntry]:
        """获取特定记忆"""
        pass

    @abstractmethod
    async def clear(self):
        """清空记忆"""
        pass
