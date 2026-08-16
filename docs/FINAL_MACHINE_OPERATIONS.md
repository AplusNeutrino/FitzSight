# FitzSight v0.13.0 最终机器操作

## 默认本地检查

```powershell
python scripts/final_machine_check.py --output final_machine_report.json
```

默认运行确定性 Agent、提交预检、交接检查与 localhost Streamlit 健康检查；不会请求 DeepSeek。

## DeepSeek 显式在线验证

只有参赛者明确决定并配置真实密钥时才运行：

```powershell
python scripts/final_machine_check.py --include-deepseek --output final_machine_report_with_deepseek.json
```

本轮发布不运行该命令；状态保持 `deepseek_live: not_requested`。

## 演示回退

1. Live：Streamlit 本地界面。
2. Local：确定性 CLI。
3. Video：离线 HTML / H.264 MP4。

GOAI 门户上传、最终提交与回执均为人工操作；初赛只上传 `FitzSight_GOAI_初赛方案_CN.pdf`。
