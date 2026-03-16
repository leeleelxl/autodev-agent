# AutoDev - 多 Agent 协作代码生成系统

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> 通过 5 个专业 Agent 的协作，实现从需求分析到代码实现、测试、审查的完整自动化流程

## 🎯 项目概述

AutoDev 是一个基于多 Agent 协作的代码生成系统，通过 Architect、Developer、Tester、Reviewer 和 Orchestrator 五个专业 Agent 的协作，生成高质量、模块化、可维护的代码。

**核心特性**：
- 🤖 5 个专业 Agent 协作
- ✅ 自动测试生成（100% 覆盖）
- 🔍 自动代码审查（平均识别 9.6 个问题）
- 📊 质量评分系统（平均 66.4/100）
- 🏗️ Clean Architecture 设计

## 📊 实验结果

在 5 个不同复杂度的任务上对比 Single LLM：

| 任务 | Single LLM | AutoDev | 优势 |
|------|-----------|---------|------|
| 计算器 | 1文件/85行 | 2文件/300行 | 测试+质量 |
| TODO | 1文件/144行 | 5文件/304行 | 模块化 |
| 认证 | 1文件/222行 | 16文件/527行 | Clean Arch |
| API | 1文件/224行 | 14文件/564行 | 可维护 |
| 爬虫 | 1文件/143行 | 9文件/318行 | 分层设计 |

**关键数据**：
- 平均生成 **9.2 个模块化文件** vs 1 个
- **100% 测试覆盖** vs 0%
- 平均识别 **9.6 个潜在问题** vs 0 个
- 质量评分 **66.4/100**

详细报告：[多任务对比实验](docs/reports/MULTI_TASK_REPORT.md)

## 🚀 快速开始

### 安装

```bash
git clone https://github.com/leeleelxl/autodev-agent.git
cd autodev-agent
pip install -r requirements.txt
```

### 配置

```bash
cp .env.example .env
# 编辑 .env 填入你的 API Key
```

### 运行

```bash
# 命令行模式
python main.py

# Web UI 模式
streamlit run examples/app_demo.py

# 运行实验
python tests/test_multi_task.py
```

## 📁 项目结构

```
autodev-agent/
├── src/                    # 核心代码
│   ├── agents/            # 5 个 Agent
│   ├── llm/               # LLM 客户端
│   ├── memory/            # Memory 系统
│   ├── tools/             # Tools 工具集
│   └── utils/             # 工具函数
├── docs/                   # 文档
│   ├── reports/           # 实验报告
│   └── guides/            # 使用指南
├── experiments/            # 实验相关
│   ├── results/           # 实验结果
│   └── baselines/         # Baseline 代码
├── examples/               # 示例代码
├── tests/                  # 测试文件
├── main.py                 # 命令行入口
└── README.md               # 本文件
```

## 🏗️ 系统架构

```
用户输入
    ↓
Orchestrator（编排器）
    ↓
┌─────────────────────────────────────┐
│  Phase 1: 架构设计                   │
│  Architect Agent                    │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│  Phase 2: 代码实现                   │
│  Developer Agent + Tools            │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│  Phase 3: 测试生成                   │
│  Tester Agent + CodeExecutor        │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│  Phase 4: 代码审查                   │
│  Reviewer Agent + Tools             │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│  Phase 5: 迭代改进                   │
│  Developer Agent                    │
└─────────────────────────────────────┘
    ↓
最终输出（代码 + 测试 + 文档）
```

## 📚 文档

- [多任务对比实验报告](docs/reports/MULTI_TASK_REPORT.md)
- [详细对比分析](docs/reports/FINAL_COMPARISON.md)
- [诚实评估报告](docs/reports/HONEST_EVALUATION.md)
- [演示指南](docs/guides/DEMO_GUIDE.md)
- [项目概述](docs/guides/PROJECT_SUMMARY.md)

## 🎓 技术亮点

### 1. Markdown 代码块 > JSON

**问题**：JSON 格式不可靠，LLM 经常生成语法错误

**解决方案**：采用 Markdown 代码块（参考 Cursor、Aider）

**结果**：成功率从 50% 提升到 100%

### 2. 代码完整性检查

自动检测缺失依赖，警告缺少的模块

### 3. 迭代改进机制

Phase 5 自动修复问题，质量评分驱动

## 🔬 对比实验

### vs Single LLM

| 指标 | Single LLM | AutoDev | 差距 |
|------|-----------|---------|------|
| 平均文件数 | 1.0 | 9.2 | **9.2x** |
| 测试覆盖 | 0% | 100% | **+100%** |
| 问题识别 | 0 | 9.6 | **+9.6** |
| 质量评分 | ? | 66.4/100 | **可量化** |

### vs GPT Engineer

*正在进行中...*

## 🎯 适用场景

### ✅ 推荐使用
- 生产环境项目
- 团队协作开发
- 长期维护的项目
- 复杂业务逻辑

### ❌ 不推荐使用
- 快速原型
- 简单脚本
- 一次性任务

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📝 License

MIT License

## 👤 作者

[Your Name]

---

**最后更新**: 2025-01-19
