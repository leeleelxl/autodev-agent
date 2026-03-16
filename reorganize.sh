#!/bin/bash

# 创建新的目录结构
mkdir -p docs/reports
mkdir -p docs/guides
mkdir -p experiments/results
mkdir -p experiments/baselines
mkdir -p examples
mkdir -p tests

# 移动文档
mv MULTI_TASK_REPORT.md docs/reports/ 2>/dev/null
mv FINAL_COMPARISON.md docs/reports/ 2>/dev/null
mv HONEST_EVALUATION.md docs/reports/ 2>/dev/null
mv TEST_REPORT.md docs/reports/ 2>/dev/null

mv DEMO_GUIDE.md docs/guides/ 2>/dev/null
mv PROJECT_SUMMARY.md docs/guides/ 2>/dev/null

# 移动实验结果
mv multi_task_results.json experiments/results/ 2>/dev/null
mv autodev_generated experiments/results/ 2>/dev/null

# 移动 baseline 代码
mv baseline_single_llm.py experiments/baselines/ 2>/dev/null
mv baseline_clean.py experiments/baselines/ 2>/dev/null
mv autodev_output.py experiments/baselines/ 2>/dev/null

# 移动示例代码
mv example_calculator.py examples/ 2>/dev/null
mv generated_calculator.py examples/ 2>/dev/null

# 移动测试文件
mv test_*.py tests/ 2>/dev/null

# 移动 app 文件到 examples
mv app_demo.py examples/ 2>/dev/null
mv app_simple.py examples/ 2>/dev/null
mv app.py examples/ 2>/dev/null

echo "✓ 文件整理完成"
