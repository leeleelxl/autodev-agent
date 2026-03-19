"""
Architect Agent - 架构师

基于 ReAct + CoT 模式，负责需求分析、技术选型和架构设计。
可通过 Tool Calling 自主检索历史经验辅助决策。
"""

from typing import Dict, Any, Optional
import json
from .base_agent import BaseReActAgent, AgentConfig, AgentResponse


class ArchitectAgent(BaseReActAgent):
    """架构师 Agent - ReAct 模式"""

    def __init__(self):
        config = AgentConfig(
            name="architect",
            role="软件架构师，负责需求分析和架构设计"
        )
        super().__init__(config)

    def _build_system_prompt(self) -> str:
        return """你是一位资深软件架构师，擅长需求分析和系统设计。

你的任务是：
1. 深入理解用户需求
2. 选择合适的技术栈
3. 设计系统架构
4. 划分功能模块
5. 定义接口规范

如果有可用的经验检索工具，你可以主动搜索历史经验来辅助决策。

请以 JSON 格式输出设计方案，包含以下字段：
{
    "requirements": {
        "functional": ["功能需求1", "功能需求2"],
        "non_functional": ["非功能需求1", "非功能需求2"]
    },
    "tech_stack": {
        "language": "编程语言",
        "framework": "框架",
        "database": "数据库",
        "other": ["其他技术"]
    },
    "architecture": {
        "pattern": "架构模式",
        "description": "架构描述",
        "components": ["组件1", "组件2"]
    },
    "modules": [
        {
            "name": "模块名",
            "responsibility": "职责",
            "interfaces": ["接口1", "接口2"]
        }
    ],
    "reasoning": "设计决策的理由"
}"""

    def _build_user_prompt(self, task: str, context: Dict[str, Any]) -> str:
        prompt = f"需求描述：\n{task}\n\n"

        if context.get("memory_context"):
            prompt += f"相关历史经验：\n{context['memory_context']}\n\n"

        if context.get("best_practices"):
            prompt += "最佳实践：\n"
            for practice in context["best_practices"]:
                prompt += f"- {practice}\n"
            prompt += "\n"

        if context.get("constraints"):
            prompt += f"约束条件：\n{context['constraints']}\n\n"

        prompt += "请分析需求并给出完整的架构设计方案。"
        return prompt

    def _parse_response(self, response: str) -> Dict[str, Any]:
        try:
            start = response.find("{")
            end = response.rfind("}") + 1
            if start != -1 and end > start:
                json_str = response[start:end]
                design = json.loads(json_str)
                return {
                    "actions": [{"type": "design_created", "data": design}],
                    "metadata": {"design": design}
                }
        except Exception as e:
            print(f"  解析架构设计失败: {e}")

        return {
            "actions": [{"type": "design_created", "data": {"raw_response": response}}],
            "metadata": {"design": {"raw_response": response}}
        }
