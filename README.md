# FitzSight v0.13.0

FitzSight 是证据驱动的金融运营调查智能体：把“为什么指标变了？”转化为受约束计划、确定性计算、可追溯 Evidence ID 与失败即关闭的结论核验。

## 设计边界

- 本地意图门控先于任何模型请求；仅支持五类批准调查。
- DeepSeek V4 只生成固定动作目录中的 JSON 计划，不生成 SQL、不计算关键数字、不执行金融动作。
- 只读 SQL、统计检验、贡献分解、异常检测与文档检索由确定性工具完成。
- Evidence Registry 追加式记录来源；EvidenceClaimVerifier 决定结论能否呈现。
- 比赛构建只使用可复现合成数据，不含真实客户 PII。

## 安装

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.lock
python -m pip install -e . --no-deps
```

## 运行

确定性 CLI（默认，不访问外部模型）：

```powershell
python scripts/agent_investigate.py --backend sqlite
```

Streamlit：

```powershell
streamlit run streamlit_app.py
```

DeepSeek V4 可选规划器：

```powershell
$env:DEEPSEEK_API_KEY = "<api-key>"
$env:FITZSIGHT_DEEPSEEK_MODEL = "deepseek-v4-flash" # 或 deepseek-v4-pro
python scripts/agent_investigate.py --planner deepseek --backend sqlite
```

模型严格白名单：`deepseek-v4-flash`（默认）和 `deepseek-v4-pro`。实现直接使用 `httpx` 调用 `https://api.deepseek.com/chat/completions`。

## 测试与检查

```powershell
python -m pytest
python scripts/final_machine_check.py --skip-streamlit --output docs/V0.13_FINAL_MACHINE_READINESS.json
python scripts/preflight_submission.py --output docs/V0.13_SUBMISSION_PREFLIGHT.json
```

默认最终机器检查不会访问 DeepSeek，并报告 `deepseek_live: not_requested`。只有显式添加 `--include-deepseek` 才会发起在线验证。

## 中文 PDF 提交物

- 最终文件：`submission/FitzSight_GOAI_初赛方案_CN.pdf`
- HTML 可复现源：`submission/deck-cn/index.html`
- 规格：中文、12 页、16:9、瑞士国际主义 / IKB 蓝
- 工具：`guizang-ppt-skill`，固定提交 `c91369c449d34755d320a8b81d0734000d99d1ab`
- 不生成或提交 PPTX；初赛门户只上传最终 PDF。

## 许可与边界

项目代码采用 MIT License。第三方模板、运行时依赖及许可证见 `THIRD_PARTY_NOTICES.md`。FitzSight 只提供分析决策支持，不提供投资建议、授信/适当性/AML 决策，也不执行交易、转账、冻结账户或对客户产生自动不利影响的动作。

## 在线 Demo 部署

入口为 `streamlit_app.py`。Streamlit Community Cloud 会安装根目录中固定版本的 `requirements.txt`；`DEEPSEEK_API_KEY` 仅通过服务器端 Secrets 配置。公开预设、会话与进程调用额度、确定性分析、安全遥测及部署验收步骤见 [`docs/ONLINE_DEMO_DEPLOYMENT.md`](docs/ONLINE_DEMO_DEPLOYMENT.md)。
