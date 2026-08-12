# GOAI 2026 — Boundless Agents × AI+金融 × 数据分析
# Master Plan / 项目总计划（GitHub 长期维护版）

> **Formal Product Name / 正式项目名：FitzSight — Financial Operations Intelligence Agent**  
> 中文：**金融经营智能分析与风险研判 Agent**  
> 赛道：**GOAI 2026 · Boundless Agents（无界应用）· AI+金融**  
> 文档定位：本文件是项目的**唯一主计划（Single Source of Truth）**。后续需求、架构、数据、实验、Demo、提交材料、风险、时间表和评审策略均应尽量在此同步维护。  
> 初版日期：**2026-08-11（UTC+8）**  
> 当前状态：**初赛冲刺 / MVP 设计阶段**  
> 当前优先级：**P0 — 先完成一个“小而完整、可运行、可验证、有证据链”的金融经营分析闭环。**

---

## 0. 文档使用方式

### 0.1 为什么要有这份文档

本项目时间非常紧，且赛事规则、作品定位、技术实现、数据设计、评审策略之间强耦合。最危险的情况不是“代码写不出来”，而是：

- 做着做着改变题目；
- 为了炫技不断增加 Agent；
- 花大量时间做 UI，却没有真正的分析闭环；
- 初赛 PPT 讲得很大，复赛时无法落地；
- 忘记数据授权、开源边界、金融合规；
- Demo 能跑，但无法证明结论来自真实工具和数据；
- Agent 给出“看起来合理”的解释，却无法展示证据；
- 项目最后变成“上传 CSV → LLM 总结”，与官方不鼓励的泛问答/简单内容生成高度相似。

因此，本文件的作用是固定以下内容：

1. 我们到底在解决什么问题；
2. 为什么这个问题适合参赛者本人；
3. 为什么选择 Boundless Agents + AI+金融；
4. 评委会期待看到什么；
5. MVP 必须包含什么、明确不包含什么；
6. 技术架构如何落地；
7. 数据如何合法、可控、可复现；
8. Agent 如何做到“有证据地分析”；
9. 如何评估 Agent，而不是只展示一次成功 Demo；
10. 8 月 16 日、9 月 3 日、9 月 22 日前分别做到什么；
11. 哪些内容永远不能为了比赛便利而牺牲。

---

## 0.2 维护原则

后续每次重大修改，请至少更新：

- `Last Updated`
- `Current Status`
- `Decision Log`
- `Risk Register`
- `Milestones`
- `Submission Checklist`

建议 GitHub 中将本文件命名为：

```text
MASTER_PLAN.md
```

或：

```text
docs/MASTER_PLAN.md
```

如项目成熟，可进一步拆分：

```text
docs/
├── MASTER_PLAN.md
├── COMPETITION_RULES.md
├── PRODUCT_SPEC.md
├── ARCHITECTURE.md
├── DATA_SPEC.md
├── EVALUATION.md
├── SECURITY_AND_COMPLIANCE.md
├── DEMO_SCRIPT.md
├── PITCH_DECK_OUTLINE.md
└── DECISION_LOG.md
```

**但在初赛阶段不建议过早拆太多文件。先保持一个总文档，避免信息碎片化。**

---

# 1. Executive Summary / 项目执行摘要

## 1.1 一句话项目定义

> **FitzSight 是一个面向金融企业经营分析人员、销售管理者和风险管理人员的 Agentic Data Analysis 系统。它能够从业务问题出发，自主选择并调用数据工具，对客户、交易、入出金、销售转化等经营数据进行分析，识别异常、下钻原因、完成统计验证，并输出带有可追溯证据的经营结论与行动建议。**

最核心的产品闭环是：

```text
Business Question
      ↓
Understand Intent
      ↓
Select Metrics / Analysis Plan
      ↓
Query Data with SQL / Python
      ↓
Detect Anomaly
      ↓
Drill Down
      ↓
Statistical Validation
      ↓
Evidence Verification
      ↓
Business Insight
      ↓
Action Recommendation
      ↓
Auditable Executive Brief
```

我们要避免的形态：

```text
User Question
      ↓
LLM
      ↓
Plausible-looking Answer
```

我们要实现的形态：

```text
User Question
      ↓
Agent
      ↓
Tools + Data + Statistics + Evidence
      ↓
Verified Answer
```

---

## 1.2 参赛赛道选择

**GOAI 2026 → Boundless Agents 无界应用 → AI+金融**

官方对 Boundless Agents 的定位包括：

- 面向真实行业场景；
- 具备任务理解；
- 流程编排；
- 工具调用；
- 知识增强；
- 多轮交互；
- 结果交付；
- 至少完成一个可演示、可验证的任务闭环；
- 不鼓励泛聊天机器人、单点问答工具或简单内容生成器；
- AI+金融重点为“面向企业经营与风险研判的金融服务 Agent”。

这与本项目高度匹配。

---

## 1.3 当前最终推荐项目方向

### 主方向

**Financial Operations Intelligence Agent**

### 更具体的业务落点

优先聚焦：

> **金融经纪 / FinTech / 支付 / 交易平台类企业的经营分析与异常诊断。**

目标不是做面向消费者的“投资建议机器人”，而是做：

> **企业内部 Business Analyst / Sales Manager / Operations Manager / Risk Analyst 的智能分析助手。**

---

## 1.4 项目最核心的 Killer Feature

### **Autonomous Anomaly Investigation**
### 自主经营异常调查

典型问题：

> “为什么欧洲业务本周净入金下降了？”

系统不能直接总结，而应自动执行：

1. 明确“业务表现”的指标集合；
2. 计算本周 vs 上周；
3. 定位显著下降的 KPI；
4. 按区域、渠道、销售团队、客户分群等维度下钻；
5. 检查是否由少量高价值客户导致；
6. 检查新客首入金转化；
7. 检查销售响应、CRM 流程或营销渠道变化；
8. 对差异进行统计检验；
9. 给出可验证的主要贡献因素；
10. 生成证据；
11. 给出有限、可执行、非越权的行动建议。

理想输出示例：

```text
Net deposits fell 18.7% WoW.

Primary drivers:
1. UK Sales Team A/B contributed 46% of the decline.
2. New-client first-deposit conversion fell from 21.4% to 17.8%.
3. High-value withdrawals increased 42%, concentrated in 11 clients.

Statistical validation:
- FTD conversion difference: p = 0.004
- Effect concentrated in leads assigned after CRM routing change.

Evidence:
- SQL Query #Q17
- Chart #C05
- Statistical Test #T02
- Customer cohort table #D11

Recommended next actions:
- Review CRM lead-routing latency after July 15 deployment.
- Audit the two affected sales teams.
- Contact high-value dormant / withdrawal-risk clients.
```

这就是整个项目的核心展示价值。

---

# 2. Competition Intelligence / 赛事情报

> **信息状态：截至 2026-08-11。正式参赛时必须再次核对官网最新通知。赛事明确保留调整赛程、评审机制和奖项的权利。**

---

## 2.1 赛事基本性质

GOAI 世界人工智能开源大赛（Global Open-source AI Challenge）由杭州市开源人工智能基金会发起，面向全球开发者、开源团队、高校、科研团队、企业 AI 团队、创业团队等。

赛事总体强调：

- 技术创新；
- 开源贡献；
- 真实应用价值；
- 工程可运行；
- 可复现；
- Demo；
- 长期成长潜力。

从目前公开信息看，这不是以单一 Benchmark 排名为核心的 Kaggle 式竞赛，而更接近：

> **高强度 AI Engineering / Product Hackathon + 开源项目孵化 + 线下路演。**

---

## 2.2 Boundless Agents 官方定位

Boundless Agents 聚焦：

- AI+眼镜
- AI+汽车
- **AI+金融**
- AI+教育
- AI+工业制造

官方强调真实用户、真实业务流程、真实任务闭环。

### AI+金融官方重点验证

- 资料理解
- 规则匹配
- 风险提示
- 投研整理
- 流程辅助

本项目会重点向“企业经营与风险研判”延伸，而不是做消费级股票建议。

---

## 2.3 官方核心作品要求

项目至少应完成：

- 一个可演示的任务闭环；
- 一个可验证的任务闭环；
- 明确目标用户；
- 明确场景痛点；
- 明确交互流程；
- 明确技术路线；
- 明确数据来源；
- 明确合规边界；
- 明确后续迭代计划。

还应说明：

- 使用哪些模型；
- Agent 架构；
- 工具接口；
- 知识库；
- 数据处理；
- 部署方式；
- 数据授权；
- 隐私保护；
- 风险提示；
- 行业边界。

---

## 2.4 官方评审关注

Boundless Agents 当前公开的评审关注包括：

1. **行业场景价值**
2. **Agent 能力与任务闭环**
3. **产品体验与 Demo 完成度**
4. **技术实现深度与工程可复现性**
5. **安全、合规与开放复用价值**

因此项目优先级必须是：

```text
闭环 > 可运行 > 证据 > 真实场景 > 可复现 > UI炫技
```

而不是：

```text
模型数量 > Agent数量 > 动画 > Prompt复杂度
```

---

## 2.5 赛程

### 初赛

- 报名/初赛阶段：2026-07-16 至 2026-08-16
- **初赛作品截止：2026-08-16 23:59（UTC+8）**
- 初赛提交：
  - 作品简介
  - 方案 PPT / PDF
  - 原型或视频：可选

### 初赛评审

- 2026-08-17 至 2026-08-24
- **Top 30 进入复赛**

### 复赛

- 2026-08-25 至 2026-09-03
- **复赛截止：2026-09-03**
- 提交：
  - 更新方案
  - Demo
  - 运行说明
  - 代码或等价工程材料

### 复赛评审

- 2026-09-04 至 2026-09-10
- **Top 15 进入决赛**

### 决赛

- **2026-09-22**
- 杭州线下决赛答辩与展示
- 路演 PPT
- 现场 Demo
- 项目一页纸
- 答辩材料

### GOAI DAY

- **2026-09-23**
- 颁奖
- 项目展示
- 生态对接

---

## 2.6 奖项

Boundless Agents 当前公布：

- 冠军：500,000 RMB
- 亚军：300,000 RMB
- 季军：100,000 RMB
- 第 4–10 名：开源新锐奖，5,000 RMB / 队
- 第 11–15 名：开源影响力奖，3,000 RMB / 队
- 入围复赛优胜奖：500 RMB / 队
- 有效方案参与奖：纪念 T 恤（限量并按排名）

全场大奖：

- **1 名**
- **1,000,000 RMB**
- 从四大赛道冠军中决出。

奖金均为税前金额，实际规则以最终官方通知为准。

---

## 2.7 赛事整体评价：我们应该如何看待它

### 正面

- 组织背景强；
- 产业合作方较多；
- 奖金池高；
- 明确强调 Demo 和工程落地；
- 对个人、学生、开发者开放；
- 商业模型 / API 可合理使用；
- 项目知识产权原则上仍归参赛者；
- 对开源、复现、文档、真实场景有明确要求。

### 不确定性

这是首届赛事，因此目前缺少：

- 往届获奖项目质量基准；
- 往届奖金到账经验；
- 往届评审争议；
- 长期招聘市场认可度；
- 赛事品牌长期影响力；
- 成熟的历年“上分套路”。

因此项目不能以“拿奖证书”为唯一目标。

### 正确参赛逻辑

即使最终没有获奖，项目仍应具有：

- GitHub Portfolio 价值；
- 面试项目价值；
- AI Engineer / Data Scientist / Analyst 履历价值；
- 可继续扩展成产品的价值；
- 开源项目价值。

---

# 3. Why This Project Fits the Builder / 为什么这个项目适合参赛者

## 3.1 个人能力与项目的直接映射

现有经历可以形成非常完整的故事线：

### 数据科学背景

已有能力包括：

- Python
- SQL
- Excel
- Statistics
- Machine Learning
- Data Cleaning
- Data Modelling
- Data Visualization
- Analytical reasoning

### 金融业务数据经验

曾经实际参与金融业务相关的数据分析，包括：

- 客户注册数据；
- 首次入金；
- 入金 / 出金；
- 交易量；
- 销售转化；
- 销售团队效率；
- 客户分类 / 聚类；
- 不同地区业务分析；
- 系统变更前后效率变化；
- 日报/运营数据整合。

这些经历直接支持本项目的问题定义。

---

## 3.2 项目叙事优势

我们不是：

> “AI 很火，所以做一个金融 Agent。”

而是：

> “在真实金融业务数据分析工作中，发现大量分析任务需要人工在 Excel、SQL、Python、BI 和业务规则之间往返。许多问题不是不会算，而是调查过程碎片化、重复、耗时，并且结论缺乏统一证据链。因此希望构建一个能够自主完成数据查询、异常诊断、统计验证和证据化汇报的 Financial Operations Intelligence Agent。”

这个叙事天然具有：

- Problem–Builder Fit
- Domain credibility
- Technical credibility
- Product motivation
- 可展示的真实业务流程理解

---

## 3.3 必须遵守的职业与数据边界

**绝不使用任何前雇主/实习企业的真实内部数据、客户数据、CRM 数据、交易数据、个人信息、内部报表或非公开流程文档。**

项目应只使用：

1. 自主生成的合成数据；
2. 明确可公开使用的公开数据；
3. 自己定义的通用金融经营规则；
4. 模拟的组织结构和事件日志。

所有名称均应虚构。

禁止：

- 真实客户 ID；
- 真实员工姓名；
- 真实账户；
- 真实企业 KPI；
- 真实内部策略；
- 真实内部数据库结构；
- 任何无法确认许可范围的数据。

---

# 4. Product Vision / 产品愿景

## 4.1 Vision

> **让企业经营问题从“人工找数据、人工写 SQL、人工解释”变成“Agent 自主调查、工具真实执行、结论有证据、建议可追溯”。**

---

## 4.2 产品不是 BI Dashboard 的替代品

传统 BI：

```text
User
 ↓
Open Dashboard
 ↓
Select Filter
 ↓
Look at Chart
 ↓
Form Hypothesis
 ↓
Export Data
 ↓
Run SQL
 ↓
Use Python
 ↓
Ask Colleague
 ↓
Write Report
```

FitzSight：

```text
User asks a business question
        ↓
Agent creates investigation plan
        ↓
Queries relevant data
        ↓
Runs analysis
        ↓
Finds anomalies
        ↓
Validates hypotheses
        ↓
Returns evidence-backed conclusion
```

因此产品定位不是：

> “另一个 Dashboard。”

而是：

> **“Analytical Investigation Layer on top of enterprise data.”**

---

# 5. Target Users / 目标用户

## 5.1 Primary User

### Financial Business Analyst

需求：

- 每日 / 每周经营分析；
- 净入金变化；
- 交易活跃度；
- 新客转化；
- 渠道表现；
- 销售团队表现；
- 客户生命周期；
- 异常解释；
- Management report。

---

## 5.2 Secondary Users

### Sales Manager

关心：

- 团队转化；
- Lead → FTD；
- 不同销售的表现；
- 响应速度；
- 客户跟进；
- 高潜客户。

### Operations Manager

关心：

- 业务异常；
- 系统变化；
- 流程效率；
- 地区差异；
- 运营影响因素。

### Risk / Compliance Analyst

MVP 中只做：

- 异常提示；
- 风险信号；
- 可疑模式提示；
- 需要人工复核的标记。

**不做自动执法、不做账户冻结、不做客户定罪。**

---

# 6. Problem Statement / 问题定义

## 6.1 核心问题

金融企业经营数据通常存在于多个表或系统：

```text
CRM
Transactions
Deposits
Withdrawals
Trading
Marketing
Sales
Customer profiles
System change logs
```

当管理者提出：

> “为什么本周净入金下降？”

分析师需要：

1. 拉数据；
2. 检查日期；
3. 写 SQL；
4. 做同比/环比；
5. 分地区；
6. 分销售；
7. 分渠道；
8. 看大客户；
9. 看新客户；
10. 检查系统变化；
11. 做统计；
12. 生成图表；
13. 写报告。

大量时间消耗在：

- data plumbing；
- repetitive analysis；
- hypothesis switching；
- reporting。

---

## 6.2 关键机会

LLM 最适合：

- 理解业务问题；
- 规划分析过程；
- 选择工具；
- 解释结果；
- 编排调查；
- 生成结构化报告。

Python / SQL 最适合：

- 真正算数；
- 聚合；
- 检验；
- 模型；
- 可重复分析。

因此采用：

```text
LLM = Planner / Reasoner / Orchestrator
SQL = Data Retrieval
Python = Statistics / ML / Charts
Rules = Guardrails
Evidence Store = Traceability
```

---

# 7. Project Scope / 项目范围

## 7.1 MVP 必做功能

### P0. Business Health Check

自动计算：

- Registered Users
- Active Users
- New Clients
- First-Time Depositors
- FTD Conversion Rate
- Total Deposits
- Total Withdrawals
- Net Deposits
- Trading Volume
- Active Traders
- Retention
- Sales Conversion

输出：

- 当前值；
- WoW / MoM；
- 异常；
- Top positive / negative contributor。

---

### P0. Deposit & Withdrawal Analysis

支持问题：

> Why did net deposits fall?

分析：

```text
Net Deposit
  ↓
Deposit vs Withdrawal
  ↓
Region
  ↓
Channel
  ↓
Sales Team
  ↓
Customer Segment
  ↓
High-value customers
```

---

### P0. Sales Conversion Analysis

分析：

```text
Lead
 ↓
Contact
 ↓
Qualified
 ↓
FTD
 ↓
Active trader
```

指标：

- Lead → Contact
- Contact → FTD
- FTD → Active Trader
- Response Time
- Conversion by salesperson
- Conversion by team
- Conversion by region
- Conversion by channel

---

### P1. Customer Intelligence

功能：

- RFM-like features；
- Customer segmentation；
- High Value；
- Growth；
- Dormant；
- Churn Risk；
- New；
- Low Engagement。

可以先规则 + 聚类。

后续再加入预测模型。

---

### P0. Autonomous Anomaly Investigation

这是 Killer Feature。

系统收到开放问题后：

1. 判断问题类型；
2. 选择 KPI；
3. 建分析计划；
4. 调数据；
5. 找异常；
6. 下钻；
7. 生成假设；
8. 调用统计工具；
9. 比较证据；
10. 输出 Root Cause Candidates；
11. 标注置信度；
12. 给 Evidence References。

---

## 7.2 MVP 不做

为控制范围，初赛/复赛前明确不做：

- 自动交易；
- 股票买卖建议；
- 个股 Buy/Sell signal；
- 高频行情；
- 真实 KYC；
- 自动 AML 执法；
- 自动冻结账户；
- 自动转账；
- 自动修改 CRM；
- 自动联系真实客户；
- 复杂实时流计算；
- 自训练大模型；
- 15 个 Agent；
- 全金融行业万能平台；
- 真实企业 SaaS 多租户；
- 手机 App；
- 原生桌面 App。

---

# 8. Core User Stories / 核心用户故事

## US-01：解释经营异常

> As an Operations Manager, I want to ask why net deposits declined this week, so that I can identify actionable operational causes.

Definition of Done：

- 能计算本周净入金；
- 能与上周对比；
- 能找到主要贡献维度；
- 能识别是否是少量大额提款；
- 能检查 FTD；
- 能提供至少两类证据；
- 不允许无数据依据地编理由。

---

## US-02：销售团队诊断

> As a Sales Manager, I want to know which sales teams caused conversion deterioration.

Done：

- 按 team / salesperson 分解；
- 控制 lead 数量差异；
- 计算 conversion；
- 可运行 significance test；
- 输出排名；
- 可定位异常团队。

---

## US-03：客户风险识别

> As an Analyst, I want to identify dormant high-value clients or withdrawal-risk segments.

Done：

- 定义特征；
- 生成 segment；
- 可解释；
- 不做未经验证的个人定罪；
- 输出仅用于人工复核。

---

## US-04：系统变化影响分析

> As an Operations Analyst, I want to evaluate whether a CRM routing change affected sales conversion.

Done：

- 明确 intervention date；
- before / after；
- 控制时间窗口；
- 描述性统计；
- 显著性检验；
- 有条件可做 regression / interrupted time-series；
- 不把 correlation 自动称为 causation。

---

# 9. System Architecture / 系统架构

## 9.1 推荐架构原则

Boundless Agents 不需要为了“多 Agent”而多 Agent。

首版采用：

> **1 个 Orchestrator + 3 个 Specialist Agents + 1 个 Verifier（可选） + 一组强工具。**

如果开发时间不足：

> **1 个主 Agent + Tools + Verifier layer** 也可以。

关键是任务闭环，不是 Agent 数量。

---

## 9.2 推荐 Logical Architecture

```text
┌───────────────────────────────────────────────────────┐
│                    User Interface                     │
│  Chat + KPI cards + Investigation Trace + Evidence   │
└──────────────────────────┬────────────────────────────┘
                           │
                           ▼
┌───────────────────────────────────────────────────────┐
│                Orchestrator / Analyst Agent           │
│                                                       │
│  Intent → Plan → Tool Selection → Hypothesis → Report │
└───────────────┬──────────────────┬────────────────────┘
                │                  │
       ┌────────▼────────┐  ┌──────▼─────────┐
       │ Data Specialist │  │ Risk / Business│
       │     Agent       │  │ Specialist     │
       └────────┬────────┘  └──────┬─────────┘
                │                  │
                └────────┬─────────┘
                         ▼
                ┌─────────────────┐
                │    Verifier     │
                │ Evidence/Stats  │
                └────────┬────────┘
                         ▼
┌───────────────────────────────────────────────────────┐
│                       Tool Layer                      │
│ SQL | Python | KPI | Stats | Segmentation | Charts   │
│ Schema | Data Quality | Evidence | Report             │
└──────────────────────────┬────────────────────────────┘
                           ▼
┌───────────────────────────────────────────────────────┐
│                        Data Layer                     │
│ Synthetic CRM | Transactions | Trading | Events      │
└───────────────────────────────────────────────────────┘
```

---

# 10. Agent Responsibilities / Agent 职责

## 10.1 Orchestrator / Lead Analyst Agent

职责：

- 理解用户问题；
- 判断分析类型；
- 建 investigation plan；
- 调度工具；
- 决定下一步下钻；
- 综合结果；
- 写最终管理层摘要。

禁止：

- 自己凭空计算数字；
- 无工具证据时生成精确 KPI；
- 将“可能”改写成“确定”；
- 直接执行高风险操作。

---

## 10.2 Data Specialist Agent

职责：

- schema inspection；
- data quality；
- SQL generation；
- aggregation；
- cohort construction；
- date window；
- join consistency。

输出：

```json
{
  "query_id": "Q17",
  "dataset": ["transactions", "customers"],
  "metric": "net_deposit",
  "time_window": "...",
  "result_ref": "D11"
}
```

---

## 10.3 Business / Risk Specialist Agent

职责：

- 根据金融运营逻辑解释；
- 构造业务假设；
- 判断需要什么额外数据；
- 识别合规边界；
- 对建议分类为：
  - Informational
  - Review Required
  - Human Approval Required

---

## 10.4 Verifier

Verifier 是项目可信度的关键。

检查：

1. 所有数字是否来自 Tool output；
2. 时间窗口是否一致；
3. 分母是否正确；
4. Statistical test 是否合理；
5. 结论是否过度；
6. 是否有证据；
7. 是否至少有一个替代解释；
8. 是否把相关性错误写成因果关系；
9. 建议是否越权。

输出：

```text
Verified
Partially Verified
Insufficient Evidence
Rejected
```

---

# 11. Tool Layer / 工具体系

## 11.1 必须优先实现的工具

### `inspect_schema()`

返回：

- 表名；
- 字段；
- 类型；
- 日期范围；
- 行数；
- null ratio。

---

### `run_sql(query)`

用途：

- groupby；
- aggregation；
- join；
- cohort；
- filtering。

要求：

- 只读；
- query log；
- timeout；
- row limit。

---

### `calculate_kpi(metric, period, dimensions)`

统一定义：

- FTD；
- Conversion；
- Net Deposit；
- Trading Volume；
- Retention。

最大好处：

> 避免 Agent 每次自己重新定义 KPI。

---

### `compare_periods(metric, current, baseline)`

返回：

- Current
- Baseline
- Absolute Difference
- Percentage Change
- Contribution

---

### `run_statistical_test()`

首版支持：

- t-test
- Mann–Whitney U
- Chi-square
- proportion z-test（可选）

---

### `detect_anomaly()`

首版可简单：

- z-score；
- IQR；
- rolling baseline；
- percentage threshold。

不要一开始搞复杂深度学习异常检测。

---

### `segment_customers()`

支持：

- rules；
- KMeans；
- optional classifier。

---

### `generate_chart()`

必须基于真实分析结果生成，而不是 LLM 想象。

---

### `register_evidence()`

每次工具执行写：

```text
Evidence ID
Tool
Parameters
Timestamp
Data range
Output hash / reference
```

---

# 12. Data Design / 数据设计

## 12.1 核心策略

### **Synthetic Financial Operations Dataset**

这是项目的一项重要创新点，而不是权宜之计。

理由：

- 无企业数据泄露风险；
- Ground Truth 可控；
- 可注入异常；
- 可用于 Benchmark；
- 可公开；
- 可复现；
- 可以验证 Agent 是否真的找到原因。

---

## 12.2 数据规模建议

MVP：

- 20,000 customers
- 12 months
- 5 regions
- 5 channels
- 40–60 salespeople
- 100,000–300,000 transaction records
- 50,000+ trading records
- 50–100 system / campaign events

足够展示，但不会拖垮本地 Demo。

---

## 12.3 建议表结构

### `customers`

```text
customer_id
registration_date
region
country
acquisition_channel
assigned_salesperson
assigned_team
risk_profile_mock
customer_segment_gt
```

---

### `deposits`

```text
deposit_id
customer_id
timestamp
amount
currency
method
status
```

---

### `withdrawals`

```text
withdrawal_id
customer_id
timestamp
amount
currency
status
```

---

### `trades`

```text
trade_id
customer_id
timestamp
instrument_group
volume
pnl_mock
```

---

### `sales_activity`

```text
activity_id
customer_id
salesperson_id
timestamp
activity_type
response_time_minutes
outcome
```

---

### `salespeople`

```text
salesperson_id
team_id
region
tenure_months
```

---

### `business_events`

这是非常关键的表。

```text
event_id
date
event_type
region
affected_team
description
expected_effect
ground_truth_tag
```

事件可以包含：

- CRM routing change
- Marketing campaign
- Payment outage
- Sales team staffing change
- Regional holiday
- Whale withdrawal event
- Onboarding friction
- Promotion expiration

---

# 13. Synthetic Ground Truth / 合成异常注入

## 13.1 为什么要注入异常

如果数据完全随机，Agent 只能找到随机噪声。

我们需要故意生成：

> **有明确因果机制但对 Agent 隐藏的异常场景。**

这样才能建立评测。

---

## 13.2 Scenario A：CRM Routing Change

日期：

```text
2026-07-15
```

机制：

```text
CRM routing change
      ↓
lead assignment latency +35%
      ↓
response time ↑
      ↓
FTD conversion ↓
```

只影响：

- Europe；
- Team A / B；
- New leads。

Ground Truth：

```json
{
  "root_cause": "crm_routing_change",
  "affected_metrics": [
    "lead_response_time",
    "ftd_conversion"
  ],
  "affected_scope": [
    "Europe",
    "Team A",
    "Team B"
  ]
}
```

---

## 13.3 Scenario B：Whale Withdrawal

11 个高价值客户集中提款：

```text
withdrawals +42%
net deposits ↓
```

Agent 应该识别：

> 不是所有客户都恶化，而是高度集中在少数客户。

---

## 13.4 Scenario C：Marketing Quality Drop

某渠道 Lead 数量上升：

```text
Leads +60%
FTD conversion -30%
```

制造：

> volume looks good, quality is bad。

---

## 13.5 Scenario D：Sales Team Performance

某团队：

- response time ↑
- contact rate ↓
- FTD ↓

但其他团队稳定。

---

## 13.6 Scenario E：False Correlation Trap

故意制造：

- 某地区交易量下降；
- 同时发生营销活动结束；
- 但真正原因是账户活跃结构改变。

用于测试 Agent 是否：

> 看到时间接近就直接宣布因果。

---

# 14. Evaluation Framework / Agent 评估框架

这是项目与普通 Demo 拉开差距的重要部分。

---

## 14.1 评估问题

不是只问：

> “Agent 的答案好不好看？”

而是：

1. 是否找到正确指标？
2. 是否使用正确时间窗口？
3. 是否调用正确工具？
4. 是否找到 Ground Truth Root Cause？
5. 是否引用证据？
6. 数字是否准确？
7. 是否会承认证据不足？
8. 是否产生幻觉？
9. 是否把相关性误写为因果？
10. 是否给出越权金融建议？

---

## 14.2 Metrics

### Root Cause Accuracy

```text
Correct root cause / total scenarios
```

---

### Evidence Coverage

最终重要 claim 中：

```text
claims with valid evidence / all factual claims
```

目标：

> ≥ 90%

---

### Numeric Accuracy

关键 KPI 与 ground truth 对比。

---

### Tool Success Rate

```text
successful tool executions / attempted calls
```

---

### Investigation Completion Rate

Agent 是否完成：

```text
Plan
→ Query
→ Analyze
→ Verify
→ Report
```

---

### Hallucination Rate

统计：

- 不存在的字段；
- 不存在的数字；
- 不存在的事件；
- 未执行却声称执行的工具。

---

### Overclaim Rate

例如：

```text
“caused by”
```

但证据只能支持：

```text
“associated with”
```

---

# 15. Evidence-First Design / 证据优先设计

## 15.1 所有核心结论都要绑定证据

例如：

> “FTD conversion fell 3.6 percentage points.”

必须绑定：

```text
Evidence: D14
Query: Q21
Period: Jul 15–31 vs Jul 1–14
```

---

## 15.2 UI 中加入 View Evidence

用户点击：

```text
View Evidence
```

看到：

- SQL；
- Table；
- Chart；
- Statistical Test；
- Filter；
- Time range。

这是非常适合比赛 Demo 的设计。

---

## 15.3 Claim Confidence

建议每条核心发现：

```text
High
Medium
Low
```

规则示例：

High：

- ≥2 independent evidence types；
- statistical validation；
- stable across reasonable window。

Medium：

- one strong evidence；
- no contradiction。

Low：

- weak signal；
- small sample；
- multiple plausible explanations。

---

# 16. Statistical Analysis / 统计分析策略

## 16.1 统计不是装饰

必须解决具体问题。

例如：

> Conversion from 21.4% → 17.8%

不能只说：

> “下降明显”。

应该：

- proportion test；
- confidence interval；
- sample size；
- effect size。

---

## 16.2 推荐测试

### Conversion

- two-proportion z-test
- Chi-square

### Deposit distributions

因为金额通常 heavy-tail：

- Mann–Whitney U
- bootstrap CI

### Average response time

先检查分布：

- t-test 或 Mann–Whitney

### Before/After system change

MVP：

- before-after comparison
- regression

进阶：

- interrupted time-series
- Difference-in-Differences（如果有合适 control group）

---

# 17. ML Strategy / 机器学习策略

## 17.1 原则

> **ML 是 Agent 的工具，不是项目中心。**

不要：

> “我们的创新是用了 XGBoost。”

应该：

> “Agent 在客户流失风险调查中，会根据任务需要调用 churn-risk model。”

---

## 17.2 MVP ML

优先顺序：

1. Rule-based customer segmentation
2. KMeans segmentation
3. Logistic Regression / LightGBM churn model（若时间允许）

---

## 17.3 Explainability

每次模型输出至少显示：

- probability；
- top features；
- model version；
- training dataset version。

---

# 18. UX / Demo Interface

## 18.1 页面布局

推荐：

```text
┌────────────────────────────────────────────────────────┐
│ FitzSight                                               │
├───────────────┬────────────────────────────────────────┤
│ KPI Overview  │ Chat / Investigation                   │
│               │                                        │
│ Net Deposit   │ Why did EU net deposits fall?         │
│ FTD           │                                        │
│ Trading       │ Plan                                   │
│ Retention     │ 1. Compare WoW                         │
│               │ 2. Drill region/team                   │
│               │ 3. Test conversion                     │
├───────────────┼────────────────────────────────────────┤
│ Filters       │ Findings                               │
│               │ Evidence cards                        │
└───────────────┴────────────────────────────────────────┘
```

---

## 18.2 必须让评委“看到 Agent 在做事”

展示：

```text
Understanding question...
Planning analysis...
Querying transactions...
Comparing periods...
Drilling down by region...
Testing conversion difference...
Checking business events...
Verifying evidence...
Generating report...
```

但必须是真执行，不要伪动画。

---

# 19. Recommended Tech Stack / 技术栈

## 19.1 Backend

优先：

- Python
- FastAPI

---

## 19.2 Data

初版：

- DuckDB

理由：

- 本地；
- CSV/Parquet 友好；
- SQL；
- 易部署；
- Demo 稳定。

复赛可换：

- PostgreSQL

但不是必要。

---

## 19.3 Data Processing

- pandas / polars
- numpy
- scipy
- statsmodels
- scikit-learn

---

## 19.4 Agent

可选：

- OpenAI Responses / Agents SDK
- LangGraph
- Pydantic AI
- 自定义轻量 orchestration

选择原则：

> **稳定、可调试、能留下 trace。**

不要为了框架名而框架。

---

## 19.5 Frontend

最快：

### Streamlit

优势：

- 快；
- Python 统一；
- 适合比赛。

若已有前端能力：

- React / Next.js

但当前时间下不建议为了漂亮 UI 大规模写前端。

---

## 19.6 Visualization

- Plotly
- matplotlib

---

# 20. Security / 安全设计

## 20.1 SQL Safety

Agent 只能：

```text
SELECT
```

禁止：

```text
INSERT
UPDATE
DELETE
DROP
ALTER
```

---

## 20.2 Tool Permissions

工具分级：

### L0 — Read Only

- schema
- SQL select
- KPI
- statistics

允许自动执行。

### L1 — Local Analysis

- ML inference
- report generation

允许自动执行。

### L2 — External Business Action

例如：

- CRM update
- customer contact
- ticket creation

MVP 不自动执行。

---

# 21. Financial Compliance Boundary / 金融合规边界

## 21.1 本项目不是

- Investment Advisor
- Broker execution system
- AML enforcement engine
- Credit decision engine
- Automated compliance decision maker

---

## 21.2 输出必须定位为

- analytical assistance；
- operational insight；
- risk signal；
- management decision support。

不是：

- legal conclusion；
- guaranteed forecast；
- investment recommendation。

---

## 21.3 UI Disclaimer

建议：

> This system provides analytical decision support based on the supplied operational data. It does not provide investment advice, legal conclusions, or automated compliance decisions. High-impact actions require human review.

---

# 22. Open Source Strategy / 开源策略

## 22.1 推荐开源内容

- synthetic dataset generator；
- schema；
- benchmark scenarios；
- tool interfaces；
- Agent workflow；
- evaluation harness；
- example prompts；
- demo config；
- README；
- deployment guide。

---

## 22.2 不提交

- API Keys；
- Secrets；
- 任何真实金融公司数据；
- 任何客户 PII；
- 任何未经授权数据；
- 私有账号信息。

---

## 22.3 License

候选：

- Apache-2.0
- MIT

如果后续涉及第三方依赖，应统一做：

```text
THIRD_PARTY_NOTICES.md
```

---

# 23. Repository Structure / GitHub 结构

推荐：

```text
FitzSight/
├── README.md
├── MASTER_PLAN.md
├── LICENSE
├── .gitignore
├── .env.example
├── pyproject.toml
│
├── app/
│   ├── api/
│   ├── agents/
│   ├── tools/
│   ├── services/
│   └── prompts/
│
├── data/
│   ├── README.md
│   ├── synthetic/
│   └── schemas/
│
├── generator/
│   ├── generate_customers.py
│   ├── generate_transactions.py
│   └── inject_scenarios.py
│
├── evaluation/
│   ├── benchmark.json
│   ├── evaluate_claims.py
│   ├── evaluate_root_cause.py
│   └── reports/
│
├── frontend/
│
├── notebooks/
│   └── exploration.ipynb
│
├── tests/
│   ├── test_kpis.py
│   ├── test_sql_safety.py
│   ├── test_scenarios.py
│   └── test_evidence.py
│
├── docs/
│   ├── architecture.md
│   ├── data_dictionary.md
│   ├── compliance.md
│   └── demo_script.md
│
└── scripts/
    ├── setup.sh
    └── run_demo.sh
```

---

# 24. README 必须讲清的内容

README 第一屏：

```text
What is FitzSight?
What problem does it solve?
Who is it for?
What can it actually do?
How do I run it?
```

推荐结构：

1. Problem
2. Demo GIF / screenshot
3. Core workflow
4. Architecture
5. Example investigation
6. Synthetic dataset
7. Evaluation
8. Quick Start
9. Safety
10. License

---

# 25. Demo Scenario / 决赛级核心演示

## 25.1 Demo Question

> **Why did European business performance deteriorate in July?**

---

## 25.2 Agent 预期流程

### Stage 1 — Intent

识别：

```text
business_performance_investigation
```

---

### Stage 2 — KPI Selection

自动选择：

- Net Deposit
- FTD Conversion
- Trading Volume
- Retention

---

### Stage 3 — Period Comparison

发现：

```text
Net Deposit     -19%
FTD Conversion  -14%
Trading Volume   -5%
Retention        stable
```

---

### Stage 4 — Drill Down

按：

```text
Country
Sales Team
Channel
Customer Segment
```

---

### Stage 5 — Findings

发现：

- 2 个 sales teams 贡献多数 conversion decline；
- High-value withdrawals 增加；
- 新 Lead response time 恶化。

---

### Stage 6 — Business Events

查到：

```text
CRM routing change
2026-07-15
```

---

### Stage 7 — Statistical Verification

Before / After：

```text
FTD:
21.4%
→
17.8%
```

检验：

```text
p = 0.004
```

---

### Stage 8 — Evidence

展示：

- Q17 SQL
- D11 table
- T02 statistical test
- C05 chart
- E03 business event

---

### Stage 9 — Recommendation

不直接自动改系统。

建议：

1. Review routing latency；
2. Compare affected vs unaffected teams；
3. Audit lead distribution；
4. Contact high-value at-risk customers；
5. Rollback only after human validation。

---

# 26. Pitch Narrative / 路演故事

## 26.1 Opening

> Financial analysts spend less time “thinking” than expected. A large part of their day is spent locating data, rewriting SQL, checking definitions, switching between dashboards, validating anomalies and turning all of that into a management report.

---

## 26.2 Problem

传统工具：

```text
Dashboard tells you WHAT happened.
```

FitzSight：

```text
Agent investigates WHY it happened.
```

---

## 26.3 Differentiator

不是：

> Chat with your CSV

而是：

> **Evidence-grounded autonomous financial operations investigation.**

---

## 26.4 Technical Differentiator

```text
LLM orchestration
+
SQL execution
+
statistical validation
+
synthetic ground-truth benchmark
+
evidence-linked claims
+
human-in-the-loop boundaries
```

---

# 27. Competition Strategy / 评审策略

## 27.1 我们希望评委记住的 3 件事

### 1.

> 这个项目来自真实金融数据分析工作流理解。

### 2.

> Agent 不只是说，而是真的查询、计算、验证。

### 3.

> 每个重要结论都有证据，可以点击查看。

---

## 27.2 不要试图让评委记住 20 个 Feature

只需要：

```text
Question
→ Investigation
→ Evidence
→ Decision
```

---

# 28. Risk Register / 风险登记表

| ID | 风险 | 级别 | 处理 |
|---|---|---:|---|
| R01 | 时间不足 | Critical | 严格 P0/P1 |
| R02 | 题目范围过大 | Critical | 只做经营异常调查 |
| R03 | 最后变成 ChatCSV | Critical | 强制 Tool + Evidence |
| R04 | LLM 幻觉数字 | Critical | 数字必须来自工具 |
| R05 | 合成数据不真实 | High | 加业务约束和异常机制 |
| R06 | Agent 找不到 root cause | High | benchmark + scenario tuning |
| R07 | Demo 网络/API 失败 | High | local fallback / cached model output |
| R08 | SQL 出错 | High | schema tool + validation |
| R09 | UI 花太多时间 | High | Streamlit / simple web |
| R10 | 过度多 Agent | High | 1 orchestrator + specialists |
| R11 | 泄露企业数据 | Critical | synthetic only |
| R12 | 金融建议越权 | Critical | clear boundary |
| R13 | 初赛 PPT 过度承诺 | High | 所有 Feature 标 MVP / Roadmap |
| R14 | 复赛要求变化 | Medium | 每日检查官网/群 |
| R15 | 统计方法不恰当 | Medium | verifier + fixed analysis templates |
| R16 | 开源 license 问题 | Medium | dependency audit |
| R17 | Demo 只有 happy path | High | 加至少 3 benchmark cases |
| R18 | 评委看不懂技术 | Medium | 用业务流程讲技术 |
| R19 | 评委认为创新不足 | High | 强调 benchmark + evidence graph |
| R20 | UI 没有过程感 | Medium | trace panel |

---

# 29. Timeline / 时间计划

## 29.1 2026-08-11 — Definition Day

P0：

- [ ] GitHub repo
- [ ] MASTER_PLAN.md
- [ ] 项目名暂定
- [ ] Problem Statement
- [ ] MVP Scope
- [ ] 核心 Demo Scenario
- [ ] 架构图
- [ ] 数据表设计
- [ ] 初赛 PPT 大纲

当天绝对不要：

- 花数小时选 logo；
- 大规模前端开发；
- 训练模型。

---

## 29.2 2026-08-12 — Data + Baseline

- [ ] Synthetic data generator v0
- [ ] customers
- [ ] deposits
- [ ] withdrawals
- [ ] sales activity
- [ ] business events
- [ ] CRM anomaly injection
- [ ] SQL baseline analysis
- [ ] 手工验证 root cause

Definition of Done：

> 不用 Agent 的情况下，Python/SQL 可以正确找到 Ground Truth。

---

## 29.3 2026-08-13 — Tool Layer

- [ ] schema tool
- [ ] SQL tool
- [ ] KPI tool
- [ ] comparison tool
- [ ] statistics tool
- [ ] evidence registry
- [ ] unit tests

---

## 29.4 2026-08-14 — Agent MVP

- [ ] Orchestrator
- [ ] tool calling
- [ ] investigation plan
- [ ] anomaly drilldown
- [ ] verifier
- [ ] final report

目标：

> 输入一个预定义问题，Agent 能从头跑到报告。

---

## 29.5 2026-08-15 — Demo + PPT

- [ ] Streamlit
- [ ] KPI cards
- [ ] Investigation trace
- [ ] Evidence cards
- [ ] Chart
- [ ] Demo recording
- [ ] PPT v1
- [ ] README

---

## 29.6 2026-08-16 — Submission Day

原则：

> **中午前完成可提交版本，不要 23:50 才上传。**

Checklist：

- [ ] 官网最终规则确认
- [ ] 项目简介 ≤平台要求
- [ ] PPT/PDF
- [ ] repo privacy / public status确认
- [ ] secrets 检查
- [ ] 数据 license
- [ ] README
- [ ] 演示视频（若提交）
- [ ] 提交成功截图
- [ ] 邮件确认
- [ ] 备份 PDF

---

# 30. 初赛评审等待期：8/17–8/24

不要停工。

### Week Objective

从：

```text
one working demo
```

扩展到：

```text
evaluated reproducible system
```

任务：

- [ ] 5 synthetic scenarios
- [ ] evaluation harness
- [ ] test suite
- [ ] evidence trace
- [ ] better UI
- [ ] architecture docs
- [ ] deployment script
- [ ] video polish
- [ ] cost/latency measurement

---

# 31. 复赛期：8/25–9/3

目标：

> **可以给陌生评委一键运行。**

必须有：

- README
- environment
- `.env.example`
- synthetic data
- one-command startup
- demo
- code
- architecture
- benchmark results
- limitations
- compliance explanation

建议增加：

```text
make demo
```

或：

```text
docker compose up
```

---

# 32. 决赛准备：9/10–9/22

如果进入 Top 15：

重点从“功能增加”切换为：

- 稳定；
- 路演；
- 答辩；
- Demo robustness；
- benchmark；
- business story。

### Demo 准备 3 套

1. Live Demo
2. Local Backup Demo
3. Video Backup

---

# 33. Pitch Deck / 初赛 PPT 建议结构

### Slide 1 — Title

FitzSight  
Agentic Financial Operations Intelligence

### Slide 2 — Problem

金融经营分析为什么慢。

### Slide 3 — Existing Workflow

Excel + SQL + Python + BI + Manual report。

### Slide 4 — Our Solution

Question → Investigation → Evidence → Decision。

### Slide 5 — User Scenario

“Why did net deposits fall?”

### Slide 6 — Agent Workflow

真实工具调用。

### Slide 7 — Architecture

Agent + Tools + Data。

### Slide 8 — Synthetic Benchmark

Ground Truth anomalies。

### Slide 9 — Demo / Prototype

截图。

### Slide 10 — Differentiation

不是 ChatCSV。

### Slide 11 — Safety / Compliance

Synthetic data + read-only + human review。

### Slide 12 — Open Source

Generator + benchmark + tools。

### Slide 13 — Roadmap

初赛 → 复赛 → Production。

### Slide 14 — Team / Builder Fit

Data Science + Financial Analytics experience。

---

# 34. Judge Q&A / 预判答辩问题

## Q1：为什么不用 Power BI Copilot？

回答重点：

- BI 擅长可视化和查询；
- FitzSight 强调 multi-step investigation；
- 自动下钻；
- hypothesis；
- statistics；
- evidence；
- benchmark。

---

## Q2：这不就是 Chat with CSV？

回答：

> ChatCSV 通常是问答层；FitzSight 是 investigation workflow。用户不需要知道要查哪张表、写什么 SQL、做什么统计。Agent 负责构造并验证调查链。

展示：

- trace；
- queries；
- tests；
- evidence。

---

## Q3：LLM 会不会胡说？

回答：

- numeric claims only from tools；
- evidence registry；
- verifier；
- confidence；
- reject unsupported claims。

---

## Q4：为什么用 synthetic data？

回答：

1. 金融数据高度敏感；
2. 可公开；
3. 可复现；
4. 能建立 Ground Truth；
5. 使 Agent 能被定量评测。

---

## Q5：合成数据是不是没有业务价值？

回答：

> Demo 数据是合成的，但 schema、KPI、异常调查 workflow 和 Tool contract 面向真实企业数据设计。工具层与数据源解耦，可替换为真实数据库。

---

## Q6：为什么要 Agent？

回答：

普通 fixed pipeline：

```text
固定问题 → 固定分析
```

Agent：

```text
开放业务问题
→ 动态计划
→ 选择工具
→ 根据中间结果调整调查
→ 验证
```

---

## Q7：你怎么评估它？

回答：

- root-cause accuracy；
- numeric accuracy；
- evidence coverage；
- hallucination；
- tool success；
- task completion。

---

# 35. Competition Pitfalls / 比赛特别注意

## 35.1 不要把“500 万奖池”当项目商业模型

奖金是 upside，不是 expected revenue。

---

## 35.2 不要过度依赖官方算力补贴

Boundless 当前初赛开发资源补贴：

> 单队价值上限约 200 RMB，且依审核/排名发放。

项目必须能在合理成本下运行。

---

## 35.3 决赛原则上线下杭州

提前考虑：

- 时间；
- 出行；
- 电脑；
- 网络；
- 备用 Demo。

---

## 35.4 比赛规则可能更新

每天至少一次：

```text
Official Website
Official Group
Email
```

---

## 35.5 项目知识产权

官方协议当前表述：

- 自己的作品知识产权原则上仍归参赛者；
- 组委会可在赛事合理展示、宣传、案例等范围使用已提交的公开材料；
- 第三方依赖和数据授权责任由团队承担。

因此：

- 商业秘密不要放 PPT；
- secrets 不要上 GitHub；
- 未授权数据不要提交。

---

# 36. Web / Community Intelligence / 网络公开讨论结论

截至 2026-08-11，公开网络的特点是：

### 事实

这是首届赛事。

因此公开内容主要是：

- 官方公告；
- 合作方解读；
- 赛道导师文章；
- 参赛项目实践；
- 技术踩坑。

缺乏：

- 往届参赛者复盘；
- 获奖者奖金体验；
- 长期品牌认可度数据。

所以不能把“没看到负面评价”等同于“经过多年验证”。

---

## 36.1 从 Agent Infra 公开实践中可迁移的经验

虽然我们参加的是 Boundless Agents，不受 AgentTeams 必选规则约束，但 Agent Infra 的导师/参赛实践透露的工程审美仍非常值得参考：

### 经验 A

> Agent 数量不是越多越好。

真正重要的是：

- 职责边界；
- 独立输出；
- 工具；
- 验证。

### 经验 B

> 最小可信闭环比“大而全平台”更重要。

### 经验 C

> 结论应该有多来源证据。

### 经验 D

> Mock 数据和真实工具最好使用相同 Schema。

这对我们的 synthetic dataset → future real DB migration 非常重要。

### 经验 E

> 系统必须承认自己的边界。

因此 README 必须有：

```text
Limitations
```

---

# 37. Product Differentiation / 差异化

## 37.1 不做股票分析 Agent

原因：

- 同质化高；
- 数据接入成本；
- 财经新闻 + LLM 总结已非常常见；
- 容易被问“为什么不是现有工具？”；
- 可能触碰投资建议边界；
- 无法最大化参赛者的真实经历。

---

## 37.2 不做传统财报 RAG

典型：

```text
Upload annual report
→ ask questions
```

过于接近：

- RAG；
- document QA；
- summarizer。

Boundless 官方不鼓励单点问答。

---

## 37.3 我们真正的差异化

```text
Agentic Data Analysis
+
Financial Operations
+
Statistical Validation
+
Synthetic Benchmark
+
Evidence Trace
```

---

# 38. Innovation Claims / 可用于 PPT 的创新点

## Innovation 1 — Investigation Agent

从开放业务问题自主构建分析链。

## Innovation 2 — Evidence-linked Claims

每个关键业务结论绑定 Tool Evidence。

## Innovation 3 — Synthetic Financial Operations Benchmark

不是只提供 Demo 数据，而是：

- 场景；
- anomaly；
- ground truth；
- evaluation。

## Innovation 4 — Statistical Verification

把 Data Science 验证嵌入 Agent workflow。

## Innovation 5 — Compliance-aware Action Boundary

Agent 可以分析，但不自动执行高风险金融动作。

---

# 39. Success Metrics / 项目成功标准

## 初赛成功

- [ ] 项目定位明确
- [ ] PPT 完成
- [ ] 至少一个可运行 MVP
- [ ] Architecture 清晰
- [ ] Synthetic scenario 清晰
- [ ] Demo 有真实 Tool call
- [ ] 不泄露数据

---

## 复赛成功

- [ ] ≥3 benchmark scenarios
- [ ] Root cause evaluation
- [ ] Evidence coverage
- [ ] Repo 可运行
- [ ] UI 可演示
- [ ] Demo 稳定
- [ ] Compliance 完整

---

## 决赛成功

- [ ] 5–8 min 内讲清问题
- [ ] Live Demo <3 min
- [ ] No demo crash
- [ ] Q&A 可回答
- [ ] 评委能复述我们的核心差异

---

# 40. Development Priorities / 开发优先级

## P0 — 必须

- synthetic dataset
- one anomaly
- SQL tool
- KPI tool
- statistics tool
- evidence registry
- one Agent workflow
- final report
- simple UI
- PPT

## P1 — 进入复赛后

- more scenarios
- verifier
- benchmark
- segmentation
- trace visualization
- deployment

## P2 — 决赛

- better UX
- real DB connector demo
- multi-model support
- advanced causality
- richer reports

## P3 — 比赛后

- enterprise auth
- RBAC
- streaming
- CRM connectors
- scheduled analysis
- SaaS deployment

---

# 41. Suggested Development Backlog

## EPIC A — Data

- [ ] A1 schema
- [ ] A2 generator
- [ ] A3 CRM event
- [ ] A4 whale withdrawal
- [ ] A5 channel degradation
- [ ] A6 ground truth files
- [ ] A7 data dictionary

## EPIC B — Analytics

- [ ] B1 KPI definitions
- [ ] B2 period comparison
- [ ] B3 contribution analysis
- [ ] B4 stats
- [ ] B5 anomaly
- [ ] B6 segmentation

## EPIC C — Agent

- [ ] C1 intent
- [ ] C2 plan
- [ ] C3 tool selection
- [ ] C4 loop
- [ ] C5 verifier
- [ ] C6 report

## EPIC D — Evidence

- [ ] D1 evidence ID
- [ ] D2 tool logs
- [ ] D3 claim mapping
- [ ] D4 UI evidence

## EPIC E — UI

- [ ] E1 chat
- [ ] E2 KPI
- [ ] E3 trace
- [ ] E4 chart
- [ ] E5 report

## EPIC F — Evaluation

- [ ] F1 benchmark schema
- [ ] F2 root cause scoring
- [ ] F3 evidence scoring
- [ ] F4 hallucination scoring
- [ ] F5 latency/cost

## EPIC G — Competition

- [ ] G1 project summary
- [ ] G2 deck
- [ ] G3 architecture
- [ ] G4 video
- [ ] G5 README
- [ ] G6 submission

---

# 42. Definition of Done / “完成”的标准

一个 Feature 只有同时满足以下条件才算 Done：

- [ ] code works
- [ ] deterministic test where possible
- [ ] failure state handled
- [ ] output visible
- [ ] evidence logged
- [ ] README / docs updated
- [ ] no secrets
- [ ] demo tested from clean start

---

# 43. Anti-Scope-Creep Rules / 防止项目失控

每加一个 Feature 前问：

1. 它是否直接提高官方评审维度？
2. 它是否让 Killer Demo 更强？
3. 8 月 16 日前是否必要？
4. 有没有更简单实现？
5. 能否在 20 秒内向评委解释其价值？

如果：

```text
No
No
No
Yes
No
```

则：

> 不做。

---

# 44. Decision Log / 决策记录

## D-001 — 选择 Boundless Agents

**Decision:** Boundless Agents > Agent Infra / AI for Research / Embodied.

**Reason:** 与 Data Science + 金融经营数据分析经历匹配最高；产品/工程展示价值强；无需被 AgentTeams 固定生态强约束。

---

## D-002 — 选择 AI+金融

**Decision:** AI+金融。

**Reason:** 官方有企业经营与风险研判方向，且能最大程度利用既有领域经验。

---

## D-003 — 不做股票投资 Agent

**Reason:** 同质化、合规、经验匹配度低。

---

## D-004 — Synthetic Data First

**Reason:** 数据合规 + Ground Truth + Benchmark + 可开源。

---

## D-005 — Evidence First

**Decision:** 所有核心 claim 应链接 tool evidence。

---

## D-006 — Agent 数量服从任务

不为数量增加 Agent。

---

## D-007 — MVP 聚焦 Anomaly Investigation

核心：

> Why did X change?

---

## D-008 — 正式产品命名固定为 FitzSight

**Decision:** 所有维护中的代码、文档、包元数据、UI、PPT 与演示材料统一使用 **FitzSight**。Python import package 使用 `fitzsight`。历史 Git commit 不重写。

---

## D-009 — 代码交付包必须同步附带进度真源

**Decision:** 后续每次 AI 向用户交付新的 FitzSight 代码/文件包时，必须在同一 ZIP 中附带当次更新后的 `PROJFITZGERALD_PROGRESS.md`。

用户收到交付包后自行拆分：实现内容更新至 `AplusNeutrino/FitzSight`，进度真源更新至 `AplusNeutrino/My_Blog/docs/PROJFITZGERALD_PROGRESS.md`。

---

# 45. Known Unknowns / 尚待确认

- [ ] 团队人数最终限制
- [ ] 初赛 PPT 页数/大小限制
- [ ] 项目简介字符限制
- [ ] 是否必须 public repo
- [ ] Demo 视频长度
- [ ] 决赛每队路演时长
- [ ] 决赛答辩时长
- [ ] 交通住宿报销标准
- [ ] 官方评委名单
- [ ] Boundless 是否发布更详细 handbook
- [ ] 是否有指定技术/模型合作资源

这些必须以官方最新通知为准。

---

# 46. Submission Compliance Checklist

提交前：

- [ ] 所有数据来源可说明
- [ ] synthetic 标签明确
- [ ] 无真实用户 PII
- [ ] 无雇主内部信息
- [ ] API key 已清除
- [ ] `.env` gitignored
- [ ] third-party licenses
- [ ] model disclosure
- [ ] commercial API disclosure
- [ ] open-source boundary
- [ ] risk disclaimer
- [ ] README limitations
- [ ] claims reproducible

---

# 47. Source Intelligence / 资料来源

> 本节用于后续快速重新核验。**官方页面优先级最高。社区文章仅作为工程经验参考，不是赛事规则。**

## Official

### GOAI 官网

- https://www.goaihz.com/

### 官方报名公告

- https://www.goaihz.com/news/official-launch

### Boundless Agents 赛道详情

- https://www.goaihz.com/tracks?track=apps

### FAQ

- https://www.goaihz.com/faq

### 参赛协议

- https://www.goaihz.com/terms

### 官方新闻列表

- https://www.goaihz.com/news

---

## Community / Engineering Reference

### AgentTeams 实战复盘：OpsPilot Zero

- https://blog.csdn.net/pzb2000/article/details/163452517

可借鉴：

- 小闭环；
- 证据；
- Agent 数量不是越多越好；
- Mock / real tool schema；
- 风险等级；
- 承认限制。

### 多 Agent 运维系统设计复盘

- https://segmentfault.com/a/1190000048096834

### DevFlow AgentTeams 技术实践

- https://segmentfault.com/a/1190000048106565

> 注意：以上主要属于 Agent Infra 生态，不代表 Boundless 必须使用 AgentTeams。

---

# 48. 下一步立即执行 / NEXT ACTIONS

## 今天（2026-08-11）P0

### Step 1

创建 GitHub：

```text
FitzSight
```

### Step 2

上传：

```text
MASTER_PLAN.md
```

### Step 3

建立最小目录：

```text
FitzSight/
├── README.md
├── MASTER_PLAN.md
├── data/
├── generator/
├── app/
└── evaluation/
```

### Step 4

实现第一个 dataset：

```text
customers
sales_activity
deposits
withdrawals
business_events
```

### Step 5

注入：

```text
CRM Routing Change
```

### Step 6

不用 Agent，先用纯 Python / SQL 证明：

> Ground Truth 可以被找到。

### Step 7

然后再开始 Agent。

---

# 49. Final North Star / 项目北极星

如果开发过程中不知道下一步该做什么，就回到这一句话：

> **FitzSight 必须能让一个金融业务管理者提出“为什么这个指标变了？”，然后由 Agent 自主完成数据调查、统计验证和证据化解释，而不是只生成一个听起来像答案的文本。**

任何不帮助这个目标的功能，都不是当前优先级。

---

# 50. 项目最终价值，不以是否获奖为唯一衡量

理想情况下，本项目最终应该同时成为：

1. GOAI 参赛作品；
2. GitHub 开源项目；
3. AI Agent Engineering Portfolio；
4. Data Science Portfolio；
5. Financial Analytics Portfolio；
6. 面试中的完整案例；
7. 后续可继续扩展的真实产品原型。

因此即使赛事结果不确定，我们仍应确保：

> **每写一行核心代码、每做一个 benchmark、每补一份工程文档，都在积累可迁移的长期资产。**

---

# Appendix A — 项目一句话版本

> **FitzSight is an evidence-grounded financial operations intelligence agent that autonomously investigates business anomalies by querying enterprise-style data, performing statistical validation, and producing traceable, decision-ready insights.**

---

# Appendix B — 30 秒英文 Pitch

> Financial teams already have dashboards, SQL and BI tools, but answering a simple question such as “Why did net deposits fall this week?” can still require hours of manual investigation. FitzSight is an agentic financial operations analyst. It plans the investigation, queries the relevant data, drills into regions, sales teams and customer segments, performs statistical validation, and links every important claim back to executable evidence. Instead of chatting with a CSV, FitzSight turns a business question into a reproducible investigation and an auditable decision brief.

---

# Appendix C — 30 秒中文 Pitch

> 金融企业并不缺 Dashboard、SQL 或 BI，但当管理者问“为什么本周净入金下降”时，分析师仍需要在多张表、多个指标和大量人工判断之间反复切换。FitzSight 是一个金融经营分析 Agent：它能够自主规划调查、调用 SQL 和 Python、按区域和销售团队下钻、做统计验证，并把每一个重要结论绑定到可追溯证据。它不是“和 CSV 聊天”，而是把一个经营问题转化成一条可复现、可验证的分析闭环。

---

# Appendix D — GitHub Short Description

```text
Evidence-grounded AI agent for financial operations analytics, autonomous anomaly investigation, statistical validation and auditable business insights.
```

---

# Appendix E — 项目关键词

```text
AI Agent
Agentic Analytics
Financial Operations
Financial Analytics
Data Science
SQL
Python
Statistics
Business Intelligence
Anomaly Detection
Root Cause Analysis
Evidence Grounding
Synthetic Data
Benchmark
Human-in-the-loop
Open Source
```

---

**Last Updated:** 2026-08-11  
**Current Owner:** Project Team  
**Status:** Preliminary Competition Sprint  
**Single Source of Truth:** This document

---

# v0.4 Implementation Decisions (2026-08-11)

## D-011 — Planner output is untrusted and cannot generate SQL

The Agent planner can only choose from an approved high-level action policy. SQL and numerical calculations remain inside deterministic tools. Unknown actions, malformed JSON, executable SQL text in plan purposes, and unsupported intents are rejected.

## D-012 — Deterministic planner fallback is a required competition capability

The default Agent planner remains usable without an external model or network connection. A provider-neutral structured LLM adapter exists above the same constrained plan contract; future model providers may be connected without weakening the deterministic Tool Layer or evidence/verifier boundary.

---

# v0.5 Implementation Decisions (2026-08-11)

## D-013 — Expand by approved business intents, not unrestricted tool autonomy

FitzSight v0.5 adds a second explicit business intent, `net_deposit_anomaly_investigation`. Each supported intent has a fixed high-level action contract and a deterministic executor. The project will expand the approved intent catalog gradually rather than allowing an LLM to invent arbitrary workflows or tool parameters.

## D-014 — Net-deposit analysis distinguishes observed drivers from customer motives

The second benchmark may identify withdrawal pressure, concentration, and nearby operational events as supported observed drivers. It must not infer why customers withdrew, label customers as suspicious, or produce investment/compliance conclusions without separate evidence and authorization.

## D-015 — External model providers remain optional and bounded

The first concrete provider adapter uses the OpenAI Responses API with strict JSON-schema output and `store=False`. The local intent classifier and plan validator remain authoritative. An external model is optional; the deterministic fallback remains the default competition-safe path.

## D-016 — UI is a presentation layer, not an analytical authority

The Streamlit demo shell renders verified outputs and audit evidence. It must not recalculate business metrics or bypass the verifier. Final competition UI work should preserve this separation.


---

# v0.6 Implementation Decisions (2026-08-11)

## D-017 — Customer segmentation must be transparent and descriptive

FitzSight v0.6 introduces `behavioral_value_score_v1`, a deterministic segmentation based only on observable deposit value, trading volume and trading frequency. Hidden benchmark labels such as `customer_segment_gt` remain prohibited from normal Agent SQL. The segments are business-analysis groupings, not credit, AML, suitability, eligibility or adverse-action decisions.

## D-018 — The benchmark harness now reports evidence quality as a first-class metric

The benchmark runner reports scenario pass rate, root-cause scenario accuracy, mean evidence coverage, verifier-violation count and deterministic latency. Benchmark success therefore requires more than producing the expected headline number: the evidence and verifier path must also remain intact.

## D-019 — FitzSight is released under the MIT License

The public implementation repository uses the MIT License for the project-owned code. Third-party dependencies remain governed by their own licenses and are documented separately. This decision may be revisited only if a competition rule or future dependency creates a specific incompatibility.

## D-020 — UI charts and KPI cards are presentation-only

v0.6 UI code renders business KPI cards, intent-specific charts, plan trace and evidence cards from the verified Agent result. The UI is not allowed to recompute KPI logic or create a second, unverified analytical path.

---

# v0.7 Implementation Decisions (2026-08-11)

## D-021 — Acquisition analysis must separate volume, mix, and within-channel performance

The marketing-quality benchmark is not considered solved by observing that lead count increased while conversion fell. FitzSight must separately measure lead volume, acquisition-channel mix, and within-channel conversion performance so that “more leads” is not confused with “better business performance.”

## D-022 — Nearby events require falsification before causal attribution

A business event appearing near a KPI movement is context, not proof. v0.7 adds a deliberate false-correlation benchmark in which an office relocation occurs near an Asia FTD decline while the measurable deterioration is concentrated in Affiliate leads. The Agent must reject the office event as a supported cause.

## D-023 — Adversarial evidence/safety checks are a release gate

Release validation now includes scope-refusal, planner-policy, evidence-integrity, causal-overclaim, evaluation-boundary, and false-correlation cases. A benchmark headline is insufficient if the Agent can bypass the intended trust boundary.

## D-024 — Five scenarios complete the initial benchmark target

The initial five-scenario benchmark target is now complete: CRM routing, net-deposit withdrawal concentration, customer intelligence, marketing acquisition quality, and false-correlation falsification. Additional scenarios remain useful, but competition work should now prioritize demo/runtime validation and submission assets over expanding the catalog without a clear evaluation benefit.

---

# v0.8 Implementation Decisions (2026-08-11)

## D-025 — Stop expanding the benchmark catalog for the initial round

The five-scenario target is sufficient for the initial submission sprint. v0.8 prioritizes judge-facing clarity, runnable demo paths, reproducible submission assets, and submission preflight rather than adding more scenarios without a specific evaluation gap.

## D-026 — Competition presentation assets are generated from the verified project state

The formal initial-round PPTX/PDF summarizes the existing synthetic benchmark and safety evidence. Presentation files must not introduce new analytical claims that are not supported by repository evidence. The PDF is exported from the same PPTX and visually reviewed after rendering.

## D-027 — One-command startup must retain a deterministic fallback

`scripts/start_demo.py` selects Streamlit when the UI dependency is present, but automatically falls back to the deterministic CLI when it is not. A presentation environment must therefore remain usable without a cloud model or optional UI runtime.

## D-028 — Submission preflight is a release gate, not a portal-submission claim

The local preflight verifies required repository/submission assets, obvious secret leakage, generated-data exclusion, and presentation-file hashes. It cannot prove that the GOAI portal was successfully submitted; portal upload and confirmation evidence remain user-controlled external actions.


---

# v0.9 Implementation Decisions (2026-08-11)

## D-029 — UI presentation logic is pure and testable

KPI cards, chart specifications, investigation-trace rows and Evidence cards are derived by a pure presentation layer from the already verified Agent result. Streamlit is only a renderer. The UI must not become a second calculation path.

## D-030 — Competition-facing numbers must come from the current verified runtime

The pitch-deck builder generates demo-slide numeric claims from fresh deterministic Agent runs in a temporary synthetic-data directory. Current README/project-summary/pitch materials must be synchronized to the same fixed-seed runtime. Historical release artifacts may retain their historical numbers, but active submission assets may not rely on stale hardcoded benchmark values.

## D-031 — Offline demo artifacts are resilience assets, not live-runtime evidence

The self-contained HTML demo and MP4 backup are generated only from verified deterministic Agent outputs and provide a no-cloud presentation fallback. Their existence does not mark Streamlit or OpenAI live runtime validation as complete.

## D-032 — Provider telemetry records reproducibility metadata, never secrets or invented cost

A live OpenAI planner validation may record response ID, requested/returned model, token usage and measured planning latency. API keys are never emitted. Provider monetary cost is not hardcoded or estimated without a validated pricing source and actual usage evidence.

---

# v0.10 Implementation Decisions (2026-08-11)

## D-033 — Competition submission is user-manual only by default

FitzSight automation prepares, validates, hashes, renders, and packages local competition artifacts. It does not open or submit the GOAI portal, upload files, access Gmail for confirmation, send email, or perform other external account writes unless the user separately and explicitly requests a specific action. Repository evidence cannot be used as proof that portal submission occurred.

## D-034 — Final handoff must be self-contained and operator-oriented

The user should be able to take over with a single portable handoff packet containing the copy-ready portal text, PPT/PDF, offline demo/video, compliance/evaluation summaries, manual field map, runtime instructions, and submission checklist. Remaining external/runtime/rehearsal tasks must be clearly separated from completed local implementation work.

---

# v0.11 Implementation Decisions (2026-08-12)

## D-035 — The final-machine default must remain local and provider-safe

The one-command final-machine check may run deterministic local checks and probe a Streamlit process only through localhost. It must not call a live model provider by default. OpenAI live validation requires an explicit `--include-openai` opt-in and deliberately configured credentials/model access.

## D-036 — Final-machine readiness and external submission are separate truths

A machine can be locally demo-ready while GOAI portal submission remains incomplete. Final-machine reports therefore record local runtime/preflight/handoff state but never infer portal upload, final submission, email confirmation, or other external account actions.

## D-037 — Human rehearsal evidence must be human-performed

FitzSight may provide timing targets, operator cards, and a local timing recorder, but code presence or a synthetic timing value is not proof that the user performed a real pitch/demo/Q&A rehearsal. The corresponding roadmap tasks remain open until real user-provided rehearsal evidence exists.
