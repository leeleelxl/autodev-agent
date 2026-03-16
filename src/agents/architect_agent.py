"""
Architect Agent - 架构师

负责需求分析、技术选型和架构设计
"""

from typing import Dict, Any, Optional
import json
from .base_agent import BaseAgent, AgentConfig, AgentResponse, Message


class ArchitectAgent(BaseAgent):
    """架构师 Agent"""

    def __init__(self):
        config = AgentConfig(
            name="architect",
            role="软件架构师，负责需求分析和架构设计"
        )
        super().__init__(config)

    async def process(self, task: str, context: Optional[Dict[str, Any]] = None) -> AgentResponse:
        """
        处理架构设计任务

        分析需求并生成：
        1. 需求分析
        2. 技术栈选择
        3. 系统架构设计
        4. 模块划分
        5. 接口定义
        """
        context = context or {}

        # 构建系统提示词
        system_prompt = self._build_system_prompt()

        # 构建用户提示词
        user_prompt = self._build_user_prompt(task, context)

        # 调用 LLM
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        response_content = await self._call_llm(messages)

        # 解析响应
        design = self._parse_response(response_content)

        # 保存到记忆
        self.add_message(Message(
            role="assistant",
            content=response_content,
            metadata={"task": task, "phase": "architecture"}
        ))

        return AgentResponse(
            content=response_content,
            reasoning=design.get("reasoning", ""),
            actions=[
                {"type": "design_created", "data": design}
            ],
            metadata={
                "phase": "architecture",
                "design": design
            }
        )

    def _build_system_prompt(self) -> str:
        """构建系统提示词"""
        return """你是一位资深软件架构师，擅长需求分析和系统设计。

你的任务是：
1. 深入理解用户需求
2. 选择合适的技术栈
3. 设计系统架构
4. 划分功能模块
5. 定义接口规范

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
        "pattern": "架构模式（如 MVC, 微服务等）",
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
        """构建用户提示词"""
        prompt = f"需求描述：\n{task}\n\n"

        if context.get("constraints"):
            prompt += f"约束条件：\n{context['constraints']}\n\n"

        if context.get("preferences"):
            prompt += f"偏好设置：\n{context['preferences']}\n\n"

        prompt += "请分析需求并给出完整的架构设计方案。"

        return prompt

    def _parse_response(self, response: str) -> Dict[str, Any]:
        """解析 LLM 响应"""
        try:
            # 尝试提取 JSON
            start = response.find("{")
            end = response.rfind("}") + 1
            if start != -1 and end > start:
                json_str = response[start:end]
                return json.loads(json_str)
        except Exception as e:
            print(f"解析响应失败: {e}")

        # 如果解析失败，返回原始内容
        return {
            "raw_response": response,
            "reasoning": "解析失败，返回原始响应"
        }
