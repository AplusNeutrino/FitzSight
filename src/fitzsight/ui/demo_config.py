from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
import os

ALLOWED_MODELS = frozenset({"deepseek-v4-flash", "deepseek-v4-pro"})
ALLOWED_BACKENDS = frozenset({"auto", "duckdb", "sqlite"})


def _value(name: str, secrets: Mapping[str, object], environ: Mapping[str, str]) -> str:
    raw = secrets.get(name)
    if raw is None or not str(raw).strip():
        raw = environ.get(name, "")
    return str(raw).strip()


def secret_value(
    name: str,
    secrets: Mapping[str, object],
    environ: Mapping[str, str] | None = None,
) -> str:
    """Read one server-side secret without logging or persisting it."""

    return _value(name, secrets, os.environ if environ is None else environ)


def _boolean(value: str, *, default: bool) -> bool:
    if not value:
        return default
    normalized = value.casefold()
    if normalized in {"1", "true", "yes", "on"}:
        return True
    if normalized in {"0", "false", "no", "off"}:
        return False
    raise ValueError(f"Expected a boolean setting, received {value!r}.")


def _positive_int(value: str, *, default: int, maximum: int) -> int:
    if not value:
        return default
    parsed = int(value)
    if parsed < 1 or parsed > maximum:
        raise ValueError(f"Expected an integer from 1 to {maximum}, received {parsed}.")
    return parsed


@dataclass(frozen=True)
class OnlineDemoConfig:
    public_demo: bool = False
    default_model: str = "deepseek-v4-flash"
    backend: str = "auto"
    max_live_calls_per_session: int = 3
    max_live_calls_global: int = 30

    @classmethod
    def from_sources(
        cls,
        secrets: Mapping[str, object],
        environ: Mapping[str, str] | None = None,
    ) -> "OnlineDemoConfig":
        env = os.environ if environ is None else environ
        model = _value("FITZSIGHT_DEEPSEEK_MODEL", secrets, env) or cls.default_model
        if model not in ALLOWED_MODELS:
            raise ValueError(f"Unsupported DeepSeek model {model!r}.")
        backend = _value("FITZSIGHT_BACKEND", secrets, env) or cls.backend
        if backend not in ALLOWED_BACKENDS:
            raise ValueError(f"Unsupported data backend {backend!r}.")
        return cls(
            public_demo=_boolean(
                _value("FITZSIGHT_PUBLIC_DEMO", secrets, env),
                default=False,
            ),
            default_model=model,
            backend=backend,
            max_live_calls_per_session=_positive_int(
                _value("FITZSIGHT_MAX_LIVE_CALLS_PER_SESSION", secrets, env),
                default=3,
                maximum=20,
            ),
            max_live_calls_global=_positive_int(
                _value("FITZSIGHT_MAX_LIVE_CALLS_GLOBAL", secrets, env),
                default=30,
                maximum=500,
            ),
        )
