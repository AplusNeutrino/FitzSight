# FitzSight 最终机器检查清单

## 1. 安装与本地检查

```powershell
python -m pip install -r requirements.lock
python -m pip install -e . --no-deps
python -m pytest
python scripts/final_machine_check.py --skip-streamlit --output final_machine_report.json
```

必须满足：`local_core_ready=true`、确定性 Agent 为 `verified`、提交预检通过，并且 `deepseek_live.status=not_requested`。

## 2. Streamlit 健康检查

```powershell
python scripts/validate_streamlit_runtime.py
```

在最终演示机器确认本地页面、五类场景、Evidence ID 和失败状态均可见。

## 3. DeepSeek 在线验证（非本轮发布证据）

默认不运行。只有参赛者明确决定使用真实密钥时才执行：

```powershell
python scripts/final_machine_check.py --include-deepseek --output final_machine_report_with_deepseek.json
```

不要把未运行状态写成在线成功，也不要填入推测延迟。

## 4. GOAI 人工提交

- 仅上传 `FitzSight_GOAI_初赛方案_CN.pdf`。
- 人工检查 12 页、中文字体、文件大小和门户预览。
- 人工确认最终提交并保存截图、邮件或回执。
- 自动化脚本不访问、不修改、不提交赛事门户。
