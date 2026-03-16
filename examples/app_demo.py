"""
最简化测试版 - 无需完整依赖

用于快速测试 UI 布局
"""

import streamlit as st

st.set_page_config(page_title="AutoDev", page_icon="🤖", layout="wide")

st.title("🤖 AutoDev - AI Agent 开发系统")
st.markdown("多 Agent 协作的代码生成系统")

# 侧边栏
with st.sidebar:
    st.header("⚙️ 配置")

    provider = st.selectbox(
        "LLM 提供商",
        ["anthropic", "moonshot", "qwen"],
        format_func=lambda x: {
            "anthropic": "Claude (Anthropic)",
            "moonshot": "Kimi (Moonshot)",
            "qwen": "Qwen (通义千问)"
        }[x]
    )

    api_key = st.text_input("API Key", type="password", placeholder="输入你的 API Key")

    st.divider()

    st.subheader("🛠️ 工具配置")
    use_docker = st.checkbox("使用 Docker 沙箱", value=False)
    enable_memory = st.checkbox("启用记忆系统", value=True)

    st.divider()

    if enable_memory:
        st.subheader("💾 记忆统计")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("短期", "0")
        with col2:
            st.metric("长期", "0")

# 主界面
tab1, tab2, tab3, tab4 = st.tabs(["📝 任务执行", "🧠 记忆浏览", "📊 工作流可视化", "📈 性能分析"])

with tab1:
    st.header("任务执行")

    task_input = st.text_area(
        "输入开发任务",
        placeholder="例如：创建一个 TODO 应用，支持添加、删除、标记完成任务",
        height=150
    )

    col1, col2 = st.columns([1, 4])

    with col1:
        execute_btn = st.button("🚀 执行工作流", type="primary", use_container_width=True)

    if execute_btn:
        if not api_key:
            st.warning("⚠️ 请先在侧边栏配置 API Key")
        elif not task_input:
            st.warning("⚠️ 请输入开发任务")
        else:
            # 模拟执行
            with st.spinner("正在执行工作流..."):
                import time
                time.sleep(2)

            st.success("✅ 工作流执行完成（演示模式）")

            # 显示模拟结果
            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("执行状态", "✅ 成功")
            with col2:
                st.metric("执行阶段", "5")
            with col3:
                st.metric("代码质量", "85/100")

            st.divider()

            # 模拟阶段
            st.subheader("📋 执行阶段")

            phases = [
                ("ARCHITECTURE", "架构设计完成"),
                ("DEVELOPMENT", "代码实现完成"),
                ("TESTING", "测试用例生成完成"),
                ("REVIEW", "代码审查完成"),
                ("IMPROVEMENT", "代码优化完成")
            ]

            for i, (name, desc) in enumerate(phases, 1):
                with st.expander(f"阶段 {i}: {name}", expanded=(i == 1)):
                    st.info(desc)
                    st.code(f"# {name} 阶段的输出\nprint('Hello, World!')", language="python")

            st.divider()

            # 模拟代码输出
            st.subheader("📦 最终输出")

            st.markdown("**生成的代码:**")
            with st.expander("📄 todo_app.py"):
                st.code("""
class TodoApp:
    def __init__(self):
        self.tasks = []

    def add_task(self, task):
        self.tasks.append({"task": task, "done": False})

    def remove_task(self, index):
        if 0 <= index < len(self.tasks):
            self.tasks.pop(index)

    def mark_done(self, index):
        if 0 <= index < len(self.tasks):
            self.tasks[index]["done"] = True

if __name__ == "__main__":
    app = TodoApp()
    app.add_task("学习 Python")
    print(app.tasks)
""", language="python")

            st.markdown("**代码审查:**")
            col1, col2 = st.columns(2)
            with col1:
                st.metric("质量分数", "85/100")
            with col2:
                st.metric("问题数量", "2")

with tab2:
    st.header("记忆浏览")

    search_query = st.text_input("🔍 搜索记忆", placeholder="输入关键词搜索...")

    if st.button("搜索"):
        st.info("演示模式：显示模拟记忆")

        memories = [
            {"type": "architecture", "content": "设计了一个 MVC 架构的 Web 应用"},
            {"type": "code", "content": "实现了用户认证功能"},
            {"type": "success", "content": "成功完成了 REST API 开发"}
        ]

        for mem in memories:
            with st.expander(f"[{mem['type']}] {mem['content'][:50]}..."):
                st.text(mem['content'])

with tab3:
    st.header("工作流可视化")

    st.subheader("执行时间线")

    phases = ["架构设计", "代码实现", "测试生成", "代码审查", "迭代改进"]
    progress = [100, 100, 100, 100, 80]

    for phase, prog in zip(phases, progress):
        st.text(phase)
        st.progress(prog / 100)

    st.divider()

    st.subheader("工作流程图")
    st.code("""
graph LR
    A[需求输入] --> B[架构设计]
    B --> C[代码实现]
    C --> D[测试生成]
    D --> E[代码审查]
    E --> F{质量检查}
    F -->|通过| G[完成]
    F -->|不通过| C
""", language="mermaid")

with tab4:
    st.header("性能分析")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("总执行时间", "2.5 分钟")
    with col2:
        st.metric("Token 使用", "15,234")
    with col3:
        st.metric("成功率", "100%")

    st.divider()

    st.subheader("代码质量分布")

    import random

    # 模拟图表数据
    st.bar_chart({
        "架构设计": 90,
        "代码实现": 85,
        "测试覆盖": 80,
        "代码规范": 88
    })

st.sidebar.markdown("---")
st.sidebar.caption("AutoDev v0.1.0")
