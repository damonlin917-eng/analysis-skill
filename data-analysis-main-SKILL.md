---
name: data-analysis-main
description: 数据分析主控 Skill。负责理解用户需求、判断分析阶段、调度子 Skill（数据处理/诊断分析）、验收分析结果。不直接参与数据处理和分析执行，只负责任务分配和结果验收。分析过程中的数据临时存储在缓存目录，分析完成后自动清理。
---

# Data Analysis Main Skill

## Overview

这是数据分析体系的**主控 Skill**，扮演仲裁者/调度员角色：
- 理解用户的数据分析需求
- 判断当前需要什么处理（数据处理 vs 诊断分析）
- 调度相应的子 Skill 执行具体任务
- 验收分析结果是否到位
- 管理分析过程中的临时缓存

## 核心设计原则

| 原则 | 说明 |
|------|------|
| **不直接处理数据** | 只调度子 Skill，不自己执行 SQL 或分析 |
| **按需调度** | 需要数据时调用 Data Processing，需要分析时调用 Diagnostic |
| **迭代验证** | 分析结果不够深入时，继续调度子 Skill 补充 |
| **缓存管理** | 临时数据存缓存，分析完成后清理 |

## 与子 Skill 的协作

### 子 Skill 1: data-processing

负责数据查询、清洗、统计。

**调用时机**：
- 用户需要了解数据情况
- 需要特定指标或统计结果
- 需要对比分析的基础数据

**调用方式**：
```
# 读取 data-processing skill 执行数据处理
python /mnt/skills/public/data-processing/scripts/process.py --files <path> --action query --sql "..."
```

### 子 Skill 2: diagnostic-analysis

负责业务分析、归因、建议。

**调用时机**：
- 用户问"为什么"
- 需要业务洞察
- 需要行动建议

**调用方式**：
```
# 读取 diagnostic-analysis skill 执行诊断分析
python /mnt/skills/public/diagnostic-analysis/scripts/analyze.py --input <缓存数据> --goal "分析目标"
```

## 工作流程

### Step 1: 理解需求

分析用户的问题，判断需要什么：

| 用户问题类型 | 需要调用的子 Skill |
|-------------|-------------------|
| "这个数据怎么样" | Data Processing |
| "有多少/占比多少" | Data Processing |
| "为什么下降" | Data Processing → Diagnostic |
| "应该怎么办" | Diagnostic |
| "分析一下" | Both (先 Data 再 Diagnostic) |

### Step 2: 调度执行

1. **调用 Data Processing**：
   - 传递具体的数据查询需求
   - 指定输出到缓存目录

2. **获取处理结果**：
   - 从缓存读取处理结果
   - 评估结果是否足够

3. **调用 Diagnostic**：
   - 传递分析目标 + 缓存数据
   - 明确需要什么洞察

### Step 3: 验收结果

判断分析是否到位：

**到位的标准**：
- 回答了用户的核心问题
- 有数据支撑
- 有明确的归因或建议
- 用户没有进一步追问

**不到位的情况**：
- 分析浮于表面
- 缺少关键数据
- 归因不清晰
- 没有可执行的建议

### Step 4: 清理缓存

分析完成后，清理临时缓存：
```bash
rm -rf /mnt/user-data/workspace/.analysis-cache/*
```

## 缓存管理

### 缓存目录结构

```
/mnt/user-data/workspace/.analysis-cache/
├── session_{timestamp}/
│   ├── data_query_1.json    # Data Processing 输出
│   ├── data_query_2.json    # Data Processing 输出
│   ├── diagnostic_1.json    # Diagnostic 输出
│   └── summary.md           # 分析摘要
```

### 缓存原则

- **按需写入**：只缓存关键结果，不缓存原始数据
- **可追溯**：每个缓存文件有清晰命名
- **及时清理**：分析完成后删除整个 session 目录

## Main Skill 输出格式

### 最终回答用户时

```markdown
## 分析结论

[核心发现]

## 数据支撑

[关键数据指标]

## 归因分析

[原因分析]

## 行动建议

[具体建议]
```

### 判断需要更多分析时

```markdown
需要进一步分析：
1. [缺失的数据点] → 调用 Data Processing
2. [需要深入的维度] → 调用 Diagnostic
```

## 决策树

```
用户输入
    ↓
判断问题类型
    ↓
┌─────────────────────────────────────┐
│  需要数据？                          │
│    ↓ 是                            │
│  调用 Data Processing               │
│    ↓                               │
│  结果够用？                         │
│    ├─ 是 → 继续或结束              │
│    └─ 否 → 返回"需要更多数据"      │
│                                      │
│  需要分析？                         │
│    ↓ 是                            │
│  调用 Diagnostic                    │
│    ↓                               │
│  分析到位？                         │
│    ├─ 是 → 返回最终答案            │
│    └─ 否 → 继续补充分析            │
└─────────────────────────────────────┘
```

## 注意事项

1. **不要假设**：不确定用户需求时，主动询问
2. **不要跳过数据**：分析必须有数据支撑，不能凭空猜测
3. **不要一次做满**：分步骤执行，每步验证
4. **保持上下文**：记住之前的分析进展，避免重复

## 错误处理

| 错误 | 处理方式 |
|------|----------|
| Data Processing 失败 | 重试或返回错误，明确告知用户 |
| Diagnostic 分析不清晰 | 补充调用，提供更具体的要求 |
| 缓存写入失败 | 警告用户，尝试继续执行 |
| 用户需求不明确 | 询问澄清，不要猜测 |

---

*本 Skill 是数据分析体系的协调层，核心价值在于合理调度和结果验收。*
