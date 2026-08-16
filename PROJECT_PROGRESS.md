# FitzSight 项目进度

## v0.13.0 已完成

- 统一产品名称为 FitzSight。
- 移除旧 Provider 的代码、依赖、环境变量、CLI 选项与 UI 入口。
- 新增 DeepSeek V4 Flash/Pro 严格白名单 Provider，使用 `httpx` 直接请求。
- 保留网络前意图门控、确定性工具与失败即关闭核验。
- 新增 Provider Mock、错误路径、遥测脱敏和网络前拒绝测试。
- 将最终机器检查改为 `--include-deepseek` 显式在线开关；默认 `deepseek_live: not_requested`。
- 用 guizang Swiss / IKB 模板制作中文 12 页 HTML，并导出 PDF-only 提交物。
- 将上传包和最终机器包改为显式允许列表，排除虚拟环境、缓存、生成数据、旧稿和临时输出。

## 后续人工动作

1. 在最终演示机器运行完整检查和 Streamlit 健康检查。
2. 人工上传 `FitzSight_GOAI_初赛方案_CN.pdf`，复核门户内容并保存回执。
3. 若需要 Provider 在线证据，单独决定是否运行 `--include-deepseek`；当前发布不声称在线成功或真实延迟。
