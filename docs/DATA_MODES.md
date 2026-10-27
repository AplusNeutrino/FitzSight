# 数据模式：导入不生成，演示显式选择

`build_agent_runtime` 和 `scripts/agent_investigate.py` 默认使用 **import**。这是对旧版“缺表自动生成”行为的有意不兼容修复；已有脚本如需生成模拟数据，必须显式选择 demo。

| 模式 | 完整数据目录 | 缺少必需表 |
|---|---|---|
| import（默认） | 原样读取，不写源 CSV | 列出缺少文件并失败，不创建目录、不补模拟数据 |
| demo（显式） | 原样读取，不重新生成 | 仅在不存在或空目录生成；非空目录拒绝，避免覆盖或混合 |

必需文件：`customers.csv`、`sales_activity.csv`、`deposits.csv`、`withdrawals.csv`、`trades.csv`、`business_events.csv`。同名目录不算文件。`salespeople.csv` 是生成器的额外表，当前调查 runtime 不要求它。完整但损坏的 CSV 仍由加载器报错，不会触发修复或合成回退；加载失败会关闭数据库连接。

## 命令

从仓库根目录运行，默认规则规划器不调用外部模型：

```bash
# 专用空目录，明确生成合成演示数据
python scripts/agent_investigate.py --data-mode demo --data-dir /tmp/fitzsight-demo-new --backend sqlite
# 读取已有数据；缺表失败
python scripts/agent_investigate.py --data-mode import --data-dir /path/to/csv-bundle --backend duckdb
```

CLI JSON 的 `runtime.data_mode` 记录所选模式。模式只表示“是否允许初始化合成数据”，不证明数据来源真实或业务口径正确。import 也可以读取已生成的合成 bundle。

Python：

```python
store, registry, agent = build_agent_runtime(
    data_dir="/path/to/csv-bundle", backend="duckdb",
    planner=ConstrainedRulePlanner(), data_mode="import",
)
```

`generator_config` 只允许用于 demo；import 传入它会报错，避免参数被默默忽略。完整目录在 demo 下也不会因 generator_config 改变而重建；需要新种子请使用新空目录。

## 演示入口和限制

Streamlit、start_demo、竞赛构建/评测/演示检查脚本明确使用 demo。Streamlit 当前仍是固定合成演示入口，不提供用户数据导入界面；导入使用 CLI 或 runtime。在线 Provider 验证脚本仍需原有显式授权开关，此变更没有启用在线模型。

本次只解决模式和缺表生成边界，**不**代表 M2 的字段契约、数据质量、去重、金融状态/币种核对、快照或幂等导入已完成。底层显式 `write_csv_bundle` 是生成器 API，仍可写文件，不应用于导入；不要把演示目录与外部数据混用。此模式检查不提供多进程生成锁或事务发布；同一演示目录应由单个初始化进程使用，相关可靠性属于后续工作。

验收证据见 [RUN-04](validation/2026-10-27-run04.md)。历史验证记录保留当时命令，不应复制旧命令期待继续自动生成数据。
