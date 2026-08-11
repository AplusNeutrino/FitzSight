from fitzsight.evidence.registry import EvidenceRegistry
from fitzsight.tools.statistics import StatisticalTestTool


def test_two_proportion_detects_large_drop():
    tool = StatisticalTestTool(EvidenceRegistry())
    result = tool.two_proportion(
        success_a=230,
        n_a=1000,
        success_b=140,
        n_b=1000,
        label_a="pre",
        label_b="post",
    )
    assert result.data["difference_pp_b_minus_a"] < -8
    assert result.data["p_value"] < 0.001
    assert result.data["significant_at_0_05"] is True
