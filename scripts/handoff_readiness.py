from __future__ import annotations

import argparse
import json
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def _zip_ok(path: Path) -> bool:
    try:
        with zipfile.ZipFile(path) as archive:
            return archive.testzip() is None
    except (FileNotFoundError, zipfile.BadZipFile):
        return False


def readiness_report(*, require_final_machine_kit: bool = True) -> dict[str, object]:
    required = {
        "portal_copy": ROOT / "submission" / "PORTAL_COPY.md",
        "final_chinese_pdf": ROOT / "submission" / "FitzSight_GOAI_初赛方案_CN.pdf",
        "deck_html_source": ROOT / "submission" / "deck-cn" / "index.html",
        "offline_html": ROOT / "submission" / "FitzSight_Offline_Demo.html",
        "offline_video": ROOT / "submission" / "FitzSight_Offline_Demo_Backup.mp4",
        "manual_checklist": ROOT / "submission" / "MANUAL_SUBMISSION_CHECKLIST.md",
        "manual_handoff_zip": ROOT / "submission" / "FitzSight_Manual_Handoff.zip",
        "final_machine_kit": ROOT / "submission" / "FitzSight_Final_Machine_Kit.zip",
    }
    presence = {name: path.exists() for name, path in required.items()}
    if not require_final_machine_kit:
        presence["final_machine_kit"] = True
    ready = all(presence.values()) and _zip_ok(required["manual_handoff_zip"])
    if require_final_machine_kit:
        ready = ready and _zip_ok(required["final_machine_kit"])
    return {
        "product": "FitzSight",
        "version": "0.13.0",
        "automated_artifact_preparation_ready": ready,
        "artifacts": presence,
        "manual_handoff_zip_integrity": _zip_ok(required["manual_handoff_zip"]),
        "final_machine_kit_integrity": _zip_ok(required["final_machine_kit"]) if require_final_machine_kit else None,
        "competition_upload_allowlist": ["FitzSight_GOAI_初赛方案_CN.pdf"],
        "deepseek_live": "not_requested",
        "external_write_actions_performed": False,
        "manual_user_actions_remaining": [
            "Upload the final Chinese PDF in the GOAI portal",
            "Review and confirm the final portal submission",
            "Capture the portal confirmation evidence",
            "Run the local final-machine check and timed rehearsal",
        ],
        "ready_for_user_takeover": ready,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Report FitzSight handoff readiness without external actions.")
    parser.add_argument("--output", default=None)
    args = parser.parse_args()
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
