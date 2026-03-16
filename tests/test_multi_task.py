"""
多任务 Baseline 对比实验

测试 5 个不同复杂度的任务
"""

import asyncio
import time
from pathlib import Path
import sys
import json

sys.path.insert(0, str(Path(__file__).parent))

from src.agents import Orchestrator, ArchitectAgent, DeveloperAgent, TesterAgent, ReviewerAgent
from src.llm import LLMFactory, LLMProvider, LLMMessage
from src.tools import CodeExecutor, CodeAnalyzer, Linter
from src.memory import MemoryManager, ExperienceMemory
from dotenv import load_dotenv
import os

load_dotenv()


# 定义测试任务
TASKS = [
    {
        "id": 1,
        "name": "简单任务：计算器",
        "description": "创建一个命令行计算器，支持加减乘除",
        "complexity": "简单"
    },
    {
        "id": 2,
        "name": "中等任务：TODO 列表",
        "description": "创建一个 TODO 列表应用，支持添加、删除、标记完成，使用 JSON 文件存储",
        "complexity": "中等"
    },
    {
        "id": 3,
        "name": "中等任务：用户认证",
        "description": "创建用户认证系统：用户注册（密码哈希）、登录（JWT token）、Token 验证、SQLite 数据库、错误处理",
        "complexity": "中等"
    },
    {
        "id": 4,
        "name": "复杂任务：REST API",
        "description": "创建一个图书管理 REST API：CRUD 操作、分页、搜索、输入验证、错误处理、SQLite 数据库",
        "complexity": "复杂"
    },
    {
        "id": 5,
        "name": "复杂任务：网络爬虫",
        "description": "创建一个网络爬虫：爬取新闻网站标题和链接、支持多页爬取、错误重试、保存到 CSV、遵守 robots.txt",
        "complexity": "复杂"
    }
]


async def run_single_llm(task_desc: str):
    """Baseline: Single LLM"""
    api_key = os.getenv("MOONSHOT_API_KEY")
    llm = LLMFactory.create_client(LLMProvider.MOONSHOT, api_key)

    prompt = f"""请实现以下任务：

{task_desc}

要求：
1. 直接输出完整的 Python 代码
2. 包含所有必要的功能
3. 添加错误处理

请使用 Markdown 代码块输出，格式：
```python
# filename: xxx.py
代码内容
```
"""

    start_time = time.time()

    response = await llm.chat(
        messages=[LLMMessage(role="user", content=prompt)],
        temperature=0.7,
        max_tokens=4096
    )

    execution_time = time.time() - start_time

    # 提取代码块
    import re
    pattern = r'```python\s*\n(.*?)\n```'
    code_blocks = re.findall(pattern, response.content, re.DOTALL)

    files = []
    for code_block in code_blocks:
        # 提取文件名
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

    total_lines = sum(len(f["content"].split('\n')) for f in files)
    has_tests = any('test' in f["path"].lower() or 'assert' in f["content"].lower() for f in files)

    return {
        "files": files,
        "execution_time": execution_time,
        "total_lines": total_lines,
        "has_tests": has_tests,
        "tokens": response.usage.get("input_tokens", 0) + response.usage.get("output_tokens", 0)
    }


async def run_autodev(task_desc: str):
    """AutoDev: 多 Agent 协作"""
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

    total_lines = sum(len(f.get("content", "").split('\n')) for f in code_files)
    has_tests = len(test_files) > 0

    return {
        "files": code_files,
        "test_files": test_files,
        "execution_time": execution_time,
        "total_lines": total_lines,
        "has_tests": has_tests,
        "quality_score": review.get("score", 0),
        "issues": review.get("issues", []),
        "phases": len(result.get("phases", []))
    }


async def run_comparison():
    """运行完整对比实验"""
    results = []

    for task in TASKS:
        print("\n" + "=" * 80)
        print(f"任务 {task['id']}: {task['name']}")
        print(f"复杂度: {task['complexity']}")
        print("=" * 80)

        # Single LLM
        print("\n[1/2] Single LLM...")
        try:
            single_result = await run_single_llm(task["description"])
            print(f"  ✓ 完成: {len(single_result['files'])} 个文件, {single_result['total_lines']} 行, {single_result['execution_time']:.1f}s")
        except Exception as e:
            print(f"  ✗ 失败: {e}")
            single_result = {"error": str(e)}

        # AutoDev
        print("\n[2/2] AutoDev...")
        try:
            autodev_result = await run_autodev(task["description"])
            print(f"  ✓ 完成: {len(autodev_result['files'])} 个文件, {autodev_result['total_lines']} 行, {autodev_result['execution_time']:.1f}s")
        except Exception as e:
            print(f"  ✗ 失败: {e}")
            autodev_result = {"error": str(e)}

        results.append({
            "task": task,
            "single_llm": single_result,
            "autodev": autodev_result
        })

    # 保存结果
    with open("multi_task_results.json", "w") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    # 打印汇总
    print("\n" + "=" * 80)
    print("汇总结果")
    print("=" * 80)

    print("\n| 任务 | Single LLM | AutoDev | 对比 |")
    print("|------|-----------|---------|------|")

    for r in results:
        task_name = r["task"]["name"]

        if "error" not in r["single_llm"]:
            single_info = f"{len(r['single_llm']['files'])}文件/{r['single_llm']['total_lines']}行/{r['single_llm']['execution_time']:.0f}s"
        else:
            single_info = "失败"

        if "error" not in r["autodev"]:
            autodev_info = f"{len(r['autodev']['files'])}文件/{r['autodev']['total_lines']}行/{r['autodev']['execution_time']:.0f}s"
            quality = f"质量{r['autodev']['quality_score']}"
        else:
            autodev_info = "失败"
            quality = "-"

        print(f"| {task_name} | {single_info} | {autodev_info} | {quality} |")

    print("\n结果已保存到: multi_task_results.json")


if __name__ == "__main__":
    asyncio.run(run_comparison())
