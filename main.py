"""
AutoDev 主入口

技术栈：
- LangChain: LLM 抽象层 + Tool Calling / Function Calling
- LangGraph: StateGraph 状态机驱动工作流
- ReAct: Thought → Action → Observation 循环
- Chain-of-Thought: 结构化推理
"""

import asyncio
import os
from dotenv import load_dotenv

from src.agents import (
    Orchestrator,
    ArchitectAgent,
    DeveloperAgent,
    TesterAgent,
    ReviewerAgent,
)
from src.llm import create_langchain_llm
from src.tools import ARCHITECT_TOOLS, DEVELOPER_TOOLS, TESTER_TOOLS, REVIEWER_TOOLS
from src.memory import MemoryManager, ExperienceMemory

# 加载环境变量
load_dotenv()


async def main():
    """主函数"""
    print("=" * 60)
    print("  AutoDev - 多 Agent 协作代码生成系统")
    print("  LangChain + LangGraph + ReAct + CoT")
    print("=" * 60)

    # 读取配置
    provider = os.getenv("DEFAULT_PROVIDER", "moonshot")
    api_key = os.getenv("MOONSHOT_API_KEY", "")
    model = os.getenv("DEFAULT_MODEL", "kimi-k2-turbo-preview")

    if not api_key:
        print("  ✗ 未配置 API Key，请设置 .env 文件")
        return

    # 创建 LangChain LLM（统一接口，支持 Tool Calling）
    llm = create_langchain_llm(
        provider=provider,
        api_key=api_key,
        model=model,
        temperature=0.7,
        timeout=120,
    )
    print(f"  ✓ LLM: {model} ({provider})")

    # 创建 Agents（ReAct 模式）
    architect = ArchitectAgent()
    developer = DeveloperAgent()
    tester = TesterAgent()
    reviewer = ReviewerAgent()

    # 为每个 Agent 设置 LLM 和专属工具（Function Calling）
    architect.set_llm(llm)
    architect.set_tools(ARCHITECT_TOOLS)

    developer.set_llm(llm)
    developer.set_tools(DEVELOPER_TOOLS)

    tester.set_llm(llm)
    tester.set_tools(TESTER_TOOLS)

    reviewer.set_llm(llm)
    reviewer.set_tools(REVIEWER_TOOLS)

    print(f"  ✓ Agents: architect, developer, tester, reviewer")
    print(f"  ✓ Tools: execute_code, analyze_code, lint_code, search_experience")

    # 创建 Orchestrator（LangGraph 状态机）
    orchestrator = Orchestrator()
    orchestrator.register_agent(architect)
    orchestrator.register_agent(developer)
    orchestrator.register_agent(tester)
    orchestrator.register_agent(reviewer)

    # 设置记忆系统
    memory_manager = MemoryManager(persist_dir="./data/chroma")
    experience_memory = ExperienceMemory(persist_dir="./data/chroma")
    orchestrator.set_memory(memory_manager, experience_memory)

    stats = memory_manager.get_stats()
    print(f"  ✓ Memory: 短期 {stats['short_term']['count']} 条, "
          f"长期 {stats['long_term']['total_memories']} 条")

    # 示例任务
    task = """
    创建一个简单的 TODO 应用：
    - 支持添加、删除、标记完成任务
    - 使用 Python 实现
    - 包含命令行界面
    """

    print(f"\n  任务: {task.strip()}")

    # 执行 LangGraph 工作流
    result = await orchestrator.execute_workflow(task)

    # 输出结果
    print("\n" + "=" * 60)
    print(f"  状态: {'成功' if result['success'] else '失败'}")
    print(f"  迭代次数: {result.get('iterations', 0)}")
    print(f"  最终分数: {result.get('final_score', 0)}/100")

    if result.get("phases"):
        print(f"  阶段数: {len(result['phases'])}")
        for phase in result["phases"]:
            tools = phase.get("tools_used", [])
            tools_str = f" (工具: {', '.join(t['tool'] for t in tools)})" if tools else ""
            print(f"    - {phase['name']}{tools_str}")

    if result.get("error"):
        print(f"  错误: {result['error']}")

    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
