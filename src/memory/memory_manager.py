"""
Memory Manager - 统一的记忆管理器

整合短期和长期记忆
"""

from typing import List, Dict, Any, Optional
from .base_memory import MemoryEntry
from .short_term_memory import ShortTermMemory
from .long_term_memory import LongTermMemory


class MemoryManager:
    """记忆管理器 - 整合短期和长期记忆"""

    def __init__(self, persist_dir: str = "./data/chroma"):
        self.short_term = ShortTermMemory(max_size=100)
        self.long_term = LongTermMemory(persist_dir=persist_dir)

    async def add(self, content: str, metadata: Dict[str, Any], save_to_long_term: bool = False):
        """
        添加记忆

        Args:
            content: 记忆内容
            metadata: 元数据
            save_to_long_term: 是否同时保存到长期记忆
        """
        # 添加到短期记忆
        await self.short_term.add(content, metadata)

        # 如果需要，保存到长期记忆
        if save_to_long_term:
            await self.long_term.add(content, metadata)

    async def search(self, query: str, use_long_term: bool = True, top_k: int = 5) -> List[MemoryEntry]:
        """
        搜索记忆

        Args:
            query: 查询内容
            use_long_term: 是否搜索长期记忆
            top_k: 返回结果数量

        Returns:
            相关记忆列表
        """
        results = []

        # 搜索短期记忆
        short_term_results = await self.short_term.search(query, top_k)
        results.extend(short_term_results)

        # 搜索长期记忆
        if use_long_term:
            long_term_results = await self.long_term.search(query, top_k)
            results.extend(long_term_results)

        # 去重并按时间排序
        unique_results = {m.id: m for m in results}
        sorted_results = sorted(
            unique_results.values(),
            key=lambda m: m.timestamp,
            reverse=True
        )

        return sorted_results[:top_k]

    async def consolidate(self):
        """
        整合记忆

        将重要的短期记忆转移到长期记忆
        """
        # 获取短期记忆
        recent_memories = self.short_term.get_recent(n=50)

        # 筛选重要记忆（可以基于元数据中的重要性标记）
        important_memories = [
            m for m in recent_memories
            if m.metadata.get("importance", 0) > 0.7
        ]

        # 保存到长期记忆
        for memory in important_memories:
            await self.long_term.add(memory.content, memory.metadata)

    async def get_context(self, query: str, max_tokens: int = 2000) -> str:
        """
        获取相关上下文

        Args:
            query: 查询内容
            max_tokens: 最大 token 数（粗略估计）

        Returns:
            格式化的上下文字符串
        """
        memories = await self.search(query, use_long_term=True, top_k=10)

        context_parts = []
        current_length = 0

        for memory in memories:
            # 粗略估计 token 数（1 token ≈ 4 字符）
            estimated_tokens = len(memory.content) // 4

            if current_length + estimated_tokens > max_tokens:
                break

            context_parts.append(f"[{memory.metadata.get('type', 'unknown')}] {memory.content}")
            current_length += estimated_tokens

        return "\n\n".join(context_parts)

    def get_stats(self) -> Dict[str, Any]:
        """获取记忆统计信息"""
        return {
            "short_term": {
                "count": len(self.short_term.memories),
                "max_size": self.short_term.max_size
            },
            "long_term": self.long_term.get_stats()
        }
