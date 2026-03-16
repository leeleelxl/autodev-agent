"""
测试 Base Agent
"""

import pytest
from src.agents.base_agent import BaseAgent, AgentConfig, AgentResponse


class MockAgent(BaseAgent):
    """测试用的 Mock Agent"""

    async def process(self, task: str, context=None) -> AgentResponse:
        return AgentResponse(
            content=f"处理任务: {task}",
            actions=[],
            metadata={}
        )


@pytest.mark.asyncio
async def test_agent_creation():
    """测试 agent 创建"""
    config = AgentConfig(name="test", role="测试角色")
    agent = MockAgent(config)

    assert agent.config.name == "test"
    assert agent.config.role == "测试角色"


@pytest.mark.asyncio
async def test_agent_process():
    """测试 agent 处理任务"""
    config = AgentConfig(name="test", role="测试角色")
    agent = MockAgent(config)

    response = await agent.process("测试任务")

    assert response.content == "处理任务: 测试任务"
    assert isinstance(response.actions, list)
