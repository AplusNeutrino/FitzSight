# Optional Model Provider Boundary

## OpenAI Responses planner

v0.6 includes an optional `OpenAIResponsesPlanner`.

The provider exists only above the deterministic FitzSight intent/tool boundary.

```text
Question
  ↓
local scope classifier
  ↓
OpenAI Responses planner (optional)
  ↓ strict JSON schema
local plan validator
  ↓
deterministic investigation engine
```

## Request policy

The provider implementation:

- uses `client.responses.create(...)`;
- uses `text.format.type = "json_schema"`;
- enables strict schema adherence;
- uses the SDK `output_text` convenience property;
- sends `store=False`;
- never exposes SQL/tool arguments in the allowed output schema.

The implementation follows the current official OpenAI Responses/Structured Outputs API shape as checked on 2026-08-11.

Official references:

- https://platform.openai.com/docs/api-reference/responses
- https://platform.openai.com/docs/quickstart

## Local validation remains authoritative

Even strict model output is not trusted automatically.

After the provider returns JSON:

1. FitzSight parses it;
2. requires the exact allowed object shape;
3. checks the intent against the local classifier;
4. checks the exact action sequence;
5. rejects SQL/high-impact language in step purposes;
6. only then passes control to the deterministic executor.

## Credentials

`OPENAI_API_KEY` must come from the environment.

Never commit credentials.

The model name is supplied through:

```text
FITZSIGHT_MODEL
```

or CLI `--model`.

## Build validation boundary

The build sandbox does not have a live API credential. Therefore v0.6 validates the provider using a fake Responses client and verifies the exact request configuration and local post-generation validation.

A live API call remains a deployment-environment validation task.
