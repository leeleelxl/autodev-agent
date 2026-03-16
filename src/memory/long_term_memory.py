"""
长期记忆 - 向量数据库存储
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid

from .base_memory import BaseMemory, MemoryEntry


class LongTermMemory(BaseMemory):
    """长期记忆 - 使用向量数据库存储历史经验"""

    def __init__(self, persist_dir: str = "./data/chroma"):
        self.persist_dir = persist_dir
        # TODO: 初始化 ChromaDB
        self.collection = None

    async def add(self, content: str, metadata: Dict[str, Any]) -> str:
        """添加记忆到向量数据库"""
        memory_id = str(uuid.uuid4())

        # TODO: 实现向量化和存储
        # 1. 使用 embedding model 生成向量
        # 2. 存储到 ChromaDB

        return memory_id

    async def search(self, query: str, top_k: int = 5) -> List[MemoryEntry]:
        """向量搜索相关记忆"""
        # TODO: 实现向量搜索
        # 1. 将 query 向量化
        # 2. 在 ChromaDB 中搜索
        # 3. 返回最相关的记忆

        return []

    async def get(self, memory_id: str) -> Optional[MemoryEntry]:
        """获取特定记忆"""
        # TODO: 从 ChromaDB 获取
        return None

    async def clear(self):
        """清空记忆"""
        # TODO: 清空 ChromaDB collection
        pass
