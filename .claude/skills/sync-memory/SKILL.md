---
name: sync-memory
description: 同步和审查当前对话的重要信息到 memory 系统
invocation: manual
---

# Memory 同步工具

执行以下步骤：

1. **审查当前对话**
   - 识别所有重要的决策、发现、问题和解决方案
   - 识别用户的新偏好或反馈
   - 识别项目的新进展或变化

2. **检查现有 memory**
   - 读取 `.claude/memory/MEMORY.md` 索引
   - 读取相关的现有 memory 文件
   - 判断是更新现有 memory 还是创建新的

3. **保存或更新 memory**
   - 按照 memory 类型（user/feedback/project/reference）分类
   - 使用规范的 frontmatter 格式
   - 更新 MEMORY.md 索引

4. **确认**
   - 列出保存的 memory 条目
   - 询问用户是否有遗漏

**使用场景：**
- 对话中做出重要决策后
- 完成一个功能模块后
- 遇到重要问题并解决后
- 对话即将结束时
