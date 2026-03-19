"""
Reviewer Agent - 代码审查员

基于 ReAct + CoT 模式，负责代码审查和优化建议。
可通过 Tool Calling 自主调用代码分析器和 Linter 进行自动化检查。
"""

from typing import Dict, Any, Optional, List
import json
import re
from .base_agent import BaseReActAgent, AgentConfig, AgentResponse


class ReviewerAgent(BaseReActAgent):
    """代码审查员 Agent - ReAct 模式"""

    def __init__(self):
        config = AgentConfig(
            name="reviewer",
            role="代码审查员，负责代码质量检查和优化建议"
        )
        super().__init__(config)

    def _build_system_prompt(self) -> str:
        return """你是一位资深代码审查专家，擅长发现代码问题并提供改进建议。

审查维度：
1. **完整性** - 所有 import 的模块是否都存在？代码能否直接运行？
2. 代码质量 - 可读性、可维护性、复杂度
3. 最佳实践 - 设计模式、编码规范
4. 性能 - 算法效率、资源使用
5. 安全性 - 潜在漏洞、输入验证
6. 测试 - 测试覆盖率、测试质量

你可以使用工具来分析代码结构、检查代码质量、搜索历史经验。
在审查前，主动使用工具进行自动化分析，然后结合人工审查给出综合评价。

**重要：首先检查代码完整性**
- 检查所有 import 语句
- 确认所有依赖模块都已提供
- 如果缺少文件，必须标记为 HIGH 严重性问题

请以 JSON 格式输出审查结果：
{
    "score": 85,
    "issues": [
        {
            "severity": "high/medium/low",
            "category": "完整性/质量/性能/安全/测试",
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

        prompt += "\n请进行全面的代码审查。"
        return prompt

    def _parse_response(self, response: str) -> Dict[str, Any]:
        review = self._parse_review(response)
        return {
            "actions": [{"type": "review_completed", "result": review}],
            "metadata": {"review": review}
        }

    def _parse_review(self, response: str) -> Dict[str, Any]:
        try:
            start = response.find("{")
            end = response.rfind("}") + 1
            if start != -1 and end > start:
                json_str = response[start:end]
                return json.loads(json_str)
        except Exception as e:
            print(f"  解析审查结果失败: {e}")

        return {"raw_response": response, "score": 0, "issues": []}
