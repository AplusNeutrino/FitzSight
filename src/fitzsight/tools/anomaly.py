from __future__ import annotations

from typing import Iterable, Sequence

import numpy as np

from fitzsight.evidence.registry import EvidenceRegistry
from .base import ToolResult


class AnomalyDetectionTool:
    """Deterministic robust anomaly detector for scalar time-series values.

    The baseline center is the median. Scale is 1.4826 * MAD, with sample standard
    deviation as a fallback when MAD is zero. This is intentionally simple and
    inspectable for the competition MVP; it is not presented as a forecasting
    model or causal detector.
    """

    def __init__(self, registry: EvidenceRegistry) -> None:
        self.registry = registry

    def baseline_threshold(
        self,
        *,
        baseline_values: Iterable[float],
        current_values: Iterable[float],
        current_labels: Sequence[str] | None = None,
        direction: str = "two_sided",
        threshold: float = 3.5,
    ) -> ToolResult:
        baseline = np.asarray(list(baseline_values), dtype=float)
        current = np.asarray(list(current_values), dtype=float)
        if len(baseline) < 3:
            raise ValueError("baseline_values must contain at least 3 observations")
        if len(current) == 0:
            raise ValueError("current_values must be non-empty")
        if not np.all(np.isfinite(baseline)) or not np.all(np.isfinite(current)):
            raise ValueError("anomaly detector requires finite numeric values")
        if direction not in {"high", "low", "two_sided"}:
            raise ValueError("direction must be high, low, or two_sided")
        if threshold <= 0:
            raise ValueError("threshold must be positive")

        if current_labels is None:
            labels = [str(i) for i in range(len(current))]
        else:
            labels = [str(value) for value in current_labels]
            if len(labels) != len(current):
                raise ValueError("current_labels length must match current_values")

        center = float(np.median(baseline))
        mad = float(np.median(np.abs(baseline - center)))
        robust_scale = 1.4826 * mad
        scale_method = "mad"
        if robust_scale <= 1e-12:
            robust_scale = float(np.std(baseline, ddof=1)) if len(baseline) > 1 else 0.0
            scale_method = "std_fallback"
        if robust_scale <= 1e-12:
            robust_scale = 1.0
            scale_method = "unit_fallback"

        z_scores = (current - center) / robust_scale
        if direction == "high":
            flags = z_scores > threshold
        elif direction == "low":
            flags = z_scores < -threshold
        else:
            flags = np.abs(z_scores) > threshold

        observations = [
            {
                "label": label,
                "value": float(value),
                "robust_z": float(z),
                "is_anomaly": bool(flag),
            }
            for label, value, z, flag in zip(labels, current, z_scores, flags, strict=True)
        ]

        payload = {
            "method": "baseline_robust_threshold",
            "direction": direction,
            "threshold": float(threshold),
            "baseline_n": int(len(baseline)),
            "current_n": int(len(current)),
            "baseline_center": center,
            "baseline_scale": robust_scale,
            "scale_method": scale_method,
            "lower_threshold": center - threshold * robust_scale,
            "upper_threshold": center + threshold * robust_scale,
            "anomaly_count": int(np.sum(flags)),
            "anomaly_rate": float(np.mean(flags)),
            "observations": observations,
        }
        record = self.registry.register(
            "anomaly_detection.baseline_threshold",
            {
                "direction": direction,
                "threshold": threshold,
                "baseline_n": len(baseline),
                "current_n": len(current),
            },
            payload,
        )
        return ToolResult(record.evidence_id, "anomaly_detection.baseline_threshold", payload)
