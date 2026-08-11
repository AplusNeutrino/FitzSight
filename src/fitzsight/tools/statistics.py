from __future__ import annotations

import math
from typing import Iterable

import numpy as np
from scipy.stats import chi2_contingency, mannwhitneyu, norm, ttest_ind

from fitzsight.evidence.registry import EvidenceRegistry
from .base import ToolResult


class StatisticalTestTool:
    def __init__(self, registry: EvidenceRegistry) -> None:
        self.registry = registry

    def two_proportion(
        self,
        *,
        success_a: int,
        n_a: int,
        success_b: int,
        n_b: int,
        label_a: str = "A",
        label_b: str = "B",
    ) -> ToolResult:
        for success, n, label in ((success_a, n_a, label_a), (success_b, n_b, label_b)):
            if n <= 0 or success < 0 or success > n:
                raise ValueError(f"Invalid binomial counts for {label}: success={success}, n={n}")

        p_a = success_a / n_a
        p_b = success_b / n_b
        pooled = (success_a + success_b) / (n_a + n_b)
        pooled_se = math.sqrt(pooled * (1 - pooled) * (1 / n_a + 1 / n_b))
        z = (p_b - p_a) / pooled_se if pooled_se else 0.0
        p_value_z = float(2 * norm.sf(abs(z))) if pooled_se else 1.0

        table = [[success_a, n_a - success_a], [success_b, n_b - success_b]]
        chi2, p_value_chi2, _, _ = chi2_contingency(table, correction=False)

        unpooled_se = math.sqrt(
            p_a * (1 - p_a) / n_a + p_b * (1 - p_b) / n_b
        )
        diff = p_b - p_a
        ci_low = diff - 1.96 * unpooled_se
        ci_high = diff + 1.96 * unpooled_se

        payload = {
            "test": "two_proportion",
            "label_a": label_a,
            "label_b": label_b,
            "success_a": success_a,
            "n_a": n_a,
            "success_b": success_b,
            "n_b": n_b,
            "rate_a": p_a,
            "rate_b": p_b,
            "difference_pp_b_minus_a": diff * 100,
            "z_statistic": float(z),
            "p_value": p_value_z,
            "chi2_statistic": float(chi2),
            "chi2_p_value": float(p_value_chi2),
            "difference_95ci_pp": [ci_low * 100, ci_high * 100],
            "significant_at_0_05": p_value_z < 0.05,
        }
        params = {
            "success_a": success_a,
            "n_a": n_a,
            "success_b": success_b,
            "n_b": n_b,
            "label_a": label_a,
            "label_b": label_b,
        }
        record = self.registry.register("statistical_test.two_proportion", params, payload)
        return ToolResult(record.evidence_id, "statistical_test.two_proportion", payload)

    def continuous_two_sample(
        self,
        values_a: Iterable[float],
        values_b: Iterable[float],
        *,
        method: str = "mannwhitney",
        label_a: str = "A",
        label_b: str = "B",
    ) -> ToolResult:
        a = np.asarray(list(values_a), dtype=float)
        b = np.asarray(list(values_b), dtype=float)
        if len(a) == 0 or len(b) == 0:
            raise ValueError("Both samples must be non-empty")
        if method == "mannwhitney":
            statistic, p_value = mannwhitneyu(a, b, alternative="two-sided")
        elif method == "welch_t":
            statistic, p_value = ttest_ind(a, b, equal_var=False)
        else:
            raise ValueError("method must be 'mannwhitney' or 'welch_t'")

        payload = {
            "test": method,
            "label_a": label_a,
            "label_b": label_b,
            "n_a": int(len(a)),
            "n_b": int(len(b)),
            "median_a": float(np.median(a)),
            "median_b": float(np.median(b)),
            "mean_a": float(np.mean(a)),
            "mean_b": float(np.mean(b)),
            "statistic": float(statistic),
            "p_value": float(p_value),
            "significant_at_0_05": float(p_value) < 0.05,
        }
        params = {"method": method, "label_a": label_a, "label_b": label_b}
        record = self.registry.register("statistical_test.continuous_two_sample", params, payload)
        return ToolResult(record.evidence_id, "statistical_test.continuous_two_sample", payload)
