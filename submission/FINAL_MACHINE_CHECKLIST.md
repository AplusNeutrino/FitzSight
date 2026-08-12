# FitzSight — Final Presentation Machine Checklist

**Owner:** User  
**Execution mode:** Local/manual only

This checklist does not authorize portal uploads, email access, or any external-account write.

## 1. Copy the kit

Use `FitzSight_Final_Machine_Kit.zip` on the machine you will actually present from. Extract it to a normal local folder with write permission.

## 2. Install the local demo environment

From the extracted `FitzSight_Final_Machine_Kit` folder:

```bash
python -m venv .venv
```

Windows:

```bat
.venv\Scripts\activate
pip install -e ".[demo]"
```

macOS/Linux:

```bash
. .venv/bin/activate
pip install -e ".[demo]"
```

If you do not want the optional OpenAI SDK/runtime, installing `.[ui]` is enough for Streamlit. The deterministic CLI/offline fallback remains usable without the model provider.

## 3. One-command readiness check

Windows:

```bat
RUN_FINAL_CHECKS.bat
```

macOS/Linux:

```bash
sh RUN_FINAL_CHECKS.sh
```

Equivalent direct command:

```bash
python scripts/final_machine_check.py --output final_machine_report.json
```

Keep the generated `final_machine_report.json` as local runtime evidence.

Required minimum before presentation:

- `local_core_ready = true`
- deterministic Agent smoke = PASS
- submission preflight = PASS
- handoff readiness = PASS

For the live UI path, also require:

- `streamlit_live.passed = true`

If Streamlit is not available or fails, use the deterministic CLI or offline HTML/video. Do not improvise a different analytical path.

## 4. Optional OpenAI live planner

This is deliberately **not** part of the default final-machine command.

Only if you intentionally configure a stable key/model:

```bash
python scripts/final_machine_check.py --include-openai --output final_machine_report_with_openai.json
```

Never put the API key in screenshots, documents, repository files, chat logs, or submission materials.

## 5. Start the demo

Windows:

```bat
START_DEMO.bat
```

macOS/Linux:

```bash
sh START_DEMO.sh
```

Fallback files:

```text
submission/FitzSight_Offline_Demo.html
submission/FitzSight_Offline_Demo_Backup.mp4
```

## 6. Human rehearsal

Record real timings yourself:

```bash
python scripts/rehearsal_assistant.py --mode pitch --interactive --output pitch_rehearsal.json
python scripts/rehearsal_assistant.py --mode demo --interactive --output demo_rehearsal.json
python scripts/rehearsal_assistant.py --mode qa --interactive --output qa_rehearsal.json
```

These reports are local evidence only. They do not submit or transmit anything.

## 7. Competition submission remains manual

The actual GOAI portal review/upload/final-submit/confirmation workflow remains entirely user-controlled. Follow `MANUAL_SUBMISSION_CHECKLIST.md` when you are ready.
