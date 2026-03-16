"""
Tester Agent - 测试工程师

负责测试用例生成和代码测试
"""

from typing import Dict, Any, Optional, List
import json
from .base_agent import BaseAgent, AgentConfig, AgentResponse, Message


class TesterAgent(BaseAgent):
    """测试工程师 Agent"""

    def __init__(self):
        config = AgentConfig(
            name="tester",
            role="测试工程师，负责测试用例生成和代码测试"
        )
        super().__init__(config)

    async def process(self, task: str, context: Optional[Dict[str, Any]] = None) -> AgentResponse:
        """
        处理测试任务

        生成测试用例并执行测试
        """
        context = context or {}

        system_prompt = self._build_system_prompt()
        user_prompt = self._build_user_prompt(task, context)

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        response_content = await self._call_llm(messages)

        # 解析测试用例
        test_cases = self._parse_tests(response_content)

        self.add_message(Message(
            role="assistant",
            content=response_content,
            metadata={"task": task, "phase": "testing"}
        ))

        return AgentResponse(
            content=response_content,
            actions=[
                {"type": "tests_generated", "tests": test_cases}
            ],
            metadata={
                "phase": "testing",
                "test_cases": test_cases
            }
        )

    def _build_system_prompt(self) -> str:
        """构建系统提示词"""
        return """你是一位资深测试工程师，擅长编写全面的测试用例。

你的任务是：
1. 分析代码功能和边界条件
2. 设计测试用例（单元测试、集成测试）
3. 考虑正常情况和异常情况
4. 确保测试覆盖率
5. 编写清晰的测试代码

请以 JSON 格式输出测试文件，格式如下：
{
    "test_files": [
        {
            "path": "测试文件路径",
            "content": "测试代码",
            "description": "测试说明",
            "coverage": ["覆盖的功能点"]
        }
    ],
    "test_plan": {
        "unit_tests": ["单元测试列表"],
        "integration_tests": ["集成测试列表"],
        "edge_cases": ["边界情况"]
    },
    "reasoning": "测试策略说明"
}"""

    def _build_user_prompt(self, task: str, context: Dict[str, Any]) -> str:
        """构建用户提示词"""
        prompt = f"测试任务：\n{task}\n\n"

        if context.get("code"):
            prompt += f"待测试代码：\n{context['code']}\n\n"

        if context.get("design"):
            prompt += f"设计文档：\n{json.dumps(context['design'], ensure_ascii=False, indent=2)}\n\n"

        prompt += "请生成完整的测试用例。"

        return prompt

    def _parse_tests(self, response: str) -> List[Dict[str, Any]]:
        """解析测试用例"""
        try:
            start = response.find("{")
            end = response.rfind("}") + 1
            if start != -1 and end > start:
                json_str = response[start:end]
                data = json.loads(json_str)
                return data.get("test_files", [])
        except Exception as e:
            print(f"解析测试用例失败: {e}")

        return []
