import json
from types import SimpleNamespace

import pytest

from fitzsight.agent.planner import NET_DEPOSIT_ACTIONS, NET_DEPOSIT_INTENT, UnsupportedIntentError
from fitzsight.providers.openai_planner import OpenAIResponsesPlanner

QUESTION = "Why did European net deposits fall in the week starting August 3?"


class FakeResponses:
    def __init__(self):
        self.calls = []

    def create(self, **kwargs):
        self.calls.append(kwargs)
        payload = {
            "intent": NET_DEPOSIT_INTENT,
            "steps": [
                {"action": action, "purpose": f"Perform approved {action} analysis."}
                for action in NET_DEPOSIT_ACTIONS
            ],
        }
        return SimpleNamespace(output_text=json.dumps(payload))


class FakeClient:
    def __init__(self):
        self.responses = FakeResponses()


def test_openai_responses_planner_uses_strict_structured_output_and_local_validation():
    client = FakeClient()
    planner = OpenAIResponsesPlanner(model="test-model", client=client)
    plan = planner.plan(QUESTION)

    assert plan.intent == NET_DEPOSIT_INTENT
    assert plan.planner_mode == "openai_responses_structured"
    assert len(client.responses.calls) == 1

    call = client.responses.calls[0]
    assert call["model"] == "test-model"
    assert call["store"] is False
    assert call["text"]["format"]["type"] == "json_schema"
    assert call["text"]["format"]["strict"] is True
    assert call["text"]["format"]["schema"]["properties"]["intent"]["enum"] == [
        NET_DEPOSIT_INTENT
    ]


def test_openai_provider_is_not_called_for_unsupported_question():
    client = FakeClient()
    planner = OpenAIResponsesPlanner(model="test-model", client=client)
    with pytest.raises(UnsupportedIntentError):
        planner.plan("Which stock should I buy tomorrow?")
    assert client.responses.calls == []
