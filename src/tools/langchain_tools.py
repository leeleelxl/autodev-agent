"""
LangChain Tools 定义

将 AutoDev 的原生工具（CodeExecutor, CodeAnalyzer, Linter）
包装为 LangChain Tool，支持 Function Calling / Tool Calling。

LLM 可以自主决定何时调用哪个工具（而非硬编码调用）。
"""

import asyncio
import concurrent.futures
from typing import Optional
from langchain_core.tools import tool


def _run_async(coro):
    """在新线程中运行 async 协程，避免嵌套事件循环问题"""
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
        future = pool.submit(asyncio.run, coro)
        return future.result()


@tool
def execute_code(code: str, language: str = "python", timeout: int = 30) -> str:
    """在隔离环境中执行代码并返回输出结果。用于验证代码是否能正确运行。

    Args:
        code: 要执行的代码
        language: 编程语言，默认 python
        timeout: 超时时间（秒）
    """
    from src.tools.code_executor import CodeExecutor

    executor = CodeExecutor(use_docker=False)
    result = _run_async(executor.execute(code, language=language, timeout=timeout))

    if result.success:
        return f"执行成功:\n{result.output}"
    else:
        return f"执行失败:\n{result.error}"


@tool
def analyze_code(code: str) -> str:
    """分析 Python 代码结构（AST 解析），返回函数、类、复杂度、潜在问题等信息。

    Args:
        code: 要分析的 Python 代码
    """
    from src.tools.code_analyzer import CodeAnalyzer

    analyzer = CodeAnalyzer()
    result = _run_async(analyzer.execute(code))

    if result.success:
        output = result.output
        summary = output.get("summary", "")
        functions = [f["name"] for f in output.get("functions", [])]
        classes = [c["name"] for c in output.get("classes", [])]
        issues = output.get("issues", [])

        report = f"分析摘要: {summary}\n"
        report += f"函数: {', '.join(functions) if functions else '无'}\n"
        report += f"类: {', '.join(classes) if classes else '无'}\n"
        if issues:
            report += "问题:\n"
            for issue in issues:
                report += f"  - [{issue['severity']}] {issue['message']}\n"
        return report
    else:
        return f"分析失败: {result.error}"


@tool
def lint_code(code: str) -> str:
    """使用 pylint 检查代码质量，返回质量分数和问题列表。

    Args:
        code: 要检查的 Python 代码
    """
    from src.tools.linter import Linter

    linter = Linter()
    result = _run_async(linter.execute(code))

    if result.success:
        output = result.output
        return output.get("summary", "检查完成，无详细信息")
    else:
        return f"检查失败: {result.error}"


@tool
def search_experience(query: str) -> str:
    """从经验记忆库中检索相似的历史任务经验（成功/失败案例），用于辅助决策。

    Args:
        query: 搜索查询（任务描述或关键词）
    """
    from src.memory.experience_memory import ExperienceMemory

    exp_memory = ExperienceMemory(persist_dir="./data/chroma")
    experiences = _run_async(exp_memory.get_similar_experiences(query, top_k=3))

    if not experiences:
        return "未找到相关历史经验。"

    report = "相关历史经验:\n"
    for i, exp in enumerate(experiences, 1):
        exp_type = exp.get("type", "unknown")
        content = exp.get("content", "")[:200]
        report += f"\n{i}. [{exp_type}] {content}\n"

    return report


# 所有可用工具列表
ALL_TOOLS = [execute_code, analyze_code, lint_code, search_experience]

# 按角色分组的工具
ARCHITECT_TOOLS = [search_experience]
DEVELOPER_TOOLS = [execute_code, analyze_code, lint_code]
TESTER_TOOLS = [execute_code, analyze_code]
REVIEWER_TOOLS = [analyze_code, lint_code, search_experience]
