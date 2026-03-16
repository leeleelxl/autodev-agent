# AutoDev - 自主软件开发 Agent 系统

## 🎯 项目概述

AutoDev 是一个基于多 Agent 协作的自主软件开发系统，通过 5 个专业 Agent 的协作，实现从需求分析到代码实现、测试、审查的完整自动化开发流程。

**项目地址**: https://github.com/leeleelxl/autodev-agent

## ✨ 核心特性

### 1. 多 Agent 协作架构
- **Architect Agent** - 需求分析、技术选型、架构设计
- **Developer Agent** - 代码实现、自动分析、质量检查
- **Tester Agent** - 测试用例生成、自动执行
- **Reviewer Agent** - 代码审查、问题识别、改进建议
- **Orchestrator** - 工作流编排、上下文管理、迭代优化

### 2. 三层 Memory 系统
- **短期记忆** - 当前会话的临时记忆（100 条）
- **长期记忆** - ChromaDB 向量数据库持久化存储
- **经验学习** - 从成功和失败中学习，积累最佳实践

### 3. 完整的 Tools 工具集
- **CodeExecutor** - 代码执行器（本地/Docker 沙箱）
- **CodeAnalyzer** - AST 代码分析（函数、类、复杂度）
- **Linter** - Pylint 代码质量检查（0-10 分）

### 4. 多 LLM 支持
- **Claude** (Anthropic) - 推理能力强
- **Kimi** (Moonshot) - 中文友好
- **Qwen** (通义千问) - 国产模型
- 支持为不同 Agent 配置不同的 LLM

### 5. Web UI 界面
- **Streamlit** 可视化界面
- 4 个功能 Tab：任务执行、记忆浏览、工作流可视化、性能分析
- 实时显示工作流进度
- 代码质量可视化

## 🏗️ 系统架构

```
用户输入
    ↓
Orchestrator（编排器）
    ↓
┌─────────────────────────────────────┐
│  Phase 1: 架构设计                   │
│  Architect Agent                    │
│  - 需求分析                          │
│  - 技术选型                          │
│  - 架构设计                          │
└─────────────────────────────────────┘
    ↓ (设计文档)
┌─────────────────────────────────────┐
│  Phase 2: 代码实现                   │
│  Developer Agent + Tools            │
│  - 代码生成                          │
│  - CodeAnalyzer 分析                │
│  - Linter 质量检查                   │
└─────────────────────────────────────┘
    ↓ (代码文件)
┌─────────────────────────────────────┐
│  Phase 3: 测试生成                   │
│  Tester Agent + CodeExecutor        │
│  - 测试用例生成                      │
│  - 自动执行测试                      │
└─────────────────────────────────────┘
    ↓ (测试结果)
┌─────────────────────────────────────┐
│  Phase 4: 代码审查                   │
│  Reviewer Agent + Tools             │
│  - 工具自动分析                      │
│  - LLM 综合审查                     │
│  - 评分和建议                        │
└─────────────────────────────────────┘
    ↓ (审查报告)
┌─────────────────────────────────────┐
│  Phase 5: 迭代改进（如需要）         │
│  Developer Agent                    │
│  - 修复问题                          │
│  - 优化代码                          │
└─────────────────────────────────────┘
    ↓
最终输出（代码 + 测试 + 文档）
```

## 📊 测试验证

### 测试结果（2025-01-19）
- ✅ 单个 Agent 测试通过
- ✅ 完整工作流测试通过
- ✅ Memory 系统正常
- ✅ Tools 集成正常
- ✅ 代码质量: 80/100

### 性能指标
- 执行时间: 60-90 秒
- 代码质量: 80/100
- 成功率: 100%

## 🚀 快速开始

### 1. 安装依赖
```bash
git clone https://github.com/leeleelxl/autodev-agent.git
cd autodev-agent
pip install -r requirements.txt
```

### 2. 配置 API Key
```bash
cp .env.example .env
# 编辑 .env 填入你的 API Key
```

### 3. 运行测试
```bash
# 简单测试
python test_simple.py

# 完整工作流
python test_quick.py

# Web UI
streamlit run app_demo.py
```

### 4. 运行主程序
```bash
python main.py
```

## 📁 项目结构

```
autodev-agent/
├── src/
│   ├── agents/          # Agent 系统
│   ├── llm/             # LLM 客户端
│   ├── memory/          # Memory 系统
│   ├── tools/           # Tools 工具集
│   └── utils/           # 工具函数
├── experiments/         # Baseline 实验
├── tests/               # 单元测试
├── docs/                # 文档
├── app.py               # Web UI（完整版）
├── app_simple.py        # Web UI（简化版）
├── app_demo.py          # Web UI（演示版）
├── main.py              # 命令行入口
└── test_quick.py        # 快速测试
```

## 🎓 技术亮点

### 1. 创新的多 Agent 协作
- 分工明确，各司其职
- 自动上下文传递
- 智能迭代改进

### 2. 三层 Memory 架构
- 短期记忆（会话级）
- 长期记忆（向量数据库）
- 经验学习（成功/失败案例）

### 3. 自动化质量保证
- 代码生成后自动分析
- 自动执行测试
- 自动代码审查
- 基于评分的自动改进

### 4. 工具深度集成
- CodeExecutor（沙箱执行）
- CodeAnalyzer（AST 分析）
- Linter（质量检查）

## 📈 Baseline 对比实验

### 实验设计
- **对比对象**: GPT Engineer, Single LLM
- **测试任务**: 15 个（简单/中等/复杂）
- **评估指标**: 成功率、代码质量、测试覆盖、Token 效率

### 预期优势
- 代码质量: +15-20% vs GPT Engineer
- 测试覆盖: +25-30% vs Single LLM
- 首次成功率: +10-15% vs GPT Engineer

## 📚 文档

- [LLM 提供商配置](docs/LLM_PROVIDERS.md)
- [Memory 系统使用](docs/MEMORY_GUIDE.md)
- [Tools 工具集](docs/TOOLS_GUIDE.md)
- [Web UI 使用](docs/WEB_UI_GUIDE.md)
- [Baseline 实验](docs/BASELINE_EXPERIMENT.md)
- [测试报告](TEST_REPORT.md)

## 🎯 适用场景

- 简历项目展示
- Agent 实习申请
- 技术博客素材
- 开源项目贡献
- 学术研究

## 📝 License

MIT License

## 👤 作者

[Your Name]

---

**最后更新**: 2025-01-19
**项目状态**: ✅ 生产就绪
**测试状态**: ✅ 所有测试通过
