"""
Reviewer Agent - 代码审查员

负责代码审查和优化建议
"""

from typing import Dict, Any, Optional, List
import json
from .base_agent import BaseAgent, AgentConfig, AgentResponse, Message


class ReviewerAgent(BaseAgent):
    """代码审查员 Agent"""

    def __init__(self):
        config = AgentConfig(
            name="reviewer",
            role="代码审查员，负责代码质量检查和优化建议"
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
        处理代码审查任务

        检查代码质量并提供改进建议
        """
        context = context or {}

        # 先使用工具进行自动分析
        tool_analysis = await self._analyze_with_tools(context)

        system_prompt = self._build_system_prompt()
        user_prompt = self._build_user_prompt(task, context, tool_analysis)

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        response_content = await self._call_llm(messages)

        # 解析审查结果
        review_result = self._parse_review(response_content)

        # 合并工具分析结果
        if tool_analysis:
            review_result["tool_analysis"] = tool_analysis

        self.add_message(Message(
            role="assistant",
            content=response_content,
            metadata={"task": task, "phase": "review"}
        ))

        return AgentResponse(
            content=response_content,
            actions=[
                {"type": "review_completed", "result": review_result}
            ],
            metadata={
                "phase": "review",
                "review": review_result
            }
        )

    def _build_system_prompt(self) -> str:
        """构建系统提示词"""
        return """你是一位资深代码审查专家，擅长发现代码问题并提供改进建议。

审查维度：
1. 代码质量 - 可读性、可维护性、复杂度
2. 最佳实践 - 设计模式、编码规范
3. 性能 - 算法效率、资源使用
4. 安全性 - 潜在漏洞、输入验证
5. 测试 - 测试覆盖率、测试质量

请以 JSON 格式输出审查结果：
{
    "score": 85,  // 总分 0-100
    "issues": [
        {
            "severity": "high/medium/low",
            "category": "质量/性能/安全/测试",
            "location": "文件:行号",
            "description": "问题描述",
            "suggestion": "改进建议"
        }
    ],
    "strengths": ["优点1", "优点2"],
    "summary": "总体评价",
    "reasoning": "审查思路"
}"""

    async def _analyze_with_tools(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """使用工具进行自动分析"""
        tool_results = {
            "analysis": [],
            "quality": []
        }

        code_files = context.get("code_files", [])

        for file in code_files:
            code = file.get("content", "")
            file_path = file.get("path", "")

            # 代码分析
            if self.code_analyzer:
                analysis = await self.code_analyzer.execute(code)
                if analysis.success:
                    tool_results["analysis"].append({
                        "file": file_path,
                        "result": analysis.output
                    })

            # 质量检查
            if self.linter:
                quality = await self.linter.execute(code)
                if quality.success:
                    tool_results["quality"].append({
                        "file": file_path,
                        "result": quality.output
                    })

        return tool_results

    def _build_user_prompt(self, task: str, context: Dict[str, Any], tool_analysis: Dict[str, Any]) -> str:
        """构建用户提示词"""
        prompt = f"审查任务：\n{task}\n\n"

        if context.get("code_files"):
            prompt += "待审查代码：\n"
            for file in context["code_files"]:
                prompt += f"\n文件: {file.get('path')}\n"
                prompt += f"```python\n{file.get('content')}\n```\n"

        if context.get("design"):
            prompt += f"\n设计文档：\n{json.dumps(context['design'], ensure_ascii=False, indent=2)}\n\n"

        if context.get("test_results"):
            prompt += f"\n测试结果：\n{json.dumps(context['test_results'], ensure_ascii=False, indent=2)}\n\n"

        # 添加工具分析结果
        if tool_analysis:
            prompt += "\n自动分析结果：\n"

            # 代码分析结果
            if tool_analysis.get("analysis"):
                prompt += "\n代码结构分析：\n"
                for item in tool_analysis["analysis"]:
                    prompt += f"- {item['file']}: {item['result'].get('summary', '')}\n"

            # 质量检查结果
            if tool_analysis.get("quality"):
                prompt += "\n代码质量检查：\n"
                for item in tool_analysis["quality"]:
                    quality = item['result']
                    prompt += f"- {item['file']}: {quality.get('summary', '')}\n"

        prompt += "\n请结合自动分析结果进行全面的代码审查。"

        return prompt

    def _parse_review(self, response: str) -> Dict[str, Any]:
        """解析审查结果"""
        try:
            start = response.find("{")
            end = response.rfind("}") + 1
            if start != -1 and end > start:
                json_str = response[start:end]
                return json.loads(json_str)
        except Exception as e:
            print(f"解析审查结果失败: {e}")

        return {
            "raw_response": response,
            "score": 0,
            "issues": []
        }
