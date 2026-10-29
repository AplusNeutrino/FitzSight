# 请求契约第一批

`fitzsight.investigation.request.InvestigationRequest.from_dict` 严格接受 metric、filters、baseline、current、timezone、currency、data_snapshot，不默默忽略未知字段。filters目前仅region（Europe/Asia/Americas）；metric仅net_deposits.v1，currency仅USD。

日期为严格YYYY-MM-DD、日历有效、起止包含；基线必须早于本期，不允许重叠。允许不同窗口长度，但不自动按天归一化。timezone目前仅source_naive，明确沿用源时间，不冒充UTC或时区转换。data_snapshot必须显式sha256:加64位小写十六进制；这里只验证格式，尚未验证实际文件内容哈希，不提供快照真实性保证。

对象及Period不可变，JSON输出为独立字典。三地区/三组时期测试只证明契约接受和往返正确，**不是整链参数化验收**。本批没有接入CLI/UI/引擎；旧调查继续固定场景。下一批须接入执行器、快照核对和demo配置，同时迁移N-C1—N-C5参数核验，不能用新请求驱动旧固定查询。

## 显式内容核对（RUN-19）

`fingerprint_net_inputs(data_dir)` 对business_events/customers/deposits/withdrawals四个CSV逐字节计算SHA-256；清单采用format=fitzsight.net-inputs.v1、files为文件名到哈希的映射，JSON按键排序、无多余空格、UTF-8，再计算清单SHA-256。请求的 `verify_snapshot(data_dir)` 比较此标识，内容不匹配时拒绝；构造请求本身仍只检查格式。

目录位置和mtime不参与标识；其他文件（包括评测真值）不参与。缺文件、目录冒充文件、符号链接拒绝，不生成或修改源数据。这不是CSV质量验证，也不是签名或不可变数据库快照；调用者必须防止并发写入。检查后的文件仍可能改变，后续执行器必须使用冻结输入或独立核对实际加载的数据，不能用本方法声称已完成运行时快照绑定。本批未自动接入旧runtime或调查链。

## 请求绑定的输入会话（RUN-20）

```python
from fitzsight.investigation.inputs import open_net_input_store

with open_net_input_store(request, data_dir, backend="duckdb") as session:
    assert session.snapshot.snapshot_id == request.data_snapshot
    # 后续执行器应只使用 session.store；它持有已核对副本的内存表。
    columns, rows = session.store.execute("SELECT COUNT(*) FROM customers")
```

该入口只复制四张批准源表到私有临时目录，再对**实际待加载副本**执行请求指纹核对；不匹配时不创建数据库。SQLite加载为内存表，DuckDB显式materialize为内存表；成功加载后先删除临时CSV，再交出会话。因此后续源文件修改或删除不会改变该会话结果。正常退出、消费方异常或加载失败都会关闭已创建连接；临时目录由上下文清理。额外CSV（包括真值）不复制、不加载，不补合成数据。

这是输入会话接口，**尚未接入旧runtime、调查引擎或CLI/UI**。它不执行请求中的指标/地区/窗口过滤，后续必须协调全部查询与Claim核验，不可将本例计作参数化调查完成。`AnalyticsStore.load_csv_directory(materialize=True)`是底层物化选项，单独调用不提供指纹核对；默认行为保持兼容。

边界：字节指纹不证明CSV业务口径、跨表事务一致性、历史客户归属或来源真实性；复制时如果发生改动，只有最终副本仍匹配预先指定标识才会接受，不提供上游原子快照。数据库仍可被持有store的可信程序代码写入，不是防篡改/权限隔离系统；不防同进程或同OS身份恶意修改临时文件。本入口不持久化重放数据，退出后内存数据丢失。物化增加临时磁盘与内存成本，尚未做规模性能验收。

## 请求驱动金额执行（RUN-23）

```python
from fitzsight.investigation.request import InvestigationRequest
from fitzsight.investigation.net_cashflows import execute_net_cashflows

request = InvestigationRequest.from_dict(request_json)
result = execute_net_cashflows(request, data_dir, backend="duckdb")  # 或 sqlite
assert result.scope == "net_cashflow_amounts.v1"
print(result.metrics)
```

`request_json`使用本文既有严格契约和预先指定的四文件指纹。入口不生成数据：私有副本核对 → 双后端物化 → 三张金额源表字段预检 → 请求地区/两期绑定查询 → 金额及分解 → N-C1/N-C2独立重算。返回原请求、已核对清单、六项金额/恒等检查、两条声明及证据；退出时关闭数据库。保持source_naive/USD语义，不做汇率、时区转换或每日归一化。文字使用实际地区及“两个期间”，不把不等长窗口写成周环比。

这是**金额阶段接口**，结果类型为`NetCashflowResult`，不提供完整五声明调查、诊断、自然语言参数抽取、事件归因或CLI/UI入口。N-C3—N-C5、demo配置及其他核心调查链仍待迁移。旧runtime仍使用固定场景，不会自动调用本入口。此前RUN-18—20“尚未接入”的描述保留为对应批次历史。

独立复核金额声明时，必须将原始、可信的`InvestigationRequest`通过`expected_request=`传入`verify_net_change`/`verify_net_decomposition`，不可从待核验的证据重新推定请求。新路径比对完整请求（含snapshot/timezone/metric）、声明地区/窗口、四来源的批准SQL与日期/地区绑定参数，并沿用来源完整性、有限数值、币种和定义快照校验。带request的证据若省略expected_request将被拒绝；旧场景核验规则保留。

测试覆盖三地区×三组时期×双后端18组合，每组重复执行；关键数字、声明、请求、清单及SQL参数/摘要一致，证据执行时间戳允许变化。手工数据独立算式为基线(100−20)×k=80k，本期(75−15)×k=60k，净变−20k，入金变−25k，出金变−5k；pending和结束次日零点排除、结束日23:59:59包含。这仅是金额阶段跨场景验收，不能代替M1三条整链要求。

边界：完整SQL与参数核对不证明原始数据真实、客户主键唯一、JOIN无重复、历史地区归属正确或外部/内部划转分类正确；注册器仍不签名、不持久化。四文件指纹包括本阶段暂不使用的business_events，事件表业务校验在后续完整调查迁移。每份SQL最多5000行，超限明确拒绝。金额仍沿用现有数值表示，定点金额和统一数据质量由M2推进。返回对象的嵌套字典可变，导出不是防篡改存储，也不是持久化重放验收。

## 请求驱动集中度（RUN-24）

`execute_net_cashflows(request, data_dir, backend="duckdb", top_customers=11)`在同一个已核对输入会话中返回N-C1/N-C2及N-C3；scope为`net_cashflow_concentration.v1`。不传top_customers或传None仍返回原金额两声明接口。top_customers为调用者显式分析配置，只接受正整数（拒绝bool），不暗用演示场景的11；它不是新增的请求JSON字段。

计算复用四份金额查询中的本期提款明细，先按customer_id合计，再取最多N个客户的金额总和/所有客户提款总和，不增加SQL或重新读取CSV。N超过实际提款客户数时分子覆盖全部客户；无提款或全零时比例为null/insufficient_evidence，负金额拒绝。结果在metrics.customer_concentration中记录N、分子、分母、比例和计算状态；未加入客户排名展示、根因或客户动机判断。

独立核验N-C3时必须同时传`expected_request=request, expected_customer_count=11`，并沿用来源完整性/摘要/金额重算。原请求、原配置与证据分别核对，不能用证据自报的N代替原配置；还核对当前期间、地区及批准提款SQL和绑定参数。新证据缺少外部请求时拒绝；旧固定场景核验兼容。规范文字使用实际地区和明确起止日期（末端不含），不再固定European/current-week。

18个地区/期间/后端组合均实测并重复运行，客户A=30k+20k、B=10k，前1占50k/60k；空表、全零、N大于实际客户数及负金额双后端验证。N-C4/N-C5、完整调查、demo配置和CLI/UI仍未迁移。此比例描述提款集中度，不代表余额集中度、客户风险或因果；数据质量、去重、定点金额及持久化边界沿用上文。

## 请求驱动地区对照（RUN-25）

`execute_net_cashflows(request, data_dir, backend="duckdb", include_regional=True)`增加N-C4，scope为`net_cashflow_regional.v1`。同时传`top_customers=11`返回N-C1—N-C4；不传时返回N-C1/N-C2/N-C4。include_regional只接受bool，默认False兼容原入口；它是执行配置，不是请求JSON字段。

同一个已核对输入会话复用区域SQL：基线、本期分别查询全地区入金/出金，增加四份完整行证据。每地区分母为输入customers表的COUNT(DISTINCT customer_id)，包括没有流水的客户；计算两期人均净额之差，再取其他可计算地区变化的中位数。不等长窗口不按天归一化，不自动构造实验对照组。

新结果使用metrics.regional_control.target_change，避免把Asia/Americas结果存为europe_change；旧固定引擎字段保留兼容。报告使用实际地区和两期日期，明确输入客户表分母，不声称历史期末注册数。缺目标/对照时null和insufficient_evidence，真实零值是computed。非目标地区的非USD流水同样拒绝。

独立核验`verify_regional(claim, registry, expected_request=request)`必须使用原始可信请求；比对声明/证据的地区、四日期、快照等上下文，再核对四来源批准SQL及绑定参数，沿用完整性和金额/人数/中位数重算。带请求证据不能省略外部请求核验。

实测覆盖三地区三时期双后端、无流水客户、日期/pending过滤、重复执行、缺地区、零变化和来源参数篡改。N-C5、完整调查、demo与CLI/UI仍待办。聚合重算不是独立源系统审计；客户主键重复导致的JOIN放大、历史归属、源数据真实性、定点金额和持久化仍待M2/M4。地区对照仅为描述性比较，不代表因果。


## 显式事件查询配置（RUN-20261030-27）

`EventSelection` 是 N-C5 参数化的查询基础，尚未接入 `execute_net_cashflows` 或 Claim 核验。示例仅构造批准 SQL 和绑定值，不返回已核验调查：

```python
from fitzsight.investigation.event_selection import EventSelection, event_lookup_query

selection = EventSelection.from_dict({
    "event_type": "HIGH_VALUE_WITHDRAWAL_CLUSTER",
    "period": {"start": "2026-02-03", "end": "2026-02-05"},
})
sql, parameters = event_lookup_query(request, selection)
# 未来执行接线应在已核对的同一输入会话内调用 SQL 工具，
# 并把原 request 与原 selection 交给独立声明核验器。
```

配置不可变，JSON字段严格匹配，只批准现有高价值提款聚集事件类型；不从日志猜事件类型或日期。地区来自原请求，不能另传地区覆盖。事件窗口独立于现金流基线/本期，采用 `source_naive` 日历日期，包含结束日全日（SQL转换为次日零点排他边界），不隐式选“事件前后两天”。同日按event_id排序；不在查询层去重或推断因果。

查询函数不读文件、不校验快照内容、不执行SQL、不生成声明。实际执行、schema检查、完整性/事件事实核验、原请求与原配置绑定及CLI/UI/demo迁移属于后续任务；本轮三地区/三窗口查询通过不等于整链验收。未来重放须保存原事件配置，不从可变证据反推期望值。
