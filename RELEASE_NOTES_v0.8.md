# FitzSight v0.8.0 Release Notes

**Theme:** Initial-Round Submission Sprint

v0.8 stops expanding the core benchmark catalog and converts the existing validated system into competition-facing submission and demo assets.

## Added

- `scripts/start_demo.py`
  - one-command demo launcher;
  - Streamlit when the UI dependency is available;
  - deterministic CLI fallback otherwise;
  - explicit `--mode ui|cli|auto`;
  - dry-run command inspection.
- `scripts/preflight_submission.py`
  - checks required submission files;
  - verifies generated CSVs are not packaged;
  - scans for obvious OpenAI-style secrets;
  - reports PPTX/PDF hashes and sizes.
- `scripts/build_pitch_deck.py`
  - reproducibly generates the formal 12-slide initial-round deck;
  - exports PDF through LibreOffice when available.
- `submission/FitzSight_GOAI_Initial_Round.pptx`.
- `submission/FitzSight_GOAI_Initial_Round.pdf`.
- `submission/DEMO_RUNBOOK.md`.
- `submission/PITCH_SPEAKER_NOTES.md`.
- `submission/SUBMISSION_CHECKLIST.md`.

## Preserved architecture boundaries

- model/planner cannot generate arbitrary SQL or high-impact financial actions;
- deterministic tools own numerical calculation;
- supported factual claims require Evidence IDs;
- verification failure remains fail closed;
- UI/deck remain presentation layers rather than analytical authorities.

## Runtime status

DuckDB deployment runtime was already validated before v0.8. OpenAI live API and Streamlit live runtime remain pending until separate real deployment evidence is provided.

## Build validation

```text
59 tests collected
58 passed, 1 skipped
compileall PASS
5 / 5 deterministic benchmark scenarios PASS
8 / 8 adversarial cases PASS
submission preflight PASS
```

The single build-sandbox skip is the DuckDB-specific integration test. Separate deployment evidence has already validated DuckDB.

Presentation validation:

```text
12-slide PPTX generated
PDF exported from same PPTX
PDF render-review PASS
PPTX SHA-256 25e11a245cc09017e7a6f710f605cf13a59c457711e19dc900773fc8118553f1
PDF  SHA-256 41e58215828281891c6138d18a379926f4ad111efb1b599754db656626f43421
```
