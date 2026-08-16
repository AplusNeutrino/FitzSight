import json

import pytest

from fitzsight.agent.planner import (
    NET_DEPOSIT_INTENT,
    PlanValidationError,
    UnsupportedIntentError,
)
from fitzsight.providers.deepseek_planner import (
    DEEPSEEK_CHAT_COMPLETIONS_URL,
    DeepSeekChatPlanner,
    DeepSeekPlannerConfigurationError,
)


NET_QUESTION = "Why did European net deposits fall in the week starting August 3?"


class FakeResponse:
    def __init__(self, payload, *, error=None):
        self.payload = payload
        self.error = error

    def raise_for_status(self):
        if self.error:
            raise self.error

    def json(self):
        return self.payload


class FakeClient:
    def __init__(self, *, payload=None, error=None):
        self.calls = []
        self.payload = payload
        self.error = error

    def post(self, url, **kwargs):
        self.calls.append((url, kwargs))
        payload = self.payload
        if payload is None:
            body = kwargs["json"]
            system = body["messages"][0]["content"]
            marker = "Example JSON shape: "
            plan = json.loads(system.split(marker, 1)[1])
            payload = {
                "id": "chatcmpl_test_123",
                "model": body["model"],
                "choices": [
                    {
                        "finish_reason": "stop",
                        "message": {"role": "assistant", "content": json.dumps(plan)},
                    }
                ],
                "usage": {
                    "prompt_tokens": 42,
                    "completion_tokens": 18,
                    "total_tokens": 60,
                },
            }
        return FakeResponse(payload, error=self.error)


def test_deepseek_planner_defaults_to_flash_and_uses_json_output(monkeypatch):
    monkeypatch.delenv("FITZSIGHT_DEEPSEEK_MODEL", raising=False)
    client = FakeClient()
    planner = DeepSeekChatPlanner(api_key="test-secret", client=client)
    plan = planner.plan(NET_QUESTION)

    assert planner.model == "deepseek-v4-flash"
    assert plan.intent == NET_DEPOSIT_INTENT
    assert plan.planner_mode == "deepseek_chat_json"
    assert len(client.calls) == 1
    url, call = client.calls[0]
    assert url == DEEPSEEK_CHAT_COMPLETIONS_URL
    assert call["headers"]["Authorization"] == "Bearer test-secret"
    assert call["json"]["response_format"] == {"type": "json_object"}
    assert call["json"]["thinking"] == {"type": "disabled"}
    assert call["json"]["stream"] is False
    assert call["json"]["max_tokens"] == 800
    assert planner.last_telemetry["provider"] == "deepseek"
    assert planner.last_telemetry["request_id"] == "chatcmpl_test_123"
    assert planner.last_telemetry["total_tokens"] == 60
    assert "test-secret" not in json.dumps(planner.last_telemetry)


def test_deepseek_planner_allows_pro_model():
    planner = DeepSeekChatPlanner(
        model="deepseek-v4-pro", api_key="test-secret", client=FakeClient()
    )
    assert planner.model == "deepseek-v4-pro"


@pytest.mark.parametrize("model", ["deepseek-chat", "deepseek-reasoner", "other-model"])
def test_deepseek_planner_rejects_non_v4_models(model):
    with pytest.raises(DeepSeekPlannerConfigurationError):
        DeepSeekChatPlanner(model=model, api_key="test-secret", client=FakeClient())


def test_deepseek_provider_is_not_called_for_unsupported_question():
    client = FakeClient()
    planner = DeepSeekChatPlanner(api_key="test-secret", client=client)
    with pytest.raises(UnsupportedIntentError):
        planner.plan("Which stock should I buy tomorrow?")
    assert client.calls == []


@pytest.mark.parametrize(
    "payload",
    [
        {},
        {"choices": []},
        {"choices": [{"finish_reason": "length", "message": {"content": "{}"}}]},
        {"choices": [{"finish_reason": "stop", "message": {"content": ""}}]},
    ],
)
def test_deepseek_planner_rejects_incomplete_responses(payload):
    planner = DeepSeekChatPlanner(
        api_key="test-secret", client=FakeClient(payload=payload)
    )
    with pytest.raises(DeepSeekPlannerConfigurationError):
        planner.plan(NET_QUESTION)


def test_deepseek_planner_wraps_transport_errors_without_key_disclosure():
    planner = DeepSeekChatPlanner(
        api_key="must-not-appear",
        client=FakeClient(error=TimeoutError("transport failed with must-not-appear")),
    )
    with pytest.raises(DeepSeekPlannerConfigurationError) as exc_info:
        planner.plan(NET_QUESTION)
    assert "must-not-appear" not in str(exc_info.value)


def test_deepseek_planner_rejects_invalid_json():
    payload = {
        "id": "invalid-json",
        "model": "deepseek-v4-flash",
        "choices": [{"finish_reason": "stop", "message": {"content": "not-json"}}],
    }
    planner = DeepSeekChatPlanner(api_key="test-secret", client=FakeClient(payload=payload))
    with pytest.raises(PlanValidationError, match="invalid JSON"):
        planner.plan(NET_QUESTION)


def test_deepseek_planner_wraps_http_errors():
    planner = DeepSeekChatPlanner(
        api_key="test-secret",
        client=FakeClient(error=RuntimeError("HTTP 429")),
    )
    with pytest.raises(DeepSeekPlannerConfigurationError, match="RuntimeError"):
        planner.plan(NET_QUESTION)


def test_deepseek_telemetry_records_response_model_and_excludes_prompt():
    client = FakeClient()
    planner = DeepSeekChatPlanner(model="deepseek-v4-pro", api_key="test-secret", client=client)
    planner.plan(NET_QUESTION)
    telemetry = planner.last_telemetry
    assert telemetry["requested_model"] == "deepseek-v4-pro"
    assert telemetry["response_model"] == "deepseek-v4-pro"
    assert telemetry["thinking"] == "disabled"
    assert "prompt" not in telemetry
    assert "reasoning_content" not in telemetry
