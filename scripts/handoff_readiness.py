from __future__ import annotations

import argparse
import json
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Report FitzSight handoff readiness without performing external actions."
    )
    parser.add_argument("--output", default=None)
    return parser.parse_args()


def _zip_ok(path: Path) -> bool:
    try:
        with zipfile.ZipFile(path) as archive:
            return archive.testzip() is None
    except (FileNotFoundError, zipfile.BadZipFile):
        return False


def readiness_report() -> dict[str, object]:
    required = {
        "portal_copy": ROOT / "submission" / "PORTAL_COPY.md",
        "pitch_pptx": ROOT / "submission" / "FitzSight_GOAI_Initial_Round.pptx",
        "pitch_pdf": ROOT / "submission" / "FitzSight_GOAI_Initial_Round.pdf",
        "offline_html": ROOT / "submission" / "FitzSight_Offline_Demo.html",
        "offline_video": ROOT / "submission" / "FitzSight_Offline_Demo_Backup.mp4",
        "manual_checklist": ROOT / "submission" / "MANUAL_SUBMISSION_CHECKLIST.md",
        "operator_boundary": ROOT / "docs" / "OPERATOR_BOUNDARY.md",
        "manual_handoff_zip": ROOT / "submission" / "FitzSight_Manual_Handoff.zip",
    }
    presence = {name: path.exists() for name, path in required.items()}
    automated_ready = all(presence.values()) and _zip_ok(required["manual_handoff_zip"])

    return {
        "product": "FitzSight",
        "version": "0.10.0",
        "automated_artifact_preparation_ready": automated_ready,
        "artifacts": presence,
        "manual_handoff_zip_integrity": _zip_ok(required["manual_handoff_zip"]),
        "external_write_actions_performed": False,
        "manual_user_actions_remaining": [
            "Actual GOAI portal review/upload/final submit",
            "Confirmation screenshot/email/receipt capture",
            "Final-machine Streamlit live validation",
            "Optional OpenAI live planner validation",
            "Timed pitch/demo and Q&A rehearsal",
        ],
        "ready_for_user_takeover": automated_ready,
    }


def main() -> int:
    args = parse_args()
    report = readiness_report()
    rendered = json.dumps(report, indent=2, ensure_ascii=False)
    print(rendered)
    if args.output:
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(rendered + "\n", encoding="utf-8")
    return 0 if report["ready_for_user_takeover"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
