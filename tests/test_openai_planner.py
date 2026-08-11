import json
from types import SimpleNamespace

import pytest

from fitzsight.agent.planner import (
    CUSTOMER_INTELLIGENCE_INTENT,
    NET_DEPOSIT_INTENT,
    UnsupportedIntentError,
)
from fitzsight.providers.openai_planner import OpenAIResponsesPlanner

NET_QUESTION = "Why did European net deposits fall in the week starting August 3?"
SEGMENT_QUESTION = (
    "How are European customer segments distributed by behavioral value, "
    "and which segment contributes most to deposits?"
)


class FakeResponses:
    def __init__(self):
        self.calls = []

    def create(self, **kwargs):
        self.calls.append(kwargs)
        schema = kwargs["text"]["format"]["schema"]
        intent = schema["properties"]["intent"]["enum"][0]
        actions = schema["properties"]["steps"]["items"]["properties"]["action"]["enum"]
        payload = {
            "intent": intent,
            "steps": [
                {"action": action, "purpose": f"Perform approved {action} analysis."}
                for action in actions
            ],
        }
        return SimpleNamespace(output_text=json.dumps(payload))


class FakeClient:
    def __init__(self):
        self.responses = FakeResponses()


def test_openai_responses_planner_uses_strict_structured_output_and_local_validation():
    client = FakeClient()
    planner = OpenAIResponsesPlanner(model="test-model", client=client)
    plan = planner.plan(NET_QUESTION)

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


def test_openai_responses_schema_supports_customer_intelligence_intent():
    client = FakeClient()
    planner = OpenAIResponsesPlanner(model="test-model", client=client)
    plan = planner.plan(SEGMENT_QUESTION)
    assert plan.intent == CUSTOMER_INTELLIGENCE_INTENT
    assert len(client.responses.calls) == 1
    call = client.responses.calls[0]
    assert call["text"]["format"]["schema"]["properties"]["intent"]["enum"] == [
        CUSTOMER_INTELLIGENCE_INTENT
    ]


def test_openai_provider_is_not_called_for_unsupported_question():
    client = FakeClient()
    planner = OpenAIResponsesPlanner(model="test-model", client=client)
    with pytest.raises(UnsupportedIntentError):
        planner.plan("Which stock should I buy tomorrow?")
    assert client.responses.calls == []
