"""
短期记忆 - 当前会话上下文
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid

from .base_memory import BaseMemory, MemoryEntry


class ShortTermMemory(BaseMemory):
    """短期记忆 - 存储当前任务的上下文"""

    def __init__(self, max_size: int = 100):
        self.max_size = max_size
        self.memories: List[MemoryEntry] = []

    async def add(self, content: str, metadata: Dict[str, Any]) -> str:
        """添加记忆"""
        memory_id = str(uuid.uuid4())
        entry = MemoryEntry(
            id=memory_id,
            content=content,
            metadata=metadata,
            timestamp=datetime.now()
        )

        self.memories.append(entry)

        # 超过最大容量时移除最旧的记忆
        if len(self.memories) > self.max_size:
            self.memories.pop(0)

        return memory_id

    async def search(self, query: str, top_k: int = 5) -> List[MemoryEntry]:
        """搜索记忆 - 简单实现，返回最近的记忆"""
        return self.memories[-top_k:]

    async def get(self, memory_id: str) -> Optional[MemoryEntry]:
        """获取特定记忆"""
        for memory in self.memories:
            if memory.id == memory_id:
                return memory
        return None

    async def clear(self):
        """清空记忆"""
        self.memories.clear()

    def get_recent(self, n: int = 10) -> List[MemoryEntry]:
        """获取最近的 n 条记忆"""
        return self.memories[-n:]
