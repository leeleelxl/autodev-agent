"""
测试完整工作流
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from src.agents import Orchestrator, ArchitectAgent, DeveloperAgent, TesterAgent, ReviewerAgent


@pytest.mark.asyncio
async def test_orchestrator_workflow():
    """测试完整的工作流"""
    orchestrator = Orchestrator()

    # 创建 mock agents
    architect = ArchitectAgent()
    developer = DeveloperAgent()
    tester = TesterAgent()
    reviewer = ReviewerAgent()

    # Mock LLM 客户端
    mock_client = MagicMock()
    mock_client.chat = AsyncMock(return_value=MagicMock(
        content='{"requirements": {}, "tech_stack": {}, "architecture": {}, "modules": [], "reasoning": "test"}',
        model="test",
        usage={}
    ))

    architect.set_llm_client(mock_client)
    developer.set_llm_client(mock_client)
    tester.set_llm_client(mock_client)
    reviewer.set_llm_client(mock_client)

    # 注册 agents
    orchestrator.register_agent(architect)
    orchestrator.register_agent(developer)
    orchestrator.register_agent(tester)
    orchestrator.register_agent(reviewer)

    # 执行工作流
    result = await orchestrator.execute_workflow("创建一个简单的计算器")

    assert result["success"] is True
    assert len(result["phases"]) >= 4  # 至少 4 个阶段
    assert "design" in result["final_output"]
