# 五类离线 CLI 演示复现

本页验证当前固定场景的执行链路，不能替代数值真值、跨时期泛化、UI 人工验收或模型效果评测。全部数据均为合成数据。规则规划器不调用外部模型。

## 环境准备

在仓库根目录，使用 Python 3.12（本轮实测 3.12.14）：

```bash
python3.12 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.lock
python -m pip install -e . --no-deps
python -m pip check
```

Windows 可使用 README 中的 PowerShell 激活方式；该平台本轮未实测。

## 一次验证五类流程和两个后端

```bash
python scripts/check_offline_flows.py --output /tmp/fitzsight-offline-flows.json
```

脚本逐个启动真实的 `agent_investigate.py` 子进程，显式指定 `--planner deterministic` 和 sqlite/duckdb，检查退出码、实际后端、意图、核验状态、最终回答状态及非空证据。默认生成种子 20260811、20,000 客户的一份临时合成数据，十次调查复用它，完成后清理；不读写用户已有导入目录。每次调查超时 120 秒会记录失败，最终有任一失败就返回非零退出码。首个流程耗时包含生成数据，不能直接用于后端性能比较。

| 流程 | 对应固定问题 |
|---|---|
| CRM 转化 | European FTD conversion after July 15 |
| 净入金 | European net deposits in the week starting August 3 |
| 客户分群 | European customer behavioral value and deposit contribution |
| 营销线索质量 | Americas lead volume/conversion after June 15 |
| 错误归因防护 | Asia conversion after July 20 and office relocation |

问题全文及本次结果见 [离线记录](validation/2026-10-27-offline-flows.json)。需要查看完整调查输出，可单独运行：

```bash
python scripts/agent_investigate.py --planner deterministic --backend duckdb --data-dir /tmp/fitzsight-synthetic-demo --question "Why did European net deposits fall in the week starting August 3?" --output /tmp/fitzsight-net-deposits.json
```

当前 runtime 在缺表时会自动生成合成数据，这是待修 P0（M1-04）。上述命令只能使用专门的演示目录，不能指向真实数据目录。

## 证据边界

`verification.passed` 目前只反映已有核验器的检查，不能证明报告中所有数字和单位正确；M1-02 的结构化数值绑定尚未完成。此检查不比较两后端所有数字，不测试 Streamlit 页面交互，也不构成独立人工复现。模型线上调用和真实业务收益均未测试。
