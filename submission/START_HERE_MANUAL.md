# FitzSight — Start Here for Manual Submission

This folder is prepared so the **remaining external submission actions are manual and user-controlled**.

No FitzSight script submits to GOAI, accesses Gmail, sends email, uploads to a portal, or changes an external account.

## What is already prepared

Use these files directly:

| Need | File |
|---|---|
| Project copy to paste | `PORTAL_COPY.md` |
| Editable pitch deck | `FitzSight_GOAI_Initial_Round.pptx` |
| Upload-safe presentation | `FitzSight_GOAI_Initial_Round.pdf` |
| Optional offline demo | `FitzSight_Offline_Demo.html` |
| Optional backup video | `FitzSight_Offline_Demo_Backup.mp4` |
| Demo sequence | `DEMO_RUNBOOK.md` |
| Pitch timing | `PITCH_REHEARSAL.md` |
| Judge questions | `JUDGE_QA.md` |
| Manual submission steps | `MANUAL_SUBMISSION_CHECKLIST.md` |
| Runtime checks to run on your machine | `RUNTIME_VALIDATION_FOR_USER.md` |

For a single portable packet, use `FitzSight_Manual_Handoff.zip`.


## Final presentation machine

For a portable executable presentation environment, use:

```text
FitzSight_Final_Machine_Kit.zip
```

Extract it on the final machine and run `RUN_FINAL_CHECKS.bat` (Windows) or `sh RUN_FINAL_CHECKS.sh` (macOS/Linux). The default check does not call a live model provider and performs no portal/email actions.

## Minimal manual path

1. Open `MANUAL_SUBMISSION_CHECKLIST.md`.
2. Open the official GOAI submission portal yourself.
3. Copy the relevant text from `PORTAL_COPY.md`.
4. Upload the PPT/PDF and optional demo/video requested by the portal.
5. Enter the public repository link: `https://github.com/AplusNeutrino/FitzSight`.
6. Review all fields yourself and submit.
7. Save the confirmation screenshot/email/receipt yourself.

## Runtime checks before a live demo

Run on the final presentation machine:

```bash
python scripts/runtime_doctor.py
python scripts/validate_streamlit_runtime.py
```

Optional model-provider path, only if you deliberately configure a stable API key/model:

```bash
python scripts/validate_openai_runtime.py
```

If Streamlit or the model provider is unavailable, use the deterministic local/offline fallback. The analytical benchmark does not depend on a cloud model.

## v0.12.1 prepared-asset status

The formal PPTX/PDF have been regenerated to the one-hero + one-refusal narrative and render-reviewed. The handoff packet includes the synchronized speaker/demo/operator sources. This prepared status does not imply Streamlit/OpenAI live runtime or GOAI portal submission success.
