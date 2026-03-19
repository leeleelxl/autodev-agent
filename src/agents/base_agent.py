"""
ReAct Base Agent - 基于 LangChain 的 ReAct 模式 Agent 基类

核心技术：
- ReAct (Reasoning + Acting): Thought → Action → Observation 循环
- Chain-of-Thought (CoT): 结构化推理，逐步分析问题
- Tool Calling / Function Calling: LLM 自主决定调用哪个工具
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_openai import ChatOpenAI


class AgentConfig(BaseModel):
    """Agent 配置"""
    name: str
    role: str
    provider: str = "moonshot"
    model: str = "kimi-k2-turbo-preview"
    temperature: float = 0.7
    max_tokens: int = 4096


class AgentResponse(BaseModel):
    """Agent 响应"""
    content: str
    reasoning: Optional[str] = None
    tool_calls: List[Dict[str, Any]] = Field(default_factory=list)
    actions: List[Dict[str, Any]] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


# CoT 推理模板 - 强制 LLM 进行结构化思考
COT_REASONING_TEMPLATE = """
在回答之前，请按以下 Chain-of-Thought 步骤进行结构化推理：

## 思考过程 (Chain-of-Thought)

### Step 1: 理解任务
- 任务的核心目标是什么？
- 有哪些约束条件？

### Step 2: 分析上下文
- 已有哪些信息可以利用？
- 还缺少什么信息？（如果缺少，考虑使用工具获取）

### Step 3: 制定方案
- 有哪些可能的方案？
- 每个方案的优劣是什么？
- 选择最优方案的理由是什么？

### Step 4: 执行计划
- 具体的执行步骤是什么？
- 每一步需要使用什么工具？

### Step 5: 验证结果
- 如何验证结果的正确性？
- 是否需要进一步改进？

请基于以上思考过程，给出你的回答。
"""


class BaseReActAgent(ABC):
    """
    ReAct Agent 基类

    实现 ReAct 模式：
    1. Thought - LLM 思考当前状态和下一步行动
    2. Action - 调用工具执行操作
    3. Observation - 观察工具返回结果
    4. 重复直到任务完成

    同时集成 Chain-of-Thought 推理，确保每次决策都有结构化的思考过程。
    """

    def __init__(self, config: AgentConfig):
        self.config = config
        self.llm: Optional[ChatOpenAI] = None
        self.tools: List = []
        self.memory_manager = None
        self.conversation_history: List = []

    def set_llm(self, llm: ChatOpenAI):
        """设置 LangChain LLM"""
        self.llm = llm

    def set_tools(self, tools: List):
        """设置 LangChain Tools（用于 Function Calling）"""
        self.tools = tools

    def set_memory_manager(self, memory_manager):
        """设置记忆管理器"""
        self.memory_manager = memory_manager

    def _build_full_system_prompt(self) -> str:
        """
        构建完整的系统提示词

        将子类的 system prompt + CoT 推理框架 + ReAct 指令合并
        """
        system_prompt = self._build_system_prompt()

        return f"""{system_prompt}

{COT_REASONING_TEMPLATE}

你可以使用以下工具来辅助完成任务。当你需要信息时，主动调用工具获取。
当你认为任务已完成，直接给出最终答案。
"""

    async def process(self, task: str, context: Optional[Dict[str, Any]] = None) -> AgentResponse:
        """
        处理任务 - ReAct 循环

        Args:
            task: 任务描述
            context: 上下文信息

        Returns:
            AgentResponse
        """
        if not self.llm:
            raise ValueError("LLM 未设置，请先调用 set_llm()")

        context = context or {}

        # 构建用户消息（包含上下文）
        user_message = self._build_user_prompt(task, context)

        # 如果有工具，绑定到 LLM（启用 Function Calling）
        if self.tools:
            llm_with_tools = self.llm.bind_tools(self.tools)
        else:
            llm_with_tools = self.llm

        # 构建消息列表（直接使用 Message 对象，避免 ChatPromptTemplate 的花括号转义问题）
        system_content = self._build_full_system_prompt()
        messages = [
            SystemMessage(content=system_content),
            HumanMessage(content=user_message),
        ]
        tool_call_log = []
        max_iterations = 5

        for iteration in range(max_iterations):
            # Thought + Action: LLM 思考并决定是否调用工具
            response = await llm_with_tools.ainvoke(messages)

            # 检查是否有工具调用（Function Calling）
            if hasattr(response, 'tool_calls') and response.tool_calls:
                # Action: 执行工具调用
                messages.append(response)

                for tool_call in response.tool_calls:
                    tool_name = tool_call["name"]
                    tool_args = tool_call["args"]

                    print(f"    🔧 [{self.config.name}] 调用工具: {tool_name}({tool_args})")

                    # 执行工具
                    tool_result = await self._execute_tool(tool_name, tool_args)

                    tool_call_log.append({
                        "iteration": iteration + 1,
                        "tool": tool_name,
                        "args": tool_args,
                        "result": str(tool_result)[:200]
                    })

                    # Observation: 将工具结果反馈给 LLM
                    from langchain_core.messages import ToolMessage
                    messages.append(ToolMessage(
                        content=str(tool_result),
                        tool_call_id=tool_call["id"]
                    ))
            else:
                # 没有工具调用，LLM 给出了最终答案
                break

        # 提取最终响应
        final_content = response.content if hasattr(response, 'content') else str(response)

        # 解析结构化输出
        parsed = self._parse_response(final_content)

        # 提取 CoT 推理过程
        reasoning = self._extract_reasoning(final_content)

        return AgentResponse(
            content=final_content,
            reasoning=reasoning,
            tool_calls=tool_call_log,
            actions=parsed.get("actions", []),
            metadata={
                "phase": self.config.name,
                "iterations": min(iteration + 1, max_iterations),
                "tools_used": [tc["tool"] for tc in tool_call_log],
                **parsed.get("metadata", {}),
            }
        )

    async def _execute_tool(self, tool_name: str, tool_args: Dict) -> str:
        """执行工具调用"""
        for tool in self.tools:
            if tool.name == tool_name:
                try:
                    result = tool.invoke(tool_args)
                    return str(result)
                except Exception as e:
                    return f"工具执行失败: {str(e)}"
        return f"未找到工具: {tool_name}"

    def _extract_reasoning(self, content: str) -> str:
        """从响应中提取 CoT 推理过程"""
        # 尝试提取 "思考过程" 部分
        markers = ["## 思考过程", "### Step 1", "思考：", "分析："]
        for marker in markers:
            if marker in content:
                idx = content.index(marker)
                # 找到推理结束的位置（通常在最终答案之前）
                end_markers = ["## 最终", "## 输出", "```python", "```json", "{"]
                end_idx = len(content)
                for em in end_markers:
                    if em in content[idx + len(marker):]:
                        candidate = content.index(em, idx + len(marker))
                        end_idx = min(end_idx, candidate)
                return content[idx:end_idx].strip()
        return ""

    @abstractmethod
    def _build_system_prompt(self) -> str:
        """构建系统提示词（子类实现）"""
        pass

    @abstractmethod
    def _build_user_prompt(self, task: str, context: Dict[str, Any]) -> str:
        """构建用户提示词（子类实现）"""
        pass

    @abstractmethod
    def _parse_response(self, response: str) -> Dict[str, Any]:
        """解析响应（子类实现）"""
        pass
