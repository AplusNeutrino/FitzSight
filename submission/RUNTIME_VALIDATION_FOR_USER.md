# FitzSight v0.13.0 运行验证

## 默认离线验证

```powershell
python -m pytest
python scripts/final_machine_check.py --skip-streamlit --output docs/V0.13_FINAL_MACHINE_READINESS.json
```

该命令不调用外部模型，报告中应为 `deepseek_live.status=not_requested`。

## Streamlit 本地健康检查

```powershell
python scripts/validate_streamlit_runtime.py
```

## DeepSeek 在线验证（显式选择）

```powershell
$env:DEEPSEEK_API_KEY = "<api-key>"
$env:FITZSIGHT_DEEPSEEK_MODEL = "deepseek-v4-flash"
python scripts/validate_deepseek_runtime.py
```

在线验证只保留请求 ID、请求/响应模型、耗时和 token；不保存密钥、完整提示词或思考内容。本轮提交主动未执行该步骤。
