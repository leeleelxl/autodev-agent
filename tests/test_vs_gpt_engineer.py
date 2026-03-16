"""
AutoDev vs GPT Engineer 对比实验

对比维度：
1. 架构设计
2. 工作流程
3. 代码质量
4. 用户体验
5. 实际效果
"""

import asyncio
import time
from pathlib import Path
import sys
import json

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agents import Orchestrator, ArchitectAgent, DeveloperAgent, TesterAgent, ReviewerAgent
from src.llm import LLMFactory, LLMProvider, LLMMessage
from src.tools import CodeExecutor, CodeAnalyzer, Linter
from src.memory import MemoryManager, ExperienceMemory
from dotenv import load_dotenv
import os

load_dotenv()


# 测试任务
TEST_TASK = """
创建一个简单的博客系统：
- 文章的 CRUD 操作（创建、读取、更新、删除）
- 使用 SQLite 数据库
- RESTful API 接口
- 输入验证和错误处理
- 包含基本的测试
"""


async def run_autodev(task_desc: str):
    """AutoDev: 多 Agent 协作"""
    print("\n" + "=" * 80)
    print("AutoDev: 多 Agent 协作系统")
    print("=" * 80)

    orchestrator = Orchestrator()

    for agent_cls in [ArchitectAgent, DeveloperAgent, TesterAgent, ReviewerAgent]:
        orchestrator.register_agent(agent_cls())

    orchestrator.register_tools(
        code_executor=CodeExecutor(use_docker=False),
        code_analyzer=CodeAnalyzer(),
        linter=Linter()
    )

    memory = MemoryManager(persist_dir="./data/chroma")
    experience = ExperienceMemory(persist_dir="./data/chroma")
    orchestrator.set_memory(memory, experience)

    api_key = os.getenv("MOONSHOT_API_KEY")
    llm = LLMFactory.create_client(LLMProvider.MOONSHOT, api_key)

    for agent in orchestrator.agents.values():
        agent.set_llm_client(llm)

    start_time = time.time()
    result = await orchestrator.execute_workflow(task_desc)
    execution_time = time.time() - start_time

    code_files = result.get("final_output", {}).get("code_files", [])
    test_files = result.get("final_output", {}).get("test_files", [])
    review = result.get("final_output", {}).get("review", {})

    # 保存代码
    output_dir = Path("experiments/results/autodev_blog")
    output_dir.mkdir(parents=True, exist_ok=True)

    for file in code_files:
        file_path = output_dir / file.get("path", "")
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(file.get("content", ""))

    return {
        "system": "AutoDev",
        "files": len(code_files),
        "total_lines": sum(len(f.get("content", "").split('\n')) for f in code_files),
        "has_tests": len(test_files) > 0,
        "quality_score": review.get("score", 0),
        "issues": len(review.get("issues", [])),
        "execution_time": execution_time,
        "phases": len(result.get("phases", [])),
        "architecture": "Multi-Agent (5 agents)",
        "workflow": "Architect → Developer → Tester → Reviewer → Improvement"
    }


async def simulate_gpt_engineer(task_desc: str):
    """
    模拟 GPT Engineer 的工作方式

    GPT Engineer 特点：
    1. 单 Agent 多轮对话
    2. 需要用户确认
    3. 迭代式开发
    """
    print("\n" + "=" * 80)
    print("GPT Engineer: 单 Agent 迭代式开发")
    print("=" * 80)

    api_key = os.getenv("MOONSHOT_API_KEY")
    llm = LLMFactory.create_client(LLMProvider.MOONSHOT, api_key)

    start_time = time.time()

    # Round 1: 理解需求
    print("\n[Round 1] 理解需求...")
    clarify_prompt = f"""作为 GPT Engineer，请分析以下需求并提出澄清问题：

{task_desc}

请列出你需要澄清的问题（3-5 个）。"""

    clarify_response = await llm.chat(
        messages=[LLMMessage(role="user", content=clarify_prompt)],
        temperature=0.7,
        max_tokens=1024
    )

    print(f"  提出了澄清问题")

    # Round 2: 生成代码（假设用户回答了问题）
    print("\n[Round 2] 生成代码...")
    code_prompt = f"""基于以下需求生成完整的代码：

{task_desc}

假设用户已经回答了所有澄清问题，请直接生成代码。

使用 Markdown 代码块格式：
```python
# filename: xxx.py
代码内容
```
"""

    code_response = await llm.chat(
        messages=[LLMMessage(role="user", content=code_prompt)],
        temperature=0.7,
        max_tokens=4096
    )

    # 提取代码
    import re
    pattern = r'```python\s*\n(.*?)\n```'
    code_blocks = re.findall(pattern, code_response.content, re.DOTALL)

    files = []
    for code_block in code_blocks:
        filename = None
        for line in code_block.split('\n'):
            if line.strip().startswith('# filename:'):
                filename = line.split(':', 1)[1].strip()
                break

        if not filename:
            filename = f"file_{len(files) + 1}.py"

        files.append({
            "path": filename,
            "content": code_block
        })

    execution_time = time.time() - start_time

    # 保存代码
    output_dir = Path("experiments/results/gpt_engineer_blog")
    output_dir.mkdir(parents=True, exist_ok=True)

    for file in files:
        file_path = output_dir / file.get("path", "")
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(file.get("content", ""))

    total_lines = sum(len(f["content"].split('\n')) for f in files)
    has_tests = any('test' in f["path"].lower() for f in files)

    return {
        "system": "GPT Engineer",
        "files": len(files),
        "total_lines": total_lines,
        "has_tests": has_tests,
        "quality_score": None,  # GPT Engineer 没有自动评分
        "issues": 0,  # GPT Engineer 没有自动问题识别
        "execution_time": execution_time,
        "phases": 2,  # 理解需求 + 生成代码
        "architecture": "Single Agent",
        "workflow": "Clarify → Generate → (User Review) → Iterate"
    }


async def compare():
    """运行对比实验"""
    print("\n" + "=" * 80)
    print("AutoDev vs GPT Engineer 对比实验")
    print("=" * 80)
    print(f"\n任务: {TEST_TASK.strip()}")

    # 运行 AutoDev
    autodev_result = await run_autodev(TEST_TASK)

    # 模拟 GPT Engineer
    gpt_engineer_result = await simulate_gpt_engineer(TEST_TASK)

    # 对比结果
    print("\n" + "=" * 80)
    print("对比结果")
    print("=" * 80)

    comparison = {
        "task": TEST_TASK.strip(),
        "autodev": autodev_result,
        "gpt_engineer": gpt_engineer_result
    }

    # 保存结果
    with open("experiments/results/autodev_vs_gpt_engineer.json", "w") as f:
        json.dump(comparison, f, indent=2, ensure_ascii=False)

    # 打印对比表格
    print("\n### 架构对比")
    print(f"| 维度 | GPT Engineer | AutoDev |")
    print(f"|------|-------------|---------|")
    print(f"| 架构 | {gpt_engineer_result['architecture']} | {autodev_result['architecture']} |")
    print(f"| 工作流 | {gpt_engineer_result['workflow']} | {autodev_result['workflow']} |")
    print(f"| 阶段数 | {gpt_engineer_result['phases']} | {autodev_result['phases']} |")

    print("\n### 代码质量对比")
    print(f"| 指标 | GPT Engineer | AutoDev | 优势 |")
    print(f"| 文件数 | {gpt_engineer_result['files']} | {autodev_result['files']} | {'AutoDev' if autodev_result['files'] > gpt_engineer_result['files'] else 'GPT Engineer'} |")
    print(f"| 代码行数 | {gpt_engineer_result['total_lines']} | {autodev_result['total_lines']} | - |")
    print(f"| 测试 | {'✓' if gpt_engineer_result['has_tests'] else '✗'} | {'✓' if autodev_result['has_tests'] else '✗'} | {'AutoDev' if autodev_result['has_tests'] and not gpt_engineer_result['has_tests'] else '-'} |")
    print(f"| 质量评分 | {gpt_engineer_result['quality_score'] or '无'} | {autodev_result['quality_score']}/100 | AutoDev |")
    print(f"| 问题识别 | {gpt_engineer_result['issues']} | {autodev_result['issues']} | AutoDev |")

    print("\n### 用户体验对比")
    print(f"| 维度 | GPT Engineer | AutoDev |")
    print(f"|------|-------------|---------|")
    print(f"| 执行时间 | {gpt_engineer_result['execution_time']:.1f}s | {autodev_result['execution_time']:.1f}s |")
    print(f"| 需要人工介入 | ✓ (确认问题) | ✗ (全自动) |")
    print(f"| 学习曲线 | 低 | 中 |")

    print("\n结果已保存到: experiments/results/autodev_vs_gpt_engineer.json")


if __name__ == "__main__":
    asyncio.run(compare())
