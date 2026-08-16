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
    "submission/FitzSight_GOAI_初赛方案_CN.pdf",
    "submission/PORTAL_COPY.md",
    "submission/START_HERE_MANUAL.md",
    "submission/MANUAL_SUBMISSION_CHECKLIST.md",
    "submission/RUNTIME_VALIDATION_FOR_USER.md",
    "submission/FINAL_MACHINE_CHECKLIST.md",
    "submission/FitzSight_Offline_Demo.html",
    "submission/FitzSight_Offline_Demo.json",
    "submission/FitzSight_Offline_Demo_Backup.mp4",
    "docs/ARCHITECTURE.md",
    "docs/MODEL_PROVIDER.md",
    "docs/COMPLIANCE_AND_SAFETY.md",
    "docs/V0.13_VALIDATION.md",
    "docs/PROJFITZGERALD_PROGRESS_SNAPSHOT.md",
    "RELEASE_NOTES_v0.13.md",
    "THIRD_PARTY_NOTICES.md",
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


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
            copied.append({"name": destination.name, "source": rel, "bytes": destination.stat().st_size, "sha256": sha256(destination)})

        actions = {
            "product": "FitzSight",
            "version": "0.13.0",
            "execution_policy": "external_submission_user_manual_only",
            "competition_upload_allowlist": ["FitzSight_GOAI_初赛方案_CN.pdf"],
            "automation_boundary": {
                "local_prepare_validate_package": True,
                "portal_upload": False,
                "portal_submit": False,
                "email_access": False,
                "external_account_write": False,
            },
            "provider_validation": {
                "deepseek_live": "not_requested",
                "verified": ["offline deterministic runtime", "mock provider contract"],
            },
        }
        (stage / "MANUAL_ACTIONS.json").write_text(json.dumps(actions, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        manifest = {
            "product": "FitzSight",
            "version": "0.13.0",
            "purpose": "user_manual_submission_handoff",
            "network_actions_performed": False,
            "external_submission_performed": False,
            "files": copied,
        }
        (stage / "HANDOFF_MANIFEST.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        if output.exists():
            output.unlink()
        with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
            for path in sorted(p for p in stage.iterdir() if p.is_file()):
                archive.write(path, path.name)

    with zipfile.ZipFile(output) as archive:
        required = {"FitzSight_GOAI_初赛方案_CN.pdf", "PORTAL_COPY.md", "MANUAL_ACTIONS.json", "HANDOFF_MANIFEST.json"}
        missing_names = required - set(archive.namelist())
        if archive.testzip() is not None or missing_names:
            raise RuntimeError(f"Invalid manual handoff ZIP; missing={sorted(missing_names)}")
    return {
        "product": "FitzSight",
        "version": "0.13.0",
        "output": str(output),
        "bytes": output.stat().st_size,
        "sha256": sha256(output),
        "integrity": "PASS",
        "external_submission_performed": False,
        "network_actions_performed": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the local FitzSight manual handoff packet.")
    parser.add_argument("--output", default=str(ROOT / "submission" / "FitzSight_Manual_Handoff.zip"))
    args = parser.parse_args()
    print(json.dumps(build_packet(Path(args.output)), indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
