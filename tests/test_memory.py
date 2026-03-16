"""
测试 Memory 系统
"""

import pytest
from src.memory import ShortTermMemory, LongTermMemory, MemoryManager


@pytest.mark.asyncio
async def test_short_term_memory():
    """测试短期记忆"""
    memory = ShortTermMemory(max_size=5)

    # 添加记忆
    id1 = await memory.add("测试内容1", {"type": "test"})
    id2 = await memory.add("测试内容2", {"type": "test"})

    assert len(memory.memories) == 2

    # 获取记忆
    entry = await memory.get(id1)
    assert entry is not None
    assert entry.content == "测试内容1"

    # 测试容量限制
    for i in range(10):
        await memory.add(f"内容{i}", {"type": "test"})

    assert len(memory.memories) == 5  # 最多保留 5 条


@pytest.mark.asyncio
async def test_long_term_memory():
    """测试长期记忆"""
    memory = LongTermMemory(persist_dir="./test_data/chroma")

    # 清空测试数据
    await memory.clear()

    # 添加记忆
    id1 = await memory.add("Python 是一门编程语言", {"type": "knowledge", "topic": "programming"})
    id2 = await memory.add("FastAPI 是一个 Web 框架", {"type": "knowledge", "topic": "framework"})

    # 搜索记忆
    results = await memory.search("Web 框架", top_k=2)
    assert len(results) > 0
    assert "FastAPI" in results[0].content or "FastAPI" in results[1].content if len(results) > 1 else True

    # 获取统计
    stats = memory.get_stats()
    assert stats["total_memories"] >= 2

    # 清理
    await memory.clear()


@pytest.mark.asyncio
async def test_memory_manager():
    """测试记忆管理器"""
    manager = MemoryManager(persist_dir="./test_data/chroma")

    # 添加到短期记忆
    await manager.add("短期内容", {"type": "temp"}, save_to_long_term=False)

    # 添加到长期记忆
    await manager.add("重要内容", {"type": "important", "importance": 0.9}, save_to_long_term=True)

    # 搜索
    results = await manager.search("重要", use_long_term=True, top_k=5)
    assert len(results) > 0

    # 获取上下文
    context = await manager.get_context("重要内容", max_tokens=1000)
    assert "重要" in context

    # 统计
    stats = manager.get_stats()
    assert "short_term" in stats
    assert "long_term" in stats
