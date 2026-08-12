# FitzSight Initial-Round Submission Assets

This directory contains the current competition-facing assets generated from the implemented and validated FitzSight project state.

## Presentation

- `FitzSight_GOAI_Initial_Round.pptx` — editable 12-slide deck.
- `FitzSight_GOAI_Initial_Round.pdf` — PDF exported from the same PPTX and visually reviewed after rendering.
- `PITCH_SPEAKER_NOTES.md` — concise notes generated from the same current verified metrics used by the demo slides.

## Offline demo fallbacks

- `FitzSight_Offline_Demo.html` — self-contained five-workflow offline evidence demo.
- `FitzSight_Offline_Demo.json` — compact source summary from five verified Agent runs.
- `FitzSight_Offline_Demo_Backup.mp4` — deterministic 1280x720 H.264 backup video generated from the verified offline-demo data.

## Submission operations

- `PORTAL_COPY.md` — ready-to-paste Chinese/English project introduction and safety copy.
- `DEMO_RUNBOOK.md` — recommended live-demo route and fallback order.
- `DEMO_VIDEO_SCRIPT.md` — real screen-recording plan if Streamlit is validated on the final machine.
- `PITCH_REHEARSAL.md` — 6:30 pitch / 2:20 demo timing target and rehearsal log.
- `SUBMISSION_CHECKLIST.md` — repository, compliance, runtime, and portal submission checklist.
- `JUDGE_QA.md` — judge-facing Q&A preparation.
- `FitzSight_GOAI_Upload_Bundle.zip` — convenience bundle; the actual portal may still require individual uploads.

## v0.10 manual handoff boundary

- `START_HERE_MANUAL.md` — single entry point for the user taking over the external submission.
- `MANUAL_SUBMISSION_CHECKLIST.md` — actual portal/upload/confirmation steps; **user-manual only**.
- `RUNTIME_VALIDATION_FOR_USER.md` — final-machine Streamlit and optional OpenAI validation commands.
- `GOAI_FIELD_MAP.md` — prepared-source-to-portal-field map.
- `FitzSight_Manual_Handoff.zip` — portable packet containing the prepared submission assets and manual instructions.

Project automation stops at local preparation, validation, hashing, packaging, and instructions. It does not submit to GOAI, access Gmail, send email, or modify external accounts by default.

## Evidence boundary

The v0.12.1 formal deck is built from fresh verified deterministic FitzSight runs plus checked-in v0.12 hero/holdout/ablation evidence. Its main narrative is one CRM/FTD hero + one false-correlation refusal; the remaining workflows are breadth proof. Current submission assets do not rely on stale benchmark constants. The offline HTML/MP4 are resilience artifacts, not evidence that Streamlit or OpenAI live runtime has been validated. Those external runtimes remain separately tracked until actual deployment output exists.

## v0.11 final-machine kit

- `FINAL_MACHINE_CHECKLIST.md` — final presentation-machine install/validation/fallback checklist.
- `REHEARSAL_OPERATOR_CARD.md` — compact pitch/demo/Q&A operator card.
- `REHEARSAL_PLAN.json` — machine-readable timing targets.
- `FitzSight_Final_Machine_Kit.zip` — portable executable presentation-machine packet with source, launchers, offline fallbacks and the manual handoff ZIP.

The default final-machine validator remains local-only except for its localhost Streamlit health probe. The OpenAI live planner is an explicit opt-in (`--include-openai`); portal/email actions remain user-manual only.
## v0.12.1 formal-deck status

`FitzSight_GOAI_Initial_Round.pptx` and `.pdf` are synchronized with the v0.12 evidence contract and have been render-reviewed. The deck includes actual runtime-derived hero trace/answer imagery. Live Streamlit/OpenAI-provider evidence remains separate and is not implied by these assets.

