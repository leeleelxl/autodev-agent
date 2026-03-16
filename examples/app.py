"""
AutoDev Web UI - Streamlit 界面

可视化 Agent 工作流和记忆系统
"""

import streamlit as st
import asyncio
import json
from datetime import datetime

from src.agents import (
    Orchestrator,
    ArchitectAgent,
    DeveloperAgent,
    TesterAgent,
    ReviewerAgent
)
from src.llm import LLMFactory, LLMProvider
from src.tools import CodeExecutor, CodeAnalyzer, Linter
from src.memory import MemoryManager, ExperienceMemory
from src.utils import Config


# 页面配置
st.set_page_config(
    page_title="AutoDev - AI Agent System",
    page_icon="🤖",
    layout="wide"
)

# 标题
st.title("🤖 AutoDev - 自主软件开发 Agent 系统")
st.markdown("多 Agent 协作的代码生成系统")

# 侧边栏 - 配置
with st.sidebar:
    st.header("⚙️ 配置")

    # LLM 选择
    provider = st.selectbox(
        "LLM 提供商",
        ["anthropic", "moonshot", "qwen"],
        format_func=lambda x: {
            "anthropic": "Claude (Anthropic)",
            "moonshot": "Kimi (Moonshot)",
            "qwen": "Qwen (通义千问)"
        }[x]
    )

    api_key = st.text_input("API Key", type="password")

    # 工具配置
    st.subheader("🛠️ 工具配置")
    use_docker = st.checkbox("使用 Docker 沙箱", value=False)
    enable_memory = st.checkbox("启用记忆系统", value=True)

    st.divider()

    # 记忆统计
    if enable_memory:
        st.subheader("💾 记忆统计")
        if st.button("刷新统计"):
            st.rerun()

# 初始化 session state
if "orchestrator" not in st.session_state:
    st.session_state.orchestrator = None
    st.session_state.workflow_result = None
    st.session_state.memory_manager = None

# 主界面
tab1, tab2, tab3, tab4 = st.tabs(["📝 任务执行", "🧠 记忆浏览", "📊 工作流可视化", "📈 性能分析"])

with tab1:
    st.header("任务执行")

    # 任务输入
    task_input = st.text_area(
        "输入开发任务",
        placeholder="例如：创建一个 TODO 应用，支持添加、删除、标记完成任务",
        height=150
    )

    col1, col2 = st.columns([1, 4])

    with col1:
        execute_btn = st.button("🚀 执行工作流", type="primary", use_container_width=True)

    with col2:
        if st.session_state.workflow_result:
            st.success("✓ 工作流已完成")

    # 执行工作流
    if execute_btn and task_input and api_key:
        with st.spinner("正在执行工作流..."):
            # 初始化系统
            orchestrator = Orchestrator()

            # 注册 agents
            orchestrator.register_agent(ArchitectAgent())
            orchestrator.register_agent(DeveloperAgent())
            orchestrator.register_agent(TesterAgent())
            orchestrator.register_agent(ReviewerAgent())

            # 注册工具
            orchestrator.register_tools(
                code_executor=CodeExecutor(use_docker=use_docker),
                code_analyzer=CodeAnalyzer(),
                linter=Linter()
            )

            # 设置记忆系统
            if enable_memory:
                memory_manager = MemoryManager(persist_dir="./data/chroma")
                experience_memory = ExperienceMemory(persist_dir="./data/chroma")
                orchestrator.set_memory(memory_manager, experience_memory)
                st.session_state.memory_manager = memory_manager

            # 设置 LLM
            try:
                llm_client = LLMFactory.create_client(
                    provider=LLMProvider(provider),
                    api_key=api_key
                )

                for agent in orchestrator.agents.values():
                    agent.set_llm_client(llm_client)

                # 执行工作流
                result = asyncio.run(orchestrator.execute_workflow(task_input))

                st.session_state.orchestrator = orchestrator
                st.session_state.workflow_result = result

                st.rerun()

            except Exception as e:
                st.error(f"执行失败: {str(e)}")

    elif execute_btn and not api_key:
        st.warning("请先在侧边栏配置 API Key")

    # 显示结果
    if st.session_state.workflow_result:
        result = st.session_state.workflow_result

        st.divider()

        # 总体状态
        col1, col2, col3 = st.columns(3)

        with col1:
            status = "✅ 成功" if result["success"] else "❌ 失败"
            st.metric("执行状态", status)

        with col2:
            st.metric("执行阶段", len(result["phases"]))

        with col3:
            review = result.get("final_output", {}).get("review", {})
            score = review.get("score", 0)
            st.metric("代码质量", f"{score}/100")

        # 各阶段详情
        st.subheader("📋 执行阶段")

        for i, phase in enumerate(result["phases"], 1):
            with st.expander(f"阶段 {i}: {phase['name'].upper()}", expanded=(i == len(result["phases"]))):
                st.markdown(f"**结果:**")
                st.text_area(
                    f"phase_{i}_result",
                    value=phase["result"][:1000] + "..." if len(phase["result"]) > 1000 else phase["result"],
                    height=200,
                    label_visibility="collapsed"
                )

        # 最终输出
        if result.get("final_output"):
            st.subheader("📦 最终输出")

            output = result["final_output"]

            # 代码文件
            if output.get("code_files"):
                st.markdown("**生成的代码:**")
                for file in output["code_files"]:
                    with st.expander(f"📄 {file.get('path', 'unknown')}"):
                        st.code(file.get("content", ""), language="python")

            # 测试文件
            if output.get("test_files"):
                st.markdown("**测试用例:**")
                for file in output["test_files"]:
                    with st.expander(f"🧪 {file.get('path', 'unknown')}"):
                        st.code(file.get("content", ""), language="python")

            # 审查结果
            if output.get("review"):
                st.markdown("**代码审查:**")
                review = output["review"]

                col1, col2 = st.columns(2)

                with col1:
                    st.metric("质量分数", f"{review.get('score', 0)}/100")

                with col2:
                    issues = review.get("issues", [])
                    st.metric("问题数量", len(issues))

                if issues:
                    st.markdown("**发现的问题:**")
                    for issue in issues:
                        severity_color = {
                            "high": "🔴",
                            "medium": "🟡",
                            "low": "🟢"
                        }.get(issue.get("severity", "low"), "⚪")

                        st.markdown(f"{severity_color} **[{issue.get('category')}]** {issue.get('description')}")
                        st.caption(f"建议: {issue.get('suggestion')}")

with tab2:
    st.header("🧠 记忆浏览")

    if st.session_state.memory_manager:
        memory_manager = st.session_state.memory_manager

        # 搜索记忆
        search_query = st.text_input("搜索记忆", placeholder="输入关键词...")

        if search_query:
            with st.spinner("搜索中..."):
                results = asyncio.run(memory_manager.search(
                    search_query,
                    use_long_term=True,
                    top_k=10
                ))

                st.markdown(f"找到 **{len(results)}** 条相关记忆")

                for i, mem in enumerate(results, 1):
                    with st.expander(f"记忆 {i} - {mem.metadata.get('type', 'unknown')}"):
                        st.markdown(f"**时间:** {mem.timestamp}")
                        st.markdown(f"**内容:**")
                        st.text(mem.content)
                        st.json(mem.metadata)

        # 记忆统计
        st.divider()
        st.subheader("📊 统计信息")

        stats = memory_manager.get_stats()

        col1, col2 = st.columns(2)

        with col1:
            st.metric("短期记忆", f"{stats['short_term']['count']} 条")

        with col2:
            st.metric("长期记忆", f"{stats['long_term']['total_memories']} 条")

        # 最近的记忆
        st.subheader("🕐 最近记忆")
        recent = memory_manager.short_term.get_recent(n=5)

        for mem in recent:
            st.markdown(f"**{mem.timestamp.strftime('%H:%M:%S')}** - {mem.metadata.get('type', 'unknown')}")
            st.caption(mem.content[:100] + "..." if len(mem.content) > 100 else mem.content)

    else:
        st.info("记忆系统未启用，请在侧边栏启用并执行任务")

with tab3:
    st.header("📊 工作流可视化")

    if st.session_state.workflow_result:
        result = st.session_state.workflow_result

        # 工作流时间线
        st.subheader("⏱️ 执行时间线")

        phases = result["phases"]

        # 使用 Streamlit 的进度展示
        for i, phase in enumerate(phases):
            progress = (i + 1) / len(phases)
            st.progress(progress, text=f"{phase['name'].upper()}")

        # 阶段流程图
        st.subheader("🔄 阶段流程")

        flow_diagram = """
        ```mermaid
        graph LR
            A[需求输入] --> B[架构设计]
            B --> C[代码实现]
            C --> D[测试生成]
            D --> E[代码审查]
            E --> F{质量检查}
            F -->|分数 < 80| G[迭代改进]
            G --> E
            F -->|分数 >= 80| H[完成]
        ```
        """
        st.markdown(flow_diagram)

        # 各阶段详情
        st.subheader("📝 阶段详情")

        for phase in phases:
            st.markdown(f"**{phase['name'].upper()}**")
            st.progress(1.0)

    else:
        st.info("请先在「任务执行」标签页执行工作流")

with tab4:
    st.header("📈 性能分析")

    if st.session_state.workflow_result:
        result = st.session_state.workflow_result

        # Token 使用统计（如果有）
        st.subheader("💰 Token 使用")
        st.info("Token 统计功能开发中...")

        # 代码质量趋势
        st.subheader("📊 代码质量")

        review = result.get("final_output", {}).get("review", {})
        score = review.get("score", 0)

        # 质量分布
        import plotly.graph_objects as go

        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=score,
            title={'text': "代码质量分数"},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [0, 50], 'color': "lightgray"},
                    {'range': [50, 80], 'color': "gray"},
                    {'range': [80, 100], 'color': "lightgreen"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 80
                }
            }
        ))

        st.plotly_chart(fig, use_container_width=True)

        # 问题分布
        issues = review.get("issues", [])
        if issues:
            st.subheader("⚠️ 问题分布")

            severity_counts = {}
            for issue in issues:
                severity = issue.get("severity", "unknown")
                severity_counts[severity] = severity_counts.get(severity, 0) + 1

            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("🔴 High", severity_counts.get("high", 0))
            with col2:
                st.metric("🟡 Medium", severity_counts.get("medium", 0))
            with col3:
                st.metric("🟢 Low", severity_counts.get("low", 0))

    else:
        st.info("请先在「任务执行」标签页执行工作流")

# 底部信息
st.divider()
st.caption("AutoDev v0.1.0 | 多 Agent 协作系统 | GitHub: leeleelxl/autodev-agent")
