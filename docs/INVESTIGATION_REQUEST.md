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
