# FitzSight — Initial-Round Portal Copy

> Prepared for user-manual submission. The user should verify the actual portal fields/limits immediately before upload. FitzSight automation prepares this copy but does not open, edit, or submit the portal.
>
> Official track page: https://www.goaihz.com/tracks?track=apps

## Project name

**FitzSight**

## Track

**Boundless Agents · AI+金融**

## One-line positioning

**Evidence-grounded Financial Operations Intelligence Agent**

中文：**面向 Brokerage / FinTech Operations Analyst 的证据驱动金融运营调查 Agent**

## Compact Chinese project introduction — 436 Chinese characters

FitzSight 是一个面向金融企业经营分析与风险研判的证据驱动 Agent。金融团队并不缺 Dashboard、SQL 或 BI，但当管理者追问“为什么净入金下降、转化率恶化或渠道质量变化”时，分析师仍需跨表查询、下钻、统计检验并人工整理证据。FitzSight 将问题转化为受约束的调查计划，由只读 SQL、Python 统计、贡献分解、异常检测与客户行为分层工具完成计算，再由 Evidence Registry 和 Verifier 将每条重要结论绑定到可追溯证据；模型只负责受限规划，不能生成 SQL、执行交易、冻结账户或自行计算关键业务数字。项目使用可复现合成数据，已实现 CRM/FTD、净入金、客户智能、营销线索质量和伪相关排除 5 个闭环场景；当前基准 5/5 通过，8 个对抗安全案例 8/8 通过。项目采用 MIT License，提供代码、示例数据生成器、测试、评测与部署文档，目标是把“问一个经营问题”变成可复现、可验证、可审计的金融经营调查。

## Short Chinese version

FitzSight 是一个证据驱动的金融经营分析 Agent。它把“为什么这个指标变了？”转化为受约束调查计划，通过只读 SQL、统计检验、贡献分解和异常检测完成计算，并用 Evidence Registry + Verifier 将重要结论绑定到可追溯证据。项目已实现 5 个金融经营闭环场景和 8 个对抗安全案例，使用合成数据、MIT 开源，并保留无云模型的确定性 Demo 路径。

## English project introduction

FitzSight is an evidence-grounded Financial Operations Intelligence Agent for business operations and risk analysis. It turns questions such as “Why did net deposits fall?” or “Why did conversion deteriorate?” into a constrained investigation plan. Read-only SQL and deterministic Python tools perform the calculations, while an append-only Evidence Registry and fail-closed Verifier bind each material claim to executable evidence. The model, when enabled, may plan only approved high-level actions; it cannot generate SQL, execute trades, freeze accounts, or calculate critical business metrics itself. The project uses reproducible synthetic data and currently implements five closed-loop workflows covering CRM/FTD anomalies, net-deposit shocks, customer intelligence, marketing lead quality, and false-correlation rejection. The five-scenario benchmark passes 5/5 and the adversarial release gate passes 8/8. FitzSight is MIT licensed and includes code, synthetic-data generation, tests, evaluation assets, deployment documentation, and deterministic offline demo paths.

## Repository

https://github.com/AplusNeutrino/FitzSight

## Suggested optional-demo description

A reproducible local demo is available through `python scripts/start_demo.py`. The deterministic fallback requires no cloud model. The package also contains a self-contained offline HTML demo and an H.264 MP4 backup generated from five verified Agent runs; Streamlit and OpenAI planner paths are optional runtimes and are separately validated when dependencies/credentials are available.

## Safety / compliance statement

FitzSight is analytical decision support only. It does not provide investment advice, automated compliance conclusions, credit decisions, suitability decisions, AML enforcement, trading execution, account freezes, transfers, or automated adverse customer actions. The competition build uses reproducible synthetic data and no real customer PII or former-employer confidential datasets.
## v0.12.1 reviewer-facing positioning

**Primary user:** Brokerage / FinTech Operations Analyst  
**Hero chain:** acquisition → FTD conversion → client-fund flows  
**Main story:** one bounded-adaptive CRM/FTD investigation + one false-correlation refusal.  
**Evaluation v2:** eight unseen-seed/question-paraphrase runs route and verify 8/8 with 100% evidence coverage; supported-candidate rate is 75% because one unseen CRM seed correctly returns `insufficient_evidence`. The controlled no-verifier-gate experiment is an architecture ablation, not a Generic LLM baseline.

Tagline: **Autonomous investigation. Human decision.**

