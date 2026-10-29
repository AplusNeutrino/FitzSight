# FitzSight 职业竞争力导向调整计划

日期：2026-10-26。核查仓库：AplusNeutrino/FitzSight。基线：main，ed61aa9c086d99b99b81a7e0467f44ee866c9d5e，v0.13.0。

## 一、结论与定位

建议保留“证据驱动的金融运营调查”主线，将 FitzSight 从固定场景竞赛 Demo 升级为“金融运营数据分析与可验证 AI 调查工作台”。优先服务金融数据分析、数据治理/数据开发、金融 AI 应用岗位。市场风险分析作为完成核心能力后的独立插件，不作为当前重写方向。

原因：当前代码已经具备 SQL、贡献分解、统计检验、客户分群、工具证据记录、受约束规划、结论核验与 Streamlit 界面。这些与用户的金融客户数据实习、数据科学背景及现有数据治理/评测方向存在连续性。转向全套投资组合/衍生品系统会新增大量业务与验证成本，削弱现有优势。

职业目标：让招聘方看到用户能定义金融业务指标、建设可信数据链路、解释指标变化、开发受约束 AI 应用，并用实验和测试证明结果。个人项目不能替代招聘明确要求的金融机构工作年限或实际生产经验。

## 二、招聘证据与解释范围

1. 南京证券官方社会招聘列表列有数据开发工程师岗；企业在智联招聘发布的 J11151 要求硕士、三年以上数据开发经验，涉及数据平台、客户画像、精准营销、运营、风控、数据建模，以及 Hadoop/Flink/Hive。来源：https://njzq.zhiye.com/social/jobs 与 https://www.zhaopin.com/jobdetail/CC544360620J40956892208.htm 。官方列表只证明岗位存在，具体要求来自企业招聘页。
2. 腾讯官方“金融科技-AI数据产品经理—数据开发方向”检索结果涉及数仓架构、数据治理和 SQL。来源：https://careers.tencent.com/jobdesc.html?postId=2047239002926510080 。网页正文动态渲染，仅使用检索可见要求。
3. 腾讯另一个官方招聘页明确列有统计建模、因果推断、Python/SQL/Spark、LLM/RAG/知识图谱及真实 DataAgent 工作流经验，支付/金融经验优先。来源：https://careers.tencent.com/jobdesc.html?postId=2090281754874265600 。用于参考能力组合，不视为南京岗位，也不代表个人项目可以满足其全职经验要求。
4. 滴滴官方数据研发工程师 JR20260421003 涉及 Fintech 背景、数仓分层设计、Hadoop/Hive/Spark 与调优。来源：https://talent.didiglobal.com/social/p/63334 。说明工程能力缺口，不能据此推断全行业岗位占比。

上述为截至查询日的公开岗位样本，不构成录用概率预测；职位可能下线。最终以投递时的官方要求为准。

## 三、代码现状与实测发现

### 已具备，应该保留

- `src/fitzsight/agent/catalog.py`：五类批准意图与工具动作目录。
- `src/fitzsight/tools/contribution.py`：对称分解总体转化率变化，区分组内表现与结构变化，并报告重建误差。
- `src/fitzsight/tools/statistics.py`：比例检验、连续变量检验及部分置信区间。
- `src/fitzsight/tools/sql.py`：单语句只读查询限制、危险关键字/外部函数拦截、结果行数限制。
- `src/fitzsight/evidence/registry.py`、`agent/verifier.py`：证据 ID、摘要、执行状态、引用检查与因果措辞边界。
- `data/store.py`：DuckDB 与 SQLite 后端；CLI、Streamlit、CI 及测试已存在。
- `scripts/run_evaluation_v2_holdout.py`：已有留出评测雏形，历史材料正确声明合成数据和实验边界。

### 需要优先修复

| 优先级 | 发现 | 影响 | 调整 |
|---|---|---|---|
| P0 | 最小构造中证据值为 0.1，声明为 99%，核验仍通过 | 引用存在不等于结论正确 | 结构化声明绑定指标、值、单位、时间窗与证据字段；数值重算和容差验证 |
| P0 | 两组均为 0/10 时比例检验抛 ValueError | 合法业务边界会中断调查 | 单独处理退化分布、小样本、缺失、无穷值；输出方法适用性状态 |
| P0 | 意图识别、查询、事件及文档引用绑定 Europe/具体日期/Team A+B | 换一个时期或地区难以复用 | 参数化请求与指标目录；演示配置独立于执行逻辑 |
| P0 | 数据不完整时 runtime 会自动生成合成 CSV | 外部数据接入时可能掩盖数据缺失 | 显式 demo/import 模式；import 缺表即报错，绝不自动补模拟数据 |
| P1 | 数据层主要是 CSV 视图/内存库 | 尚不能证明增量管道和长期运行能力 | 数据契约、分层、幂等增量、批次清单、异常隔离 |
| P1 | EvidenceRegistry 为内存列表，结果摘要未绑定完整数据快照和查询上下文 | 不是持久化、防篡改审计系统 | run_id、数据/配置/代码版本、持久化记录与重放；准确描述保护边界 |
| P1 | 留出评测为两个种子、两类场景、八次运行 | 很难证明跨场景泛化 | 机制、日期、地区、问题表达、质量故障分别留出 |
| P1 | 因果措辞拦截主要是有限英文正则 | 中文同义表达和数值语义未覆盖 | 声明类型驱动渲染，补充中英文误述案例 |

本次运行：`python -m pytest -q tests/test_sql_safety.py tests/test_statistics.py tests/test_evidence.py tests/test_multi_intent_planner.py`，13 passed。
另做两次独立最小探针，确认数值错配被放行及全零计数异常。
全量测试启动后因多个测试反复生成数据耗时较长，主动中止，没有全量通过结论。当前验证环境也不等同锁定环境：pytest 9.1.1、numpy 2.3.5、pandas 2.2.3、scipy 1.17.0；安装的 DuckDB 2.0.0 超出项目声明的 <2 范围，因此不把该环境当作 DuckDB 兼容性验收。未运行付费模型调用、未验证线上部署，未修改或推送远程仓库。

## 四、目标产品与范围

典型用户：金融运营分析师、数据分析师、数据团队或 AI 应用团队。
典型流程：选择数据集和口径 → 选择指标/地区/渠道/时间窗 → 检查数据质量 → 计算变化及贡献 → 核验数值/证据 → 输出事实、候选解释、局限与建议补充的数据。

首版保留三个核心问题：
1. 首次入金转化率为何下降？区分样本结构变化与组内转化变化。
2. 净入金为何下降？拆分入金、出金及客户集中度贡献，不推断客户动机。
3. 客户价值结构如何变化？明确是描述性行为分群，不作投资者适当性或信用评级。

国内展示场景优先补充“证券客户资金流与运营分析”，使用明确标注的合成数据和独立业务定义。不得把 deposit 简单改名为基金申购；基金场景必须另建订单、确认份额、净值、费用、申赎状态等模型。

## 五、分阶段路线图

工时是个人开发、学习、验证与文档的估计，不是 AI 输出代码耗时。核心约 170—240 小时；按每周 6 小时约 7—10 个月。各阶段通过后再进入下一阶段，可暂停，不要求一次做完。

### M0：建立可靠基线（8—12 小时）

任务：固定基线提交；检查锁定依赖可安装性；在隔离环境运行完整测试及五个演示流程；分开竞赛提交物与产品测试；生成现状矩阵；归档旧规划，保留竞赛版本入口。
交付：基线验证记录、问题清单、产品范围说明、架构图。
验收：记录通过/失败/跳过数量、原因和精确环境；新用户按命令可运行离线 Demo；不宣称未测功能通过。
能力证据：工程接手、缺陷定位、版本管理。

### M1：参数化与结果可信性（25—35 小时）

任务：新增 InvestigationRequest（metric、filters、baseline/current、timezone、currency、data_snapshot）；采用白名单参数和绑定查询；将固定场景从引擎移到 demo 配置。新增 MetricDefinition（分子、分母、去重键、时间归属、过滤状态、单位、版本）。新增结构化 Claim，绑定数值、证据路径和单位，由模板生成文字。处理零分母、全零/全一、小样本与非有限值；区分无法计算与零变化。运行时拆分 demo/import，导入缺表必须失败。
交付：参数化三条调查链、指标目录、数值核验器、反例测试。
验收：不改 Python 代码即可切换至少三个区域、三组时期；修改金额、百分点、币种、窗口或证据引用均被对应测试拦截；相同快照与请求得到相同结果。
个人掌握：解释“百分比”与“百分点”、分母变化、分组权重、因果与相关；手写一条关键 SQL。

### M2：可信数据管道（30—40 小时）

任务：建立 raw → staging → mart 分层；定义客户、现金流水、交易活动事实表及时间/渠道/区域维度。金额用定点数或最小货币单位；记录时区、状态、汇率日期。实现主键唯一、关联完整性、缺失、重复、晚到、状态变更与对账检查。增加导入批次清单、schema 版本、快照哈希；实现幂等写入、增量水位、回补及隔离区。运行数据不含 *_gt，真值单独保存在评测目录。
技术取舍：先沿用 DuckDB+Parquet/SQL；只有出现多用户写入需求时才引入 PostgreSQL；不要同时引入多个调度器。
交付：一条可重跑的增量链路、数据字典、质量报告、故障恢复说明。
验收：重复导入不重复计数；晚到和撤销可纠正；故障后重跑与全量重建一致；原始与汇总金额可对账；坏数据阻断或隔离并给出原因。
能力证据：金融数据口径、SQL、数据建模、数据质量、增量开发。

### M3：金融业务案例深化（25—35 小时）

任务：完成三份调查案例，每份都含问题、指标口径、数据契约、基线、结果、局限及下一步。重点打造“资金净流入下降调查”：区分资金流与收益、外部出入金与内部划转、成功与处理中/撤销；将客户集中度与资金余额/流动性指标分开。转化分析加入固定观察窗口，避免新获客客户尚未来得及转化造成假下降；分解性能效应与结构效应。分群规则版本化，展示分群稳定性和适用范围。
交付：业务定义文档、三份复现案例、一份失败/证据不足案例。
验收：三个不同种子和多组时间窗能正确运行；独立 SQL 或手算小样本对得上；报告不把净入金下降称为亏损，不把事件同期发生称为因果确定。
个人掌握：能在十分钟内讲清案例，不依赖提示词背诵。

### M4：服务化与运行可靠性（25—35 小时）

任务：提取服务层，使 CLI、UI、API 共用逻辑；提供调查创建、状态查询、结果、证据与健康检查接口；增加配置验证、超时、请求/会话隔离、错误分类、结构化日志。持久化 run_id、快照/代码/指标版本及执行记录。用 Docker Compose 提供演示部署；设置只读权限和资源上限；演示数据与外部导入分开；执行故障注入和恢复测试。
交付：API 文档、容器启动、运行说明、性能报告。
验收：同一请求跨 CLI/API/UI 的关键数字一致；重启后历史调查可查询；小规模并发会话不串数据；超时和后端不可用返回可解释错误；记录 10万/100万行合成数据上的耗时、内存和硬件条件。达不到某性能目标也必须如实记录。
不做：为了履历提前上 Kubernetes 或复杂微服务。

### M5：独立评测与 AI 增益证明（35—50 小时）

任务：保留规则规划器作基线；评测受约束模型规划器是否确有价值。测试集按场景机制、日期、区域、问题表达、数据质量故障拆分，不仅换种子。建议至少100个独立案例，覆盖5种机制和20个无变化/证据不足/数据错误案例；重复运行另行统计，不能算新案例。评测数值正确性、参数抽取、证据绑定正确率、错误断言率、正确拒答及过度拒答、延迟、token、成本。增加“合法 Evidence ID + 错数字”攻击。形成至少10份人工标准答案并盲审一部分；锁定测试集后不反复拿它调提示词。
交付：评测协议、案例清单、原始结果、对比表、错误分析。
验收：核心金额/比例/单位反例全部拦截；普通案例同时统计有用回答率，避免全拒答获得漂亮安全分；在线实验记录精确模型标识、日期、配置、样本数和成本；未调用模型时标注未测。大模型没有增益则保留可选，规则路径作为默认。
注意：100例是项目规模建议，不能据此声称生产级可靠性或真实业务收益。

### M6：求职展示与个人能力转化（22—33 小时）

任务：README 分成“招聘方快速了解”和“开发者复现”；提供中英文简介、三分钟录像、五分钟 Demo、架构图、三份案例、测试与评测报告、已知限制、变更记录。建立岗位—能力—代码—证据对应表。请2—3位有数据/金融/工程经验的人试用并记录反馈（需要本人邀请，不代发消息）。针对5—10份真实岗位逐项核对硬性要求。
验收：陌生人在新环境按说明可跑 Demo；用户可独立解释架构、关键公式、数据口径、测试设计和一个失败案例；能独立修改一条指标逻辑并补测试；简历只使用实测数字，明确个人项目、合成数据与 AI 辅助开发事实。
能力证据：技术沟通、业务表达、端到端交付、可验证所有权。

## 六、后续二选一扩展（不包含在核心工时内）

A. 数据工程主线（20—40小时）：若目标岗位明确要求分布式数据开发，选择 Spark 或 Flink 中一个，将既有流水聚合链路迁移并对比结果、成本、重跑与晚到语义。先完成单机正确性，不把本地启动等同生产集群经验。
B. 资管/市场风险主线（40—70小时）：新增独立组合插件，先做少量流动资产的历史收益、波动率、回撤与历史 VaR/ES，明确持仓口径、收益频率、币种、复权及费用。再补滚动样本外检验和压力情景。使用可合法获取和复现的数据，记录数据源、授权与缺失处理；不把 VaR 当作最大可能损失。进入此阶段前重新查验相应方法的权威资料和目标岗位要求。

核心未稳定前不新增信用评分、反洗钱判定、自动交易、完整衍生品定价、泛用多智能体体系。

## 七、建议架构与迁移原则

数据适配器 → 数据质量/快照 → 指标与语义层 → 确定性计算 → 结构化声明核验 → API/CLI/UI。
受约束规划器只在授权指标、维度和动作内组合请求；不承担金额计算。评测真值与运行数据物理隔离。持久化证据包括快照哈希、参数、SQL/工具版本、结果摘要和报告版本。

现有 `tools/`、`analytics/` 尽量复用；`agent/catalog.py` 拆成“能力目录+参数解析”；`investigation/` 去除固定地区和日期；`evidence/` 扩展持久化及语义核验；新增 `contracts/`、`metrics/`、`pipelines/`、`api/`、`evaluation/`。这些为建议目录，不要求第一天全部创建。

## 八、前三个可执行 PR

PR1 基线与缺陷：复现锁定环境、记录完整测试结果；加入数字错配、全零计数、import缺表三类回归案例；明确失败状态，不改业务定位。
PR2 指标与声明：完成净入金和转化率的 MetricDefinition/Claim 数据结构、数值/单位/时期验证；UI展示已核验字段。
PR3 参数化首个场景：将净入金调查改为受约束的区域/期间请求，旧演示问题作为兼容回归；明确内部划转与外部资金流的口径。

每个 PR 均需：一个明确业务问题、可检查改动、正确性证据、简短演示与局限。此文档只规划，不表示已经建立分支、提交或上线。

## 九、最终完成定义

项目可展示的完成：三条业务调查链可跨时间/地区复用；数据导入与质量检查可重跑；关键数值被验证；API与演示可运行；独立评测及失败案例可复现。
个人能力的完成：用户能独立解释、修改、测试和排障，而非仅能播放 AI 生成 Demo。
职业准备的完成：结合主业真实工程成果，得到目标岗位面试或同行有效反馈。FitzSight 贡献的是可检查的能力证明，不是保证就业或替代工作年限的证书。

## 十、持续执行台账（基线保留，追加更新）

一至九节是 2026-10-26 基线及当时观察；其中“本次运行”“未修改或推送”等描述仅指当时，不代表以下批次。原目标和验收标准不变。状态使用：待办 / 进行中 / 已完成 / 阻塞 / 待人工验收。已完成只覆盖对应任务范围，不能推导整个里程碑完成；后续拆分沿用编号并添加后缀。

| 稳定编号 | 范围（验收以第五节为准） | 状态 | 当前证据或缺口 |
|---|---|---|---|
| M0-01 | 固定远程基线、隔离锁定安装、全量测试 | 已完成 | 本轮验证记录；144 passed，未等同五流程演示 |
| M0-02 | 五流程离线演示、新用户复现命令 | 进行中 | CLI 已实跑；UI 与独立人工复现未验收 |
| M0-02a | 五类真实 CLI 子进程、两后端与复现说明 | 已完成 | RUN-20261027-02：10/10，合成数据、确定性规划器 |
| M0-02b | Streamlit 交互与独立新用户复现 | 待人工验收 | 不用 CLI 结果代替人工界面体验 |
| M0-03 | 产品/竞赛测试分组、现状矩阵、旧规划归档和入口、范围/架构说明 | 已完成 | RUN-20261027-03；123 产品 + 23 竞赛；现状矩阵与原位归档 |
| M1-01 | InvestigationRequest、参数白名单、三个区域/三组时期、demo 配置 | 进行中 | M1-01a绑定查询基础完成；固定地区/时间P0尚未解决 |
| M1-01a | 双后端原生SQL绑定、参数证据、净入金金额/区域查询迁移 | 已完成 | RUN-20261029-15；不等同完整请求参数化 |
| M1-01b | 首条净入金请求/指标目录、演示配置分离及三个区域/三组时期 | 进行中 | b-1净入金金额目录完成；请求和跨场景验收仍待办 |
| M1-01b-1 | 版本化净入金金额目录、证据快照及N-C1/N-C2口径核验 | 已完成 | RUN-20261029-16；仅三项金额定义，不代表数据治理完成 |
| M1-01b-1a | ISSUE-004净入金事件字段预检完整性 | 已完成 | RUN-20261029-17：六字段逐一缺失×双后端均在分析SQL之前拒绝 |
| M1-01b-2 | InvestigationRequest、demo分离、整链及固定Claim约束迁移 | 进行中 | 必须保留三个区域/三组时期及篡改验收，不只放开查询 |
| M1-01b-2a | 不可变请求契约、严格字段/日期/地区/币种校验与JSON往返 | 已完成 | RUN-20261029-18；未接入执行器，不代表整链参数化 |
| M1-01b-2b | 净入金四源文件内容指纹与请求显式核对 | 已完成 | RUN-20261029-19；非冻结快照，执行器绑定仍待办 |
| M1-01b-2c | 请求副本指纹核对、双后端物化输入会话及资源清理 | 已完成 | RUN-20261029-20；仅输入会话，调查引擎/CLI/UI绑定仍待办 |
| M1-01b-2d | 请求驱动金额执行、可信请求/SQL核验及三地区三时期双后端 | 已完成 | RUN-20261029-23；仅N-C1/N-C2，完整五声明/CLI/UI/demo迁移仍待办 |
| M1-01b-2e | 请求驱动N-C3集中度、原请求/前N配置及来源核验 | 已完成 | RUN-20261029-24；N-C4/N-C5与整链/demo/CLI/UI仍待办 |
| M1-02 | MetricDefinition、Claim、数值/单位/时期/证据绑定及反例 | 进行中 | N-C1—N-C4 已迁移；其他声明和通用指标定义仍待完成 |
| M1-02a | 净入金 N-C1 金额、单位、窗口、证据及模板校验 | 已完成 | RUN-20261027-05：28 契约测试及实际双后端校验 |
| M1-02b | 其余核心金额/比例声明、MetricDefinition 与 UI 标识 | 进行中 | N-C1—N-C4 已迁移；其他意图声明及通用指标/UI 仍待办 |
| M1-02b-1 | N-C2 存款/提款分量与原始结果重算 | 已完成 | RUN-20261027-06：针对性53、全量215、双后端CLI10/10通过 |
| M1-02b-2a | N-C3 零分母不伪装为0%及诊断传播 | 已完成 | RUN-20261028-07：针对性5、全量219通过；完整绑定仍待办 |
| M1-02b-2b | N-C3 分子/分母/客户数/窗口/来源数值绑定 | 已完成 | RUN-20261028-08：针对性87、全量249、双后端CLI10/10 |
| M1-02b-3a | N-C4 缺目标/对照地区与真实零变化区分 | 已完成 | RUN-20261028-09：针对性11、全量255通过；完整绑定仍待办 |
| M1-02b-3b | N-C4 区域人均金额、分母、窗口及来源绑定 | 已完成 | RUN-20261028-10：针对性98、全量288、CLI10/10；重算起点为SQL聚合 |
| M1-02b-4a | N-C5匹配事件措辞与驱动推断分离 | 已完成 | RUN-20261028-11：针对性23、全量298通过；独立绑定另列4b |
| M1-02b-4b | N-C5事件事实、窗口、来源及规范文字独立绑定核验 | 已完成 | RUN-20261028-12：契约97、全量339通过；固定场景/来源执行信任边界保留 |
| M1-02c-1 | ISSUE-005：N-C1/N-C2来源完整性及金额入口拒绝截断 | 已完成 | RUN-20261029-21；四来源×双后端上限边界；其他声明独立完整性待复核 |
| M1-02c-2 | N-C3/N-C4来源完整性专项核查及反例 | 已完成 | RUN-20261029-22；独立核验、区域入口及双后端上限边界 |
| M1-03 | 统计边界、零分母、非有限值与适用状态 | 进行中 | 子任务如下 |
| M1-03a | 二项计数全零/全一/稀疏/非法输入 | 已完成 | 39 项统计测试；明确 null 区间，常规公式兼容 |
| M1-03b | 连续样本非有限值/常量/小样本；调用链无法计算语义 | 已完成 | b-1/b-2验证通过；不代表抽样设计、因果或所有上游汇总均已核验 |
| M1-03b-1 | 连续检验有限实数一维输入校验，拒绝时不写成功证据 | 已完成 | RUN-20261028-13：统计94、全量394通过；常量/小样本仍待b-2 |
| M1-03b-2 | 常量/小样本/计算溢出适用状态与调用链无法计算语义 | 已完成 | RUN-20261028-14：针对性106、全量405通过；小样本并列采用保守不可用 |
| M1-04 | 显式 demo/import、导入缺表失败 | 已完成 | RUN-20261027-04：默认 import 无生成，demo 空目录初始化；文件保护及 CLI 回归 |
| M1-H | 本人讲解比例/百分点、分母、权重、因果并手写 SQL | 待人工验收 | 不由自动测试代替 |
| M2-01 | 第五节 M2 全部数据管道任务及对账/恢复验收 | 待办 | 依赖 M1 口径；执行前拆分子编号 |
| M3-01 | 三条金融调查案例、资金语义/观察窗/分解/分群与独立复算 | 待办 | 依赖 M1/M2 |
| M3-H | 本人十分钟案例讲解 | 待人工验收 | 不代为宣称掌握 |
| M4-01 | 服务/API、持久化、隔离/故障恢复、容器和规模性能实测 | 待办 | 依赖核心链路和数据契约 |
| M5-01 | 独立评测协议/留出、攻击测试、规则基线、原始结果 | 待办 | mock 不计作模型实测 |
| M5-H | 人工标准答案与独立盲审；需凭据的在线实验 | 待人工验收 | 未调用付费模型；在线未测须明确披露 |
| M6-01 | 中英文展示、复现、录像/Demo、案例/限制、岗位能力证据表 | 待办 | 依赖前期证据 |
| M6-H | 本人独立修改/讲解、陌生人复现、2—3人反馈及职业结果 | 待人工验收 | 不自动联系他人、不承诺就业 |
| EXT-CHOICE | 第六节 A/B 可选扩展 | 待办（可选） | 核心之外，须选择一个；不自动展开两个 |

### RUN-20261027-01（北京时间 2026-10-27 13:21）

- 批次：M0-01 + M1-03a；预算不超过两小时。先安装锁定环境，再修复统计边界，运行针对性和全量测试，最后记录并提交。不扩大到整个 M1。
- 验收：合法全零/全一不崩溃、稀疏样本概率有明确方法；非法计数拒绝且不写成功证据；普通样本兼容；全量无失败。均已获得本轮证据。
- 远程依据：起点 main `e8db233f81bd18c1375a137d5b2bb58494c97ef0`；代码基线 `ed61aa9c086d99b99b81a7e0467f44ee866c9d5e`；无未合并 PR，仓库未发现 AGENTS.md；已阅读 README、既有进度记录和完整计划。
- 完成：修复全零/全一计数异常；稀疏表改用 Fisher 双侧检验，输出适用性与方法；无效计数拒绝；不输出误导性的退化 Wald 区间。
- 涉及文件：`src/fitzsight/tools/statistics.py`、`tests/test_statistics.py`、本计划、`docs/validation/2026-10-27-statistics-baseline.md` 及同目录 pytest txt/xml 原始记录。
- 验证：锁定安装及 pip check 成功；统计 39 passed；全量 144 passed / 0 failed / 0 errors / 0 skipped，76.28 秒。环境、命令、限制见[验证记录](validation/2026-10-27-statistics-baseline.md)。合成/mock 测试不代表生产或在线模型收益。
- 提交依据：本记录与代码同提交，标题 `fix: handle sparse proportion tests and record locked baseline`；以以上 main 为父提交，使用 expected_sha 并发检查，禁止强推。若提交期间 main 更新，应先重新核对再提交。
- 已解决问题：第三节“全零 0/10 比例检验抛 ValueError”的计数边界由 M1-03a 解决，见常量、精确概率与非法输入测试。原问题历史保留；统计 P0 总项尚未关闭。
- 新问题：ISSUE-001，991361 条 generator.py timedelta 弃用警告（尚未解决）；ISSUE-002，连续变量非有限/常量输入未统一处理；ISSUE-003，稀疏差值区间不可用，已明确 null 和方法，不声称区间验收完成。
- 剩余与下一批：优先完成 M0-02 五流程独立离线演示及 M0-03 现状矩阵，检查并修复 ISSUE-001；随后推进 M1-02 数值绑定和 M1-04 import 缺表 P0。保持每批有独立验收，不扩展可选项目。
- 当前不存在只能等待人工的全局阻塞；保留定时任务继续推进。M0—M6 整体未完成，人工事项未代验收。


### RUN-20261027-02（北京时间 2026-10-27 15:21）

- 起点：重新读取远程 main `eeda4e457a76476eda40b450fdd62b4b6470919c`，独立 checkout；核对 README、完整本计划、PROJECT_PROGRESS、IMPLEMENTATION_STATUS、最近提交与实现。无未合并 PR，未发现 AGENTS.md 或前轮未完成的远程编辑。
- 批次范围：M0-02a 与 ISSUE-001；预算两小时以内。步骤：保存旧生成器指纹 → 修复标量时间运算 → 检验数据不变和弃用警告 → 运行五类 CLI/两后端 → 全量测试 → 写回证据及提交。不扩大为 M0 或 M1 整体完成。
- 验收及完成：三种种子七表（21/21）修复前后 CSV SHA-256 一致；生成器在弃用警告转错误条件下通过；五类真实 CLI 在 SQLite、DuckDB 共 10/10 通过。CLI 核验通过不代表数值绑定已实现。
- 涉及文件：`src/fitzsight/data/generator.py`、`tests/test_generator.py`、`scripts/check_offline_flows.py`、README、`docs/OFFLINE_DEMO_CHECK.md`、本计划及 `docs/validation/2026-10-27-run02*`、`2026-10-27-offline-flows.json`、`2026-10-27-generator-fingerprints.json`。
- 验证：生成器 3 passed；全量 `pytest -q -W error::DeprecationWarning` 为 145 passed / 0 failed / 0 errors / 0 skipped，100.56 秒，无警告摘要。隔离 CPython 3.12.14、NumPy 2.5.2、pandas 2.3.3、SciPy 1.18.0、DuckDB 1.5.5；pip check 无冲突。[完整记录](validation/2026-10-27-run02.md)。未测试付费模型、真实业务收益、部署或 UI 交互。
- 问题更新：ISSUE-001 已在锁定环境解决，改用标准库 timedelta，不屏蔽警告；证据为新回归测试、21 个生成表指纹及严格全量通过。前轮 991361 警告记录保留。ISSUE-002/003 和其余 P0 未解决，本轮无新增阻塞。
- 提交依据：本记录与修改同提交，标题 `fix: preserve demo data while removing timedelta warnings`；父提交为上述最新 main，推送使用 expected_sha 并发检查，禁止强推。
- 下一批：M0-03 产品/竞赛测试分类、现状矩阵及旧规划归档入口；随后 M1-04 导入隔离与 M1-02 数值绑定。M0-02b 和其他个人掌握/盲审/反馈保留待人工验收；还有可自动推进任务，不暂停。


### RUN-20261027-03（北京时间 2026-10-27 17:19）

- 远程基线：`8fa778bb23d2afcec2dc14dad5e7926fd7de40af`，重新 fetch 后独立 checkout；已读 README、计划全文、旧进度记录、CI、相关源码与测试。无未合并 PR，仓库未发现 AGENTS.md 或前轮仍在进行的远程工作。
- 批次：M0-03，预算两小时以内。步骤为分类测试 → 核对收集集合 → 分组实跑 → 建立源码/证据/缺口矩阵与产品范围架构 → 原位归档旧规划 → 记录并提交。验收保持默认测试无遗漏、两组无重叠、全组执行通过、历史正文保留及文档可定位。
- 完成：product/competition 分类及 CI 分步；混合留出测试拆成路由与历史结果检查，断言不减少；默认 146 = 123 + 23、交集为空。新增 `docs/PRODUCT_BASELINE.md`、`docs/archive/README.md`，旧文档增加当前计划入口，保留固定竞赛提交。M0-03 已完成；M0-02b 人工交互/独立复现仍未完成，不能宣称 M0 整体验收。
- 涉及文件：`tests/conftest.py`、`tests/test_v12_evaluation.py`、`pyproject.toml`、`.github/workflows/ci.yml`、README、MASTER_PLAN、PROJECT_PROGRESS、IMPLEMENTATION_STATUS、旧进度快照、本计划、上述新文档与 `docs/validation/2026-10-27-run03*`、测试分类 JSON。
- 验证：产品 123 passed（139.43 秒）、竞赛 23 passed（归档修改后重跑 2.56 秒），两组均无失败/错误/跳过；另组选集的 deselected 不计作跳过。采用 strict markers 和弃用警告转错误；pip check 无冲突。CPython 3.12.14、pytest 9.1.1、NumPy 2.5.2、pandas 2.3.3、SciPy 1.18.0、DuckDB 1.5.5。[本轮证据](validation/2026-10-27-run03.md)。远程 CI 尚未验收，不与本地结果混同。
- 问题更新：旧 MASTER_PLAN 与网站快照自称唯一真源的歧义已通过归档头注和入口解决，历史正文 2/2 保留校验通过。新发现限制：marker 分类不等于最小依赖隔离，收集仍导入全部模块；已在矩阵披露，本轮不新增依赖重构任务。原有数值绑定、连续样本、稀疏区间、导入模式缺口保持未完成。
- 提交依据：标题 `test: separate product checks from competition artifacts`，以本轮最新 main 为父提交，expected_sha 并发保护，禁止强推；代码与本记录同提交。
- 下一批：M1-04 显式 demo/import 与缺表不写入回归，随后 M1-02 数值/单位/时期绑定；保持离线，不自动启用付费模型。人工学习、盲审、同行反馈与职业结果不代验收。仍有自动推进事项，继续任务。


### RUN-20261027-04（北京时间 2026-10-27 19:23）

- 起点：重新读取远程 main `b42784a3b613983b46aef9a165b244b88bedbeaa`，独立 checkout；阅读 README、本计划全文、旧进度记录、runtime/store、CLI/UI 和调用点；无未合并 PR，未发现 AGENTS.md 或前轮远程重叠工作。
- 批次 M1-04，预算两小时以内：分离模式 → 显式迁移演示入口 → 增加文件保护与 CLI 测试 → 全量和两后端五流程 → 更新文档和提交。验收包括六张表逐一缺失拒绝、默认导入不创建/覆盖文件、非空残缺 demo 拒绝生成、完整 bundle 可读取且字节不变。
- 完成：runtime/CLI 默认 import；显式 demo 只初始化不存在/空目录，完整目录原样读取；加载失败关闭连接；CLI 输出模式；Streamlit/启动器/竞赛评测入口显式 demo。M1-04 生成边界验收已完成，不等于 M2 导入质量/契约验收或 M1 整体完成。
- 涉及文件：`src/fitzsight/runtime.py`、`scripts/agent_investigate.py`、`start_demo.py`、`final_machine_check.py`、`check_offline_flows.py`、既有 build/evaluation/benchmark/latency/validate 调用脚本、`streamlit_app.py`、新 `tests/test_runtime_data_modes.py` 与相关演示测试夹具、README、DATA_MODES/OFFLINE_DEMO_CHECK/PRODUCT_BASELINE、本计划及 run04 验证文件。
- 验证：针对性 20 passed（4.30 秒）；最终全量 163 passed / 0 failed / 0 errors / 0 skipped（62.70 秒），strict markers 与弃用警告转错误，无警告摘要；五类实际 CLI × SQLite/DuckDB 10/10。锁定 CPython 3.12.14、pytest 9.1.1、NumPy 2.5.2、pandas 2.3.3、SciPy 1.18.0、DuckDB 1.5.5；pip check 无冲突。[完整证据](validation/2026-10-27-run04.md)。全部合成/离线，mock 和通过的旧核验器不代表真实收益或数值绑定已完成。
- 问题解决证据：第三节“runtime 缺表自动生成 CSV”P0 由 M1-04 修复，原描述保留为历史；缺失文件、损坏文件、已有字节保护、CLI 缺表非零退出均有测试。新披露限制：demo 初始化不是多进程事务发布，使用单进程专用目录；独立 schema/质量/来源校验仍待 M2。没有新增全局阻塞。
- 兼容性：旧调用若依赖隐式生成，须明确 `data_mode="demo"` / `--data-mode demo`；已迁移仓库演示调用并通过回归。[迁移说明](DATA_MODES.md)。历史验证命令不改写。
- 提交依据：`fix: separate import runtime from synthetic demo generation`；以本轮最新 main 为父提交，expected_sha 并发检查、不强推。代码和进度同提交。
- 下一批：M1-02 从核心指标 Claim 的数值/单位/证据字段绑定和错数字反例入手，再推进参数化及连续样本边界。人工复现、盲审、学习讲解、反馈和职业结果保持待人工验收；仍有自动推进任务，继续执行。


### RUN-20261027-05（北京时间 2026-10-27 21:20）

- 基线：重新 fetch main `f5f85b6e3ba54502b541f75dcb4146044b99f915` 后独立 checkout，已读 README、计划全文、旧进度记录与 Claim/核验器/净入金实现。无未合并 PR，未发现 AGENTS.md 或前轮重叠远程工作。
- 批次 M1-02a，预算两小时以内：迁移 N-C1 → 绑定金额/单位/币种/区域/时间窗/证据字段 → 从四份 SQL 结果重算 → 模板文字一致性与反例 → 回归和提交。范围限定单条声明；M1-02 总项及原数值错配 P0 仍进行中，不削弱其余验收要求。
- 完成及验收：增加 NetChangeBinding 与规范渲染；错金额、单位、币种、窗口、字段、引用、中文错误文字、删除绑定/声明、重复声明、非有限/布尔/字符串/极大数均被相应用例拒绝；内部自洽但错误的分解也被原 SQL 结果重算拦截。现金流查询发现非 USD 拒绝，不做虚假汇率换算。
- 涉及文件：`investigation/numeric_claims.py`、`investigation/models.py`、`investigation/net_deposit.py`、`agent/verifier.py`（均在 src/fitzsight 下）、`tests/test_numeric_claims.py`、NUMERIC_CLAIMS、PRODUCT_BASELINE、本计划及 run05 验证记录。
- 验证：首轮数值+真实引擎 27 passed；补充边界后数值契约 28 passed；最终全量 191 passed / 0 failed / 0 errors / 0 skipped（244.01 秒），strict markers/弃用警告转错误，无警告摘要。双后端五类实际 CLI 10/10，SQLite/DuckDB 的 `numeric_binding:N-C1` 明确执行通过。[完整证据](validation/2026-10-27-run05.md)。
- 环境：旧临时 venv 的 Python 入口丢失，首个命令退出127、未执行测试；新建隔离环境按 requirements.lock 安装成功，pip check 无冲突。CPython 3.12.14、pytest 9.1.1、NumPy 2.5.2、pandas 2.3.3、SciPy 1.18.0、DuckDB 1.5.5。手算/合成数据与 Mock 不代表生产收益；未启用付费模型。
- 问题更新：N-C1 的“有效证据 ID + 错数字/文字”路径已修复；通用反例及其他声明仍未迁移，不关闭整个 P0。新明确边界：工具参数未签名、SQL 过滤/截断/源数据质量不是本轮校验对象；见 [契约说明](NUMERIC_CLAIMS.md)。环境问题已通过重建解决，无全局阻塞。
- 提交依据：`feat: bind net deposit change claim to numeric evidence`，以最新 main 为父提交，expected_sha 并发检查、不强推；进度和代码同提交。
- 下一批 M1-02b：继续迁移其余净入金金额/比例声明，补通用 MetricDefinition 与 UI 标识；之后推进参数化和连续样本边界。人工复现、盲审、本人讲解、同行反馈和职业结果仍待人工验收；保留持续任务。


### RUN-20261027-06（北京时间 2026-10-28 03:16 完成验证）

- 起点：本批于10月27日读取 main `a73f87c101e56899be80bab2a1695b5e343dae10`、README、完整计划和旧进度、相关源码/测试/提交；10月28日03:13恢复时再次远程核对 main 未变、PR 为空，接续未提交工作，没有重复开发。仓库没有 AGENTS.md。
- 批次 M1-02b-1，预计工作量两小时以内：N-C2 绑定和规范文本 → 两个分量逐一重算 → 篡改/删除反例 → 回归与双后端CLI → 更新文档。验收范围限定 N-C2，不扩大为整个 M1-02。
- 完成：N-C2 绑定存款/提款变化及净变化、金额单位/USD/Europe/四个日期/证据；从原四份SQL结果重算。即使两个分量同时加100、净额仍正确、证据摘要和文字自洽，也被重算拒绝。删除绑定/必需声明、重复、错误类型、文字、来源引用及非法数字不能绕过。
- 文件：src/fitzsight 下 investigation/numeric_claims.py、investigation/net_deposit.py、agent/verifier.py；tests/test_numeric_claims.py；NUMERIC_CLAIMS、PRODUCT_BASELINE、本计划及 docs/validation/2026-10-27-run06*。
- 验证：针对性53 passed（5.46秒）；全量215 passed（66.83秒），无失败/错误/跳过/警告摘要，strict markers、弃用警告转错误；两后端五类真实CLI 10/10，N-C1和N-C2校验均明确通过。[完整记录](validation/2026-10-27-run06.md)。使用手算/合成数据，Mock仅分支测试，不代表生产收益、UI或人工盲审。
- 环境：旧入口探测退出127、新安装未完成时测试退出1（pytest缺失）均未运行测试；恢复后完成锁定安装，pip check无冲突，再执行上列验证。CPython3.12.14、pytest9.1.1、NumPy2.5.2、pandas2.3.3、SciPy1.18.0、DuckDB1.5.5。未启用付费模型或云资源。
- 问题更新：N-C2有效证据配错分量的路径已解决，见补偿性篡改反例；一般数值P0仍未关闭。没有新增全局阻塞。参数/来源结果信任边界、SQL过滤/截断、数据质量等限制继续保留。
- 提交依据：`feat: verify net deposit decomposition against source amounts`；以上最新main为父提交，expected_sha并发检查、不强推；本记录与代码同提交。
- 下一批：M1-02b继续迁移N-C3集中度比例及分母口径，随后其余声明、通用MetricDefinition/UI；M0-02b与独立盲审、本人学习讲解、同行反馈、职业结果保持待人工验收。仍有可自动推进事项，持续任务不暂停，M0—M6整体未完成。

### RUN-20261028-07（北京时间 2026-10-28 05:19）

- 起点：重新读取远程main `466b1b6e1608ee81502caa36fa6df43fef76711f`，fetch后独立checkout；核对README、计划全文、PROJECT_PROGRESS、IMPLEMENTATION_STATUS、相关提交及实现。没有AGENTS.md、未合并PR或前轮远程重叠编辑。
- 批次 M1-02b-2a，预算两小时以内：先修复N-C3零分母口径 → 传播无法计算状态到声明/诊断 → 双后端导入测试 → 全量回归 → 记录提交。N-C3完整绑定单列M1-02b-2b，不用本轮结果代替。
- 完成：本期提款总额不为正时集中度为null，附unavailable状态与原因；N-C3为insufficient_evidence，集中度高低诊断为null，驱动类型undetermined，不再显示0%。空CSV在DuckDB中推断为文本金额导致SUM失败，已用显式数值转换修复本调查的聚合。
- 文件：src/fitzsight/investigation/net_deposit.py、tests/test_net_deposit_agent.py、NUMERIC_CLAIMS、本计划和docs/validation/2026-10-28-run07*。
- 验证：针对性5 passed（25.29秒），涵盖正常案例和空表/全零提款×两后端真实导入。全量219 passed（83.80秒），无失败/错误/跳过/警告摘要，strict markers及弃用警告转错误。[执行记录](validation/2026-10-28-run07.md)。首次夹具漏planner导致4失败；修正后发现空表类型与测试日期序列化问题，原始失败日志均保留，未冒充通过。本轮未重跑五类CLI。
- 环境：复用隔离环境并重新核实CPython3.12.14、pytest9.1.1、NumPy2.5.2、pandas2.3.3、SciPy1.18.0、DuckDB1.5.5；pip check无冲突。全部合成数据，无付费模型/云资源、金融交易或对外联系。
- 问题更新：N-C3零分母伪装为0%的问题及该调查空表DuckDB聚合失败已修复，证据为双后端实际导入测试。数值绑定P0未整体解决；全报告含date对象不能直接用默认json.dumps，既有CLI有自身序列化路径，本轮仅验证集中度null可序列化，不声称统一服务序列化已完成。
- 提交依据：`fix: distinguish unavailable withdrawal concentration from zero`；以上最新main为父提交，expected_sha并发检查、不强推。
- 下一批：M1-02b-2b绑定集中度分子/分母/客户数/日期/来源并补篡改反例；随后通用指标目录、参数化及连续统计边界。M0-02b及学习讲解、盲审、同行反馈和职业结果继续待人工验收。仍有可自动推进任务，不暂停，不宣称M0—M6完成。

### RUN-20261028-08（北京时间 2026-10-28 07:20）

- 基线：远程main `549cbc1dcd7326d9c555cceaac702571ebb784e8`；重新fetch独立checkout，已读README、计划全文/进度、旧状态文档、近期提交及相关代码。仓库无AGENTS.md，未合并PR为空，未发现前轮重叠远程工作。
- 批次M1-02b-2b，两小时以内：结构化绑定 → 源明细按客户重算 → 文本/状态一致性 → 篡改与删除反例 → 全量和双后端CLI → 更新提交。范围只覆盖N-C3，不关闭整个数值P0。
- 完成：ConcentrationBinding绑定比例、分子/分母、客户数、单位、币种、区域、起止窗口及来源；按customer_id重算前N客户金额与总额，独立于排名SQL汇总。核验要求恰有一个N-C3；零分母必须null/证据不足，规范文本不可随意改写。
- 验收：手算A=30+20、B=10、前1占50/60；错比例/金额/单位/币种/区域/窗口/客户数/引用/字段、中文错误文字、删除绑定/声明、重复声明被拒绝；篡改汇总结果并同步比例和文字仍被来源重算拦截。旧N-C1/N-C2反例补合法N-C3，避免无关失败冒充旧契约验证。
- 文件：src/fitzsight/investigation/concentration_claims.py、models.py、net_deposit.py、agent/verifier.py；tests/test_concentration_claims.py、test_numeric_claims.py；NUMERIC_CLAIMS、PRODUCT_BASELINE、本计划及run08验证文件。
- 验证：针对性87 passed（26.58秒）；双后端五类真实CLI 10/10，N-C3检查在SQLite/DuckDB均明确通过。全量249 passed（87.57秒），无失败/错误/跳过/警告摘要，strict markers及弃用警告转错误。[完整证据](validation/2026-10-28-run08.md)。全部手算/合成/既有Mock数据，不代表生产收益或人工验收。
- 环境：复用隔离环境重新检查，CPython3.12.14、pytest9.1.1、NumPy2.5.2、pandas2.3.3、SciPy1.18.0、DuckDB1.5.5；pip check无冲突。未调用付费模型、云资源或执行交易/联系他人。
- 问题更新：N-C3有效引用配错比例/分子/分母路径已修复，零分母规则保留并核验。来源负值/非有限/非USD失败关闭；统一数据质量报告待M2。SQL过滤/截断、参数可信性、快照等边界尚未解决，无新增全局阻塞。
- 提交依据：`feat: bind withdrawal concentration to customer source totals`，使用上述main为父提交及expected_sha并发检查，不强推。
- 下一批：迁移N-C4区域人均金额及对应分母；随后通用指标目录、参数化和连续统计边界。M0-02b、独立盲审、本人讲解、同行反馈和职业结果仍待人工验收。仍有自动可推进事项，任务继续，M0—M6未整体完成。

### RUN-20261028-09（北京时间 2026-10-28 09:23）

- 起点：远程main `6ba1a03a6b3029c5f84065a99f66a2180b9458e1`，旧工作区维护清理后重新clone并核对HEAD；读取README、计划全文与台账、旧进度/实现状态、近期提交及相关源码测试。无AGENTS.md、未合并PR或前轮远程重叠编辑。
- 批次M1-02b-3a，两小时以内：N-C4缺失口径 → null及原因/状态传播 → 实际CSV导入双后端测试 → 全量回归 → 写回提交。N-C4完整数值绑定单列M1-02b-3b，原验收要求不降低。
- 完成：缺目标地区或没有可计算对照地区时，不再补0美元；人均零分母为null，缺失一期变化为null；对照仅计算有效地区并记录数量。N-C4为insufficient_evidence、比较诊断为null；真正零变化仍computed。
- 验收：只保留欧洲、只保留非欧洲、存提款全零，分别在SQLite/DuckDB实际import→SQL→引擎→核验；正常及原有零提款用例保留。针对性11 passed（57.30秒）。全量255 passed（115.88秒），无失败/错误/跳过/警告摘要，strict markers及弃用警告转错误。[证据](validation/2026-10-28-run09.md)。客户过滤产生的孤立流水仅用作边界输入，不代表M2关联完整性通过。
- 文件：src/fitzsight/investigation/net_deposit.py、tests/test_net_deposit_agent.py、NUMERIC_CLAIMS、本计划及docs/validation/2026-10-28-run09*。
- 环境：新建隔离venv按requirements.lock安装成功，pip check无冲突；CPython3.12.14、pytest9.1.1、NumPy2.5.2、pandas2.3.3、SciPy1.18.0、DuckDB1.5.5。合成数据不代表生产收益；本轮未重跑五类CLI或调用付费模型/云资源，未执行交易或对外联系。
- 问题更新：N-C4缺失比较伪装零变化的路径已修复，证据为双后端缺失反例与真实零值正例。完整数值绑定仍未完成；客户分母仍是当前表，注册时点/历史快照/币种/非有限值/地区键/数据契约问题保留，不关闭一般数值P0。无新增全局阻塞。
- 提交依据：`fix: preserve unavailable regional comparisons instead of zero`；上述main为父提交，expected_sha并发检查、不强推；代码与进度同提交。
- 下一批：M1-02b-3b绑定N-C4两期区域金额和客户分母、窗口、来源，再推进通用指标目录与参数化。M0-02b、独立盲审、本人讲解、同行反馈和职业结果仍待人工验收。仍有可自动推进事项，继续任务，不宣称整体完成。

### RUN-20261028-10（北京时间 2026-10-28 11:17）

- 起点：远程main `da0b27a7510ae24411633523dccbd9c2531f09b0`；重新fetch独立checkout，读取README、完整计划/台账、旧进度与实现状态、近期提交及相关实现。无AGENTS.md、未合并PR或前轮重叠远程工作。
- 批次M1-02b-3b，两小时以内：两期区域金额/客户数/窗口/来源绑定 → SQL聚合结果重算 → 文字与缺失状态核验 → 篡改/双后端测试 → 全量与CLI → 更新提交。不扩大为通用指标目录或数值P0全部验收。
- 完成：RegionalBinding保存两期各地区金额、客户分母、目标变化和对照中位数、币种/单位/区域/日期及四个来源；重新计算每期人均净额之差，再算对照中位数；唯一必需N-C4、绑定/派生结果/文字一致性和缺失状态检查。区域SQL拒绝非USD/缺币种现金流，不混合标价。
- 验收：手算欧洲基线(100-20)/2=40、本期(90-30)/3=20、变化-20，对照10/30中位数20；篡改金额/分母/单位/币种/区域/日期/引用/文字、同步修改派生数字及文本、删除/重复声明均拒绝。缺目标/对照null规则保留；非欧洲EUR在双后端实际导入拒绝。
- 文件：src/fitzsight/investigation/regional_claims.py、models.py、net_deposit.py、agent/verifier.py；tests/test_regional_claims.py、test_numeric_claims.py、test_net_deposit_agent.py；NUMERIC_CLAIMS、PRODUCT_BASELINE、本计划及run10验证文件。
- 验证：针对性98 passed（54.18秒）；双后端五类实际CLI 10/10，N-C4检查均明确通过。全量288 passed（109.66秒），无失败/错误/跳过/警告摘要，strict markers及弃用警告转错误。[完整证据](validation/2026-10-28-run10.md)。旧反例保留合法N-C4防止无关失败；全部手算/合成/既有Mock，非生产收益、UI或人工盲审。
- 环境：旧venv入口失效探测退出127，未执行测试；新隔离环境锁定安装成功、pip check无冲突。CPython3.12.14、pytest9.1.1、NumPy2.5.2、pandas2.3.3、SciPy1.18.0、DuckDB1.5.5。未调用付费模型/云资源、交易或对外联系。
- 问题更新：N-C4有效引用配错人均金额/分母路径已修复，见手算与篡改测试；对照地区混合币种标美元问题增加拒绝路径。重算起点是SQL聚合，JOIN/COUNT DISTINCT/过滤/截断/签名和历史客户快照仍未独立验证。当前客户分母不代表历史期末注册基数；一般数值P0不关闭，无新增全局阻塞。
- 提交依据：`feat: verify regional per-customer claims against aggregate evidence`；上述main为父提交、expected_sha并发检查、不强推，代码和进度同提交。
- 下一批：核查N-C5事件缺失仍使用肯定文字的反例并绑定事实/措辞；随后其他意图数值契约、指标目录、参数化及连续统计边界。M0-02b、独立盲审、本人讲解、同行反馈、职业结果保持待人工验收。还有自动可推进事项，继续任务，不宣称整体完成。


### RUN-20261028-11（北京时间 2026-10-28 13:19启动，15:21续接核对）

- 起点：远程main `6bf58d6b9197ae8c466218ab5efefa45d7f24955`；重新fetch独立worktree，读取README、计划全文/台账、旧进度与实现状态、相关代码和近期提交。无AGENTS.md、未合并PR。续接时再次核对远程main未变化，接续已有工作，不重复开批次。
- 批次M1-02b-4a：检查事件匹配条件 → 修复生成文字 → 双后端实际导入反例 → 全量回归 → 更新提交。工作量小于两小时；续接只收尾已有批次。独立事件绑定列M1-02b-4b，原验收要求不降低。
- 完成：事件缺失时明确未找到匹配日志，不再断言事件存在，也不将“未找到”解释为现实中没有事件；存在事件时仅陈述日志事实，移除将其直接认定为提款驱动的文字。
- 验收：空日志、错误类型、错误地区、窗口外事件、存在事件但存提款全零，各在SQLite/DuckDB实际CSV导入后执行。检查匹配列表、诊断、状态、置信度和文字；全零现金流保留根因证据不足。针对性23 passed（108.53秒），全量298 passed（166.71秒），JUnit失败/错误/跳过均0，strict markers及弃用警告转错误，无警告摘要。[验证记录](validation/2026-10-28-run11.md)。本轮未重跑五类CLI/UI；合成数据非生产收益或人工盲审。
- 文件：src/fitzsight/investigation/net_deposit.py、tests/test_net_deposit_agent.py、docs/NUMERIC_CLAIMS.md、本计划及docs/validation/2026-10-28-run11*。
- 环境：复用隔离venv重新核对CPython3.12.14、pytest9.1.1、NumPy2.5.2、pandas2.3.3、SciPy1.18.0、DuckDB1.5.5，pip check无冲突。续接轮询进程句柄失效，完整测试输出和JUnit仍在，已核对；无付费模型/云资源、金融交易或对外联系。
- 问题更新：N-C5缺事件仍肯定表述、事件存在时过度推断驱动的生成路径已修复，双后端反例为证据。verifier尚未独立验证N-C5匹配事实/窗口/来源、唯一性及篡改文字，保持待办；一般P0不关闭，无新增全局阻塞。
- 提交依据：`fix: align operational event claims with matched evidence`；使用上述main为父提交及expected_sha并发检查、不强推，代码与进度同提交。
- 下一批：M1-02b-4b独立事件事实绑定及删除/重复/篡改反例，之后其他意图数值契约、指标目录、参数化及连续统计边界。M0-02b、本人讲解、独立盲审、同行反馈、职业结果保持待人工验收。仍有自动可推进任务，不暂停，不宣称M0—M6完成。


### RUN-20261028-12（北京时间 2026-10-28 17:12）

- 起点：远程main `85b4b7cd3514169fde658c4296a9906691a2c035`；重新fetch独立worktree，核对README、完整计划/台账、PROJECT_PROGRESS、IMPLEMENTATION_STATUS、相关实现和近期提交。无AGENTS.md、未合并PR或重叠远程工作。
- 批次M1-02b-4b，预计两小时以内：结构化事件绑定 → 从来源逐行匹配 → 唯一性/状态/文字核验 → 篡改及双后端回归 → 更新提交。只覆盖净入金N-C5，不关闭整个M1-02或一般数值P0。
- 实现：EventBinding绑定地区、类型、窗口、匹配ID及来源；核验器重新匹配完整SQL结果，检查规范文字、状态、置信度；要求恰有一个N-C5。拒绝缺绑定、错误ID/来源/窗口、删除/重复/篡改文字、截断/预览、坏日期、重复事件ID等；同步伪造“未找到”与文字仍被来源拦截。
- 文件：src/fitzsight/investigation/event_claims.py、models.py、net_deposit.py、agent/verifier.py；tests/test_event_claims.py、test_numeric_claims.py、test_net_deposit_agent.py；NUMERIC_CLAIMS、PRODUCT_BASELINE、本计划及run12验证文件。
- 验证过程：首轮8 failed、109 passed（252.52秒），SQLite日期被存为带时间字符串，新核验器误拒绝；补日期/无时区时间戳兼容及测试后，契约97 passed（9.28秒）。原失败txt/XML保留；旧数值反例均补合法N-C5，防止无关失败冒充验收。最终全量结果见下方及[完整记录](validation/2026-10-28-run12.md)。全部手工/合成输入，非生产收益或人工盲审；本轮未重跑CLI/UI。
- 环境：旧venv入口不存在，探测退出2未运行测试；新隔离环境锁定安装及editable安装成功，pip check无冲突。CPython3.12.14、pytest9.1.1、NumPy2.5.2、pandas2.3.3、SciPy1.18.0、DuckDB1.5.5。无付费模型/云资源、交易或对外联系。
- 问题更新：N-C5有效引用配错事实/文字的路径已有独立核验；SQLite兼容缺陷已修正并纳入回归。当前契约仍固定Europe和日期，仅批准查询；SQL执行、注册器真实性、现实日志完整性、整个diagnosis对象不在本批独立验收范围。带时区输入拒绝，时区参数化待M1-01；持久化审计待M4，无新增全局阻塞。
- 提交依据：`feat: verify operational event claims against source rows`；以上main为父提交及expected_sha并发检查，不强推，代码和进度同提交。
- 下一批：优先M1-03b连续样本小样本/常量/非有限边界，随后参数化首条净入金请求与指标目录、其他意图声明；不扩张可选项目。M0-02b、本人讲解、独立盲审、同行反馈及职业结果继续待人工验收。还有自动可推进事项，继续任务，不宣称M0—M6整体完成。

- 最终验收：全量339 passed（289.26秒），JUnit确认失败/错误/跳过均0，无警告摘要；包含两后端实际导入，首轮8项失败均在修复后全量通过。M1-02b-4b范围完成，原计划核心与人工事项继续保留。


### RUN-20261028-13（北京时间 2026-10-28 19:19）

- 起点：远程main `a57d367e681be998a24cde8e76f92e71bf14d054`；重新fetch并独立worktree，核对README、完整计划/历史进度、PROJECT_PROGRESS、IMPLEMENTATION_STATUS、近期提交及统计工具/调用链。无AGENTS.md、未合并PR或远程重叠编辑。
- 批次M1-03b-1，两小时以内：输入类型/维度/有限性校验 → 两种方法及两侧输入反例 → 正常迭代器兼容 → 全量回归 → 更新提交。M1-03b-2保留常量、小样本、计算溢出与调用链无法计算语义，不降低原验收标准。
- 完成：连续检验拒绝空样本、NaN/正负无穷、None、布尔、字符串、嵌套数组、复数及无法转浮点的巨大整数；所有拒绝都发生在写入成功证据之前。未知方法先拒绝且不消耗输入生成器。合法数值列表、NumPy数值和生成器保持相同结果。
- 文件：src/fitzsight/tools/statistics.py、tests/test_statistics.py、本计划及docs/validation/2026-10-28-run13*。
- 验证：统计94 passed（1.81秒），所有警告转错误；最终全量结果见下方及[验证记录](validation/2026-10-28-run13.md)。手工/合成输入，非生产收益或人工验收；未重跑CLI/UI。
- 环境：复用隔离venv、pip check无冲突，PYTHONPATH=src并核对模块来自本轮worktree。CPython3.12.14、pytest9.1.1、NumPy2.5.2、pandas2.3.3、SciPy1.18.0、DuckDB1.5.5。无付费模型/云资源、交易或对外联系。
- 问题更新：ISSUE-002中的非有限/错误类型输入写入成功统计证据路径已阻断，见两方法两侧反例；常量/小样本仍未解决，有限输入也可能在中间计算溢出，保留M1-03b-2。上游部分调用预先float转换，工具无法恢复转换前类型；统一导入数据质量待M2。本批无新增全局阻塞。
- 提交依据：`fix: reject invalid continuous samples before statistical evidence`；以上main为父提交、expected_sha并发检查，不强推，代码与计划同提交。
- 下一批：M1-03b-2方法适用状态、null传播与调用链反例，之后参数化净入金请求及指标目录。M0-02b、独立盲审、本人讲解、同行反馈和职业结果仍待人工验收；还有自动可推进事项，不暂停，不宣称整体完成。

- 续接收尾（北京时间2026-10-28 21:18）：重新核对远程main仍为上述提交、PR为空，检查既有修改与完整测试证据，未重复开批次。最终全量394 passed（318.77秒），JUnit失败/错误/跳过均0，strict markers及弃用警告转错误，无警告摘要。M1-03b-1已完成，M1-03b及统计P0整体未关闭。


### RUN-20261028-14（北京时间 2026-10-28 23:22）

- 起点：远程main `2e62762cbfec55ca5446ac88f4415668f73d85c5`；重新fetch独立worktree，核对README、计划全文/历史、PROJECT_PROGRESS、IMPLEMENTATION_STATUS、相关提交与源码调用点；无AGENTS.md、未合并PR或重叠远程工作。
- 批次M1-03b-2，两小时以内：明确方法适用性 → null/原因输出 → 调查链显著性传播 → 单元及双后端实际导入 → 全量回归 → 更新提交。保留离线确定性，不自动扩展置换/付费模型。
- 完成内容：Welch单侧不足2或双侧常量、秩检验全体常量/小样本并列分别返回不可用原因；数值警告/溢出失败关闭为null推断。普通无并列小样本仍执行精确秩检验。调查链仅显著性为true时进入事件归因，诊断不可用时为null而非false；描述性中位数变化仍可保留。
- 验证：针对性106 passed（17.40秒），所有警告转错误；含手算精确概率、异常及SQLite/DuckDB实际CSV导入常量响应时间。最终全量结果见下方与[验证记录](validation/2026-10-28-run14.md)。合成输入不代表生产收益或人工验收；本轮未重跑CLI/UI。
- 文件：src/fitzsight/tools/statistics.py、investigation/engine.py；tests/test_statistics.py、test_investigation.py；本计划及docs/validation/2026-10-28-run14*。
- 环境：复用隔离venv，pip check无冲突，PYTHONPATH=src并核对模块路径；CPython3.12.14、pytest9.1.1、NumPy2.5.2、pandas2.3.3、SciPy1.18.0、DuckDB1.5.5。未启用付费模型/云资源、金融交易或对外联系。
- 问题更新：ISSUE-002的连续检验常量/小样本/非有限结果及响应显著性传播已获得针对性证据；小样本并列保守不可用可能降低回答率，已披露，后续独立评测统计拒答。稀疏比例差值区间ISSUE-003仍待办，所有业务汇总/抽样设计/因果推断不由本批自动验收，无新增全局阻塞。
- 提交依据：`fix: preserve unavailable continuous inference through investigations`；以上main为父提交，expected_sha并发检查、不强推，代码和计划同提交。
- 下一批：参数化首条净入金请求及指标目录，或补稀疏比例差值区间方法；通用声明核验继续推进。M0-02b、独立盲审、本人讲解、同行反馈和职业结果保持待人工验收。仍有自动可推进事项，继续任务，不宣称整体完成。

- 最终验收：全量405 passed（330.29秒），JUnit失败/错误/跳过均0，无警告摘要。M1-03b范围完成；M1-03保留进行中，ISSUE-003及其余P0不关闭。


### RUN-20261029-15（北京时间 2026-10-29 01:18）

- 起点：远程main `e93396f5793e6c017bbf14d16b364ea8683ecb51`；重新fetch独立worktree，核对README、计划全文/台账、根目录PROJECT_PROGRESS与IMPLEMENTATION_STATUS、近期提交及源码/上轮测试证据。无AGENTS.md、未合并PR或远程重叠工作。首次读取旧进度误用docs路径失败，随后读取根目录真实文件，不依赖旧缓存。
- 批次M1-01a，两小时以内：双后端绑定接口 → 参数类型及证据 → 净入金金额/区域查询迁移 → 实际双后端小样本及全量回归 → 文档提交。检查发现SQL工具没有参数入口，先完成请求参数化的必要依赖，不将基础接口当成三个区域/三组时期验收。
- 完成：通过原生占位符传递日期/地区，表名限制为deposits/withdrawals；记录成功和失败调用的参数副本。类型/有限性校验先于执行；保留只读校验、行数限制和compact证据。说明见[SQL参数契约](SQL_PARAMETERS.md)。
- 验收：针对性33 passed（1.65秒），所有警告转错误。实际SQLite/DuckDB测试注入字符串原值匹配、日期首尾边界、pending排除、区域汇总手算30/7、参数副本、类型拒绝、参数数量失败证据及CTE/截断/compact路径。全量结果见收尾及[验证记录](validation/2026-10-29-run15.md)。手工/合成/既有Mock，不代表生产收益；未重跑CLI/UI或人工盲审。
- 文件：src/fitzsight/data/store.py、tools/sql.py、investigation/net_deposit.py；tests/test_sql_parameters.py、test_numeric_claims.py；SQL_PARAMETERS、本计划与docs/validation/2026-10-29-run15*。
- 环境：复用隔离venv，PYTHONPATH=src核对模块来自本worktree，pip check无冲突；CPython3.12.14、pytest9.1.1、NumPy2.5.2、pandas2.3.3、SciPy1.18.0、DuckDB1.5.5。未调用付费模型/云资源、金融交易或对外联系。
- 问题更新：SQL工具缺少绑定参数的依赖已解决；完整InvestigationRequest、MetricDefinition、事件及其他调查迁移、快照/历史客户/时区语义仍待办。绑定和参数记录不等于签名防篡改或业务口径核验；不关闭参数化P0，无新增全局阻塞。
- 提交依据：`feat: bind net deposit query values through both SQL backends`；以上main为父提交，expected_sha并发检查、不强推，代码与计划同提交。
- 下一批：M1-01b从净入金请求与指标定义入手，协调固定Claim核验和demo配置，保留三个区域/三组时期验收。ISSUE-003、其他意图声明及后续里程碑继续待办；本人学习、独立盲审、同行反馈、职业结果保持待人工验收。仍有自动可推进事项，继续任务，不宣称整体完成。

- 验证过程：首次全量1 failed、430 passed（194.20秒），旧币种拒绝测试的SQL替身未接收parameters；更新替身并新增日期/地区/占位符断言，原EUR必须拒绝断言保持。随后SQL与数值契约89 passed（1.59秒）；初次失败txt/XML保留，最终全量另记。

- 最终全量431 passed（184.40秒），JUnit失败/错误/跳过均0，strict markers及弃用警告转错误，无警告摘要。M1-01a范围验收完成；M1-01和核心M0—M6仍未整体完成。

- 续接收尾（北京时间2026-10-29 03:16）：重新确认远程main未变、PR为空，接续已验证批次，不重复开发。源码/测试/说明文档diff检查通过；原始失败日志含pytest输出尾随空格，原样保留。


### RUN-20261029-16（北京时间 2026-10-29 05:14启动）

- 起点：远程main `c11fb954c3440b88943942b6f58edc29df95b234`；重新fetch独立worktree，读取README、完整计划/台账、PROJECT_PROGRESS、IMPLEMENTATION_STATUS、近期提交、上轮验证记录和相关源码。无AGENTS.md、未合并PR或前轮远程重叠工作。
- 批次M1-01b-1，两小时以内：明确现有金额口径 → 不可变版本目录 → 驱动证据定义快照 → N-C1/N-C2核验 → 定义篡改/独立手算双后端 → 全量回归与提交。本批先稳定请求参数化依赖的指标定义，不宣称已实现InvestigationRequest。
- 完成：net_deposits.v1、net_deposit_change.v1、net_deposit_decomposition.v1三项定义，含分子/分母、流水键及尚未去重政策、时间归属、状态、单位、币种、版本和局限。未知/无版本ID拒绝；JSON快照独立，不影响不可变目录。证据必须携带完整批准定义，N-C1/N-C2拒绝定义缺失/重复/篡改，原独立来源金额重算不削弱。
- 验证过程：首轮2 failed、84 passed（1.63秒），新双后端夹具漏了事件SQL必需的affected_team列；补齐后针对性86 passed（1.28秒），所有警告转错误。失败txt/XML保留。手算基线100−20=80、本期75−15=60、变化−20，pending1000排除，实际SQLite/DuckDB导入执行并通过核验。全量结果另记及[验证记录](validation/2026-10-29-run16.md)。
- 文件：src/fitzsight/metrics/{__init__,catalog}.py、investigation/net_deposit.py、numeric_claims.py；tests/test_metric_catalog.py、test_numeric_claims.py；METRIC_CATALOG、NUMERIC_CLAIMS、本计划和run16验证文件。
- 环境：复用隔离venv并检查pip check无冲突；PYTHONPATH=src确认来自本轮worktree。CPython3.12.14、pytest9.1.1、NumPy2.5.2、pandas2.3.3、SciPy1.18.0、DuckDB1.5.5。手工/合成/既有Mock不代表生产收益；未重跑CLI/UI，未调用付费模型/云资源、交易或联系他人。
- 问题更新：N-C1/N-C2缺少版本化口径快照的问题已解决；旧无快照证据不能静默标为新契约通过，需重新执行。目录不强制去重/历史快照/时区/内部划转分类，不关闭M2/M3或参数化P0。新记ISSUE-004：事件schema预检未列affected_team，缺列会在后续SQL失败而非预检拒绝；本轮夹具补全，统一schema/数据契约待补，无全局阻塞。
- 提交依据：`feat: version net deposit metric definitions and verify evidence snapshots`；以上main为父提交，expected_sha并发检查、不强推，代码和计划同提交。
- 下一批：M1-01b-2请求模型及demo配置，协调N-C1—N-C5地区/窗口核验；其他指标目录/UI、ISSUE-003/004继续待办。本人学习、盲审、陌生人复现、同行反馈和职业结果保持待人工验收。仍有自动可推进工作，不暂停，不宣称整体完成。

- 最终全量461 passed（170.62秒），JUnit失败/错误/跳过均0，无警告摘要；strict markers及弃用警告转错误。M1-01b-1范围完成，M1整体及后续里程碑仍未完成。


### RUN-20261029-17（北京时间2026-10-29 07:14）

- 基线：远程main `26a98298f8b5570c4732cd800cc590797a519d27`；重新fetch独立worktree，核对README、计划及历史、两份根目录进度、近期提交、上轮验证及事件查询/schema实现；无AGENTS.md、未合并PR或远程重叠工作。
- 本批预算缩小为M1-01b-1a：补预检字段 → 六字段逐一删除×双后端 → 既有完整输入/事件契约回归 → 更新提交。请求模型涉及多条固定Claim约束，本轮未展开，M1-01b-2仍待办，不降低原验收。
- 完成：business_events预检加入实际SELECT所需affected_team；缺字段在schema阶段明确报表名/字段名，未执行任何金额或事件SQL，也没有产生分析结果证据。
- 验证：83 passed（3.32秒），失败/错误/跳过0，strict markers且所有警告转错误。12个缺字段用例实际加载SQLite/DuckDB；既有双后端完整CSV手算正例与事件事实篡改测试通过。[验证记录](validation/2026-10-29-run17.md)。本轮未重跑全量、CLI/UI，不能沿用上轮461项当成本轮全量。
- 环境：复用隔离venv、pip check无冲突、PYTHONPATH=src确认本worktree；CPython3.12.14、pytest9.1.1、NumPy2.5.2、pandas2.3.3、SciPy1.18.0、DuckDB1.5.5。手工/合成数据非生产收益，无付费模型/云资源、金融交易或对外联系。
- 文件：src/fitzsight/investigation/net_deposit.py、tests/test_net_schema.py、本计划和run17验证md/txt/xml。
- 问题更新：ISSUE-004已解决，证据为缺affected_team与其余五字段均在分析前拒绝；RUN-16历史失败保留。没有新增阻塞；统一数据类型/主键/质量契约仍待M2。
- 提交依据：`fix: validate all required event columns before net deposit analysis`；以上main为父提交，expected_sha并发检查，不强推。
- 下一批：M1-01b-2请求模型与demo配置分离，协调N-C1—N-C5窗口/地区核验；ISSUE-003和其余里程碑继续。学习讲解、独立盲审、同行反馈、职业结果保留待人工验收。仍有自动可推进任务，不暂停，不宣称整体完成。


### RUN-20261029-18（北京时间2026-10-29 09:14）

- 基线：远程main `a2a9a3e96952f7956cd45ec56dab66161267a95a`；fresh fetch独立worktree，读取README、路线图/历史进度、根目录进度文档和近期提交；无AGENTS.md、未合并PR及远程重叠工作。
- 批次M1-01b-2a，小于两小时：请求类型与白名单 → 严格日期和非重叠期间 → 显式币种/源时间/快照格式 → 正反例与JSON往返 → 文档提交。只交付请求契约，完整执行器与demo配置迁移保留待办。
- 实现：InvestigationRequest/Period不可变；拒绝未知/缺失字段、额外filters、非法日期、重叠窗口、未知指标/地区、非USD和未实现时区转换。快照只验证标识格式，不冒充内容哈希实测。
- 验证：63 passed（1.57秒），strict markers及全部警告转错误，失败/错误/跳过0。含请求九种地区/期间组合、非法输入反例、JSON往返与既有指标双后端手算测试。命令和边界见[记录](validation/2026-10-29-run18.md)。未跑全量/CLI/UI；九种契约组合不是整链跨场景通过。
- 文件：investigation/request.py、tests/test_request.py、docs/INVESTIGATION_REQUEST.md、本计划及run18验证md/txt/xml。
- 问题/剩余：无新增阻塞；请求尚未进入执行器，避免接受参数后仍计算固定场景。snapshot内容核对、demo配置、全部Claim窗口/地区协调仍待办。ISSUE-003和M2—M6保留；人工掌握、盲审、同行反馈及职业结果待人工验收。
- 提交依据：`feat: add strict immutable investigation request contract`；以上main为父提交，expected_sha检查，不强推。离线手工/合成测试，无付费模型/云资源、交易或对外联系。
- 下一批：接通净入金执行器及可信请求上下文，迁移demo配置与N-C1—N-C5校验；仍有自动可推进工作，不暂停，不宣称整体完成。


### RUN-20261029-19（北京时间2026-10-29 11:18）

- 基线：远程main `ba615864e27e1c3fc92d6ae6ca5402d3cd9cd030`；重新fetch独立worktree，读取README、路线图全文/进度、根目录历史文档、相关提交及request/runtime源码；无AGENTS.md、未合并PR和远程重叠工作。
- 批次M1-01b-2b，小于两小时：定义四文件内容清单 → 流式SHA-256 → 请求显式匹配 → 独立哈希/改动/搬迁/缺文件反例 → 文档提交。此为请求执行绑定依赖，不宣称接通整链。
- 完成：固定四张净入金源表的版本化字节清单；请求verify_snapshot显式核对内容，拒绝不匹配；缺文件/非普通文件/符号链接拒绝，无隐式生成或写入。目录搬迁不改标识，其他文件不参与。
- 验证：42 passed（1.27秒），失败/错误/跳过0，strict markers、全部警告转错误；手工文件逐一变更、独立哈希、JSON请求和无写入验证。未跑全量/SQL整链/CLI/UI，不声称真实业务收益。命令见[验证记录](validation/2026-10-29-run19.md)。
- 文件：data/snapshot.py、investigation/request.py、tests/test_snapshot.py、INVESTIGATION_REQUEST、本计划及run19验证md/txt/xml。
- 边界：字节一致不等于schema或金融口径正确；检查不冻结文件，不防并发改写或检查后替换。执行器须使用冻结输入或核对实际加载数据；本批未接入runtime，快照运行绑定仍待办。无新增全局阻塞。
- 提交依据：`feat: verify request snapshot against net deposit input contents`；以上main为父提交，expected_sha检查、不强推。离线手工数据，无付费模型/云资源、交易或对外联系。
- 下一批：接入净入金执行器、可信请求上下文与输入冻结策略，迁移demo配置和N-C1—N-C5参数约束；其余M1/P0和M2—M6未完成，人工讲解/盲审/反馈/职业结果继续待人工验收。仍有自动可推进事项，继续任务。


### RUN-20261029-20（北京时间2026-10-29 13:14启动）

- 基线：远程main `3da7e8ce8272625db9753358af03e8f3f06f0dbd`；fresh fetch独立worktree，读取README、计划基线/台账/历史、PROJECT_PROGRESS、IMPLEMENTATION_STATUS、近期提交及上轮验证记录，核对request/snapshot/store/runtime源码。无适用AGENTS.md、未合并PR或已发现的远程重叠工作。
- 批次M1-01b-2c，小于两小时：复制批准源表 → 核对实际副本 → 双后端物化 → 源文件变化/会话隔离/异常清理反例 → 全量回归 → 更新提交。解决DuckDB视图在指纹核对后仍会重新读源文件的依赖，完整请求执行和N-C1—N-C5迁移继续待办。
- 完成：open_net_input_store返回请求、已核对清单和内存表；四文件副本与请求不符时先于数据库构造拒绝。DuckDB显式建表而非CSV视图，SQLite沿用物化；成功后删除副本才交出store。退出/加载失败/消费方异常关闭连接。默认旧store路径兼容，源文件不写入，额外真值文件不加载。
- 验证：针对性88 passed（1.39秒），strict markers、全部警告转错误。实际SQLite/DuckDB验证源文件改写/删除后四表SUM仍为30、两个不同快照会话分别30/99且不串数据；四文件逐一改动拒绝、无效文件拒绝、复制副本篡改及清理测试。异常注入与复制篡改使用测试替身，仅证明对应分支；不计作外部系统实测。全量另记及[验证记录](validation/2026-10-29-run20.md)。
- 文件：src/fitzsight/data/store.py、investigation/inputs.py、tests/test_net_input_session.py、INVESTIGATION_REQUEST、本计划及run20验证md/txt/xml。
- 环境：复用隔离venv，PYTHONPATH=src确认本轮路径，pip check无冲突；CPython3.12.14、pytest9.1.1、NumPy2.5.2、pandas2.3.3、SciPy1.18.0、DuckDB1.5.5。离线手工/合成数据，不代表生产收益；未运行独立CLI/UI、付费模型、云资源、交易或对外联系。
- 问题更新：新入口的核对后源文件漂移由副本核对+物化解决，双后端删除源文件后查询为证据；旧runtime未迁移，不能宣称全局解决。物化增加内存/磁盘成本，规模性能未测；无持久化或跨表原子快照保证，不防同进程写库或同OS身份恶意修改副本。金融schema/数据质量、冻结持久化与重放仍在M2/M4，无新增全局阻塞。
- 提交依据：`feat: materialize verified net deposit input sessions`；以上main为父提交，expected_sha并发检查，不强推，代码与记录同提交。
- 下一批：将输入会话用于请求驱动净入金执行，同步迁移demo配置和全部Claim地区/窗口约束；保留三个区域/三组时期验收。ISSUE-003和其余M1/P0、M2—M6尚未完成；本人讲解/独立盲审/同行反馈/职业结果继续待人工验收。仍有自动可推进工作，继续任务。

- 最终全量535 passed（160.84秒），JUnit失败/错误/跳过均0，strict markers及弃用警告转错误，无警告摘要。M1-01b-2c范围完成；M1整链与M0—M6仍未整体完成。


### RUN-20261029-21（北京时间2026-10-29 15:20启动）

- 基线：远程main `c8fe5a5ff1062ac3aee1e276988194fd699503e2`；重新fetch独立worktree，读取README、计划全文及历史、PROJECT_PROGRESS、IMPLEMENTATION_STATUS、近期提交、上轮测试记录与request/input/store/net-deposit/核验源码。无AGENTS.md、未合并PR或发现的远程重叠工作。
- 优先级调整：复现ISSUE-005，N-C1/N-C2会接受truncated=True的合法摘要来源，将部分行重算的自洽金额放行。首次探针误改冻结字段失败，随后以新注册证据完成复现，详见验证记录。按P0优先先修复，完整请求参数化仍待办。
- 批次M1-02c-1，小于两小时：来源完整性判定 → 金额计算前拒绝 → N-C1/N-C2独立复核 → 四来源元数据反例与双后端上限边界 → 全量 → 更新提交。保留原始基线及三个区域/三组时期等验收标准。
- 完成：要求truncated严格False、rows完整列表、row_count严格整数且匹配行数、无preview标记；四个金额查询任一不完整即拒绝，不产生driver decomposition。核验器不依赖引擎先验，同样拒绝不完整来源。旧测试夹具补真实工具已有元数据，原数字/币种反例不削弱。
- 验证：针对性154 passed（2.00秒），strict markers和全部警告转错误，失败/错误/跳过0。四来源×八类不完整元数据均同时拒绝N-C1/N-C2；实际SQLite/DuckDB各四类超限拒绝、恰好上限和空结果正例通过。全量结果另记，命令/环境/探针见[验证记录](validation/2026-10-29-run21.md)。手工/合成/既有Mock非生产收益；未运行独立CLI/UI或在线模型。
- 文件：src/fitzsight/investigation/numeric_claims.py、net_deposit.py；tests/test_numeric_claims.py、test_cashflow_completeness.py；NUMERIC_CLAIMS、本计划及run21验证md/txt/xml。
- 环境：复用隔离venv，pip check无冲突，PYTHONPATH=src确认本worktree；CPython3.12.14、pytest9.1.1、NumPy2.5.2、pandas2.3.3、SciPy1.18.0、DuckDB1.5.5。无付费模型/云资源、金融交易或对外联系。
- 问题更新：ISSUE-005的N-C1/N-C2截断来源误放行已修复，依据为修复前True探针及修复后四来源反例；不声称所有调查来源完整性已解决。新增M1-02c-2待办复核N-C3/N-C4独立完整性。超过明细行数限制目前明确拒绝，大规模可核验聚合仍待后续实现；SQL过滤/JOIN语义、数据真实性、防篡改和其余P0不在本批关闭范围，无全局阻塞。
- 提交依据：`fix: reject incomplete SQL sources for net deposit amounts`；以上main为父提交，expected_sha检查，不强推，代码与进度同提交。
- 下一批：先核查N-C3/N-C4来源完整性，再继续请求驱动净入金执行/demo及窗口地区核验；ISSUE-003、M1整链及M2—M6仍未完成。本人学习讲解、独立盲审、同行反馈、职业结果保持待人工验收。还有自动可推进工作，继续任务，不宣称整体完成。

- 最终全量577 passed（170.24秒），JUnit失败/错误/跳过均0，strict markers及弃用警告转错误，无警告摘要。M1-02c-1范围完成，未关闭M1整体或人工验收。


### RUN-20261029-22（北京时间2026-10-29 17:15启动）

- 基线：远程main `ef70e9237f1ecf232a09bcc63e6e60c7c5ca5cc0`；重新fetch独立worktree，读取README、完整计划/历史、PROJECT_PROGRESS、IMPLEMENTATION_STATUS、相关提交与上轮验证，核对N-C3/N-C4/SQL/引擎实现。无AGENTS.md、未合并PR或发现的远程重叠工作。
- 批次M1-02c-2，两小时以内：写独立反例并确认失败 → 复用完整性判定 → 区域计算入口拒绝 → 正反例及双后端 → 全量回归 → 更新提交。范围是N-C3/N-C4及区域查询，原核心/参数化验收标准保留。
- 完成：N-C3明细、N-C4四来源均要求严格未截断标记、匹配整数行数和完整rows，无preview；核验器独立检查，不靠上游保护。区域计算拒绝截断/不完整结果，避免漏地区污染对照。旧测试夹具只补真实SQL已有元数据，保留原手算和篡改要求。
- 验证过程：修复前44 failed（1.62秒），40个来源元数据反例错误放行、4个双后端区域超限未抛错；无收集/环境错误，原始before txt/XML保留。修复后针对性229 passed（1.81秒），strict markers和全部警告转错误，失败/错误/跳过0。实际SQLite/DuckDB两时期max_rows=1截断拒绝、max_rows=2两地区完整结果通过；既有空明细/零分母/缺地区正例保留。全量另记与[验证记录](validation/2026-10-29-run22.md)。
- 文件：src/fitzsight/investigation/{concentration_claims,regional_claims,net_deposit}.py；tests/{test_comparison_completeness,test_concentration_claims,test_regional_claims}.py；NUMERIC_CLAIMS、本计划及run22验证md/txt/xml（含修复前失败）。
- 环境：复用隔离venv，pip check无冲突，PYTHONPATH=src核对本worktree；CPython3.12.14、pytest9.1.1、NumPy2.5.2、pandas2.3.3、SciPy1.18.0、DuckDB1.5.5。手工/合成/既有Mock非生产收益；未独立运行CLI/UI，未调用付费模型/云资源、交易或对外联系。
- 问题更新：ISSUE-005后续N-C3/N-C4缺口在本范围解决，证据为修复前44失败及修复后通过。SQL过滤/JOIN、聚合前数据质量、注册器真实性/持久化仍不由元数据证明；不宣称所有调查/所有P0已解决。没有新增阻塞。
- 提交依据：`fix: require complete sources for concentration and regional claims`；以上main为父提交，expected_sha并发检查，不强推，代码与进度同提交。
- 下一批：继续请求驱动净入金执行，协调demo和N-C1—N-C5地区/窗口核验；ISSUE-003和M1其余事项、M2—M6未完成。本人掌握、盲审、同行反馈、职业结果保留待人工验收。仍有自动可推进事项，继续任务，不宣称整体完成。

- 最终全量621 passed（167.62秒），JUnit失败/错误/跳过均0，strict markers及弃用警告转错误，无警告摘要。M1-02c-2范围完成；M0—M6及人工验收仍未整体完成。


### RUN-20261029-23（北京时间2026-10-29 19时启动，21:19续接）

- 基线：远程main `9cbbcc0f40c28e6a896f2f7013f19e9903d00e0f`，重新fetch独立worktree，读取README、计划全文/历史、PROJECT_PROGRESS、IMPLEMENTATION_STATUS、近期提交/验证及请求、输入会话、SQL、金额核验源码。无适用AGENTS.md、未合并PR或发现的远程重叠工作。续接时main未变；未提交临时目录丢失，原测试结果未取回，不计通过，恢复本批修改重新验证，未另开重叠批次。
- 批次M1-01b-2d，实际工作预算小于两小时：连接已核对输入会话 → 复用金额SQL → 显式请求核验 → 三地区/三时期/双后端手算与篡改反例 → 全量 → 文档提交。范围限定金额与分解，不降低原三条整链、全部声明和demo迁移验收。
- 完成：execute_net_cashflows使用真实请求窗口/地区、核对后物化的数据计算；输出范围明确为net_cashflow_amounts.v1，仅N-C1/N-C2。独立核验使用调用者原请求而非证据自报上下文，同时比对四来源批准SQL与绑定参数，原数值/定义/完整性校验保留。文字用实际地区/期间，避免不等长窗口被称为周环比；旧固定引擎复用同一SQL模板。
- 验证：针对性164 passed（3.61秒），失败/错误/跳过0，strict markers及全部警告转错误。18个三地区×三时期×双后端实际CSV组合各重复执行，手算80k→60k、净变−20k、入金−25k、出金−5k匹配；结束日末秒包含、次日零点及pending排除，输入字节不变。完整命令及全量结果见[验证记录](validation/2026-10-29-run23.md)。
- 文件：investigation/{cashflow_queries,net_cashflows,net_deposit,numeric_claims}.py、tests/test_net_cashflows.py、INVESTIGATION_REQUEST、NUMERIC_CLAIMS、本计划及run23验证md/txt/xml。
- 环境：复用隔离venv，PYTHONPATH=src核对本worktree，pip check无冲突；CPython3.12.14、pytest9.1.1、NumPy2.5.2、pandas2.3.3、SciPy1.18.0、DuckDB1.5.5。手工/合成及既有mock非生产收益；未运行独立CLI/UI、付费模型、云资源、交易或对外联系。
- 问题与边界：金额阶段“请求未进入执行器”依赖已解决；整个净入金调查仍未参数化。SQL参数核验不证明数据真实或JOIN唯一性；定点金额/关系质量/历史归属仍待M2，来源5000行上限仍明确拒绝。临时目录丢失后已恢复并重测，无新增全局阻塞。输出嵌套数据非不可变审计，不替代M4持久化。
- 提交依据：`feat: execute request-bound net cashflow amounts with source verification`；以上最新main为父提交，expected_sha并发检查、不强推，代码与进度同提交。
- 下一批：在本金额入口基础上迁移N-C3/N-C4和N-C5的请求窗口/地区约束、再接demo与CLI/UI，保留完整调查验收；ISSUE-003、其他核心调查、M2—M6仍待办。本人讲解、独立盲审、同行反馈和职业结果保持待人工验收；有自动可推进事项，继续任务，不宣称整体完成。

- 最终全量683 passed（178.31秒），JUnit失败/错误/跳过均0，strict markers与弃用警告转错误，无警告摘要。M1-01b-2d金额阶段范围完成；完整参数化及M0—M6、人工验收仍未完成。


### RUN-20261029-24（北京时间2026-10-29 23:16启动）

- 起点：远程main `2e0438d7c51c377be2150b0027f595f574b8e8c5`；重新fetch独立worktree，读取README、计划全文/历史、PROJECT_PROGRESS、IMPLEMENTATION_STATUS、近期提交/上轮验证，核对金额执行及集中度源码/测试。无AGENTS.md、未合并PR或发现的远程重叠编辑。
- 批次M1-01b-2e，两小时以内：集中度原请求核验 → 复用本期明细计算 → 显式前N配置 → 双后端手算与篡改 → 全量 → 更新提交。验收限N-C3，保留完整三调查及原M0—M6验收标准。
- 完成：金额接口可显式传top_customers正整数，在同一物化会话内增加N-C3；默认仍只返回金额两声明。复用本期明细按客户合计，不新增SQL/CSV读取；文字用实际地区/期间。独立核验原请求和原N、当前窗口、地区、批准SQL与绑定参数，并保留完整性、有限非负金额、分子/分母/比例重算。零/空提款null，负提款拒绝，N超过实际客户数取全部。
- 验证：针对性176 passed（4.84秒），失败/错误/跳过0，strict markers及全部警告转错误。三地区×三时期×双后端18组合各重复执行，独立手算A=30k+20k、B=10k、前1占50k/60k；原两金额声明不变、SQL仍4份。另有空/零/超出客户数、负金额与自洽N/比例/窗口/地区/快照/SQL篡改反例。完整命令/全量结果见[验证记录](validation/2026-10-29-run24.md)。
- 文件：investigation/concentration_claims.py、net_cashflows.py、tests/test_request_concentration.py、INVESTIGATION_REQUEST、本计划和run24验证md/txt/xml。
- 环境：CPython3.12.14、pytest9.1.1、NumPy2.5.2、pandas2.3.3、SciPy1.18.0、DuckDB1.5.5；复用隔离venv，PYTHONPATH=src核对本worktree，pip check无冲突。手工/合成/既有mock非生产收益；无独立CLI/UI、付费模型/云资源、交易或对外联系。
- 问题更新：新请求金额路径缺少N-C3已在本范围补齐，固定场景旧核验兼容；并不关闭完整参数化P0。top_customers是单独显式配置，后续服务重放需保存原值，不从证据反推；金融数据真实性/去重/历史归属/定点金额仍待M2，不宣称持久化防篡改。无新增阻塞。
- 提交依据：`feat: add request-bound withdrawal concentration to cashflow execution`；以上main为父提交、expected_sha并发检查，不强推，代码与记录同提交。
- 下一批：迁移N-C4地区对照和N-C5事件窗口，再接完整调查/demo/CLI/UI。ISSUE-003、其他核心调查、M2—M6继续待办；本人学习、独立盲审、同行反馈和职业结果保持待人工验收。仍有自动推进工作，任务继续，不宣称整体完成。

- 最终全量725 passed（186.81秒），JUnit失败/错误/跳过均0，strict markers及弃用警告转错误，无警告摘要。M1-01b-2e范围完成，不代表完整参数化或M0—M6整体完成。
