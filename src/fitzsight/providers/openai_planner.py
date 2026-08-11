from __future__ import annotations

import json
import os
import time
from typing import Any

from fitzsight.agent.catalog import INTENT_ACTIONS, actions_for_intent, classify_supported_intent
from fitzsight.agent.planner import StructuredJSONPlanner, UnsupportedIntentError


class OpenAIPlannerConfigurationError(RuntimeError):
    """Raised when the optional OpenAI planner cannot be initialized."""


class OpenAIResponsesPlanner:
    """Optional live planner using the OpenAI Responses API.

    The provider is deliberately narrow:
    - a deterministic local classifier gates the question before API use;
    - the selected intent is fixed locally;
    - Structured Outputs may emit only the published action names;
    - local `validate_plan` still checks exact order and scope after generation;
    - the model never receives permission to produce SQL/tool arguments.

    The OpenAI SDK is imported lazily so the core deterministic demo has no
    dependency on an external provider.
    """

    mode = "openai_responses_structured"

    def __init__(
        self,
        *,
        model: str | None = None,
        client: Any | None = None,
    ) -> None:
        self.model = (model or os.getenv("FITZSIGHT_MODEL", "")).strip()
        if not self.model:
            raise OpenAIPlannerConfigurationError(
                "No model configured. Set FITZSIGHT_MODEL or pass model=..."
            )
        self._client = client
        self.last_telemetry: dict[str, Any] | None = None

    def _client_or_create(self):
        if self._client is not None:
            return self._client
        try:
            from openai import OpenAI
        except ImportError as exc:
            raise OpenAIPlannerConfigurationError(
                "OpenAI SDK is not installed. Install the optional dependency with "
                '`pip install -e ".[openai]"`.'
            ) from exc
        self._client = OpenAI()
        return self._client

    @staticmethod
    def _schema(intent: str) -> dict[str, Any]:
        actions = list(actions_for_intent(intent))
        return {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "intent": {"type": "string", "enum": [intent]},
                "steps": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "additionalProperties": False,
                        "properties": {
                            "action": {"type": "string", "enum": actions},
                            "purpose": {"type": "string"},
                        },
                        "required": ["action", "purpose"],
                    },
                },
            },
            "required": ["intent", "steps"],
        }

    @staticmethod
    def _instructions(intent: str) -> str:
        actions = actions_for_intent(intent)
        return (
            "You are FitzSight's constrained financial-operations planning component. "
            "The local application has already classified the question into an approved "
            f"intent: {intent}. Return exactly that intent and exactly this action sequence "
            f"in the same order: {', '.join(actions)}. "
            "For each action, write one concise purpose explaining the analytical reason. "
            "Do not output SQL, code, table names, numeric results, tool parameters, "
            "investment advice, trade actions, transfers, account freezes, or customer-contact actions."
        )

    def plan(self, question: str):
        # Local scope gate occurs before provider invocation.
        try:
            intent = classify_supported_intent(question)
        except ValueError as exc:
            raise UnsupportedIntentError(
                "Question is outside the approved FitzSight v0.7 intent catalog."
            ) from exc
        client = self._client_or_create()
        started = time.perf_counter()
        response = client.responses.create(
            model=self.model,
            instructions=self._instructions(intent),
            input=question,
            text={
                "format": {
                    "type": "json_schema",
                    "name": "fitzsight_agent_plan",
                    "description": "A constrained FitzSight investigation plan.",
                    "strict": True,
                    "schema": self._schema(intent),
                }
            },
            store=False,
        )
        elapsed = time.perf_counter() - started
        usage = getattr(response, "usage", None)
        def usage_value(name: str) -> int | None:
            value = getattr(usage, name, None) if usage is not None else None
            return int(value) if isinstance(value, (int, float)) else None
        self.last_telemetry = {
            "provider": "openai",
            "api": "responses",
            "response_id": getattr(response, "id", None),
            "requested_model": self.model,
            "response_model": getattr(response, "model", None),
            "planning_seconds": elapsed,
            "input_tokens": usage_value("input_tokens"),
            "output_tokens": usage_value("output_tokens"),
            "total_tokens": usage_value("total_tokens"),
            "store": False,
            "intent": intent,
        }
        raw = getattr(response, "output_text", None)
        if not isinstance(raw, str) or not raw.strip():
            raise OpenAIPlannerConfigurationError(
                "OpenAI Responses API returned no output_text for the planner."
            )
        return StructuredJSONPlanner.parse(
            question,
            raw,
            planner_mode=self.mode,
        )
