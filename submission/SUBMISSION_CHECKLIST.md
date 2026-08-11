# FitzSight — GOAI Initial-Round Submission Checklist

## Package identity

- [x] Product name is **FitzSight**.
- [x] Track wording is **GOAI 2026 · Boundless Agents · AI+金融**.
- [x] Public implementation repository is `AplusNeutrino/FitzSight`.
- [x] MIT License is included.
- [x] Third-party notices are included.

## Initial-round presentation assets

- [x] `FitzSight_GOAI_Initial_Round.pptx` generated.
- [x] `FitzSight_GOAI_Initial_Round.pdf` exported from the same deck.
- [x] PDF rendered and visually reviewed for clipping / overlap.
- [x] 12-slide narrative aligns with the implemented v0.7/v0.8 product state.
- [x] Benchmark metrics in the deck are synthetic and labelled through the project narrative.

## Technical evidence

- [x] Five deterministic benchmark scenarios.
- [x] Five-scenario benchmark pass rate: 100% in the current synthetic benchmark suite.
- [x] Eight adversarial release-gate cases.
- [x] EvidenceClaimVerifier remains fail closed.
- [x] DuckDB deployment runtime previously validated.
- [x] Deterministic planner fallback remains available without an external model.
- [ ] OpenAI Responses live planner runtime validated on the final submission/demo environment.
- [ ] Streamlit runtime smoke-tested on the final submission/demo environment.

## Data / compliance

- [x] Synthetic benchmark data only.
- [x] No former-employer exports or confidential business datasets.
- [x] No real customer PII.
- [x] No API secrets committed.
- [x] `_gt` evaluation fields remain prohibited from normal Agent SQL.
- [x] No investment advice / trading actions / AML enforcement / credit decisions.

## Demo readiness

- [x] One-command launcher implemented: `python scripts/start_demo.py`.
- [x] CLI fallback available.
- [x] Demo runbook prepared.
- [ ] Streamlit live path verified on final presentation laptop.
- [ ] Screen recording completed.
- [ ] Offline/local recording copied to a second location.

## Portal submission — user action

These items require the actual GOAI portal / email workflow and must not be marked complete from repository evidence alone.

- [ ] Re-check the latest official submission fields and file-size limits.
- [ ] Upload project introduction.
- [ ] Upload PPT/PDF.
- [ ] Add repository link.
- [ ] Add demo/video link if supplied.
- [ ] Submit before the deadline rather than at the final minute.
- [ ] Capture confirmation screenshot / email.
- [ ] Save a final offline copy of all submitted assets.
