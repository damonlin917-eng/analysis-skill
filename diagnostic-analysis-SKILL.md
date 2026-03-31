---
name: diagnostic-analysis
description: 诊断分析 Skill。负责业务理解、归因分析、异常检测、对比分析和行动建议。不直接读取原始数据，而是读取 Data Processing 处理后的缓存结果，结合企业知识进行深度分析。分析结果供 Main Skill 最终呈现给用户。
---

# Diagnostic Analysis Skill

## Overview

这是数据分析体系的**诊断分析层**，负责：
- 理解业务含义（不只是看数字）
- 归因分析（为什么发生变化）
- 异常检测（发现数据中的异常点）
- 对比分析（与同期/目标/竞品对比）
- 行动建议（基于分析给出具体建议）

## 核心定位

| 定位 | 说明 |
|------|------|
| **业务理解优先** | 理解数据背后的业务含义 |
| **缓存数据输入** | 不读取原始数据，只读处理后的结果 |
| **分析+建议输出** | 不仅分析原因，还给出行动建议 |

## 与 Main Skill 的协作

### 输入

- 缓存目录路径
- 分析目标（用户的问题）
- 可选：企业知识（业务术语、规则）

### 输出

- 分析报告（JSON 格式）
- 归因分析
- 行动建议

## 核心能力

### 1. 业务语义理解

**能力说明**：
- 理解列名的业务含义
- 识别业务指标（KPI、行业术语）
- 连接数据与业务上下文

**实现方式**：
```json
// 输入：数据列名
["sales", "region", "period", "customer_type"]

// 输出：语义理解
{
  "sales": {"type": "金额", "business_meaning": "销售收入"},
  "region": {"type": "区域", "business_meaning": "销售区域"},
  "period": {"type": "时间", "business_meaning": "统计周期"},
  "customer_type": {"type": "分类", "business_meaning": "客户类型"}
}
```

### 2. 归因分析

**能力说明**：
- 分析指标变化的原因
- 识别关键影响因素
- 区分主因和次因

**分析方法**：

| 方法 | 适用场景 |
|------|----------|
| 相关性分析 | 多因素影响时，找出相关性最强的因素 |
| 分层分析 | 复杂数据时，按维度拆解（地区→产品→客户） |
| 对比分析 | 与历史/目标对比，找出差异点 |
| 异常聚焦 | 找出异常值，重点分析 |

**输出格式**：
```json
{
  "analysis_type": "归因分析",
  "target": "华东区Q3销量下降原因",
  "key_findings": [
    {
      "factor": "客户流失",
      "impact": "贡献下降的40%",
      "evidence": "Q3新客户数量下降30%，老客户复购率下降15%"
    },
    {
      "factor": "竞品冲击",
      "impact": "贡献下降的35%",
      "evidence": "竞品A在华东区推出低价策略，市场份额上升5%"
    },
    {
      "factor": "产品结构",
      "impact": "贡献下降的25%",
      "evidence": "高毛利产品销量占比下降10%"
    }
  ],
  "confidence": "高"
}
```

### 3. 异常检测

**能力说明**：
- 自动发现数据中的异常点
- 识别趋势异常、点异常、模式异常

**检测规则**：

| 异常类型 | 检测方法 | 示例 |
|----------|----------|------|
| 数值异常 | 超过 3σ 或 IQR*1.5 | 单日销量异常高 |
| 趋势异常 | 斜率突变 | 连续增长突然下降 |
| 分布异常 | 与历史分布差异大 | 某区域占比异常 |
| 模式异常 | 偏离典型模式 | 周末销量异常低于工作日 |

**输出格式**：
```json
{
  "analysis_type": "异常检测",
  "target": "orders 表全量数据",
  "anomalies": [
    {
      "type": "数值异常",
      "location": "华东区 2024-08-15",
      "description": "单日销量 50000，是日均的 5 倍",
      "severity": "高"
    },
    {
      "type": "趋势异常",
      "location": "华南区 Q3",
      "description": "连续 3 个月环比下降超过 20%",
      "severity": "中"
    }
  ]
}
```

### 4. 对比分析

**能力说明**：
- 与历史同期对比
- 与目标对比
- 与竞品/行业对比
- 维度间对比

**对比维度**：

| 对比类型 | 数据来源 | 分析重点 |
|----------|----------|----------|
| 同期对比 | 去年同周期 | 增长/下降幅度 |
| 环比对比 | 上个周期 | 变化趋势 |
| 目标对比 | 预设目标 | 完成率 |
| 维度对比 | 内部维度（区域/产品） | 差异分布 |

**输出格式**：
```json
{
  "analysis_type": "对比分析",
  "target": "华东区 Q3 销售",
  "comparisons": [
    {
      "type": "同期对比",
      "baseline": "华东区 Q3 2023",
      "current": "华东区 Q3 2024",
      "change_pct": -15%,
      "detail": "销量从 10000 下降到 8500",
      "assessment": "显著下降"
    },
    {
      "type": "目标对比",
      "baseline": "Q3 目标 10000",
      "current": "实际 8500",
      "achievement_rate": "85%",
      "gap": "1500",
      "assessment": "未达标"
    },
    {
      "type": "区域对比",
      "baseline": "华南区 Q3",
      "current": "华东区 Q3",
      "difference": "华东比华南低 20%",
      "assessment": "落后"
    }
  ]
}
```

### 5. 行动建议

**能力说明**：
- 基于分析结果给出具体建议
- 区分短期/中期/长期
- 建议需要可执行

**输出格式**：
```json
{
  "analysis_type": "行动建议",
  "target": "华东区 Q3 销量下降",
  "recommendations": [
    {
      "priority": "高",
      "horizon": "短期",
      "action": "启动客户流失预警",
      "detail": "对 Q3 未复购客户进行一对一沟通，识别流失原因",
      "expected_impact": "预计挽回 10% 流失客户"
    },
    {
      "priority": "中",
      "horizon": "中期",
      "action": "调整产品组合",
      "detail": "增加高毛利产品推广力度，优化产品结构",
      "expected_impact": "预计提升毛利率 5%"
    },
    {
      "priority": "低",
      "horizon": "长期",
      "action": "竞品监控体系",
      "detail": "建立竞品价格和策略监控机制",
      "expected_impact": "提前应对市场变化"
    }
  ]
}
```

## 与 Data Processing 协作

### 数据契约

Data Processing 输出到缓存的数据，Diagnostic 读取：

```
缓存目录/
├── query_01_q1_sales.json    # 详细查询结果
├── query_02_region.json      # 区域对比数据
├── summary_orders.json       # 统计摘要
└── manifest.json             # 数据来源说明
```

### 数据读取方式

```python
# 伪代码
def read_cache(cache_dir):
    results = {}
    for file in os.listdir(cache_dir):
        if file.endswith('.json'):
            results[file] = json.load(open(os.path.join(cache_dir, file)))
    return results
```

## 企业知识（可选输入）

如果用户提供了企业知识，Diagnostic 可以：

```json
{
  "business_glossary": {
    "sales": "含税销售额",
    "customer_type": {"A": "战略客户", "B": "重点客户", "C": "普通客户"}
  },
  "business_rules": {
    "正常毛利率": ">20%",
    "客户流失标准": "90天未下单"
  },
  "industry_context": {
    "行业特点": "季节性明显，Q3为淡季",
    "竞争格局": "前三名占据60%市场份额"
  }
}
```

## 分析结果输出

### 完整分析报告

```json
{
  "analysis_id": "session_001_analysis_01",
  "goal": "分析华东区Q3销量下降原因",
  "timestamp": "2026-03-31T23:00:00",
  
  "semantic_understanding": { ... },
  
  "findings": {
    "basic_stats": { ... },
    "anomalies": [ ... ],
    "comparisons": [ ... ]
  },
  
  "causal_analysis": {
    "main_factors": [ ... ],
    "confidence": "高/中/低"
  },
  
  "recommendations": [
    { "priority": "高", "horizon": "短期", "action": "..." },
    { "priority": "中", "horizon": "中期", "action": "..." },
    { "priority": "低", "horizon": "长期", "action": "..." }
  ],
  
  "limitations": [
    "缺乏竞品详细数据",
    "客户访谈数据不足"
  ]
}
```

### Main Skill 需要的最小输出

```json
{
  "conclusion": "华东区Q3销量下降的主要原因是客户流失（40%）和竞品冲击（35%）",
  "key_data": {
    "下降幅度": "-15%",
    "客户流失影响": "-6%",
    "竞品冲击影响": "-5.25%"
  },
  "top_recommendation": "启动客户流失预警，优先联系 Q3 未复购客户"
}
```

## 错误处理

| 错误 | 处理方式 |
|------|----------|
| 缓存数据不足 | 返回"需要补充数据"，列明需要什么 |
| 分析不置信 | 明确标注置信度，说明原因 |
| 缺少企业知识 | 基于通用业务理解给出分析 |

## 注意事项

1. **分析必须有数据支撑**：不要凭空猜测
2. **归因要谨慎**：相关不等于因果
3. **建议要可执行**：不要给出空洞的建议
4. **标注局限性**：明确哪些是推测，哪些是确认

---

*本 Skill 是数据分析体系的分析层，核心价值在于深度业务理解和行动建议。*