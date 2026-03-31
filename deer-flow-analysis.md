# Deer Flow 数据类 Skill 分析报告

**分析日期**: 2026-03-31
**项目**: bytedance/deer-flow
**Skill 数量**: 17 个 public skills

---

## 一、Deer Flow Skills 概览

| Skill 名称 | 功能描述 |
|------------|----------|
| bootstrap | 初始化引导 |
| chart-visualization | 图表可视化 |
| claude-to-deerflow | 迁移工具 |
| **consulting-analysis** | 咨询分析报告框架 |
| **data-analysis** | 数据分析（SQL/统计） |
| **deep-research** | 深度网络研究 |
| find-skills | 技能发现 |
| frontend-design | 前端设计 |
| github-deep-research | GitHub 深度研究 |
| image-generation | 图片生成 |
| podcast-generation | 播客生成 |
| ppt-generation | PPT 生成 |
| skill-creator | 技能创建 |
| surprise-me | 随机惊喜 |
| vercel-deploy-claimable | Vercel 部署 |
| video-generation | 视频生成 |
| web-design-guidelines | Web 设计指南 |

---

## 二、三个数据相关 Skill 详细分析

### 1. data-analysis Skill

**定位**: 纯数据处理/分析

**核心能力**:
- 读取 Excel (.xlsx/.xls) 和 CSV 文件
- 使用 DuckDB 进行 SQL 查询
- 基础统计（mean, median, stddev, percentiles, nulls）
- 多 sheet 支持（每个 sheet 成为一张表）
- 跨文件 JOIN
- 结果导出（CSV/JSON/Markdown）
- 自动缓存机制

**支持的命令**:
```bash
python analyze.py --files <path> --action inspect      # 检查文件结构
python analyze.py --files <path> --action query --sql "SELECT..."  # SQL查询
python analyze.py --files <path> --action summary --table <表名>    # 统计摘要
```

**能力评估**:

| 分析类型 | 支持情况 |
|----------|----------|
| 描述性分析（基础统计） | ✅ 完整支持 |
| 诊断性分析（归因/异常） | ⚠️ 有限（需手动写 SQL） |
| 预测性分析（趋势/回归） | ❌ 无 |
| 规范性分析（决策建议） | ❌ 无 |

---

### 2. consulting-analysis Skill

**定位**: 专业咨询报告生成框架

**核心能力**:
- **两阶段工作流**：
  - Phase 1: 分析框架生成（选择分析模型、设计报告结构）
  - Phase 2: 报告生成（整合数据、输出最终报告）
- **分析框架库**（按领域选择）：
  - 战略与环境: SWOT, PEST, Porter's Five Forces, VRIN
  - 市场与增长: STP, BCG Matrix, Ansoff Matrix, TAM-SAM-SOM
  - 消费者与行为: AARRR, RFM, Jobs-to-be-Done
  - 财务与估值: DCF, DPO, Comparable Company, EVA
  - 竞争与定位: Benchmarking, Strategic Group Mapping, Value Chain
- **输出格式**: 符合麦肯锡/BCG 咨询标准
- **语言支持**: 可配置输出语言（默认中文）

**工作流程**:
1. 理解研究主题 → 确定分析领域
2. 选择分析框架（2-4个）→ 分配到各章节
3. 定义每章的数据需求（具体指标、来源、时间范围）
4. 设计可视化方案（图表类型、数据映射）
5. **handoff**: 将数据需求交给其他 skill（deep-research, data-analysis 等）执行
6. 整合数据 → 生成最终报告

**局限性**:
- ⚠️ 不直接处理数据，只提供框架和方法论
- ⚠️ 需要依赖其他 skill 完成数据收集
- ⚠️ 不涉及企业私有知识

---

### 3. deep-research Skill

**定位**: 系统化网络研究

**核心能力**:
- **四阶段研究方法**：
  - Phase 1: 广度探索（broad exploration）
  - Phase 2: 深度挖掘（deep dive）
  - Phase 3: 多样性与验证（diversity & validation）
  - Phase 4: 逻辑一致性检查（sanity check）
- **多角度搜索**: 至少 3-5 个不同角度
- **信息来源**: 行业报告、财报、学术论文、新闻、案例研究
- **时间敏感**: 正确使用时间限定词（最新数据用当前年份）
- **迭代式搜索**: 根据发现不断优化搜索词

**适用场景**:
- 用户问 "什么是 X"
- 需要深入理解某个概念、技术、领域
- 内容创作前的研究（PPT/文档/文章）
- 需要实时信息（非纯知识）

**局限性**:
- ❌ 不处理本地数据文件
- ❌ 不涉及企业私有知识库

---

## 三、核心问题：缺乏企业知识处理

### 问题识别

| 层级 | 现状 | 问题 |
|------|------|------|
| 数据处理 | ✅ data-analysis | 纯技术处理，不理解业务含义 |
| 知识获取 | ⚠️ consulting-analysis (框架) / deep-research (网络) | 不涉及企业私有知识 |
| 知识理解 | ❌ 无 | 缺乏语义理解/知识图谱 |
| 诊断建议 | ❌ 无 | 没有归因/异常检测能力 |

### 什么是"企业知识"？

企业知识包括：
1. **业务术语**: KPI、业务指标、行业特定词汇
2. **历史经验**: 以往决策、失败教训、最佳实践
3. **组织上下文**: 部门架构、流程、审批链
4. **行业知识**: 市场格局、竞争格局、监管要求
5. **客户/产品信息**: 客户画像、产品定位、价格体系

**例子**:
- data-analysis 能告诉你 "销售额下降了 20%"
- 但它不能告诉你 "为什么下降"（需要结合市场/竞品/内部因素）
- 也不能告诉你 "应该怎么办"（需要业务知识）

---

## 四、Deer Flow 的数据分析能力评估

```
数据输入 → [data-analysis] → 统计结果
                     ↓
              咨询框架 + 网络研究
                     ↓
              [consulting-analysis] → 报告
                     ↑
              [deep-research] (补充外部信息)
```

**优点**:
- 工具链完整（数据处理 → 分析框架 → 报告生成 → 可视化）
- 方法论专业（符合咨询行业标准）
- 自动化程度高

**不足**:
- 数据分析层薄弱（只有描述性统计）
- 缺乏诊断性分析能力
- 没有企业知识/语义理解层
- 各 skill 之间协作依赖 handoff，没有自动感知能力

---

## 五、改进建议：构建完整的数据分析体系

### 现有能力（保留/增强）

| 层级 | Skill | 增强方向 |
|------|-------|----------|
| 数据处理 | data-analysis | 保留基础能力 |

### 需要新增的能力

| 层级 | 能力 | 说明 |
|------|------|------|
| **知识理解层** | 语义理解 | 理解业务术语、行业知识 |
| | 知识图谱 | 建立实体关系（产品-客户-渠道） |
| | 企业上下文 | 读取企业文档/知识库 |
| **诊断分析层** | 归因分析 | Why 分析（相关/回归/分层） |
| | 异常检测 | 自动发现数据中的异常点 |
| | 对比分析 | 同期/竞品/目标对比 |
| **增强分析层** | 时间序列 | 趋势预测（Prophet/statsmodels） |
| | What-if 分析 | 假设场景模拟 |

---

## 六、结论

1. **data-analysis 确实更偏向描述性分析**：只处理"数据是什么"，不处理"为什么"和"怎么办"

2. **缺乏企业知识处理**：整个 Deer Flow 没有处理私有知识库的 Skill，所有分析依赖外部数据或网络搜索

3. **定位清晰但能力有限**：
   - data-analysis = 高级 Excel/SQL 工具
   - consulting-analysis = 报告模板生成器
   - deep-research = 搜索引擎增强

4. **如果要构建更智能的数据分析助手**，需要在此基础上增加：
   - 企业知识理解（语义层）
   - 诊断性分析（归因/异常）
   - 预测性分析（趋势/预测）

---

*报告结束*
