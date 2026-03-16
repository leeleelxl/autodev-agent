"""
AutoDev 主入口
"""

import asyncio
from src.agents import (
    Orchestrator,
    ArchitectAgent,
    DeveloperAgent,
    TesterAgent,
    ReviewerAgent
)


async def main():
    """主函数"""
    # 初始化 orchestrator
    orchestrator = Orchestrator()

    # 注册所有 agents
    orchestrator.register_agent(ArchitectAgent())
    orchestrator.register_agent(DeveloperAgent())
    orchestrator.register_agent(TesterAgent())
    orchestrator.register_agent(ReviewerAgent())

    print("AutoDev Agent System 已启动")
    print("注册的 Agents:", list(orchestrator.agents.keys()))

    # TODO: 实现交互式命令行或 API 接口


if __name__ == "__main__":
    asyncio.run(main())
