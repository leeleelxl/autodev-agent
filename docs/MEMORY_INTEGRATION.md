# Memory 系统与工作流集成

## 概述

Memory 系统已完全集成到 Agent 工作流中，实现：
- 自动记忆存储和检索
- 经验学习和最佳实践应用
- 上下文增强的决策

## 集成架构

```
Orchestrator
    ├── MemoryManager (短期 + 长期记忆)
    ├── ExperienceMemory (经验学习)
    │
    └── 工作流各阶段
        ├── 开始前: 检索相关经验
        ├── 执行中: 各 Agent 使用记忆增强决策
        └── 完成后: 记录成功/失败经验
```

## 记忆使用流程

### 1. 工作流开始前

```python
# Orchestrator 自动检索相关经验
relevant_memories = await memory_manager.search(
    initial_task,
    use_long_term=True,
    top_k=5
)

# 加载最佳实践
best_practices = await experience_memory.get_best_practices(
    "software_development",
    top_k=3
)

# 添加到上下文
context["memory_context"] = memory_context
context["best_practices"] = best_practices
```

### 2. Architect Agent - 使用历史设计经验

```python
# 自动检索相关架构设计
memory_context = await memory_manager.get_context(
    query=f"架构设计 {task}",
    max_tokens=1000
)

# 在提示词中包含历史经验
prompt = f"""
需求描述：{task}

相关历史经验：
{memory_context}

最佳实践：
- {practice1}
- {practice2}

请分析需求并给出架构设计方案。
"""

# 保存设计到长期记忆
await memory_manager.add(
    content=f"架构设计: {task}\n方案: {response}",
    metadata={"type": "architecture", "importance": 0.9},
    save_to_long_term=True
)
```

### 3. Developer Agent - 代码实现记忆

```python
# 使用记忆中的代码模式
# (自动通过 Architect 传递的上下文)

# 保存代码到记忆
await memory_manager.add(
    content=f"任务: {task}\n代码: {code}",
    metadata={"type": "code", "quality_score": quality_score},
    save_to_long_term=True
)
```

### 4. 工作流完成后 - 经验记录

```python
# 成功案例
if score >= 0.7 and test_passed:
    await experience_memory.record_success(
        task=initial_task,
        solution=code,
        metadata={
            "score": score,
            "test_passed": True,
            "design": design
        }
    )

# 失败案例
else:
    await experience_memory.record_failure(
        task=initial_task,
        error=f"质量分数: {score}",
        attempted_solution=code,
        metadata={"issues": issues}
    )
```

## 记忆类型和用途

| 记忆类型 | 存储内容 | 使用场景 |
|---------|---------|---------|
| 架构设计 | 设计方案、技术选型 | Architect Agent 参考历史设计 |
| 代码实现 | 代码片段、实现模式 | Developer Agent 参考代码模式 |
| 测试策略 | 测试用例、覆盖策略 | Tester Agent 生成测试 |
| 审查经验 | 常见问题、改进建议 | Reviewer Agent 识别问题 |
| 成功案例 | 高质量解决方案 | 所有 Agent 学习最佳实践 |
| 失败案例 | 错误和教训 | 避免重复错误 |

## 记忆检索策略

### 向量相似度搜索

```python
# 基于任务描述检索
memories = await memory_manager.search(
    query="实现用户认证系统",
    use_long_term=True,
    top_k=5
)

# 返回最相关的 5 条记忆
for memory in memories:
    print(f"[{memory.metadata['type']}] {memory.content}")
```

### 最佳实践检索

```python
# 按领域检索最佳实践
best_practices = await experience_memory.get_best_practices(
    domain="testing",  # 或 "architecture", "security"
    top_k=5
)

# 只返回高分案例 (score > 0.8)
```

### 上下文生成

```python
# 生成格式化的上下文（控制 token 数量）
context = await memory_manager.get_context(
    query="数据库设计",
    max_tokens=2000
)

# 返回格式化的字符串，可直接用于提示词
```

## 记忆整合

定期将重要的短期记忆转移到长期记忆：

```python
# 自动整合（importance > 0.7）
await memory_manager.consolidate()

# 查看统计
stats = memory_manager.get_stats()
print(f"短期: {stats['short_term']['count']}")
print(f"长期: {stats['long_term']['total_memories']}")
```

## 完整示例

```python
import asyncio
from src.agents import Orchestrator, ArchitectAgent, DeveloperAgent, TesterAgent, ReviewerAgent
from src.memory import MemoryManager, ExperienceMemory
from src.tools import CodeExecutor, CodeAnalyzer, Linter
from src.llm import LLMFactory, LLMProvider

async def main():
    orchestrator = Orchestrator()

    # 注册 agents
    orchestrator.register_agent(ArchitectAgent())
    orchestrator.register_agent(DeveloperAgent())
    orchestrator.register_agent(TesterAgent())
    orchestrator.register_agent(ReviewerAgent())

    # 注册工具
    orchestrator.register_tools(
        code_executor=CodeExecutor(),
        code_analyzer=CodeAnalyzer(),
        linter=Linter()
    )

    # 设置记忆系统
    memory_manager = MemoryManager(persist_dir="./data/chroma")
    experience_memory = ExperienceMemory(persist_dir="./data/chroma")
    orchestrator.set_memory(memory_manager, experience_memory)

    # 设置 LLM
    llm = LLMFactory.create_client(LLMProvider.ANTHROPIC, api_key)
    for agent in orchestrator.agents.values():
        agent.set_llm_client(llm)

    # 执行工作流（自动使用记忆）
    result = await orchestrator.execute_workflow("创建 REST API")

    # 记忆会自动：
    # 1. 在开始前检索相关经验
    # 2. 在执行中增强决策
    # 3. 在完成后记录经验

asyncio.run(main())
```

## 记忆持久化

- **存储位置**: `./data/chroma/`
- **格式**: ChromaDB 向量数据库
- **持久化**: 自动保存到磁盘
- **跨会话**: 重启后自动加载

## 性能优化

1. **批量检索**: 一次检索多条相关记忆
2. **缓存**: 短期记忆作为缓存层
3. **异步**: 所有记忆操作都是异步的
4. **Token 控制**: 限制上下文长度避免超限

## 监控和调试

```python
# 查看记忆统计
stats = memory_manager.get_stats()
print(stats)

# 查看最近的记忆
recent = memory_manager.short_term.get_recent(n=10)
for mem in recent:
    print(f"{mem.timestamp}: {mem.content[:50]}...")

# 搜索特定类型的记忆
results = await memory_manager.search(
    "architecture",
    use_long_term=True,
    top_k=10
)
```

## 下一步优化

- [ ] 记忆重要性自动评估
- [ ] 记忆过期和清理机制
- [ ] 跨项目记忆共享
- [ ] 记忆可视化界面
