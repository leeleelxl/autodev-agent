"""
Tester Agent - 测试工程师

基于 ReAct + CoT 模式，负责测试用例生成和代码测试。
可通过 Tool Calling 自主执行代码和分析测试结果。
"""

from typing import Dict, Any, Optional, List
import json
from .base_agent import BaseReActAgent, AgentConfig, AgentResponse


class TesterAgent(BaseReActAgent):
    """测试工程师 Agent - ReAct 模式"""

    def __init__(self):
        config = AgentConfig(
            name="tester",
            role="测试工程师，负责测试用例生成和代码测试"
        )
        super().__init__(config)

    def _build_system_prompt(self) -> str:
        return """你是一位资深测试工程师，擅长编写全面的测试用例。

你的任务是：
1. 分析代码功能和边界条件
2. 设计测试用例（单元测试、集成测试）
3. 考虑正常情况和异常情况
4. 确保测试覆盖率
5. 编写清晰的测试代码

你可以使用工具来执行代码、分析代码结构，验证测试是否通过。
当你生成测试后，主动使用执行工具运行测试验证。

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
        prompt = f"测试任务：\n{task}\n\n"

        if context.get("code_files"):
            prompt += "待测试代码：\n"
            for file in context["code_files"]:
                prompt += f"\n文件: {file.get('path')}\n"
                prompt += f"```python\n{file.get('content')}\n```\n"

        if context.get("design"):
            prompt += f"\n设计文档：\n{json.dumps(context['design'], ensure_ascii=False, indent=2)}\n\n"

        prompt += "请生成完整的测试用例。"
        return prompt

    def _parse_response(self, response: str) -> Dict[str, Any]:
        test_cases = self._parse_tests(response)
        return {
            "actions": [{"type": "tests_generated", "tests": test_cases}],
            "metadata": {"test_cases": test_cases}
        }

    def _parse_tests(self, response: str) -> List[Dict[str, Any]]:
        try:
            start = response.find("{")
            end = response.rfind("}") + 1
            if start != -1 and end > start:
                json_str = response[start:end]
                data = json.loads(json_str)
                return data.get("test_files", [])
        except Exception as e:
            print(f"  解析测试用例失败: {e}")
        return []
