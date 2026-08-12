from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]

HANDOFF_FILES = (
    "submission/START_HERE_MANUAL.md",
    "submission/MANUAL_SUBMISSION_CHECKLIST.md",
    "submission/RUNTIME_VALIDATION_FOR_USER.md",
    "submission/GOAI_FIELD_MAP.md",
    "submission/FINAL_MACHINE_CHECKLIST.md",
    "submission/REHEARSAL_OPERATOR_CARD.md",
    "submission/REHEARSAL_PLAN.json",
    "submission/PORTAL_COPY.md",
    "submission/FitzSight_GOAI_Initial_Round.pptx",
    "submission/FitzSight_GOAI_Initial_Round.pdf",
    "submission/FitzSight_Offline_Demo.html",
    "submission/FitzSight_Offline_Demo.json",
    "submission/FitzSight_Offline_Demo_Backup.mp4",
    "submission/DEMO_RUNBOOK.md",
    "submission/PITCH_REHEARSAL.md",
    "submission/PITCH_SPEAKER_NOTES.md",
    "submission/JUDGE_QA.md",
    "docs/INITIAL_ROUND_PROJECT_SUMMARY.md",
    "docs/EVALUATION_SUMMARY.md",
    "docs/COMPLIANCE_AND_SAFETY.md",
    "docs/OPERATOR_BOUNDARY.md",
)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build FitzSight's local manual handoff packet. No network or external submission is performed."
    )
    parser.add_argument(
        "--output",
        default=str(ROOT / "submission" / "FitzSight_Manual_Handoff.zip"),
    )
    return parser.parse_args()


def build_packet(output: Path) -> dict[str, object]:
    missing = [rel for rel in HANDOFF_FILES if not (ROOT / rel).exists()]
    if missing:
        raise FileNotFoundError(f"Missing handoff assets: {', '.join(missing)}")

    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="fitzsight_manual_handoff_") as tmp:
        stage = Path(tmp)
        copied: list[dict[str, object]] = []
        for rel in HANDOFF_FILES:
            source = ROOT / rel
            destination = stage / source.name
            if destination.exists():
                destination = stage / rel.replace("/", "__")
            shutil.copy2(source, destination)
            copied.append(
                {
                    "name": destination.name,
                    "source": rel,
                    "bytes": destination.stat().st_size,
                    "sha256": sha256(destination),
                }
            )

        repo_link = stage / "REPOSITORY_LINK.txt"
        repo_link.write_text(
            "FitzSight public repository:\nhttps://github.com/AplusNeutrino/FitzSight\n",
            encoding="utf-8",
        )
        copied.append(
            {
                "name": repo_link.name,
                "source": "generated",
                "bytes": repo_link.stat().st_size,
                "sha256": sha256(repo_link),
            }
        )

        manual_actions = {
            "product": "FitzSight",
            "version": "0.11.0",
            "execution_policy": "external_submission_user_manual_only",
            "automation_boundary": {
                "local_prepare_validate_package": True,
                "portal_upload": False,
                "portal_submit": False,
                "gmail_access": False,
                "email_send_or_modify": False,
                "external_account_write": False,
            },
            "user_manual_actions": [
                "Open the official GOAI submission portal and verify current fields/limits",
                "Paste the prepared project copy",
                "Upload the requested PPT/PDF and optional demo/video",
                "Enter the public repository link",
                "Review the portal state and click the final submission button",
                "Save the confirmation screenshot/email/receipt",
            ],
            "environment_dependent_checks": [
                "Run Streamlit live validation on the final presentation machine",
                "Optionally run OpenAI live planner validation with deliberately configured stable credentials/model",
                "Run the final-machine readiness check on the presentation machine",
                "Perform timed pitch/demo and Q&A rehearsal",
            ],
        }
        manual_path = stage / "MANUAL_ACTIONS.json"
        manual_path.write_text(json.dumps(manual_actions, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        copied.append(
            {
                "name": manual_path.name,
                "source": "generated",
                "bytes": manual_path.stat().st_size,
                "sha256": sha256(manual_path),
            }
        )

        manifest = {
            "product": "FitzSight",
            "version": "0.11.0",
            "purpose": "user_manual_submission_handoff",
            "network_actions_performed": False,
            "external_submission_performed": False,
            "note": (
                "This packet contains prepared local artifacts only. The user performs all portal/email submission actions manually."
            ),
            "files": copied,
        }
        manifest_path = stage / "HANDOFF_MANIFEST.json"
        manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

        if output.exists():
            output.unlink()
        with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
            for path in sorted(p for p in stage.iterdir() if p.is_file()):
                archive.write(path, path.name)

    with zipfile.ZipFile(output, "r") as archive:
        bad = archive.testzip()
        if bad is not None:
            raise RuntimeError(f"Corrupt file in manual handoff ZIP: {bad}")
        names = set(archive.namelist())
        required = {
            "START_HERE_MANUAL.md",
            "MANUAL_SUBMISSION_CHECKLIST.md",
            "RUNTIME_VALIDATION_FOR_USER.md",
            "PORTAL_COPY.md",
            "FitzSight_GOAI_Initial_Round.pdf",
            "FitzSight_GOAI_Initial_Round.pptx",
            "FitzSight_Offline_Demo_Backup.mp4",
            "REPOSITORY_LINK.txt",
            "MANUAL_ACTIONS.json",
            "HANDOFF_MANIFEST.json",
        }
        missing_names = required - names
        if missing_names:
            raise RuntimeError(f"Manual handoff ZIP missing: {', '.join(sorted(missing_names))}")

    return {
        "product": "FitzSight",
        "version": "0.11.0",
        "output": str(output),
        "bytes": output.stat().st_size,
        "sha256": sha256(output),
        "integrity": "PASS",
        "external_submission_performed": False,
        "network_actions_performed": False,
    }


def main() -> int:
    args = parse_args()
    report = build_packet(Path(args.output))
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
