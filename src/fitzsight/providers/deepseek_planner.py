from __future__ import annotations

import json
import os
import time
from typing import Any

from fitzsight.agent.catalog import actions_for_intent, classify_supported_intent
from fitzsight.agent.planner import StructuredJSONPlanner, UnsupportedIntentError


DEEPSEEK_CHAT_COMPLETIONS_URL = "https://api.deepseek.com/chat/completions"
DEFAULT_DEEPSEEK_MODEL = "deepseek-v4-flash"
ALLOWED_DEEPSEEK_MODELS = frozenset({DEFAULT_DEEPSEEK_MODEL, "deepseek-v4-pro"})


class DeepSeekPlannerConfigurationError(RuntimeError):
    """Raised when the optional DeepSeek planner cannot be configured or called."""


class DeepSeekChatPlanner:
    """Bounded planner using DeepSeek V4 Chat Completions JSON Output.

    A deterministic local classifier fixes the approved intent before any
    provider call. The provider may only describe the published action
    sequence; local plan validation remains authoritative and the model never
    receives permission to create SQL, tool arguments or financial actions.
    """

    mode = "deepseek_chat_json"

    def __init__(
        self,
        *,
        model: str | None = None,
        api_key: str | None = None,
        client: Any | None = None,
        timeout_seconds: float = 30.0,
    ) -> None:
        self.model = (
            model
            or os.getenv("FITZSIGHT_DEEPSEEK_MODEL")
            or DEFAULT_DEEPSEEK_MODEL
        ).strip()
        if self.model not in ALLOWED_DEEPSEEK_MODELS:
            allowed = ", ".join(sorted(ALLOWED_DEEPSEEK_MODELS))
            raise DeepSeekPlannerConfigurationError(
                f"Unsupported DeepSeek model {self.model!r}. Allowed models: {allowed}."
            )
        self._api_key = (api_key or os.getenv("DEEPSEEK_API_KEY", "")).strip()
        if not self._api_key:
            raise DeepSeekPlannerConfigurationError(
                "No DeepSeek API key configured. Set DEEPSEEK_API_KEY."
            )
        self._client = client
        self.timeout_seconds = float(timeout_seconds)
        self.last_telemetry: dict[str, Any] | None = None

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

    @classmethod
    def _messages(cls, intent: str, question: str) -> list[dict[str, str]]:
        actions = list(actions_for_intent(intent))
        schema = json.dumps(cls._schema(intent), ensure_ascii=False, separators=(",", ":"))
        example = {
            "intent": intent,
            "steps": [
                {"action": action, "purpose": f"Explain why {action} is needed."}
                for action in actions
            ],
        }
        return [
            {
                "role": "system",
                "content": (
                    "You are FitzSight's constrained financial-operations planning component. "
                    "Return one JSON object only, without markdown. The local application already "
                    f"fixed the approved intent to {intent!r}. Return exactly that intent and exactly "
                    f"this action sequence in the same order: {', '.join(actions)}. Each purpose must "
                    "briefly explain the analytical reason. Do not output SQL, code, table names, "
                    "numeric results, tool parameters, investment advice, trades, transfers, account "
                    "freezes or customer-contact actions. "
                    f"Required JSON Schema: {schema}. "
                    f"Example JSON shape: {json.dumps(example, ensure_ascii=False)}"
                ),
            },
            {"role": "user", "content": question},
        ]

    def _post(self, payload: dict[str, Any]):
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }
        if self._client is not None:
            return self._client.post(
                DEEPSEEK_CHAT_COMPLETIONS_URL,
                headers=headers,
                json=payload,
                timeout=self.timeout_seconds,
            )
        try:
            import httpx
        except ImportError as exc:
            raise DeepSeekPlannerConfigurationError(
                'httpx is not installed. Install the optional dependency with `pip install -e ".[deepseek]"`.'
            ) from exc
        return httpx.post(
            DEEPSEEK_CHAT_COMPLETIONS_URL,
            headers=headers,
            json=payload,
            timeout=self.timeout_seconds,
        )

    def plan(self, question: str):
        try:
            intent = classify_supported_intent(question)
        except ValueError as exc:
            raise UnsupportedIntentError(
                "Question is outside the approved FitzSight v0.13 intent catalog."
            ) from exc

        request_payload = {
            "model": self.model,
            "messages": self._messages(intent, question),
            "response_format": {"type": "json_object"},
            "thinking": {"type": "disabled"},
            "max_tokens": 800,
            "temperature": 0,
            "stream": False,
        }
        started = time.perf_counter()
        try:
            response = self._post(request_payload)
            response.raise_for_status()
            payload = response.json()
        except Exception as exc:
            if isinstance(exc, DeepSeekPlannerConfigurationError):
                raise
            raise DeepSeekPlannerConfigurationError(
                f"DeepSeek Chat Completions request failed: {type(exc).__name__}."
            ) from exc
        elapsed = time.perf_counter() - started

        try:
            choice = payload["choices"][0]
            finish_reason = choice.get("finish_reason")
            raw = choice["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise DeepSeekPlannerConfigurationError(
                "DeepSeek response did not contain choices[0].message.content."
            ) from exc
        if finish_reason != "stop":
            raise DeepSeekPlannerConfigurationError(
                f"DeepSeek response did not finish normally: {finish_reason!r}."
            )
        if not isinstance(raw, str) or not raw.strip():
            raise DeepSeekPlannerConfigurationError(
                "DeepSeek Chat Completions returned empty message content."
            )

        usage = payload.get("usage") if isinstance(payload, dict) else None
        usage = usage if isinstance(usage, dict) else {}

        def usage_value(name: str) -> int | None:
            value = usage.get(name)
            return int(value) if isinstance(value, (int, float)) else None

        self.last_telemetry = {
            "provider": "deepseek",
            "api": "chat_completions",
            "request_id": payload.get("id"),
            "requested_model": self.model,
            "response_model": payload.get("model"),
            "planning_seconds": elapsed,
            "input_tokens": usage_value("prompt_tokens"),
            "output_tokens": usage_value("completion_tokens"),
            "total_tokens": usage_value("total_tokens"),
            "thinking": "disabled",
            "response_format": "json_object",
            "intent": intent,
        }
        return StructuredJSONPlanner.parse(
            question,
            raw,
            planner_mode=self.mode,
        )
