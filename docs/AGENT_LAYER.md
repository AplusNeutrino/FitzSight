# FitzSight Agent 层

FitzSight v0.13.0 采用受限规划、确定性执行和失败即关闭核验。

## Planner

- `ConstrainedRulePlanner`：默认离线规划器。
- `StructuredJSONPlanner`：Provider 中立的 JSON 解析与本地计划校验。
- `DeepSeekChatPlanner`：可选 DeepSeek V4 Chat Completions 规划器，Flash 默认、Pro 可选。

本地意图门控在网络调用前执行。模型只能返回固定意图和批准动作顺序；不能生成 SQL、工具参数、金融动作或关键数值。

## Orchestrator 与执行器

Orchestrator 依次执行批准动作；结果驱动分支也只能选择目录内动作。确定性调查执行器拥有 SQL、统计、异常、贡献和文档证据工具。

## Evidence 与 Verifier

工具输出写入追加式 Evidence Registry。最终答案的每条重要结论必须引用 Evidence ID；覆盖不足、因果越界、工具失败或禁止内容触发 `insufficient_evidence` / `failed`。
