"""
Developer Agent - 开发者

负责代码实现
"""

from typing import Dict, Any, Optional, List
import json
from .base_agent import BaseAgent, AgentConfig, AgentResponse, Message


class DeveloperAgent(BaseAgent):
    """开发者 Agent"""

    def __init__(self):
        config = AgentConfig(
            name="developer",
            role="软件开发者，负责代码实现"
        )
        super().__init__(config)
        self.code_analyzer = None
        self.linter = None

    def set_tools(self, code_analyzer=None, linter=None):
        """设置工具"""
        self.code_analyzer = code_analyzer
        self.linter = linter

    async def process(self, task: str, context: Optional[Dict[str, Any]] = None) -> AgentResponse:
        """
        处理代码开发任务

        根据设计文档生成代码
        """
        context = context or {}

        # 构建提示词
        system_prompt = self._build_system_prompt()
        user_prompt = self._build_user_prompt(task, context)

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        response_content = await self._call_llm(messages)

        # 解析代码
        code_files = self._parse_code(response_content)

        # 如果有工具，进行代码分析和质量检查
        analysis_results = []
        quality_results = []

        for file in code_files:
            code = file.get("content", "")

            # 代码分析
            if self.code_analyzer:
                analysis = await self.code_analyzer.execute(code)
                if analysis.success:
                    analysis_results.append({
                        "file": file.get("path"),
                        "analysis": analysis.output
                    })

            # 质量检查
            if self.linter:
                quality = await self.linter.execute(code)
                if quality.success:
                    quality_results.append({
                        "file": file.get("path"),
                        "quality": quality.output
                    })

        # 保存到记忆
        self.add_message(Message(
            role="assistant",
            content=response_content,
            metadata={
                "task": task,
                "phase": "development",
                "analysis": analysis_results,
                "quality": quality_results
            }
        ))

        return AgentResponse(
            content=response_content,
            actions=[
                {"type": "code_generated", "files": code_files}
            ],
            metadata={
                "phase": "development",
                "files": code_files,
                "analysis": analysis_results,
                "quality": quality_results
            }
        )

    def _build_system_prompt(self) -> str:
        """构建系统提示词"""
        return """你是一位资深软件开发工程师，擅长编写高质量、可维护的代码。

你的任务是：
1. 理解设计文档和需求
2. 编写清晰、简洁的代码
3. 遵循最佳实践和编码规范
4. 添加必要的注释和文档字符串
5. 考虑边界情况和错误处理

请以 JSON 格式输出代码文件，格式如下：
{
    "files": [
        {
            "path": "文件路径",
            "content": "文件内容",
            "description": "文件说明"
        }
    ],
    "reasoning": "实现思路和关键决策"
}"""

    def _build_user_prompt(self, task: str, context: Dict[str, Any]) -> str:
        """构建用户提示词"""
        prompt = f"开发任务：\n{task}\n\n"

        if context.get("design"):
            prompt += f"架构设计：\n{json.dumps(context['design'], ensure_ascii=False, indent=2)}\n\n"

        if context.get("existing_code"):
            prompt += f"现有代码：\n{context['existing_code']}\n\n"

        if context.get("requirements"):
            prompt += f"具体要求：\n{context['requirements']}\n\n"

        if context.get("review_issues"):
            prompt += f"需要修复的问题：\n{json.dumps(context['review_issues'], ensure_ascii=False, indent=2)}\n\n"

        prompt += "请实现代码并输出 JSON 格式的文件列表。"

        return prompt

    def _parse_code(self, response: str) -> List[Dict[str, str]]:
        """解析代码文件"""
        try:
            start = response.find("{")
            end = response.rfind("}") + 1
            if start != -1 and end > start:
                json_str = response[start:end]
                data = json.loads(json_str)
                return data.get("files", [])
        except Exception as e:
            print(f"解析代码失败: {e}")

        return []
