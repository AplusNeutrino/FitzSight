# FitzSight v0.13.0 UI / Demo

Streamlit 只展示已核验 Agent 结果，不形成第二条分析路径。

- Planner：Deterministic fallback / DeepSeek V4。
- DeepSeek 模型：`deepseek-v4-flash` / `deepseek-v4-pro` 严格选择器。
- 主界面：问题输入、KPI、图表、批准计划、执行轨迹、Evidence ID、Verifier 状态和边界提示。
- 异常状态：不支持意图、工具失败、证据不足和 Provider 错误均明确展示。

```powershell
streamlit run streamlit_app.py
python scripts/validate_streamlit_runtime.py
```

断网时使用确定性 Planner；离线 HTML 和 MP4 作为演示回退，不代表 Provider 在线验证。
