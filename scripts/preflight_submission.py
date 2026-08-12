from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = (
    "README.md",
    "LICENSE",
    "THIRD_PARTY_NOTICES.md",
    "streamlit_app.py",
    "evaluation/benchmark_catalog.json",
    "evaluation/adversarial_cases.json",
    "docs/COMPLIANCE_AND_SAFETY.md",
    "docs/INITIAL_ROUND_PROJECT_SUMMARY.md",
    "docs/V0.10_BENCHMARK_RESULTS.json",
    "docs/V0.10_ADVERSARIAL_RESULTS.json",
    "docs/V0.11_BENCHMARK_RESULTS.json",
    "docs/V0.11_ADVERSARIAL_RESULTS.json",
    "docs/V0.11_FINAL_MACHINE_READINESS.json",
    "docs/V0.9_DETERMINISTIC_LATENCY.json",
    "docs/V0.9_RUNTIME_STATUS.json",
    "docs/V0.10_HANDOFF_READINESS.json",
    "docs/FINAL_MACHINE_OPERATIONS.md",
    "docs/V0.9_VALIDATION.md",
    "docs/V0.10_VALIDATION.md",
    "docs/V0.11_VALIDATION.md",
    "RELEASE_NOTES_v0.10.md",
    "RELEASE_NOTES_v0.11.md",
    "submission/FitzSight_GOAI_Initial_Round.pptx",
    "submission/FitzSight_GOAI_Initial_Round.pdf",
    "submission/FitzSight_Offline_Demo.html",
    "submission/FitzSight_Offline_Demo.json",
    "submission/FitzSight_Offline_Demo_Backup.mp4",
    "submission/FitzSight_GOAI_Upload_Bundle.zip",
    "submission/PORTAL_COPY.md",
    "submission/DEMO_RUNBOOK.md",
    "submission/DEMO_VIDEO_SCRIPT.md",
    "submission/PITCH_REHEARSAL.md",
    "submission/SUBMISSION_CHECKLIST.md",
    "submission/JUDGE_QA.md",
    "submission/README.md",
    "submission/START_HERE_MANUAL.md",
    "submission/MANUAL_SUBMISSION_CHECKLIST.md",
    "submission/RUNTIME_VALIDATION_FOR_USER.md",
    "submission/GOAI_FIELD_MAP.md",
    "submission/FitzSight_Manual_Handoff.zip",
    "docs/OPERATOR_BOUNDARY.md",
    "scripts/build_manual_handoff.py",
    "scripts/handoff_readiness.py",
    "scripts/final_machine_check.py",
    "scripts/rehearsal_assistant.py",
    "scripts/build_final_machine_kit.py",
    "submission/FINAL_MACHINE_CHECKLIST.md",
    "submission/REHEARSAL_OPERATOR_CARD.md",
    "submission/REHEARSAL_PLAN.json",
    "submission/FitzSight_Final_Machine_Kit.zip",
    "scripts/runtime_doctor.py",
    "scripts/validate_streamlit_runtime.py",
    "scripts/validate_openai_runtime.py",
)

SECRET_PATTERNS = (
    re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b"),
    re.compile(r"OPENAI_API_KEY[ \t]*=[ \t]*[^\s#]+"),
)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def scan_secrets() -> list[str]:
    hits: list[str] = []
    text_suffixes = {".py", ".md", ".toml", ".json", ".txt", ".example", ".yaml", ".yml"}
    for path in ROOT.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in text_suffixes:
            continue
        if any(part in {".git", "__pycache__", ".pytest_cache"} for part in path.parts):
            continue
        if "SUBMISSION_PREFLIGHT" in path.name.upper():
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        for pattern in SECRET_PATTERNS:
            for match in pattern.finditer(text):
                token = match.group(0)
                if token.startswith("OPENAI_API_KEY"):
                    value = token.split("=", 1)[1].strip().strip('"\'') if "=" in token else ""
                    if value in {"", "...", "<model>", "<key>", "<api-key>"}:
                        continue
                # Documentation/tests may intentionally include obvious test-only fake keys.
                if "test-secret" in token or "must-not-appear" in token:
                    continue
                hits.append(f"{path.relative_to(ROOT)}: {token[:40]}")
    return hits


def _zip_ok(path: Path) -> bool:
    if not path.exists():
        return False
    try:
        with zipfile.ZipFile(path) as archive:
            return archive.testzip() is None
    except zipfile.BadZipFile:
        return False


def run_preflight(*, require_final_machine_kit: bool = True) -> dict[str, object]:
    required_files = tuple(
        rel for rel in REQUIRED_FILES
        if require_final_machine_kit or rel != "submission/FitzSight_Final_Machine_Kit.zip"
    )
    missing = [rel for rel in required_files if not (ROOT / rel).exists()]
    generated_csv = sorted(
        str(path.relative_to(ROOT))
        for path in (ROOT / "data" / "generated").glob("*.csv")
    )
    secrets = scan_secrets()

    asset_paths_list = [
        ROOT / "submission" / "FitzSight_GOAI_Initial_Round.pptx",
        ROOT / "submission" / "FitzSight_GOAI_Initial_Round.pdf",
        ROOT / "submission" / "FitzSight_Offline_Demo.html",
        ROOT / "submission" / "FitzSight_Offline_Demo_Backup.mp4",
        ROOT / "submission" / "FitzSight_GOAI_Upload_Bundle.zip",
        ROOT / "submission" / "FitzSight_Manual_Handoff.zip",
    ]
    if require_final_machine_kit:
        asset_paths_list.append(ROOT / "submission" / "FitzSight_Final_Machine_Kit.zip")
    asset_paths = tuple(asset_paths_list)
    assets = {}
    for path in asset_paths:
        if path.exists():
            assets[path.name] = {
                "bytes": path.stat().st_size,
                "sha256": sha256(path),
            }

    offline_demo_ok = False
    offline_json = ROOT / "submission" / "FitzSight_Offline_Demo.json"
    if offline_json.exists():
        try:
            payload = json.loads(offline_json.read_text(encoding="utf-8"))
            offline_demo_ok = payload.get("scenario_count") == 5 and payload.get("verified_runs") == 5
        except (json.JSONDecodeError, OSError):
            offline_demo_ok = False

    upload_zip = ROOT / "submission" / "FitzSight_GOAI_Upload_Bundle.zip"
    upload_zip_ok = _zip_ok(upload_zip)
    manual_handoff_zip = ROOT / "submission" / "FitzSight_Manual_Handoff.zip"
    manual_handoff_zip_ok = _zip_ok(manual_handoff_zip)
    final_machine_kit = ROOT / "submission" / "FitzSight_Final_Machine_Kit.zip"
    final_machine_kit_ok = _zip_ok(final_machine_kit) if require_final_machine_kit else None
    passed = (
        not missing
        and not generated_csv
        and not secrets
        and len(assets) == len(asset_paths)
        and offline_demo_ok
        and upload_zip_ok
        and manual_handoff_zip_ok
        and (final_machine_kit_ok is not False)
    )
    return {
        "passed": passed,
        "missing_required_files": missing,
        "generated_csv_files": generated_csv,
        "secret_hits": secrets,
        "submission_assets": assets,
        "offline_demo_verified_5_of_5": offline_demo_ok,
        "upload_bundle_zip_integrity": upload_zip_ok,
        "manual_handoff_zip_integrity": manual_handoff_zip_ok,
        "final_machine_kit_integrity": final_machine_kit_ok,
        "manual_submission_boundary": {
            "mode": "user_manual_only",
            "external_write_actions_performed": False,
            "portal_upload_or_submit_by_automation": False,
            "gmail_or_email_access_by_automation": False,
        },
        "external_actions_still_required": [
            "USER MANUAL: confirm portal-specific field/file-size constraints in the actual GOAI upload UI",
            "USER MANUAL: upload the required project introduction and PPT/PDF",
            "USER MANUAL: capture portal/email confirmation evidence",
            "USER MANUAL: run scripts/final_machine_check.py on the final presentation machine",
            "Run Streamlit live validation on a machine with the UI dependency installed",
            "Run OpenAI live planner validation only if stable credentials/model access are available",
        ],
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="FitzSight initial-round submission preflight.")
    parser.add_argument("--output", default=None)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = run_preflight()
    rendered = json.dumps(report, indent=2, ensure_ascii=False)
    print(rendered)
    if args.output:
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(rendered + "\n", encoding="utf-8")
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
