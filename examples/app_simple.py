"""
简化版 Web UI - 快速演示

更轻量的界面，专注核心功能
"""

import streamlit as st
import asyncio
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from src.agents import Orchestrator, ArchitectAgent, DeveloperAgent, TesterAgent, ReviewerAgent
from src.llm import LLMFactory, LLMProvider
from src.tools import CodeExecutor, CodeAnalyzer, Linter
from src.memory import MemoryManager, ExperienceMemory


st.set_page_config(page_title="AutoDev", page_icon="🤖", layout="wide")

st.title("🤖 AutoDev - AI Agent 开发系统")

# 侧边栏配置
with st.sidebar:
    st.header("配置")
    provider = st.selectbox("LLM", ["anthropic", "moonshot", "qwen"])
    api_key = st.text_input("API Key", type="password")
    use_memory = st.checkbox("启用记忆", value=True)

# 任务输入
task = st.text_area("开发任务", placeholder="例如：创建一个计算器应用", height=100)

if st.button("执行", type="primary"):
    if not api_key:
        st.error("请输入 API Key")
    elif not task:
        st.error("请输入任务")
    else:
        # 创建系统
        orchestrator = Orchestrator()

        # 注册组件
        for agent_cls in [ArchitectAgent, DeveloperAgent, TesterAgent, ReviewerAgent]:
            orchestrator.register_agent(agent_cls())

        orchestrator.register_tools(
            code_executor=CodeExecutor(use_docker=False),
            code_analyzer=CodeAnalyzer(),
            linter=Linter()
        )

        if use_memory:
            memory = MemoryManager()
            experience = ExperienceMemory()
            orchestrator.set_memory(memory, experience)

        # 设置 LLM
        llm = LLMFactory.create_client(LLMProvider(provider), api_key)
        for agent in orchestrator.agents.values():
            agent.set_llm_client(llm)

        # 执行
        with st.spinner("执行中..."):
            try:
                result = asyncio.run(orchestrator.execute_workflow(task))

                # 显示结果
                st.success("✓ 完成")

                col1, col2 = st.columns(2)
                with col1:
                    st.metric("阶段", len(result["phases"]))
                with col2:
                    score = result.get("final_output", {}).get("review", {}).get("score", 0)
                    st.metric("质量", f"{score}/100")

                # 显示代码
                code_files = result.get("final_output", {}).get("code_files", [])
                if code_files:
                    st.subheader("生成的代码")
                    for file in code_files:
                        with st.expander(file.get("path", "code")):
                            st.code(file.get("content", ""), language="python")

            except Exception as e:
                st.error(f"错误: {str(e)}")
