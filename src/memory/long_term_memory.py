"""
长期记忆 - 向量数据库存储
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid
import chromadb
from chromadb.config import Settings

from .base_memory import BaseMemory, MemoryEntry


class LongTermMemory(BaseMemory):
    """长期记忆 - 使用向量数据库存储历史经验"""

    def __init__(self, persist_dir: str = "./data/chroma"):
        self.persist_dir = persist_dir

        # 初始化 ChromaDB
        self.client = chromadb.PersistentClient(
            path=persist_dir,
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )

        # 获取或创建 collection
        self.collection = self.client.get_or_create_collection(
            name="agent_memory",
            metadata={"description": "Agent 长期记忆存储"}
        )

    async def add(self, content: str, metadata: Dict[str, Any]) -> str:
        """添加记忆到向量数据库"""
        memory_id = str(uuid.uuid4())

        # 添加时间戳
        metadata["timestamp"] = datetime.now().isoformat()

        # 存储到 ChromaDB（自动生成 embedding）
        self.collection.add(
            ids=[memory_id],
            documents=[content],
            metadatas=[metadata]
        )

        return memory_id

    async def search(self, query: str, top_k: int = 5) -> List[MemoryEntry]:
        """向量搜索相关记忆"""
        # 在 ChromaDB 中搜索
        results = self.collection.query(
            query_texts=[query],
            n_results=top_k
        )

        memories = []
        if results["ids"] and len(results["ids"]) > 0:
            for i in range(len(results["ids"][0])):
                memory = MemoryEntry(
                    id=results["ids"][0][i],
                    content=results["documents"][0][i],
                    metadata=results["metadatas"][0][i],
                    timestamp=datetime.fromisoformat(results["metadatas"][0][i]["timestamp"]),
                    embedding=None  # ChromaDB 内部管理
                )
                memories.append(memory)

        return memories

    async def get(self, memory_id: str) -> Optional[MemoryEntry]:
        """获取特定记忆"""
        try:
            result = self.collection.get(
                ids=[memory_id],
                include=["documents", "metadatas"]
            )

            if result["ids"]:
                return MemoryEntry(
                    id=result["ids"][0],
                    content=result["documents"][0],
                    metadata=result["metadatas"][0],
                    timestamp=datetime.fromisoformat(result["metadatas"][0]["timestamp"])
                )
        except Exception as e:
            print(f"获取记忆失败: {e}")

        return None

    async def clear(self):
        """清空记忆"""
        # 删除并重新创建 collection
        self.client.delete_collection("agent_memory")
        self.collection = self.client.create_collection(
            name="agent_memory",
            metadata={"description": "Agent 长期记忆存储"}
        )

    def get_stats(self) -> Dict[str, Any]:
        """获取记忆统计信息"""
        count = self.collection.count()
        return {
            "total_memories": count,
            "collection_name": self.collection.name,
            "persist_dir": self.persist_dir
        }
