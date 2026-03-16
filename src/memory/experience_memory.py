"""
Experience Memory - 经验学习系统

从历史任务中学习和总结经验
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from .long_term_memory import LongTermMemory


class ExperienceMemory:
    """经验记忆 - 从成功和失败中学习"""

    def __init__(self, persist_dir: str = "./data/chroma"):
        self.memory = LongTermMemory(persist_dir=persist_dir)

    async def record_success(self, task: str, solution: str, metadata: Dict[str, Any]):
        """
        记录成功案例

        Args:
            task: 任务描述
            solution: 解决方案
            metadata: 额外信息（如性能指标、代码质量等）
        """
        content = f"任务: {task}\n解决方案: {solution}"
        metadata.update({
            "type": "success",
            "timestamp": datetime.now().isoformat()
        })

        await self.memory.add(content, metadata)

    async def record_failure(self, task: str, error: str, attempted_solution: str, metadata: Dict[str, Any]):
        """
        记录失败案例

        Args:
            task: 任务描述
            error: 错误信息
            attempted_solution: 尝试的解决方案
            metadata: 额外信息
        """
        content = f"任务: {task}\n尝试方案: {attempted_solution}\n失败原因: {error}"
        metadata.update({
            "type": "failure",
            "timestamp": datetime.now().isoformat()
        })

        await self.memory.add(content, metadata)

    async def get_similar_experiences(self, task: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """
        获取相似的历史经验

        Args:
            task: 当前任务
            top_k: 返回数量

        Returns:
            相似经验列表
        """
        memories = await self.memory.search(task, top_k=top_k)

        experiences = []
        for mem in memories:
            experiences.append({
                "content": mem.content,
                "type": mem.metadata.get("type"),
                "timestamp": mem.metadata.get("timestamp"),
                "metadata": mem.metadata
            })

        return experiences

    async def learn_from_feedback(self, task: str, feedback: str, score: float):
        """
        从反馈中学习

        Args:
            task: 任务描述
            feedback: 反馈内容
            score: 评分（0-1）
        """
        content = f"任务: {task}\n反馈: {feedback}\n评分: {score}"
        metadata = {
            "type": "feedback",
            "score": score,
            "timestamp": datetime.now().isoformat()
        }

        await self.memory.add(content, metadata)

    async def get_best_practices(self, domain: str, top_k: int = 5) -> List[str]:
        """
        获取某个领域的最佳实践

        Args:
            domain: 领域（如 "testing", "architecture"）
            top_k: 返回数量

        Returns:
            最佳实践列表
        """
        query = f"{domain} 最佳实践 成功案例"
        memories = await self.memory.search(query, top_k=top_k)

        # 筛选高分案例
        best_practices = []
        for mem in memories:
            if mem.metadata.get("type") == "success":
                score = mem.metadata.get("score", 0)
                if score > 0.8:
                    best_practices.append(mem.content)

        return best_practices
