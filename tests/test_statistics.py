import json
import math

import numpy as np
import pytest

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


@pytest.mark.parametrize("a,na,b,nb", [(0,10,0,20), (10,10,20,20)])
def test_constant_outcome_is_finite_without_false_precision(a, na, b, nb):
    registry = EvidenceRegistry()
    result = StatisticalTestTool(registry).two_proportion(
        success_a=a, n_a=na, success_b=b, n_b=nb,
    )
    data = result.data
    assert data["difference_pp_b_minus_a"] == 0
    assert data["p_value"] == 1
    assert data["significant_at_0_05"] is False
    assert data["inference_status"] == "constant_outcome"
    assert data["p_value_method"] == "fisher_exact_two_sided"
    assert data["difference_95ci_pp"] is None
    assert data["chi2_statistic"] is None
    assert data["z_statistic"] is None
    json.dumps(data, allow_nan=False)
    assert registry.get(result.evidence_id).status == "success"


@pytest.mark.parametrize("a,na,b,nb,expected", [
    (0,1,1,1,1.0),
    (0,10,10,10,2 / math.comb(20,10)),
    (6,8,1,5,0.10256410256410256),
])
def test_sparse_tables_use_exact_two_sided_probability(a, na, b, nb, expected):
    data = StatisticalTestTool(EvidenceRegistry()).two_proportion(
        success_a=a, n_a=na, success_b=b, n_b=nb,
    ).data
    assert data["p_value"] == pytest.approx(expected)
    assert data["p_value_method"] == "fisher_exact_two_sided"
    assert data["inference_status"] == "sparse_exact"
    assert data["difference_95ci_pp"] is None
    json.dumps(data, allow_nan=False)


@pytest.mark.parametrize("field,value", [
    (field, value)
    for field in ("success_a", "n_a", "success_b", "n_b")
    for value in (True, np.bool_(False), 1.5, float("nan"), float("inf"), None, "2")
] + [("n_a",0), ("n_b",-1), ("success_a",-1), ("success_b",11)])
def test_invalid_counts_fail_before_evidence_is_registered(field, value):
    registry = EvidenceRegistry()
    counts = dict(success_a=2, n_a=10, success_b=3, n_b=10)
    counts[field] = value
    with pytest.raises(ValueError, match="Invalid binomial counts"):
        StatisticalTestTool(registry).two_proportion(**counts)
    assert not registry.records()


def test_numpy_counts_normalized_and_large_sample_formula_unchanged():
    data = StatisticalTestTool(EvidenceRegistry()).two_proportion(
        success_a=np.int64(230), n_a=np.int64(1000), success_b=140, n_b=1000,
    ).data
    expected_z = (-0.09) / math.sqrt(0.185 * 0.815 * 0.002)
    assert data["z_statistic"] == pytest.approx(expected_z)
    assert data["chi2_statistic"] == pytest.approx(expected_z ** 2)
    assert data["p_value"] == pytest.approx(data["chi2_p_value"])
    assert data["p_value_method"] == "two_proportion_z"
    assert data["difference_95ci_pp"][0] < -9 < data["difference_95ci_pp"][1]
    json.dumps(data, allow_nan=False)
