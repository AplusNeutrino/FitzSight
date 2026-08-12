# FitzSight v0.12.1 Release Notes

## Scope

v0.12.1 is a **competition-asset synchronization and reviewer-gate patch** built on the already-published v0.12.0 core. It does not add a sixth intent, widen planner/tool authority, or claim new live-provider capabilities.

## Changes

- Regenerated the formal 12-slide `FitzSight_GOAI_Initial_Round.pptx` and same-source PDF around **one CRM/FTD hero + one false-correlation refusal**.
- Added runtime-derived hero trace and verified-answer crops to the formal deck.
- Added the tested event-dependency failure branch to the main story.
- Added Evaluation v2 holdout and controlled architecture-ablation evidence to the formal deck, retaining the 75% supported-candidate rate rather than hiding an `insufficient_evidence` holdout.
- Synchronized README, Project Summary, Pitch source, Architecture/Compliance notes, Demo Runbook, video/rehearsal/operator assets, portal copy, field map and submission checklist.
- Completed `docs/V0.12.1_GOAI_REVIEWER_GATE.md` against the official six scoring dimensions and AI+Finance personalized checks.
- Rebuilt upload, manual-handoff and final-machine packages with the synchronized formal assets.

## Evidence boundaries

The formal deck is a validated presentation artifact, not evidence of live Streamlit/OpenAI runtime. Portal/email submission and human rehearsal remain user/manual evidence-gated. Production RBAC/PII/retention controls remain blueprint-only.

## Validation

Release validation completed:

```text
87 tests collected / 86 passed / 1 skipped / 0 failed
compileall: PASS
fixed benchmark: 5/5 PASS
adversarial gate: 8/8 PASS
slide overflow test: PASS
same-source PDF: 12 pages, render-reviewed
submission preflight: PASS
handoff ready_for_user_takeover: true
final-machine local_core_ready: true
deterministic Agent smoke: verified
```

Formal deck hashes are recorded in `docs/V0.12.1_VALIDATION.md`.
