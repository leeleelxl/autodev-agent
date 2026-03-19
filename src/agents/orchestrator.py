"""
LangGraph Orchestrator - 基于状态机的 Agent 协调器

核心技术：
- LangGraph StateGraph: 有向图状态机，替代硬编码的 Phase 1→5
- 条件路由 (Conditional Edges): 根据质量评分动态决定下一步
- 状态管理: TypedDict 定义全局工作流状态
"""

from typing import Dict, Any, Optional, List, TypedDict, Annotated
from enum import Enum
import json
import operator

from langgraph.graph import StateGraph, END

from .base_agent import BaseReActAgent, AgentResponse


# ============================================================
# 工作流状态定义 (LangGraph TypedDict)
# ============================================================

class WorkflowState(TypedDict):
    """LangGraph 工作流状态

    所有 Agent 共享的全局状态，通过 StateGraph 在节点间传递。
    """
    task: str                          # 原始任务描述
    design: Optional[Dict[str, Any]]   # 架构设计结果
    code_files: List[Dict[str, str]]   # 生成的代码文件
    test_cases: List[Dict[str, Any]]   # 测试用例
    test_results: List[Dict[str, Any]] # 测试执行结果
    review: Optional[Dict[str, Any]]   # 代码审查结果
    review_score: int                  # 审查分数 (0-100)
    iteration: int                     # 当前迭代次数
    max_iterations: int                # 最大迭代次数
    phases_log: List[Dict[str, Any]]   # 阶段执行日志
    error: Optional[str]               # 错误信息
    success: bool                      # 是否成功


# ============================================================
# LangGraph Orchestrator
# ============================================================

class Orchestrator:
    """
    基于 LangGraph 的 Agent 协调器

    使用 StateGraph 构建有向图工作流：

        ┌──────────┐
        │ Architect │
        └────┬─────┘
             │
        ┌────▼─────┐
        │ Developer │◄──────────┐
        └────┬─────┘            │
             │                  │
        ┌────▼─────┐            │
        │  Tester  │            │
        └────┬─────┘            │
             │                  │
        ┌────▼─────┐   score<80 │
        │ Reviewer │────────────┘
        └────┬─────┘
             │ score>=80
        ┌────▼─────┐
        │   END    │
        └──────────┘

    条件路由：Reviewer 评分 < 80 且迭代次数未超限 → 回到 Developer 改进
    """

    def __init__(self):
        self.agents: Dict[str, BaseReActAgent] = {}
        self.memory_manager = None
        self.experience_memory = None
        self.graph = None

    def register_agent(self, agent: BaseReActAgent):
        """注册 Agent"""
        self.agents[agent.config.name] = agent

    def set_memory(self, memory_manager, experience_memory=None):
        """设置记忆系统"""
        self.memory_manager = memory_manager
        self.experience_memory = experience_memory
        for agent in self.agents.values():
            agent.set_memory_manager(memory_manager)

    def _build_graph(self) -> StateGraph:
        """
        构建 LangGraph 状态图

        定义节点（Agent）和边（转换条件）
        """
        graph = StateGraph(WorkflowState)

        # 添加节点 (每个节点对应一个 Agent 的处理函数)
        graph.add_node("architect", self._architect_node)
        graph.add_node("developer", self._developer_node)
        graph.add_node("tester", self._tester_node)
        graph.add_node("reviewer", self._reviewer_node)

        # 定义边 (工作流转换)
        graph.set_entry_point("architect")
        graph.add_edge("architect", "developer")
        graph.add_edge("developer", "tester")
        graph.add_edge("tester", "reviewer")

        # 条件路由：Reviewer 之后根据分数决定下一步
        graph.add_conditional_edges(
            "reviewer",
            self._should_improve,
            {
                "improve": "developer",  # 分数不够 → 回到 Developer
                "done": END,             # 分数达标 → 结束
            }
        )

        return graph.compile()

    # ============================================================
    # 节点函数 (每个节点对应一个 Agent)
    # ============================================================

    async def _architect_node(self, state: WorkflowState) -> Dict:
        """架构设计节点"""
        print("\n  Phase 1: 架构设计...")
        architect = self.agents.get("architect")
        if not architect:
            return {"error": "Architect agent 未注册", "success": False}

        context = {}
        if self.memory_manager:
            try:
                memories = await self.memory_manager.search(state["task"], use_long_term=True, top_k=5)
                if memories:
                    context["memory_context"] = "\n".join([m.content for m in memories])
                    print(f"    ✓ 检索到 {len(memories)} 条相关记忆")
            except Exception:
                pass

        response = await architect.process(state["task"], context)
        design = response.metadata.get("design", {})

        return {
            "design": design,
            "phases_log": state.get("phases_log", []) + [{
                "name": "architecture",
                "tools_used": response.tool_calls,
                "reasoning": response.reasoning or "",
            }]
        }

    async def _developer_node(self, state: WorkflowState) -> Dict:
        """代码实现节点"""
        iteration = state.get("iteration", 0)
        if iteration == 0:
            print("  Phase 2: 代码实现...")
        else:
            print(f"  Phase 5: 迭代改进 (第 {iteration} 轮)...")

        developer = self.agents.get("developer")
        if not developer:
            return {"error": "Developer agent 未注册", "success": False}

        context = {"design": state.get("design")}

        # 如果是迭代改进，传入审查问题
        if iteration > 0 and state.get("review"):
            issues = state["review"].get("issues", [])
            high_priority = [i for i in issues if i.get("severity") == "high"]
            context["review_issues"] = high_priority
            context["existing_code"] = "\n\n".join(
                f"# {f.get('path')}\n{f.get('content')}"
                for f in state.get("code_files", [])
            )

        task = "根据架构设计实现代码" if iteration == 0 else "根据审查意见修复代码问题"
        response = await developer.process(task, context)
        code_files = response.metadata.get("files", [])

        phase_name = "development" if iteration == 0 else f"improvement_{iteration}"

        return {
            "code_files": code_files if code_files else state.get("code_files", []),
            "phases_log": state.get("phases_log", []) + [{
                "name": phase_name,
                "tools_used": response.tool_calls,
                "files_count": len(code_files),
            }]
        }

    async def _tester_node(self, state: WorkflowState) -> Dict:
        """测试生成节点"""
        print("  Phase 3: 测试生成...")
        tester = self.agents.get("tester")
        if not tester:
            return {"error": "Tester agent 未注册", "success": False}

        context = {
            "code_files": state.get("code_files", []),
            "design": state.get("design"),
        }

        response = await tester.process("为实现的代码生成测试用例", context)
        test_cases = response.metadata.get("test_cases", [])

        return {
            "test_cases": test_cases,
            "phases_log": state.get("phases_log", []) + [{
                "name": "testing",
                "tools_used": response.tool_calls,
                "test_count": len(test_cases),
            }]
        }

    async def _reviewer_node(self, state: WorkflowState) -> Dict:
        """代码审查节点"""
        print("  Phase 4: 代码审查...")
        reviewer = self.agents.get("reviewer")
        if not reviewer:
            return {"error": "Reviewer agent 未注册", "success": False}

        context = {
            "code_files": state.get("code_files", []),
            "design": state.get("design"),
            "test_results": state.get("test_results", []),
        }

        response = await reviewer.process("审查代码质量并提供改进建议", context)
        review = response.metadata.get("review", {})
        score = review.get("score", 0)

        print(f"    审查分数: {score}/100")

        # 记录经验
        if self.experience_memory:
            try:
                simple_metadata = {
                    "score": score / 100.0,
                    "num_issues": len(review.get("issues", []))
                }
                if score >= 70:
                    await self.experience_memory.record_success(
                        task=state["task"],
                        solution=f"生成了 {len(state.get('code_files', []))} 个文件",
                        metadata=simple_metadata
                    )
                else:
                    await self.experience_memory.record_failure(
                        task=state["task"],
                        error=f"质量分数: {score}",
                        attempted_solution="见代码文件",
                        metadata=simple_metadata
                    )
            except Exception:
                pass

        return {
            "review": review,
            "review_score": score,
            "iteration": state.get("iteration", 0) + 1,
            "phases_log": state.get("phases_log", []) + [{
                "name": "review",
                "tools_used": response.tool_calls,
                "score": score,
                "issues_count": len(review.get("issues", [])),
            }]
        }

    # ============================================================
    # 条件路由函数
    # ============================================================

    def _should_improve(self, state: WorkflowState) -> str:
        """
        条件路由：决定是否需要迭代改进

        规则：
        - 审查分数 < 80 且 迭代次数 < max_iterations → 回到 Developer
        - 否则 → 结束
        """
        score = state.get("review_score", 0)
        iteration = state.get("iteration", 0)
        max_iter = state.get("max_iterations", 2)

        if score < 80 and iteration < max_iter:
            print(f"    → 分数 {score} < 80，触发迭代改进 (第 {iteration}/{max_iter} 轮)")
            return "improve"
        else:
            if score >= 80:
                print(f"    → 分数 {score} >= 80，质量达标")
            else:
                print(f"    → 已达最大迭代次数 ({max_iter})，结束")
            return "done"

    # ============================================================
    # 主执行入口
    # ============================================================

    async def execute_workflow(self, initial_task: str) -> Dict[str, Any]:
        """
        执行完整的开发工作流

        使用 LangGraph 状态机驱动：
        Architect → Developer → Tester → Reviewer → (条件) → Developer/END

        Args:
            initial_task: 初始任务描述

        Returns:
            执行结果
        """
        print("\n" + "=" * 60)
        print("  LangGraph 工作流启动")
        print("=" * 60)

        # 构建状态图
        graph = self._build_graph()

        # 初始状态
        initial_state: WorkflowState = {
            "task": initial_task,
            "design": None,
            "code_files": [],
            "test_cases": [],
            "test_results": [],
            "review": None,
            "review_score": 0,
            "iteration": 0,
            "max_iterations": 2,
            "phases_log": [],
            "error": None,
            "success": False,
        }

        try:
            # 执行 LangGraph 状态机
            final_state = await graph.ainvoke(initial_state)

            # 整合记忆
            if self.memory_manager:
                try:
                    await self.memory_manager.consolidate()
                    print("  ✓ 记忆整合完成")
                except Exception:
                    pass

            return {
                "task": initial_task,
                "success": True,
                "phases": final_state.get("phases_log", []),
                "final_output": {
                    "design": final_state.get("design"),
                    "code_files": final_state.get("code_files"),
                    "test_files": final_state.get("test_cases"),
                    "test_results": final_state.get("test_results"),
                    "review": final_state.get("review"),
                },
                "iterations": final_state.get("iteration", 0),
                "final_score": final_state.get("review_score", 0),
            }

        except Exception as e:
            print(f"\n  ✗ 工作流执行失败: {e}")

            if self.experience_memory:
                try:
                    await self.experience_memory.record_failure(
                        task=initial_task,
                        error=str(e),
                        attempted_solution="工作流执行失败",
                        metadata={"phase": "workflow"}
                    )
                except Exception:
                    pass

            return {
                "task": initial_task,
                "success": False,
                "error": str(e),
                "phases": [],
                "final_output": {},
            }
