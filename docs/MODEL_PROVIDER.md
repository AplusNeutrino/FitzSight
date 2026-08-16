# DeepSeek V4 Provider

## 配置

| 项目 | 值 |
|---|---|
| 端点 | `https://api.deepseek.com/chat/completions` |
| 默认模型 | `deepseek-v4-flash` |
| 可选模型 | `deepseek-v4-pro` |
| 密钥 | `DEEPSEEK_API_KEY` |
| 模型环境变量 | `FITZSIGHT_DEEPSEEK_MODEL` |
| HTTP 客户端 | `httpx` |

模型名执行严格白名单；旧模型名和任意值在构造 Provider 时立即拒绝。

## 请求契约

`DeepSeekChatPlanner` 发送非流式 Chat Completions 请求：

- `response_format={"type":"json_object"}`；
- `thinking={"type":"disabled"}`；
- `temperature=0`；
- `max_tokens=800`；
- 30 秒默认超时。

系统提示词要求 JSON，并提供目标 JSON 示例。收到响应后，本地 `StructuredJSONPlanner` 再次校验意图、步骤、顺序与动作白名单。

## 安全顺序

1. 本地 `classify_supported_intent` 先判定问题；不支持意图在网络调用前终止。
2. Provider 只能解释本地已固定的动作序列。
3. SQL、参数、统计数值与 Evidence ID 均由本地确定性组件产生。
4. 遥测只记录请求/响应模型、耗时、token、请求 ID 与意图；不记录密钥、完整提示词或思考内容。

## 验证状态

v0.13.0 按发布决定不执行真实 Provider 调用。单元测试使用 Mock 覆盖请求契约、错误、超时、截断、JSON 与脱敏；最终报告固定记录 `deepseek_live: not_requested`，不生成虚假的在线延迟或成功状态。

官方契约：

- https://api-docs.deepseek.com/api/create-chat-completion
- https://api-docs.deepseek.com/quick_start/pricing/
