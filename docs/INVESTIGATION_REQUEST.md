# 请求契约第一批

`fitzsight.investigation.request.InvestigationRequest.from_dict` 严格接受 metric、filters、baseline、current、timezone、currency、data_snapshot，不默默忽略未知字段。filters目前仅region（Europe/Asia/Americas）；metric仅net_deposits.v1，currency仅USD。

日期为严格YYYY-MM-DD、日历有效、起止包含；基线必须早于本期，不允许重叠。允许不同窗口长度，但不自动按天归一化。timezone目前仅source_naive，明确沿用源时间，不冒充UTC或时区转换。data_snapshot必须显式sha256:加64位小写十六进制；这里只验证格式，尚未验证实际文件内容哈希，不提供快照真实性保证。

对象及Period不可变，JSON输出为独立字典。三地区/三组时期测试只证明契约接受和往返正确，**不是整链参数化验收**。本批没有接入CLI/UI/引擎；旧调查继续固定场景。下一批须接入执行器、快照核对和demo配置，同时迁移N-C1—N-C5参数核验，不能用新请求驱动旧固定查询。

## 显式内容核对（RUN-19）

`fingerprint_net_inputs(data_dir)` 对business_events/customers/deposits/withdrawals四个CSV逐字节计算SHA-256；清单采用format=fitzsight.net-inputs.v1、files为文件名到哈希的映射，JSON按键排序、无多余空格、UTF-8，再计算清单SHA-256。请求的 `verify_snapshot(data_dir)` 比较此标识，内容不匹配时拒绝；构造请求本身仍只检查格式。

目录位置和mtime不参与标识；其他文件（包括评测真值）不参与。缺文件、目录冒充文件、符号链接拒绝，不生成或修改源数据。这不是CSV质量验证，也不是签名或不可变数据库快照；调用者必须防止并发写入。检查后的文件仍可能改变，后续执行器必须使用冻结输入或独立核对实际加载的数据，不能用本方法声称已完成运行时快照绑定。本批未自动接入旧runtime或调查链。
