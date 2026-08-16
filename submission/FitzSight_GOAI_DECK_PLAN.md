# FitzSight_GOAI_DECK_PLAN

> **项目：** FitzSight — Financial Operations Intelligence Agent  
> **赛事：** GOAI 2026 · 无界应用｜Boundless Agents · AI+金融  
> **版本基线：** FitzSight v0.13.0 本地交付工作树（基于 `c0c70fc2`）  
> **内容模式：** Knowledge Cat · Source-To-Deck / Review-only  
> **本阶段：** 只定义内容战略、Deck Architecture、证据与声明边界；不制作 PPT/PDF，不套视觉模板，不制造图片。  
> **最终口径：** **Autonomous investigation. Human decision.**

---

## 1. Presentation Objective

在 12 页内完成一次评委认知转变：

- **看前：** “这是否只是另一个金融聊天机器人、BI Copilot 或 Chat with CSV？”
- **看后：** “这是一个面向金融运营分析师、已经实现完整任务闭环、用确定性工具和 EvidenceClaimVerifier 约束结论、并能在证据不足时停止归因的调查型 Agent。”

本 Deck 只证明四件事：

1. “Why did this KPI change?” 是真实、具体、尚未被 Dashboard/BI 完成的金融运营任务；
2. FitzSight 具备真实 Agent 闭环，而非 LLM 包装；
3. 欧洲 CRM / FTD Hero 能从问题走到受约束、可复算、可追溯的答案；
4. 差异不仅是找到证据，也包括拒绝虚假因果和在证据不足时 fail closed。

**Output lane：** `review-only / deck-plan`。下一阶段由设计 Skill 依据本文制作正式中文视觉稿。

## 2. Audience

**Primary Audience：** GOAI Boundless Agents 初赛评委。  
**Starting State：** 默认怀疑数字是否由模型编造、Demo 是否只有成功路径、架构是否超过实现、金融场景是否越权。  
**Desired Shift：** 评委确认 FitzSight 服务明确角色；模型只在受限目录内规划；关键数字来自确定性工具；重要结论绑定 Evidence ID；证据不足时停止因果归因。

## 3. Core Narrative

**Product：** FitzSight — Evidence-grounded autonomous financial-operations investigation  
**Primary User：** Brokerage / FinTech Operations Analyst  
**Secondary：** Regional Operations Manager / Sales Operations Manager

金融运营团队已经拥有 Dashboard、SQL、BI、Excel 和 reporting pipeline。真正昂贵的缺口不是“没有数据”，而是：

> 从 KPI 异常到可信解释之间，仍有一条跨表、跨周期、跨维度、跨统计检验和业务事件记录的人工调查链。

```text
Question
→ local intent boundary
→ constrained planning
→ approved analytical actions
→ deterministic SQL / Python tools
→ statistics / decomposition / segmentation / falsification
→ Evidence Registry
→ EvidenceClaimVerifier
→ verified decision-support answer
→ human decision
```

| 普通工具 | 能回答什么 | 关键缺口 |
|---|---|---|
| Dashboard / BI | What happened? | 仍需人工下钻、检验与对照 |
| Chat with CSV | 快速生成解释 | 规划、计算、证据与权限边界不可控 |
| FitzSight | What changed, where, which drivers, what evidence, what cannot be claimed | 有界调查、确定性计算、fail-closed 核验 |

**Source-of-Truth：** 实际代码/测试/runtime → 当前工作树及 `origin/main` → Tracker → 正式文档 → 旧 Pitch。赛事规则始终以 GOAI 手册为最高依据。详细 Hero runtime 来自 v0.12 确定性核心；v0.13 只迁移受限规划 Provider 与提交物，不扩展 action catalog、工具权限或金融决策权限。

## 4. One-sentence Story

> **FitzSight 把“为什么这个经营指标变了？”变成一条受约束、可复算、可追溯的调查链：模型可以规划，但数字归确定性工具，结论归证据核验，最终决策归人。**

## 5. Narrative Spine

**Spine：** Old workflow → bottleneck → why Agent → bounded mechanism → Hero process → Hero proof → refusal/failure → reuse → trust architecture → evaluation → responsible path forward

### Ghost Deck

1. FitzSight 把“为什么指标变了？”变成一条可核验的金融运营调查链
2. 看见 KPI 变化不难；昂贵的是分析师仍要手工拼起“为什么”
3. 这不是问答任务：调查会分支、调用工具、检验假设并决定何时停止
4. FitzSight 把问题送进受限闭环，只有通过证据核验的答案才能到达人
5. 一个问题触发九个批准步骤，运行轨迹对用户全程可见
6. 受影响团队 FTD 下滑 7.53 个百分点；对照组仅下滑 1.21 个百分点
7. 延迟、团队贡献、事件与文档证据把 CRM routing 推到“候选原因”，而不是“已证实因果”
8. 质量也体现在拒绝：邻近事件不是因果，证据缺口则停止归因
9. 同一套有界调查架构已覆盖五类金融运营问题，而不是五个互不相干的 Demo
10. DeepSeek 可以规划，但本地门控、确定性工具与 Verifier 掌握权限和事实
11. Holdout 与消融结果表明，Verifier gate 改变的是不安全输出率，而不只是展示方式
12. 当前 PoC 已开源并可复现；真实部署先补齐企业控制，最终决策仍由人完成

## 6. GOAI Score Strategy

六项权重：行业价值 25%、Agent 闭环 25%、产品/Demo 20%、技术 15%、安全可追溯 10%、开放复用 5%。前 8 页优先覆盖官方前 3 项的 70%。

| 维度 | 主承载页 | 策略 |
|---|---|---|
| 行业价值 | 1–3 | 锁定 Operations Analyst 与人工调查链；不造 ROI |
| Agent 闭环 | 3–8 | 门控、计划、工具、分支、Evidence、Verifier、失败、follow-up |
| 产品/Demo | 5–8 | runtime-derived Hero 为中心 |
| 技术 | 4、10、11 | 四个信任边界 + holdout/ablation |
| 安全/可追溯 | 7、8、10、12 | 因果护栏、fail closed、synthetic-only、human decision |
| 开放复用 | 9、12 | 说清可复用对象，不只写 Open Source |

**Guardrails：** 不制造市场规模/ROI；不把 synthetic benchmark 当真实客户；不把 100% pass 当真实准确率；不把 ablation 当 Generic LLM 对比；不把 DeepSeek Mock 当 live PASS；不把 blueprint 当已实现。

---

## 7. 12-page Main Deck
### Slide 1

**Action Title**  
**FitzSight 把“为什么指标变了？”变成一条可核验的金融运营调查链**

**Slide Role**  
Hook + product definition。第一屏消除“泛金融聊天机器人”的误解。

**GOAI Scoring Dimension**  
行业场景价值；Agent 能力与任务闭环。

**Judge Takeaway**  
FitzSight 的单位任务不是生成报告，而是完成一次带证据边界的金融运营调查。

**Core Content**

- Product：FitzSight — Financial Operations Intelligence Agent
- Primary user：Brokerage / FinTech Operations Analyst
- Core job：回答 “Why did this KPI change?”
- Promise：bounded investigation → deterministic evidence → verified decision support
- Tagline：**Autonomous investigation. Human decision.**

**Evidence**

- `README.md`
- `docs/INITIAL_ROUND_PROJECT_SUMMARY.md`
- `MASTER_PLAN.md` §1、§4–6
- GOAI 手册第 1–2、10–11、14–15 页

**Recommended Visual**  
Typography-led opening + compact chain：`KPI change → investigation → Evidence ID → human decision`。不放功能图标墙。

**Hero Number / Quote**  
**“Autonomous investigation. Human decision.”**

**Claims Allowed**

- 面向金融运营分析师的证据驱动调查 PoC；
- 当前实现包含受限规划、确定性工具、Evidence Registry 与 Verifier；
- 输出是 decision support。

**Claims Forbidden**

- 完全自主金融 Agent；替代分析师；production-ready；真实客户 ROI。

**Transition**  
既然团队已有 Dashboard 和 SQL，为什么还需要它？下一页进入尚未被现有工具消除的人工调查链。

---

### Slide 2

**Action Title**  
**看见 KPI 变化不难；昂贵的是分析师仍要手工拼起“为什么”**

**Slide Role**  
Tension。把痛点从“数据不足”改写为“调查链碎片化”。

**GOAI Scoring Dimension**  
行业场景价值。

**Judge Takeaway**  
Dashboard 已解决“发生了什么”，但跨表、对照、统计、贡献、事件与文档核验仍由分析师手工完成。

**Core Content**

- 已有工具：Dashboard、SQL、BI、Excel、reporting pipeline
- 真实提问：“Why did European FTD conversion deteriorate after July 15?”
- 手工链：找表 → 定时间窗 → affected/control → 统计检验 → 贡献分解 → 业务事件 → 文档证据 → 汇报
- 痛点是重复切换与证据链不统一，而非“不会算”
- 不宣称未经测量的节省时间或 ROI

**Evidence**

- `MASTER_PLAN.md` §4、§6
- `docs/INITIAL_ROUND_PROJECT_SUMMARY.md` — Problem
- `src/fitzsight/agent/catalog.py`

**Recommended Visual**  
Before-process swimlane：分析师跨越 Dashboard / SQL / Python / Event Log / Document / Report；突出手工交接点。

**Hero Number / Quote**  
**“从异常到可信解释之间，仍有一条昂贵的人工调查链。”**

**Claims Allowed**

- 当前 workflow 需要跨数据与验证步骤；
- FitzSight 的目标是编排并证据化该链条。

**Claims Forbidden**

- 节省具体小时数；减少具体人力比例；所有机构流程相同。

**Transition**  
这条链为何不是一次 SQL 或问答？下一页说明调查的状态、分支与停止条件。
---

### Slide 3

**Action Title**  
**这不是问答任务：调查会分支、调用工具、检验假设并决定何时停止**

**Slide Role**  
Diagnosis + Why Agent。正面回答为什么不是 Dashboard / BI / Chat with CSV。

**GOAI Scoring Dimension**  
行业场景价值；Agent 能力与任务闭环。

**Judge Takeaway**  
Agent 的必要性来自任务编排、结果条件分支、工具调用、证据状态和失败处理，而不是聊天界面。

**Core Content**

- Dashboard：预定义指标与筛选
- Chat with CSV：常把数据和解释权交给模型
- FitzSight：先识别批准意图；生成受限计划；工具结果控制下一批准分支；统计/分解/falsification 由确定性工具完成；证据不足即停止归因；只支持批准范围内 evidence-only follow-up

**Evidence**

- `src/fitzsight/agent/catalog.py`
- `src/fitzsight/agent/planner.py`
- `src/fitzsight/agent/orchestrator.py`
- `tests/test_v12_hero_journey.py`
- `docs/V0.12_HERO_RUN.json`

**Recommended Visual**  
Dashboard / Chat with CSV / FitzSight 三列比较；只比较“分支、数字所有权、证据、失败状态、权限”。

**Hero Number / Quote**  
**“Agent 的价值不是多说一步，而是知道下一步能做什么、不能做什么、何时停止。”**

**Claims Allowed**

- Hero 使用结果条件触发的批准分支；action sequence 与 follow-up 都是封闭目录；数字不由 Planner 计算。

**Claims Forbidden**

- 任意自主 planning；任意多轮；任意工具发现/自由 SQL；多 Agent 协作。

**Transition**  
下一页把这种 Agent 性落实为可检查的成功路径与失败路径。

---

### Slide 4

**Action Title**  
**FitzSight 把问题送进受限闭环，只有通过证据核验的答案才能到达人**

**Slide Role**  
Mechanism。建立 Demo 心智模型，并提前展示 fail-closed 分支。

**GOAI Scoring Dimension**  
Agent 闭环；技术深度；安全与可追溯。

**Judge Takeaway**  
从输入到 human decision 的每层都有所有者；失败是系统状态，不是小字免责声明。

**Core Content**

```text
Question → Local intent gate → Constrained plan
→ Approved analytical actions → Deterministic SQL/Python
→ Evidence Registry → EvidenceClaimVerifier
→ Verified answer → Human decision
```

```text
unsupported intent / tool error / missing corroboration / verifier violation
→ error or boundary Evidence
→ insufficient_evidence / withhold answer
→ human review
```

**Evidence**

- `docs/ARCHITECTURE.md`
- `src/fitzsight/agent/orchestrator.py`
- `src/fitzsight/agent/verifier.py`
- `tests/test_v12_hero_journey.py::test_event_tool_failure_withholds_root_cause_but_keeps_verified_answer`

**Recommended Visual**  
水平闭环 + 明确的下方 failure rail；不要画成“LLM 位于中心并直连所有系统”。

**Hero Number / Quote**  
**“Verification failure closes the output gate.”**

**Claims Allowed**

- supported claim 必须引用成功 Evidence；event dependency 失败会记录错误并降级 `insufficient_evidence`；最终判断由人完成。

**Claims Forbidden**

- 所有工具故障自动恢复；Verifier 等同监管认证；人工确认已接入企业审批系统。

**Transition**  
闭环已定义；下一页用 runtime-derived Hero trace 展示它如何运行。
---

### Slide 5

**Action Title**  
**一个问题触发九个批准步骤，运行轨迹对用户全程可见**

**Slide Role**  
Product Demo setup。展示输入、计划、动作、状态、Evidence ID 与 follow-up。

**GOAI Scoring Dimension**  
Agent 闭环；产品体验与 Demo。

**Judge Takeaway**  
Hero 不是预写答案：它运行九个批准动作，并为每一步留下 Evidence。

**Core Content**

- Question：Why did European FTD conversion deteriorate after July 15?
- Planner mode：`deterministic_fallback`（详细 Hero runtime 的真实口径）
- 9 steps：schema → affected → control → statistics → contribution → anomaly → event → document → boundary
- 每步展示 action、status、reason、Evidence ID
- Follow-up：“What evidence supports the CRM routing change candidate?” → `verified_with_guardrail`
- Streamlit localhost health：HTTP 200 / `ok`；不等同 DeepSeek live

**Evidence**

- `docs/V0.12_HERO_RUN.json`
- `submission/FitzSight_Hero_Run_Trace.png`
- `submission/FitzSight_Hero_Run_Answer.png`
- `submission/FitzSight_Hero_Run_Evidence.png`
- `docs/V0.13_STREAMLIT_RUNTIME.json`

**Recommended Visual**  
以 runtime trace 为锚：左侧问题，中间 9-step trace，右侧 guarded answer/follow-up。可裁切现有 PNG，不得改写状态。

**Hero Number / Quote**  
**9 个批准步骤 · 18 条最终 Registry 记录 · follow-up verified_with_guardrail**

**Claims Allowed**

- runtime asset 来自确定性 Hero 执行；9 steps 已执行且 verification PASS；localhost Streamlit health 通过。

**Claims Forbidden**

- Hero 使用 live DeepSeek；DeepSeek 延迟/token/成功率已验证；UI 已完成真实用户研究。

**Transition**  
过程可见还不够；下一页展示工具实际测量了什么。

---

### Slide 6

**Action Title**  
**受影响团队 FTD 下滑 7.53 个百分点；对照组仅下滑 1.21 个百分点**

**Slide Role**  
Hero quantitative proof。用 affected-vs-control 与统计检验把“变化”变成可复算证据。

**GOAI Scoring Dimension**  
产品/Demo；Agent 闭环；技术深度。

**Judge Takeaway**  
FitzSight 先测量受影响组、对照组和响应延迟，再决定是否继续下钻。

**Core Content**

- Europe Team A+B：23.37% → 15.84%，**-7.53 pp**
- Two-proportion：p = **0.00235**；95% CI = [-11.86, -3.20] pp
- European control：21.88% → 20.66%，**-1.21 pp**
- Affected response median：94.30 → 123.45 min，**+29.15 min**
- Mann–Whitney p = **1.86e-17**
- n：affected 2452 → 322；control 3483 → 513

**Evidence**

- `docs/V0.12_HERO_RUN.json`，Evidence `E0003`–`E0006`
- `docs/V0.12.1_BENCHMARK_RESULTS.json`

**Recommended Visual**  
Affected vs control 的 pre/post slope 或 paired bars；旁边只留一个 latency callout。方法与样本量放可读脚注。

**Hero Number / Quote**  
**-7.53 pp affected vs -1.21 pp control**

**Claims Allowed**

- 合成 benchmark 中 affected 变化更大且检验显著；响应时间中位数增加；证据支持继续调查。

**Claims Forbidden**

- 对照本身证明 CRM change 造成下降；p-value 证明因果；数字来自真实公司/客户。

**Transition**  
显著变化只说明值得下钻；下一页解释 CRM routing 为何只能称为 supported candidate。
---

### Slide 7

**Action Title**  
**延迟、团队贡献、事件与文档证据把 CRM routing 推到“候选原因”，而不是“已证实因果”**

**Slide Role**  
Hero resolution + evidence chain。把“找到原因”改为“多源证据支持候选解释”。

**GOAI Scoring Dimension**  
Agent 闭环；产品/Demo；安全与可追溯。

**Judge Takeaway**  
答案不是模型总结；六条 claim 逐条连接计算、事件和文档 Evidence，并经过 Verifier。

**Core Content**

- Team A 最大负向团队贡献：**-1.87 pp**
- 27 个 post-change 日中 **8 个**延迟异常
- Event：`EVT_CRM_ROUTING_20260715`
- Document：`CRM-CHANGE-2026-0715#p1`
- C1–C6 → E0003/E0005/E0006/E0004/E0009/E0011/E0013/E0014
- EvidenceClaimVerifier：**6/6 claims verified；0 violations**
- Final status：`supported_candidate`；不是自动证明的现实因果

**Evidence**

- `docs/V0.12_HERO_RUN.json`
- `submission/FitzSight_Hero_Run_Evidence.png`
- `src/fitzsight/tools/document_evidence.py`
- `src/fitzsight/agent/verifier.py`

**Recommended Visual**  
Evidence chain / claim graph：comparison、statistics、contribution/anomaly、event/document → Evidence IDs → Verifier → guarded answer。中心标注 `supported_candidate ≠ confirmed cause`。

**Hero Number / Quote**  
**6/6 verified · 0 violations · supported_candidate**

**Claims Allowed**

- CRM routing 是该 synthetic benchmark 的 primary supported candidate；stable source/paragraph ID；贡献与异常来自确定性工具。

**Claims Forbidden**

- 已证明现实因果；production RAG；真实企业文档；Evidence ID 等于法律审计结论。

**Transition**  
可信系统还要拒绝诱人的错误解释和不完整证据。

---

### Slide 8

**Action Title**  
**质量也体现在拒绝：邻近事件不是因果，证据缺口则停止归因**

**Slide Role**  
Refusal story + fail-closed proof。唯一第二完整案例，连接 Safety、Verification 与 Technical Differentiation。

**GOAI Scoring Dimension**  
Agent 闭环；产品/Demo；安全与可追溯；技术深度。

**Judge Takeaway**  
FitzSight 会明确说明“我们不被允许得出什么结论”。

**Core Content**

**False-correlation guardrail**

- Asia FTD：**-8.13 pp**
- Affiliate FTD：**-15.81 pp**；p = **0.00463**
- nearby office relocation：found
- `nearby_event_cause_supported = false`
- `false_correlation_rejected = true`
- Verification：**4/4 PASS**

**Explicit failure branch**

```text
operational-event dependency fails
→ error Evidence
→ document corroboration unavailable
→ root_cause_status = insufficient_evidence
→ attribution withheld
→ bounded verified answer remains
```

**Evidence**

- `docs/V0.12.1_BENCHMARK_RESULTS.json`
- `docs/V0.12.1_ADVERSARIAL_RESULTS.json`
- `tests/test_v12_hero_journey.py`
- `docs/V0.12_HOLDOUT_RESULTS.json`

**Recommended Visual**  
Two-path refusal exhibit：左侧 temporal proximity 被截断、observed driver 指向 Affiliate-specific deterioration；右侧工具失败链落到 `insufficient_evidence`。

**Hero Number / Quote**  
**“它拒绝说什么，和它会说什么同样重要。”**

**Claims Allowed**

- 该 synthetic benchmark 不支持办公室搬迁为原因；event failure 会降级 attribution；一个 unseen CRM seed 返回 insufficient evidence。

**Claims Forbidden**

- 证明现实中搬迁绝无影响；已解决通用因果推断；能检测所有 false correlation；refusal 等于完整金融合规。

**Transition**  
Hero 与 refusal 证明深度；下一页用一张图证明架构的复用广度。
---

### Slide 9

**Action Title**  
**同一套有界调查架构已覆盖五类金融运营问题，而不是五个互不相干的 Demo**

**Slide Role**  
Breadth / Reusability proof。展示迁移能力，不稀释 Hero。

**GOAI Scoring Dimension**  
开放/复用；行业价值；Agent 闭环。

**Judge Takeaway**  
复用对象是“有界金融运营调查模式”，不是写死答案。

**Core Content**

| Approved intent | 分析模式 | 当前 synthetic evidence |
|---|---|---|
| CRM / FTD | affected-control + stats + contribution + event/document | Hero verified |
| Net deposits | deposit/withdrawal decomposition + concentration + control | 5 claims verified；top-11 withdrawal share 91.6% |
| Customer Intelligence | behavior features + descriptive segmentation | 6,770 customers；100% coverage；5/5 claims verified |
| Marketing lead quality | volume + mix + within-channel performance | +315.0% leads；-10.84 pp FTD；4/4 verified |
| False correlation | nearby event + falsification + causal guardrail | false correlation rejected；4/4 verified |

共同复用：intent boundary、action catalog、deterministic tools、Evidence Registry、Verifier、synthetic benchmark harness。

**Evidence**

- `src/fitzsight/agent/catalog.py`
- `docs/INITIAL_ROUND_PROJECT_SUMMARY.md`
- `docs/V0.12.1_BENCHMARK_RESULTS.json`
- `evaluation/benchmark_catalog.json`

**Recommended Visual**  
Capability matrix 或 hub-spoke；Hero/refusal 权重大，其余三个仅作 breadth proof。

**Hero Number / Quote**  
**5/5 fixed synthetic scenarios PASS**

**Claims Allowed**

- 五个批准 intent 在固定 synthetic benchmark 通过；核心安全/证据机制跨 workflow 复用。

**Claims Forbidden**

- 支持任意金融 KPI；可直连任意企业库；100% 真实准确率；segmentation 用于授信/AML/suitability。

**Transition**  
广度成立的前提是每个 workflow 都不能绕开同一权限边界。

---

### Slide 10

**Action Title**  
**DeepSeek 可以规划，但本地门控、确定性工具与 Verifier 掌握权限和事实**

**Slide Role**  
Technical trust boundary。只解释对评委有用的四个边界。

**GOAI Scoring Dimension**  
技术深度；安全与可追溯；Agent 闭环。

**Judge Takeaway**  
Planner/LLM output 是不可信输入；它不拥有 SQL、数字或金融动作权限。

**Core Content**

1. **Local intent gate before model execution**：目录外问题在网络前拒绝。
2. **Approved high-level actions only**：DeepSeek 只能返回固定 intent/action 顺序的 JSON purpose。
3. **Deterministic tools own every number**：read-only SQL、statistics、contribution、anomaly、segmentation、falsification。
4. **EvidenceClaimVerifier owns answer emission**：检查 Evidence、digest/status、因果措辞和 `_gt` 泄漏。

Explicit no-authority：任意 SQL/表/参数、交易、转账、冻结账户、联系客户、投资/授信/AML/suitability 决策。

Provider evidence：Flash/Pro whitelist、JSON Output、thinking disabled、timeout/error/invalid JSON/truncation/telemetry redaction 有 Mock tests；**DeepSeek live = not_requested**。

**Evidence**

- `src/fitzsight/providers/deepseek_planner.py`
- `src/fitzsight/agent/planner.py`
- `src/fitzsight/tools/sql.py`
- `src/fitzsight/agent/verifier.py`
- `tests/test_deepseek_planner.py`
- `docs/V0.13_VALIDATION.md`

**Recommended Visual**  
Layered trust architecture + authority legend：Question → local gate → DeepSeek/local planner → validator → tools → Evidence → Verifier；标明 can/cannot。

**Hero Number / Quote**  
**Planner output = untrusted input.**

**Claims Allowed**

- DeepSeek contract/error paths 通过 Mock；strict whitelist；deterministic fallback 可离线；SQL 仅 SELECT/WITH 且阻止外部扫描。

**Claims Forbidden**

- live DeepSeek PASS、延迟/token/cost；Hero 由 live DeepSeek 产生；供应商保证金融安全；已实现生产 SSO/RBAC/PII。

**Transition**  
边界是否改变行为不能只靠架构图；下一页用 holdout、对抗与消融给证据。
---

### Slide 11

**Action Title**  
**Holdout 与消融结果表明，Verifier gate 改变的是不安全输出率，而不只是展示方式**

**Slide Role**  
Evaluation proof。有 protocol、有 denominator、有失败样本的架构证据。

**GOAI Scoring Dimension**  
技术深度；Agent 闭环；产品/Demo；安全与可追溯。

**Judge Takeaway**  
FitzSight 没有抹平不足证据案例；去掉 verifier/evidence gate 后，同批 adversarial fixtures 全部输出不安全答案。

**Core Content**

**Fixed release gates**

- 5/5 synthetic scenarios PASS
- 8/8 adversarial cases PASS
- mean evidence coverage 100%；verifier violations 0

**Holdout seeds + paraphrases**

- 2 unseen seeds × 4 cases = 8 runs
- routing 100%；verification 100%；evidence 100%；false-correlation refusal 100%
- supported-candidate **75%**：一个 unseen CRM seed 返回 `insufficient_evidence`

**Controlled architecture ablation**

- Full FitzSight：adversarial unsafe-answer **0%**
- No-verifier-gate：adversarial unsafe-answer **100%**
- No-verifier emitted evidence coverage：66.7%
- 明确：architecture ablation，**不是 Generic LLM baseline**

**Engineering footer：** v0.13 `98 passed`；deterministic smoke `verified`；Streamlit health HTTP 200 / ok。

**Evidence**

- `docs/V0.12.1_BENCHMARK_RESULTS.json`
- `docs/V0.12.1_ADVERSARIAL_RESULTS.json`
- `docs/V0.12_HOLDOUT_RESULTS.json`
- `docs/V0.12_ABLATION_RESULTS.json`
- `docs/V0.12_EVALUATION.md`
- `docs/V0.13_VALIDATION.md`
- `docs/V0.13_STREAMLIT_RUNTIME.json`

**Recommended Visual**  
Three-tier evaluation exhibit；中心用 0% vs 100% bar；75% 用不同颜色标记“honest fail-closed result”，避免满屏绿勾。

**Hero Number / Quote**  
**Unsafe answer: 0% full vs 100% no-verifier gate**

**Claims Allowed**

- 指标只适用于指定 synthetic protocol/fixtures；holdout 覆盖两个 unseen seeds 与改写；gate 阻止四个 adversarial 输出。

**Claims Forbidden**

- 比所有 LLM 安全 100%；通用模型 benchmark 胜出；真实客户泛化/监管合格；DeepSeek 在线性能；75% 是真实根因准确率。

**Transition**  
最后说明哪些能力今天可复现，哪些必须在真实部署前补齐。

---

### Slide 12

**Action Title**  
**当前 PoC 已开源并可复现；真实部署先补齐企业控制，最终决策仍由人完成**

**Slide Role**  
Responsible close + open/reuse + next step。

**GOAI Scoring Dimension**  
安全与可追溯；开放/复用；行业价值。

**Judge Takeaway**  
团队清楚区分已实现与蓝图；可复用成果已存在，生产落地不会绕过企业治理。

**Core Content**

**Implemented / verified now**

- synthetic competition data only；five approved intents
- local intent gate + constrained planner
- deterministic read-only analytical tools
- append-only Evidence Registry + fail-closed Verifier
- fixed/holdout/adversarial/ablation evidence
- Streamlit local UI + deterministic fallback
- MIT code、tests、docs、generator、benchmark catalog

**Reusable contribution**

- bounded action pattern；deterministic tool contracts；synthetic generator
- benchmark/adversarial/evaluation cases；Evidence Registry / verifier；runbooks/docs

**Production blueprint — not current claims**

- SSO；RBAC/ABAC + row/field auth；PII masking/minimization
- tenant isolation；retention/deletion；observability/incident response
- legal/compliance/model-risk approval

Explicit boundary：不提供投资建议；不交易/转账/冻结账户；不做自动授信、AML enforcement、suitability/adverse action；不替代金融机构判断。

**Evidence**

- `LICENSE`；`THIRD_PARTY_NOTICES.md`
- `docs/COMPLIANCE_AND_SAFETY.md`
- `docs/ENTERPRISE_DEPLOYMENT_BOUNDARY.md`
- `README.md`
- `docs/V0.13_FINAL_MACHINE_READINESS.json`
- `../My_Blog/docs/PROJFITZGERALD_PROGRESS.md`

**Recommended Visual**  
Now / Reusable / Production Gate 三列矩阵；底部只留 closing line，不放虚构客户 logo。

**Hero Number / Quote**  
**Autonomous investigation. Human decision.**

**Claims Allowed**

- 项目代码 MIT；第三方依赖与 guizang AGPL 已披露；synthetic/evaluation assets 可复现；企业控制是 blueprint。

**Claims Forbidden**

- production-ready/compliance-certified；处理真实 PII；已实现 SSO/RBAC/PII/tenant；portal 已提交；真实用户 ROI 或 DeepSeek live。

**Transition**  
以清晰原则结束：先用可验证调查赢得信任，再进入受治理的真实部署。
---

## 8. Optional Appendix Recommendation

Appendix 不进入 12 页主叙事，仅用于追问，建议最多 6 页：

| Appendix | Action Title | 内容 | 证据 |
|---|---|---|---|
| A1 | 每条 Hero claim 都能回到原始 Evidence record | C1–C6 → E0003–E0014；digest/status；Verifier checks | `docs/V0.12_HERO_RUN.json` |
| A2 | Benchmark 数字有 protocol、sample 与适用边界 | fixed 5、adversarial 8、holdout 8、ablation 6 | Evaluation JSON + `docs/V0.12_EVALUATION.md` |
| A3 | 合成数据隔离真实客户，也隔离评测真值 | 表结构、seed、`*_gt` 禁止访问、synthetic documents | `docs/DATA_DICTIONARY.md`；generator；Verifier |
| A4 | Fail-closed 是可测试失败分支 | event failure；error Evidence；insufficient_evidence | `tests/test_v12_hero_journey.py` |
| A5 | DeepSeek 只替换受限 Planner | whitelist、pre-gate、JSON revalidation、telemetry redaction | Provider code + tests |
| A6 | 复现包分开代码、依赖、测试和提交边界 | README、lock、CI、final-machine、notices | v0.13 release assets |

## 9. Evidence / Asset Map

| ID | Source / Asset | Level | Main Use | Caveat |
|---|---|---|---|---|
| R1 | GOAI 手册第 7、10–15、19–20 页 | Official rule | 初赛、闭环、产品、安全、评分、红线 | 最新通知优先 |
| T1 | `../My_Blog/docs/PROJFITZGERALD_PROGRESS.md` | Tracker truth | v0.13、not_run、人工任务 | 本地分支未推送不等于 GitHub main 已更新 |
| C1 | `src/fitzsight/agent/catalog.py` | Code | 5 intents/action sequences | 不证明业务泛化 |
| C2 | `src/fitzsight/agent/planner.py` | Code + tests | classifier、validation、fallback | 非任意 planning |
| C3 | `src/fitzsight/providers/deepseek_planner.py` | Code + Mock | DeepSeek contract/boundary | live not requested |
| C4 | `src/fitzsight/tools/sql.py` | Code + tests | read-only SQL | 不是企业授权层 |
| C5 | `src/fitzsight/agent/verifier.py` | Code + tests | evidence/digest/causal gate | 不是监管审核 |
| H1 | `docs/V0.12_HERO_RUN.json` | Runtime | 9-step Hero、metrics、claims、follow-up | v0.12 deterministic core；v0.13 未改变 core authority |
| H2 | `submission/FitzSight_Hero_Run_Trace.png` | Runtime-derived image | Slide 5 trace | 可裁切，不改状态 |
| H3 | `submission/FitzSight_Hero_Run_Answer.png` | Runtime-derived image | Slide 5 answer | 标注 deterministic fallback |
| H4 | `submission/FitzSight_Hero_Run_Evidence.png` | Runtime-derived image | Slide 7 evidence chain | 不冒充 live DeepSeek |
| E1 | `docs/V0.12.1_BENCHMARK_RESULTS.json` | Evaluation | 5/5、breadth、false-correlation | fixed showcase seed |
| E2 | `docs/V0.12.1_ADVERSARIAL_RESULTS.json` | Evaluation | 8/8 policy/verifier checks | specified fixtures |
| E3 | `docs/V0.12_HOLDOUT_RESULTS.json` | Evaluation | unseen seeds、75% candidate | 2 seeds、2 workflows |
| E4 | `docs/V0.12_ABLATION_RESULTS.json` | Controlled evaluation | 0% vs 100% unsafe output | 非 LLM baseline |
| F1 | `tests/test_v12_hero_journey.py` | Test | fail-closed branch | simulated deterministic failure |
| V1 | `docs/V0.13_VALIDATION.md` | Release validation | 98 tests、scan、Provider Mock | 需回到原始证据追问 |
| V2 | `docs/V0.13_STREAMLIT_RUNTIME.json` | Local runtime | HTTP 200 / ok | health check，非用户研究 |
| V3 | `docs/V0.13_FINAL_MACHINE_READINESS.json` | Local readiness | core/smoke | DeepSeek not requested；Streamlit 分开引用 V2 |
| S1 | `docs/COMPLIANCE_AND_SAFETY.md` | Policy/map | non-use、synthetic、human review | 非合规认证 |
| S2 | `docs/ENTERPRISE_DEPLOYMENT_BOUNDARY.md` | Blueprint | Now vs production | blueprint-only |
| O1 | `LICENSE` + `THIRD_PARTY_NOTICES.md` | License | MIT/reuse/third-party | 第三方各自许可 |

**Design evidence priority：** 数字 H1/E1–E4；Demo H2–H4；边界 C1–C5/F1/S1–S2；当前状态 V1–V3/T1；规则 R1。禁止从旧 PPT/PDF 或旧 v0.9 Provider runtime 回填当前事实。

## 10. Claims Safety Matrix

| Topic | Allowed | Required Qualifier | Forbidden |
|---|---|---|---|
| Product | evidence-grounded operations investigation PoC | decision support；human decision | 自动金融决策、替代分析师 |
| Hero | -7.53 pp、-1.21 pp、+29.15 min | synthetic；supported candidate | 现实因果已证明 |
| Evidence | 6/6 verified；Evidence ID 可追溯 | current verifier protocol | 监管/法律审计 |
| False correlation | office relocation 未被 benchmark 支持 | temporal proximity ≠ causality | 现实中绝无影响 |
| Failure | dependency error → insufficient → withheld | simulated test | 所有生产故障都能恢复 |
| Benchmark | fixed 5/5；adversarial 8/8 | specified synthetic cases | 真实准确率 100% |
| Holdout | 8 runs；candidate 75% | 2 seeds × 2 workflows × 2 paraphrases | 通用泛化 |
| Ablation | full 0%；no-gate 100% unsafe | same 4 adversarial fixtures | 优于 Generic LLM |
| DeepSeek | whitelist/Mock/error tests PASS | live not requested | 在线成功/延迟/token/cost |
| Streamlit | localhost HTTP 200 / ok | health check | 完整 UX 验收 |
| Data | synthetic only | no real PII/employer data | 真实经纪商案例 |
| Segmentation | descriptive | no high-impact decisions | 授信/AML/suitability |
| Open | project code MIT | third-party separately licensed | 整包所有素材均 MIT |
| Production | controls are requirements | blueprint/roadmap | currently implemented/ready |
| Submission | PDF/local package prepared | portal remains manual | 已上传/已确认 |
---

## 11. Final Reviewer Assessment

> 以下是 Reviewer Stress Test 后的最终评分。已删除“多 workflow 平均展开”的旧结构；已将 refusal、fail-closed、holdout、ablation 和 implemented-vs-blueprint 提升为主 Deck 证据。

### Score

| Dimension | Score | Rationale |
|---|---:|---|
| Industry Value | **23 / 25** | Persona 与 KPI investigation gap 清楚；未造 ROI。尚无真实用户试点/量化影响。 |
| Agent Closed Loop | **24 / 25** | 输入、门控、计划、工具、分支、Evidence、Verifier、follow-up、failure 完整。Planner autonomy 有意受限。 |
| Product & Demo | **17 / 20** | 有 runtime-derived trace/answer、offline assets、Streamlit health。尚无用户研究、现场计时或 live DeepSeek。 |
| Technical Depth | **14 / 15** | deterministic tools、read-only SQL、evidence digest、Verifier、holdout、ablation 扎实。document corpus 非 production RAG。 |
| Safety & Traceability | **10 / 10** | false-correlation、insufficient_evidence、`*_gt` isolation、non-use、human decision 均进入主叙事。 |
| Open / Reuse | **5 / 5** | MIT code、generator、benchmark、tools、Registry、Verifier、docs、fallback 均为明确复用对象。 |
| **Total** | **93 / 100** | **初赛高可信竞争版本；剩余风险来自真实用户/现场/Provider 外部证据。** |

### Strong

- 一个 Hero 贯穿输入、9-step trace、KPI、Evidence、Verifier 与 guarded answer；
- refusal 是第二个完整行为证据，不是免责声明；
- 0% vs 100% ablation 证明 final gate 的功能作用；
- 75% candidate 诚实保留 insufficient-evidence 样本；
- 技术后置，前 8 页优先覆盖官方 70%；
- production blueprint 与当前 PoC 分离。

### Weak

- 业务数据全为 synthetic；
- 用户痛点主要来自 domain experience/workflow reconstruction，尚无访谈/时间研究；
- detailed Hero 使用 deterministic fallback，非 live DeepSeek；
- Streamlit 证据是 health check 与本地资产，不是系统化可用性研究；
- 文档证据是固定 synthetic corpus，非 production RAG。

### Missing

- 真实 Operations Analyst 试点反馈；
- 人工基线时间/质量对照；
- live DeepSeek latency/token/cost/stability；
- 真实 5–8 分钟 pitch 与 <3 分钟 Demo 计时；
- production identity/data-governance controls。

以上只能作为复赛路线图/问答，不得补写为初赛已完成。

### Risk of Overclaim

1. 把 `supported_candidate` 说成 root cause proven；
2. 把 5/5、8/8、holdout 100% 说成真实准确率；
3. 把 no-verifier ablation 说成 Generic LLM baseline；
4. 把 deterministic Hero screenshot 说成 DeepSeek live Demo；
5. 把 synthetic lookup 说成企业 RAG；
6. 把 local health check 说成完整产品验收；
7. 把 enterprise blueprint 说成 current capability；
8. 把 Open Source 写成无第三方许可边界的整体声明。

### Recommended Revision（已在本版执行）

- 改为一个 Hero + 一个 Refusal；
- 标题全部改为可争辩的 action titles；
- Hero 拆成 process、quantitative finding、evidence boundary 三页；
- false correlation 与 event-tool failure 统一为“拒绝完成不可信因果故事”；
- breadth 压缩一页；
- DeepSeek 明确 Mock PASS / live not requested；
- 主动展示 holdout 75% candidate 与不足证据；
- 结尾区分 implemented / reusable / production blueprint。

---

## HANDOFF TO DESIGN SKILL
| Slide | Final Action Title | Page Content | Visual Type | Evidence Asset | Emphasized Number / Quote | Speaker Intent |
|---:|---|---|---|---|---|---|
| 1 | FitzSight 把“为什么指标变了？”变成一条可核验的金融运营调查链 | Product、Primary User、core job、bounded investigation、human decision | Typography + compact process | `README.md`；Project Summary | “Autonomous investigation. Human decision.” | 排除“金融聊天机器人”印象 |
| 2 | 看见 KPI 变化不难；昂贵的是分析师仍要手工拼起“为什么” | Existing tools + manual cross-table investigation | Analyst workflow / swimlane | `MASTER_PLAN.md` §4、§6 | “从异常到可信解释的人工调查链” | 建立具体、无虚构 ROI 的痛点 |
| 3 | 这不是问答任务：调查会分支、调用工具、检验假设并决定何时停止 | Dashboard vs Chat with CSV vs FitzSight | Comparison matrix | planner/catalog/orchestrator；Hero test | “知道下一步与何时停止” | 证明 Agent 必要性来自任务状态 |
| 4 | FitzSight 把问题送进受限闭环，只有通过证据核验的答案才能到达人 | Success loop + explicit fail-closed rail | Closed-loop process | Architecture；Verifier；failure test | “Verification failure closes the output gate.” | 建立 Demo 心智模型 |
| 5 | 一个问题触发九个批准步骤，运行轨迹对用户全程可见 | Question、9 actions、Evidence IDs、follow-up | Runtime trace + answer | `FitzSight_Hero_Run_Trace.png`；`...Answer.png` | 9 steps；18 Registry records | 证明运行过程而非预写答案 |
| 6 | 受影响团队 FTD 下滑 7.53 个百分点；对照组仅下滑 1.21 个百分点 | affected/control、latency、p-values、sample sizes | KPI comparison | Hero JSON E0003–E0006 | -7.53 pp vs -1.21 pp | 展示确定性工具的第一层测量 |
| 7 | 延迟、团队贡献、事件与文档证据把 CRM routing 推到“候选原因”，而不是“已证实因果” | Team A -1.87 pp、8/27、event、doc、6/6 verifier | Evidence chain / claim graph | `FitzSight_Hero_Run_Evidence.png`；Hero JSON | 6/6；supported_candidate | 完成 Hero，限制因果措辞 |
| 8 | 质量也体现在拒绝：邻近事件不是因果，证据缺口则停止归因 | false correlation + dependency failure | Refusal bifurcation | Benchmark/adversarial；Hero failure test | rejected；insufficient_evidence | 把拒绝变成安全/技术差异化 |
| 9 | 同一套有界调查架构已覆盖五类金融运营问题，而不是五个互不相干的 Demo | Five intents + compact proof | Capability matrix / hub-spoke | catalog；benchmark；summary | 5/5 fixed scenarios | 证明复用，不抢 Hero |
| 10 | DeepSeek 可以规划，但本地门控、确定性工具与 Verifier 掌握权限和事实 | Four boundaries、no-authority、Mock/live line | Layered trust architecture | Provider/planner/SQL/verifier + tests | “Planner output = untrusted input.” | 解释真实权力分配 |
| 11 | Holdout 与消融结果表明，Verifier gate 改变的是不安全输出率，而不只是展示方式 | fixed、holdout 8、75%、ablation 0% vs 100%、98 tests | Evaluation stack + bars | benchmark/adversarial/holdout/ablation | 0% vs 100% unsafe | 用 protocol evidence 证明架构价值 |
| 12 | 当前 PoC 已开源并可复现；真实部署先补齐企业控制，最终决策仍由人完成 | Implemented / Reusable / Production Blueprint | Now / Reuse / Gate matrix | License；notices；safety/boundary | “Autonomous investigation. Human decision.” | 以克制、复现、清晰边界结束 |