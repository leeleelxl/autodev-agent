# Memory 系统使用指南

## 概述

AutoDev 的 Memory 系统包含三层记忆架构：

1. **短期记忆（ShortTermMemory）** - 当前会话的临时记忆
2. **长期记忆（LongTermMemory）** - 持久化的向量数据库存储
3. **经验记忆（ExperienceMemory）** - 从成功和失败中学习

## 快速开始

### 1. 基础使用

```python
from src.memory import MemoryManager

# 创建记忆管理器
memory = MemoryManager(persist_dir="./data/chroma")

# 添加记忆
await memory.add(
    content="Python 使用 def 定义函数",
    metadata={"type": "knowledge", "topic": "python"},
    save_to_long_term=True  # 保存到长期记忆
)

# 搜索记忆
results = await memory.search("如何定义函数", top_k=5)
for result in results:
    print(result.content)

# 获取上下文
context = await memory.get_context("Python 函数", max_tokens=1000)
print(context)
```

### 2. 经验学习

```python
from src.memory import ExperienceMemory

experience = ExperienceMemory()

# 记录成功案例
await experience.record_success(
    task="实现快速排序",
    solution="使用递归分治算法...",
    metadata={"score": 0.95, "performance": "O(n log n)"}
)

# 记录失败案例
await experience.record_failure(
    task="实现快速排序",
    error="栈溢出",
    attempted_solution="递归深度过大",
    metadata={"issue": "未处理边界情况"}
)

# 获取相似经验
similar = await experience.get_similar_experiences("排序算法", top_k=3)
for exp in similar:
    print(f"{exp['type']}: {exp['content']}")

# 获取最佳实践
best_practices = await experience.get_best_practices("testing", top_k=5)
```

### 3. 在 Agent 中使用

```python
from src.agents import ArchitectAgent
from src.memory import MemoryManager

# 创建 agent 和记忆管理器
agent = ArchitectAgent()
memory = MemoryManager()

# 在处理任务前，获取相关经验
context = await memory.get_context(task, max_tokens=2000)

# 将上下文传递给 agent
response = await agent.process(task, context={"memory": context})

# 保存结果到记忆
await memory.add(
    content=response.content,
    metadata={"task": task, "phase": "architecture"},
    save_to_long_term=True
)
```

## 记忆整合

定期整合记忆，将重要的短期记忆转移到长期记忆：

```python
# 整合记忆（将重要性 > 0.7 的短期记忆保存到长期）
await memory.consolidate()

# 查看统计
stats = memory.get_stats()
print(f"短期记忆: {stats['short_term']['count']} 条")
print(f"长期记忆: {stats['long_term']['total_memories']} 条")
```

## 配置

在 `.env` 中配置：

```env
CHROMA_PERSIST_DIR=./data/chroma
```

## 技术细节

- **向量数据库**: ChromaDB（自动生成 embeddings）
- **搜索算法**: 余弦相似度
- **持久化**: 本地文件系统
- **去重**: 基于记忆 ID

## 最佳实践

1. **重要记忆标记**: 设置 `importance` 字段（0-1）
2. **定期整合**: 每完成一个任务后调用 `consolidate()`
3. **上下文控制**: 使用 `max_tokens` 限制上下文长度
4. **元数据丰富**: 添加详细的 metadata 便于检索
