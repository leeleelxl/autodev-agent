"""
AutoDev 主入口
"""

import asyncio
import os
from dotenv import load_dotenv

from src.agents import (
    Orchestrator,
    ArchitectAgent,
    DeveloperAgent,
    TesterAgent,
    ReviewerAgent
)
from src.llm import LLMFactory, LLMProvider
from src.tools import CodeExecutor, CodeAnalyzer, Linter
from src.utils import Config

# 加载环境变量
load_dotenv()


async def main():
    """主函数"""
    print("=" * 60)
    print("AutoDev - 自主软件开发 Agent 系统")
    print("=" * 60)

    # 初始化 orchestrator
    orchestrator = Orchestrator()

    # 创建 agents
    architect = ArchitectAgent()
    developer = DeveloperAgent()
    tester = TesterAgent()
    reviewer = ReviewerAgent()

    # 设置 LLM 客户端（可以为不同 agent 配置不同的 LLM）
    # 这里演示使用 Claude
    if Config.ANTHROPIC_API_KEY:
        claude_client = LLMFactory.create_client(
            provider=LLMProvider.ANTHROPIC,
            api_key=Config.ANTHROPIC_API_KEY
        )
        architect.set_llm_client(claude_client)
        developer.set_llm_client(claude_client)
        tester.set_llm_client(claude_client)
        reviewer.set_llm_client(claude_client)
        print("✓ 使用 Claude API")
    else:
        print("⚠ 未配置 API Key，请设置 .env 文件")
        return

    # 注册所有 agents
    orchestrator.register_agent(architect)
    orchestrator.register_agent(developer)
    orchestrator.register_agent(tester)
    orchestrator.register_agent(reviewer)

    print(f"✓ 注册的 Agents: {list(orchestrator.agents.keys())}")

    # 创建并注册工具
    code_executor = CodeExecutor(use_docker=False)  # 开发模式使用本地执行
    code_analyzer = CodeAnalyzer()
    linter = Linter()

    orchestrator.register_tools(
        code_executor=code_executor,
        code_analyzer=code_analyzer,
        linter=linter
    )

    print(f"✓ 注册的 Tools: {list(orchestrator.tools.keys())}")
    print()

    # 示例任务
    task = """
    创建一个简单的 TODO 应用：
    - 支持添加、删除、标记完成任务
    - 使用 Python 实现
    - 包含命令行界面
    """

    print("开始执行工作流...")
    print(f"任务: {task.strip()}")
    print()

    # 执行工作流
    result = await orchestrator.execute_workflow(task)

    print()
    print("=" * 60)
    print("工作流执行完成")
    print("=" * 60)
    print(f"状态: {'成功' if result['success'] else '失败'}")
    print(f"阶段数: {len(result['phases'])}")

    # 显示各阶段摘要
    for phase in result['phases']:
        print(f"\n[{phase['name']}]")
        if phase['name'] == 'review':
            # 显示审查结果
            review_data = result['final_output'].get('review', {})
            if review_data:
                print(f"  代码质量分数: {review_data.get('score', 0)}/100")
                print(f"  问题数量: {len(review_data.get('issues', []))}")

    if result.get("error"):
        print(f"\n错误: {result['error']}")


if __name__ == "__main__":
    asyncio.run(main())
