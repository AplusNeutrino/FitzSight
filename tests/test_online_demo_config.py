from __future__ import annotations

import pytest

from fitzsight.ui.demo_config import OnlineDemoConfig, secret_value


def test_cloud_secrets_override_environment():
    config = OnlineDemoConfig.from_sources(
        {
            "FITZSIGHT_PUBLIC_DEMO": True,
            "FITZSIGHT_DEEPSEEK_MODEL": "deepseek-v4-pro",
            "FITZSIGHT_MAX_LIVE_CALLS_PER_SESSION": 4,
            "FITZSIGHT_MAX_LIVE_CALLS_GLOBAL": 40,
            "FITZSIGHT_BACKEND": "sqlite",
        },
        {
            "FITZSIGHT_PUBLIC_DEMO": "false",
            "FITZSIGHT_DEEPSEEK_MODEL": "deepseek-v4-flash",
        },
    )
    assert config.public_demo is True
    assert config.default_model == "deepseek-v4-pro"
    assert config.max_live_calls_per_session == 4
    assert config.max_live_calls_global == 40
    assert config.backend == "sqlite"


def test_online_demo_defaults_are_bounded():
    config = OnlineDemoConfig.from_sources({}, {})
    assert config.public_demo is False
    assert config.default_model == "deepseek-v4-flash"
    assert config.max_live_calls_per_session == 3
    assert config.max_live_calls_global == 30
    assert config.backend == "auto"


@pytest.mark.parametrize(
    ("name", "value"),
    [
        ("FITZSIGHT_DEEPSEEK_MODEL", "deepseek-chat"),
        ("FITZSIGHT_BACKEND", "postgres"),
        ("FITZSIGHT_MAX_LIVE_CALLS_PER_SESSION", "0"),
        ("FITZSIGHT_MAX_LIVE_CALLS_GLOBAL", "501"),
        ("FITZSIGHT_PUBLIC_DEMO", "maybe"),
    ],
)
def test_online_demo_rejects_invalid_settings(name, value):
    with pytest.raises((TypeError, ValueError)):
        OnlineDemoConfig.from_sources({name: value}, {})


def test_secret_value_prefers_cloud_secret_without_persisting_it():
    key = secret_value("DEEPSEEK_API_KEY", {"DEEPSEEK_API_KEY": "cloud-secret"}, {"DEEPSEEK_API_KEY": "env-secret"})
    assert key == "cloud-secret"
    assert "cloud-secret" not in repr(OnlineDemoConfig.from_sources({}, {}))
