# 请求契约第一批

`fitzsight.investigation.request.InvestigationRequest.from_dict` 严格接受 metric、filters、baseline、current、timezone、currency、data_snapshot，不默默忽略未知字段。filters目前仅region（Europe/Asia/Americas）；metric仅net_deposits.v1，currency仅USD。

日期为严格YYYY-MM-DD、日历有效、起止包含；基线必须早于本期，不允许重叠。允许不同窗口长度，但不自动按天归一化。timezone目前仅source_naive，明确沿用源时间，不冒充UTC或时区转换。data_snapshot必须显式sha256:加64位小写十六进制；这里只验证格式，尚未验证实际文件内容哈希，不提供快照真实性保证。

对象及Period不可变，JSON输出为独立字典。三地区/三组时期测试只证明契约接受和往返正确，**不是整链参数化验收**。本批没有接入CLI/UI/引擎；旧调查继续固定场景。下一批须接入执行器、快照核对和demo配置，同时迁移N-C1—N-C5参数核验，不能用新请求驱动旧固定查询。
