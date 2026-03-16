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
        self.code_executor = None

    def set_tools(self, code_executor=None):
        """设置工具"""
        self.code_executor = code_executor

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

        # 如果有代码执行器，运行测试
        test_results = []
        if self.code_executor and context.get("code_files"):
            for test_file in test_cases:
                test_code = test_file.get("content", "")

                # 获取对应的主代码
                main_code = self._get_main_code(test_file, context["code_files"])

                if main_code:
                    # 执行测试
                    result = await self.code_executor.execute_with_tests(
                        main_code,
                        test_code,
                        timeout=30
                    )

                    test_results.append({
                        "test_file": test_file.get("path"),
                        "success": result.success,
                        "output": result.output,
                        "error": result.error
                    })

        self.add_message(Message(
            role="assistant",
            content=response_content,
            metadata={
                "task": task,
                "phase": "testing",
                "test_results": test_results
            }
        ))

        return AgentResponse(
            content=response_content,
            actions=[
                {"type": "tests_generated", "tests": test_cases}
            ],
            metadata={
                "phase": "testing",
                "test_cases": test_cases,
                "test_results": test_results
            }
        )

    def _get_main_code(self, test_file: Dict, code_files: List[Dict]) -> Optional[str]:
        """获取测试对应的主代码"""
        test_path = test_file.get("path", "")

        # 简单匹配：test_xxx.py -> xxx.py
        if test_path.startswith("test_"):
            main_path = test_path.replace("test_", "")
            for code_file in code_files:
                if code_file.get("path") == main_path:
                    return code_file.get("content")

        # 如果只有一个代码文件，直接返回
        if len(code_files) == 1:
            return code_files[0].get("content")

        return None

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

        if context.get("code_files"):
            prompt += "待测试代码：\n"
            for file in context["code_files"]:
                prompt += f"\n文件: {file.get('path')}\n"
                prompt += f"```python\n{file.get('content')}\n```\n"

        if context.get("design"):
            prompt += f"\n设计文档：\n{json.dumps(context['design'], ensure_ascii=False, indent=2)}\n\n"

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
