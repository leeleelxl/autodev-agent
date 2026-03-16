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

    async def process(self, task: str, context: Optional[Dict[str, Any]] = None) -> AgentResponse:
        """
        处理代码审查任务

        检查代码质量并提供改进建议
        """
        context = context or {}

        system_prompt = self._build_system_prompt()
        user_prompt = self._build_user_prompt(task, context)

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        response_content = await self._call_llm(messages)

        # 解析审查结果
        review_result = self._parse_review(response_content)

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

    def _build_user_prompt(self, task: str, context: Dict[str, Any]) -> str:
        """构建用户提示词"""
        prompt = f"审查任务：\n{task}\n\n"

        if context.get("code"):
            prompt += f"待审查代码：\n{context['code']}\n\n"

        if context.get("design"):
            prompt += f"设计文档：\n{json.dumps(context['design'], ensure_ascii=False, indent=2)}\n\n"

        if context.get("tests"):
            prompt += f"测试代码：\n{context['tests']}\n\n"

        prompt += "请进行全面的代码审查并给出改进建议。"

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
