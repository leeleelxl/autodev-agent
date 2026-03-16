"""
Orchestrator - Agent 协调器

负责协调多个 agent 的工作流程
"""

from typing import List, Dict, Any, Optional
from enum import Enum
from pydantic import BaseModel, Field

from .base_agent import BaseAgent, AgentResponse, Message


class TaskStatus(str, Enum):
    """任务状态"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class Task(BaseModel):
    """任务定义"""
    id: str
    description: str
    assigned_to: Optional[str] = None
    status: TaskStatus = TaskStatus.PENDING
    dependencies: List[str] = Field(default_factory=list)
    result: Optional[AgentResponse] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class Orchestrator:
    """Agent 协调器"""

    def __init__(self):
        self.agents: Dict[str, BaseAgent] = {}
        self.tasks: Dict[str, Task] = {}
        self.workflow_history: List[Dict[str, Any]] = []
        self.context: Dict[str, Any] = {}
        self.tools: Dict[str, Any] = {}

    def register_agent(self, agent: BaseAgent):
        """注册 agent"""
        self.agents[agent.config.name] = agent

    def register_tools(self, **tools):
        """注册工具"""
        self.tools.update(tools)

        # 为 agents 设置工具
        if "developer" in self.agents:
            self.agents["developer"].set_tools(
                code_analyzer=tools.get("code_analyzer"),
                linter=tools.get("linter")
            )

        if "tester" in self.agents:
            self.agents["tester"].set_tools(
                code_executor=tools.get("code_executor")
            )

        if "reviewer" in self.agents:
            self.agents["reviewer"].set_tools(
                code_analyzer=tools.get("code_analyzer"),
                linter=tools.get("linter")
            )

    def create_task(self, task: Task):
        """创建任务"""
        self.tasks[task.id] = task

    async def execute_workflow(self, initial_task: str) -> Dict[str, Any]:
        """
        执行完整的开发工作流

        流程：需求分析 → 架构设计 → 代码实现 → 测试 → 审查 → 迭代

        Args:
            initial_task: 初始任务描述

        Returns:
            执行结果
        """
        workflow_result = {
            "task": initial_task,
            "phases": [],
            "final_output": {},
            "success": False
        }

        try:
            # Phase 1: 架构设计
            print("Phase 1: 架构设计...")
            architect = self.agents.get("architect")
            if not architect:
                raise ValueError("Architect agent 未注册")

            design_response = await architect.process(initial_task, self.context)
            self.context["design"] = design_response.metadata.get("design")
            workflow_result["phases"].append({
                "name": "architecture",
                "result": design_response.content
            })

            # Phase 2: 代码实现
            print("Phase 2: 代码实现...")
            developer = self.agents.get("developer")
            if not developer:
                raise ValueError("Developer agent 未注册")

            dev_response = await developer.process(
                "根据架构设计实现代码",
                self.context
            )
            self.context["code_files"] = dev_response.metadata.get("files", [])
            workflow_result["phases"].append({
                "name": "development",
                "result": dev_response.content
            })

            # Phase 3: 测试生成
            print("Phase 3: 测试生成...")
            tester = self.agents.get("tester")
            if not tester:
                raise ValueError("Tester agent 未注册")

            test_response = await tester.process(
                "为实现的代码生成测试用例",
                self.context
            )
            self.context["test_files"] = test_response.metadata.get("test_cases", [])
            workflow_result["phases"].append({
                "name": "testing",
                "result": test_response.content
            })

            # Phase 4: 代码审查
            print("Phase 4: 代码审查...")
            reviewer = self.agents.get("reviewer")
            if not reviewer:
                raise ValueError("Reviewer agent 未注册")

            review_response = await reviewer.process(
                "审查代码质量并提供改进建议",
                self.context
            )
            review_result = review_response.metadata.get("review", {})
            workflow_result["phases"].append({
                "name": "review",
                "result": review_response.content
            })

            # Phase 5: 迭代改进（如果需要）
            if review_result.get("score", 100) < 80:
                print("Phase 5: 迭代改进...")
                issues = review_result.get("issues", [])
                high_priority = [i for i in issues if i.get("severity") == "high"]

                if high_priority:
                    # 重新开发修复问题
                    self.context["review_issues"] = high_priority
                    improved_response = await developer.process(
                        "根据审查意见修复代码问题",
                        self.context
                    )
                    workflow_result["phases"].append({
                        "name": "improvement",
                        "result": improved_response.content
                    })

            workflow_result["success"] = True
            workflow_result["final_output"] = {
                "design": self.context.get("design"),
                "code_files": self.context.get("code_files"),
                "test_files": self.context.get("test_files"),
                "review": review_result
            }

        except Exception as e:
            workflow_result["error"] = str(e)
            print(f"工作流执行失败: {e}")

        return workflow_result

    def _decompose_task(self, task: str) -> List[Task]:
        """将任务分解为子任务"""
        # 标准工作流的任务分解
        subtasks = [
            Task(id="arch", description="架构设计", assigned_to="architect"),
            Task(id="dev", description="代码实现", assigned_to="developer", dependencies=["arch"]),
            Task(id="test", description="测试生成", assigned_to="tester", dependencies=["dev"]),
            Task(id="review", description="代码审查", assigned_to="reviewer", dependencies=["dev", "test"]),
        ]
        return subtasks

    def _assign_task(self, task: Task) -> str:
        """为任务分配合适的 agent"""
        return task.assigned_to or "developer"

    def _check_dependencies(self, task: Task) -> bool:
        """检查任务依赖是否满足"""
        for dep_id in task.dependencies:
            if dep_id not in self.tasks:
                return False
            if self.tasks[dep_id].status != TaskStatus.COMPLETED:
                return False
        return True
