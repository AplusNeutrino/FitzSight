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
