# SQL 绑定参数（M1-01a）

`ReadOnlySQLTool.run(sql, parameters=[...])` 使用两后端原生位置绑定，SQL 模板采用 `?`，参数绝不拼接到 SQL。未传 parameters 的既有调用兼容。

```python
result = sql_tool.run(
    'SELECT customer_id FROM customers WHERE region = ?',
    parameters=['Europe'],
)
```

参数容器仅接受 list/tuple；值仅接受内置 str、bool、带符号64位 int、有限 float、None。日期由调用者明确转换为 ISO 字符串，不自动推断时区。字段名/表名不能通过值绑定选择；净入金明细查询表名仅允许 deposits/withdrawals。请求级 metric、filters、timezone、currency、data_snapshot 白名单仍待实现。

SQL 模板仍经过只读校验，行数上限和 compact preview 保持生效。成功、后端失败证据都记录 `parameters.bound_parameters`；先复制参数，调用后修改原列表不会改写该记录。类型错误和 SQL 安全拒绝发生在执行之前，不产生成功证据；占位符数量等后端错误产生 error 证据并抛 RuntimeError。

净入金明细的日期/地区、区域汇总的日期已迁移。日期仍采用原口径：起始日包含，结束日的下一日排除。状态 completed 为固定 SQL 常量，金额仍要求 USD。事件查询及其他调查尚未迁移；完整参数化调查、通用指标目录、历史客户快照及数据质量验收未完成。

边界：绑定防止值成为 SQL 语法，不代替业务口径校验或数据库权限控制；记录参数不等于签名或持久化快照。证据包含原值，只应传入本任务批准的分析参数，不应传入凭据。后续参数化必须同步更新 Claim 核验的固定地区/窗口约束，不能只放开查询。
