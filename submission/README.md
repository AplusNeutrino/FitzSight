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

## Evidence boundary

Slides 4-8 are built from fresh verified deterministic FitzSight runs by `scripts/build_pitch_deck.py`; current submission assets do not rely on stale benchmark constants. The offline HTML/MP4 are resilience artifacts, not evidence that Streamlit or OpenAI live runtime has been validated. Those external runtimes remain separately tracked until actual deployment output exists.
