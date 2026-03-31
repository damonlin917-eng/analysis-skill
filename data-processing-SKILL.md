---
name: data-processing
description: 数据处理 Skill。负责读取 Excel/CSV 文件、执行 SQL 查询、生成统计摘要。支持多文件 JOIN，结果输出到缓存目录供 Diagnostic 分析使用。不负责业务理解，只负责高效准确地处理数据请求。
---

# Data Processing Skill

## Overview

这是数据分析体系的**数据处理层**，负责：
- 读取和解析 Excel/CSV 文件
- 执行 SQL 查询和统计计算
- 将结果输出到缓存目录
- 支持与 Diagnostic Skill 协作

## 核心定位

| 定位 | 说明 |
|------|------|
| **只做数据处理** | 不理解业务含义，只处理数据 |
| **结果导向** | 输出结构化数据，不输出分析 |
| **缓存输出** | 结果写到缓存，不留在上下文 |

## 与 Main Skill 的协作

### 输入

- 数据文件路径
- 查询需求（SQL 或统计目标）
- 输出缓存路径

### 输出

- JSON/CSV 格式的处理结果
- 关键指标摘要（供 Diagnostic 读取）

## 核心能力

### 1. 文件读取

支持格式：
- Excel (.xlsx, .xls)
- CSV (.csv)

**多文件支持**：
- 多个 Excel 文件 → 多个 sheet
- Excel + CSV → 统一表空间
- 支持跨文件 JOIN

### 2. SQL 查询

```bash
# 基础查询
python /mnt/skills/public/data-processing/scripts/process.py \
  --files /mnt/user-data/uploads/data.xlsx \
  --action query \
  --sql "SELECT region, SUM(sales) FROM orders GROUP BY region"

# 复杂查询
python /mnt/skills/public/data-processing/scripts/process.py \
  --files /mnt/user-data/uploads/*.xlsx \
  --action query \
  --sql "SELECT o.*, c.customer_name FROM orders o JOIN customers c ON o.customer_id = c.id"
```

### 3. 统计摘要

```bash
# 基础统计
python /mnt/skills/public/data-processing/scripts/process.py \
  --files /mnt/user-data/uploads/data.xlsx \
  --action summary \
  --table Sheet1

# 输出到缓存
python /mnt/skills/public/data-processing/scripts/process.py \
  --files /mnt/user-data/uploads/data.xlsx \
  --action summary \
  --table Sheet1 \
  --output /mnt/user-data/workspace/.analysis-cache/session_001/summary.json
```

### 4. 数据导出

支持格式：
- `.json` - JSON 数组
- `.csv` - CSV 文件
- `.md` - Markdown 表格

## 命令参数

| 参数 | 必填 | 说明 |
|------|------|------|
| `--files` | 是 | 文件路径，支持空格分隔多文件 |
| `--action` | 是 | `inspect`/`query`/`summary`/`export` |
| `--sql` | query 时 | SQL 查询语句 |
| `--table` | summary 时 | 表/Sheet 名称 |
| `--output` | 否 | 输出到缓存目录 |
| `--cache-key` | 否 | 缓存标识，用于关联多次查询 |

## 输出规范

### 查询结果输出

```json
{
  "cache_key": "q1_2024_sales",
  "sql": "SELECT region, SUM(sales) FROM orders WHERE period='Q1 2024' GROUP BY region",
  "row_count": 5,
  "columns": ["region", "total_sales"],
  "data": [
    {"region": "华东", "total_sales": 150000},
    {"region": "华南", "total_sales": 120000}
  ],
  "summary": {
    "total_sales": 270000,
    "avg_region": 135000,
    "top_region": "华东"
  }
}
```

### 统计摘要输出

```json
{
  "table": "orders",
  "metrics": {
    "sales": {
      "count": 1000,
      "mean": 5000,
      "std": 1500,
      "min": 100,
      "25%": 3000,
      "50%": 5000,
      "75%: 7000,
      "max": 20000,
      "null_count": 5
    },
    "region": {
      "count": 1000,
      "unique": 5,
      "top": "华东",
      "top_count": 300,
      "null_count": 0
    }
  }
}
```

## 缓存策略

### 缓存目录结构

```
/mnt/user-data/workspace/.analysis-cache/
└── session_{timestamp}/
    ├── query_{id}.json      # SQL 查询结果
    ├── summary_{id}.json   # 统计摘要
    └── manifest.json        # 本次分析的文件清单
```

### 缓存命名规则

| 类型 | 命名格式 | 示例 |
|------|----------|------|
| SQL 查询 | `query_{序号}_{关键标签}.json` | `query_01_q1_sales.json` |
| 统计摘要 | `summary_{表名}.json` | `summary_orders.json` |
| 导出数据 | `export_{名称}.csv` | `export_top_products.csv` |

### 缓存原则

1. **不缓存原始数据**：只缓存处理后的聚合结果
2. **关键指标优先**：count, sum, avg, top 等
3. **保留结构**：字段名、类型清晰

## 与 Diagnostic 协作

### 数据契约

当 Main Skill 调用 Diagnostic 时，传递：

```json
{
  "cache_dir": "/mnt/user-data/workspace/.analysis-cache/session_001/",
  "queries": [
    {"id": "q1", "file": "query_01_q1_sales.json"},
    {"id": "q2", "file": "query_02_region_compare.json"}
  ],
  "summary": "summary_orders.json",
  "goal": "分析华东区Q1销量下降原因"
}
```

### Diagnostic 需要的接口

Diagnostic 可以读取：
- `query_*.json` - 详细查询结果
- `summary_*.json` - 统计摘要
- `manifest.json` - 数据来源说明

## 错误处理

| 错误 | 处理方式 |
|------|----------|
| 文件不存在 | 返回错误，明确文件路径 |
| SQL 语法错误 | 返回错误，提示可能的问题 |
| 查询超时 | 限制返回行数，建议简化查询 |
| 内存不足 | 分批处理，减少 JOIN |

## 性能优化

### 大文件处理

- 使用 DuckDB 列式存储
- 避免一次性加载全量数据
- 超过 100MB 文件先采样再处理

### 频繁查询优化

- 相同文件的多次查询复用缓存
- 复杂聚合结果预计算

## 注意事项

1. **不输出业务分析**：只返回数据，不解读含义
2. **结果精简化**：不需要返回全部原始数据，聚合后输出
3. **类型保持**：数值类型保持数值，不要转成字符串
4. **NULL 处理**：明确标注 NULL 值，不要忽略

---

*本 Skill 是数据分析体系的执行层，核心价值在于高效准确地处理数据请求。*
