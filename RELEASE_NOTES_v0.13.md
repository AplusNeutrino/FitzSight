# FitzSight v0.13.0 Release Notes

- 将可选规划 Provider 迁移为 DeepSeek V4 Flash/Pro，使用严格模型白名单和直接 `httpx` 请求。
- 删除旧 Provider 类、SDK 依赖、密钥变量、CLI 参数、运行验证脚本与 UI 入口。
- 保持本地意图门控、确定性计算、Evidence Registry 和失败即关闭核验不变。
- 新增请求契约、网络前拒绝、HTTP/超时/空响应/截断/非法 JSON 与遥测脱敏测试。
- 将最终机器在线开关更名为 `--include-deepseek`；默认发布证据为 `deepseek_live: not_requested`。
- 用 guizang-ppt-skill Swiss / IKB 风格生成全中文 12 页 16:9 PDF。
- 初赛唯一上传文件改为 `FitzSight_GOAI_初赛方案_CN.pdf`，删除 PPTX 构建链与旧提交稿。
- 收紧交付包为显式允许列表并加入网站行动跟踪器快照。
