# 2026-10-27：锁定环境及比例检验边界验证

北京时间 2026-10-27 13:21。起点 main：`e8db233f81bd18c1375a137d5b2bb58494c97ef0`；实现基线 `ed61aa9c086d99b99b81a7e0467f44ee866c9d5e`。本记录与修复同提交，提交标题 `fix: handle sparse proportion tests and record locked baseline`。运行前远程无未合并 PR，仓库内未发现 AGENTS.md；读取 README、PROJECT_PROGRESS、IMPLEMENTATION_STATUS 和路线图全文。保留历史竞赛记录，不将历史完成标签视为新路线图验收。

## 批次范围与验收

1. 新建隔离 Python 环境，安装原有 requirements.lock 并检查依赖。
2. 修复 two_proportion 全零/全一导致异常的问题，明确小样本方法与无效输入行为。
3. 以手算概率、普通样本公式、非法输入和全量回归验证，保留原始输出。
4. 更新路线图后，以最新 main 为父提交提交；并发保护不允许覆盖后续更新。

验收：合法常量计数不崩溃且输出可用严格 JSON 序列化；稀疏计数精确概率正确；非法输入不产生成功证据；常规样本保留原 z/chi-square/Wald 计算；锁定环境全量测试无失败。范围不包含连续变量统计、结构化声明、import 模式和五个独立 CLI/UI 演示验收。

## 环境与实际结果

- CPython 3.12.14，Linux 6.18.55 x86_64，glibc 2.39。
- pytest 9.1.1、NumPy 2.5.2、pandas 2.3.3、SciPy 1.18.0、DuckDB 1.5.5。
- `python -m venv ../fitzsight-venv`，激活后 `python -m pip install -r requirements.lock`：成功。
- `python -m pip check`：No broken requirements found。
- `python -m pytest -q tests/test_statistics.py`：39 passed，0.91 秒。
- `python -m pytest -q --junitxml=../fitzsight-full.xml`：144 passed，0 failed，0 errors，0 skipped，76.28 秒；991361 条弃用警告。
- [原始 pytest 输出](2026-10-27-pytest.txt)、[JUnit 记录](2026-10-27-pytest.xml)。路径记录为当轮临时目录，仅作为环境元数据；复现请使用自己的 checkout。

测试包含合成数据、适配器 mock 和规则路径。全量通过不等于真实模型调用、真实业务收益、生产部署或独立人工盲审通过。单独的五个演示流程、产品/竞赛测试分组、全功能现状矩阵仍待后续 M0 验证。

## 统计契约与限制

`two_proportion` 只接受整数计数（含 NumPy 整数，不含布尔值），n 必须大于零，success 在 [0,n]。非法输入抛 ValueError，且不注册成功证据。

只有观测和期望的四格计数均至少为 5 时使用原双比例 z 检验、无连续性校正的卡方检验、非合并 Wald 区间。否则使用双侧 Fisher 精确检验，增加 `p_value_method`、`inference_status`、`asymptotic_valid` 和 `difference_95ci_method`。稀疏样本的 z、卡方统计量/概率、差值置信区间为 null；调用方必须接受 null，不能当作零。现有引擎使用数值 p_value，回归测试通过。

全零/全一状态为 constant_outcome，p=1 不证明总体等价或不存在有业务意义的差异。Fisher 检验条件于边际，仍要求适当的独立抽样假设；不证明因果。稀疏样本的可靠差值区间尚未实现，明确返回不可用，不伪造零宽区间。

方法参考：[SciPy fisher_exact](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.fisher_exact.html)、[SciPy chi2_contingency](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.chi2_contingency.html)。

## 新问题与后续

- ISSUE-001：锁定环境产生 991361 条 NumPy timedelta generic-unit 弃用警告，来自 generator.py 的时间运算。当前测试通过，未来版本可能报错；应修复类型/单位并验证种子可复现性，不能靠关闭警告冒充解决。
- ISSUE-002：连续变量检验尚未统一非有限值、单样本及常量样本行为；M1-03b 待办。
- ISSUE-003：稀疏样本差值区间不可用，已显式披露；需要区间的报告不能宣称完整区间推断。
- 既有 P0 数值错配、固定场景、自动补合成数据仍未解决。
