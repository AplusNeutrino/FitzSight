# FitzSight 在线 Demo 部署（Streamlit Community Cloud）

## 已准备内容

- 入口：`streamlit_app.py`
- 云端依赖：`requirements.txt`
- Streamlit 配置：`.streamlit/config.toml`
- Secrets 示例：`.streamlit/secrets.toml.example`
- DeepSeek 接口：`https://api.deepseek.com/chat/completions`
- 默认模型：`deepseek-v4-flash`

在线 Demo 继续保留本地安全边界。DeepSeek 只编排白名单内的调查步骤；SQL、统计、指标计算、Evidence ID 和最终核验均由本地确定性代码负责。

## 部署前

1. 将当前修改提交并推送至 GitHub。
2. 确认仓库中没有 `.env` 或 `.streamlit/secrets.toml`。
3. 不要把 API Key 写入代码、GitHub Actions 日志、Issue 或赛事表单。
4. 建议为比赛 Demo 单独创建 DeepSeek API Key，并在账户侧设置可接受的余额与用量边界。

## Streamlit Cloud 配置

1. 打开 `https://share.streamlit.io/`，选择 **New app**。
2. Repository：`AplusNeutrino/FitzSight`
3. Branch：选择包含 v0.13.0 在线 Demo 修改的分支。
4. Main file path：`streamlit_app.py`
5. Python：选择 3.11。
6. 在 **Advanced settings / Secrets** 中粘贴：

```toml
DEEPSEEK_API_KEY = "在这里填写 DeepSeek API Key"
FITZSIGHT_DEEPSEEK_MODEL = "deepseek-v4-flash"
FITZSIGHT_PUBLIC_DEMO = true
FITZSIGHT_MAX_LIVE_CALLS_PER_SESSION = 3
FITZSIGHT_MAX_LIVE_CALLS_GLOBAL = 30
FITZSIGHT_BACKEND = "sqlite"
```

7. 点击 **Deploy**。部署后将应用设为公开，并复制固定的 `https://<name>.streamlit.app` 地址。

## 公开 Demo 的限制

- 公开模式只显示五个批准场景，不开放自定义问题。
- 问题文本在公开模式下只读。
- 每个浏览器会话最多触发 3 次 DeepSeek 在线规划。
- 单个应用进程最多触发 30 次 DeepSeek 在线规划；达到上限后仍可使用 deterministic fallback。
- API Key 只从服务器端 Secrets 读取，不显示在界面、错误信息或遥测中。
- 遥测仅展示请求 ID、模型、耗时和 token；不记录完整提示词与思考内容。
- 数据均为合成数据，不提供交易、转账、授信或账户动作。

会话与进程计数会在浏览器会话或应用重启后重置，因此它们是演示级保护，不替代 DeepSeek 账户侧的用量控制。

## 上线验收

1. 打开公网地址，确认默认 Planner 为 **DeepSeek V4**，模型为 `deepseek-v4-flash`。
2. 运行欧洲 FTD 场景。
3. 展开 **DeepSeek live request telemetry**，确认存在 request ID、响应模型、耗时与 token。
4. 确认调查结果仍显示 Evidence ID、Verifier PASS 和因果措辞边界。
5. 再运行伪相关拒绝场景，确认系统拒绝把邻近事件写成已证实因果。
6. 刷新页面并确认密钥从未出现在页面、日志下载或错误信息中。

## 本地验证

```powershell
python -m pytest tests/test_online_demo_config.py tests/test_deepseek_planner.py
python scripts/validate_streamlit_runtime.py
```

真实 DeepSeek 验证仅在你准备好密钥后执行：

```powershell
$env:DEEPSEEK_API_KEY = "<your-key>"
$env:FITZSIGHT_DEEPSEEK_MODEL = "deepseek-v4-flash"
python scripts/validate_deepseek_runtime.py
```
