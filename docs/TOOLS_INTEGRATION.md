# Tools 集成到 Agent 工作流

## 概述

Tools 已完全集成到 Agent 工作流中，实现自动化的代码分析、质量检查和测试执行。

## 集成架构

```
Orchestrator
    ├── register_tools()  # 注册工具
    │   ├── CodeExecutor
    │   ├── CodeAnalyzer
    │   └── Linter
    │
    └── Agents
        ├── DeveloperAgent
        │   ├── 生成代码
        │   ├── CodeAnalyzer 分析代码结构
        │   └── Linter 检查代码质量
        │
        ├── TesterAgent
        │   ├── 生成测试用例
        │   └── CodeExecutor 执行测试
        │
        └── ReviewerAgent
            ├── CodeAnalyzer 自动分析
            ├── Linter 质量检查
            └── LLM 综合审查
```

## 工作流程

### 1. 初始化阶段

```python
from src.agents import Orchestrator
from src.tools import CodeExecutor, CodeAnalyzer, Linter

orchestrator = Orchestrator()

# 注册工具
orchestrator.register_tools(
    code_executor=CodeExecutor(use_docker=False),
    code_analyzer=CodeAnalyzer(),
    linter=Linter()
)
```

### 2. Developer Agent - 代码生成 + 自动分析

生成代码后自动进行：
- **代码结构分析**：提取函数、类、复杂度
- **质量检查**：Pylint 评分和问题检测

```python
# Developer Agent 自动调用
response = await developer.process(task, context)

# 返回结果包含
{
    "files": [...],  # 生成的代码
    "analysis": [...],  # 代码分析结果
    "quality": [...]  # 质量检查结果
}
```

### 3. Tester Agent - 测试生成 + 自动执行

生成测试用例后自动执行：
- **测试执行**：在沙箱中运行测试
- **结果收集**：成功/失败、输出、错误信息

```python
# Tester Agent 自动调用
response = await tester.process(task, context)

# 返回结果包含
{
    "test_cases": [...],  # 生成的测试
    "test_results": [  # 执行结果
        {
            "test_file": "test_xxx.py",
            "success": True,
            "output": "All tests passed!",
            "error": ""
        }
    ]
}
```

### 4. Reviewer Agent - 综合审查

结合工具分析和 LLM 判断：
- **自动分析**：代码结构 + 质量检查
- **LLM 审查**：基于工具结果进行深度分析
- **综合评分**：0-100 分

```python
# Reviewer Agent 自动调用
response = await reviewer.process(task, context)

# 返回结果包含
{
    "score": 85,
    "issues": [...],
    "tool_analysis": {  # 工具分析结果
        "analysis": [...],
        "quality": [...]
    }
}
```

## 完整示例

```python
import asyncio
from src.agents import Orchestrator, ArchitectAgent, DeveloperAgent, TesterAgent, ReviewerAgent
from src.tools import CodeExecutor, CodeAnalyzer, Linter
from src.llm import LLMFactory, LLMProvider

async def main():
    # 创建 orchestrator
    orchestrator = Orchestrator()

    # 注册 agents
    orchestrator.register_agent(ArchitectAgent())
    orchestrator.register_agent(DeveloperAgent())
    orchestrator.register_agent(TesterAgent())
    orchestrator.register_agent(ReviewerAgent())

    # 注册工具
    orchestrator.register_tools(
        code_executor=CodeExecutor(use_docker=False),
        code_analyzer=CodeAnalyzer(),
        linter=Linter()
    )

    # 设置 LLM
    llm_client = LLMFactory.create_client(
        provider=LLMProvider.ANTHROPIC,
        api_key="your_key"
    )

    for agent in orchestrator.agents.values():
        agent.set_llm_client(llm_client)

    # 执行工作流
    result = await orchestrator.execute_workflow("创建一个计算器应用")

    # 查看结果
    print(f"成功: {result['success']}")
    print(f"代码质量: {result['final_output']['review']['score']}/100")

asyncio.run(main())
```

## 工具使用统计

每个阶段的工具调用：

| 阶段 | Agent | 使用的工具 |
|------|-------|-----------|
| 架构设计 | Architect | - |
| 代码实现 | Developer | CodeAnalyzer, Linter |
| 测试生成 | Tester | CodeExecutor |
| 代码审查 | Reviewer | CodeAnalyzer, Linter |
| 迭代改进 | Developer | CodeAnalyzer, Linter |

## 性能优化

1. **并行执行**：分析和质量检查可并行
2. **缓存结果**：避免重复分析
3. **选择性执行**：根据代码变化决定是否重新分析

## 配置选项

```python
# Docker 模式（生产环境）
code_executor = CodeExecutor(use_docker=True)

# 本地模式（开发测试）
code_executor = CodeExecutor(use_docker=False)

# 自定义超时
result = await code_executor.execute(code, timeout=60)
```

## 下一步

- [ ] 添加更多工具（Git 操作、依赖分析）
- [ ] 实现工具结果缓存
- [ ] 支持自定义工具插件
- [ ] 添加工具使用统计和监控
