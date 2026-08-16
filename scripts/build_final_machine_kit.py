from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]
SELF_ARCHIVE_NAME = "FitzSight_Final_Machine_Kit.zip"

# Deliberately explicit: no virtualenv, cache, work directory, old deck or temp output can enter the kit.
ALLOWLIST = (
    ".env.example",
    "LICENSE",
    "README.md",
    "THIRD_PARTY_NOTICES.md",
    "pyproject.toml",
    "requirements.lock",
    "streamlit_app.py",
    "src",
    "evaluation",
    "synthetic_documents",
    "scripts/agent_investigate.py",
    "scripts/final_machine_check.py",
    "scripts/generate_data.py",
    "scripts/preflight_submission.py",
    "scripts/runtime_doctor.py",
    "scripts/start_demo.py",
    "scripts/validate_deepseek_runtime.py",
    "scripts/validate_streamlit_runtime.py",
    "docs/ARCHITECTURE.md",
    "docs/MODEL_PROVIDER.md",
    "docs/COMPLIANCE_AND_SAFETY.md",
    "docs/PROJFITZGERALD_PROGRESS_SNAPSHOT.md",
    "docs/V0.13_VALIDATION.md",
    "submission/FitzSight_GOAI_初赛方案_CN.pdf",
    "submission/FitzSight_Offline_Demo.html",
    "submission/FitzSight_Offline_Demo.json",
    "submission/FitzSight_Offline_Demo_Backup.mp4",
    "submission/FINAL_MACHINE_CHECKLIST.md",
    "submission/RUNTIME_VALIDATION_FOR_USER.md",
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _copy_allowlist(stage: Path) -> None:
    missing: list[str] = []
    for rel in ALLOWLIST:
        source = ROOT / rel
        target = stage / rel
        if not source.exists():
            missing.append(rel)
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        if source.is_dir():
            shutil.copytree(source, target, ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".pytest_cache"))
        else:
            shutil.copy2(source, target)
    if missing:
        raise FileNotFoundError(f"Missing allowlisted final-machine assets: {', '.join(missing)}")


def _write_launchers(stage: Path) -> None:
    (stage / "RUN_FINAL_CHECKS.bat").write_text("@echo off\r\npython scripts\\final_machine_check.py --output final_machine_report.json\r\npause\r\n", encoding="utf-8")
    (stage / "START_DEMO.bat").write_text("@echo off\r\npython scripts\\start_demo.py\r\n", encoding="utf-8")
    (stage / "RUN_FINAL_CHECKS.sh").write_text("#!/usr/bin/env sh\nset -eu\npython scripts/final_machine_check.py --output final_machine_report.json\n", encoding="utf-8")
    (stage / "START_DEMO.sh").write_text("#!/usr/bin/env sh\nset -eu\npython scripts/start_demo.py\n", encoding="utf-8")


def build_kit(output: Path) -> dict[str, object]:
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="fitzsight_final_machine_") as tmp:
        stage_parent = Path(tmp)
        stage = stage_parent / "FitzSight_Final_Machine_Kit"
        stage.mkdir()
        _copy_allowlist(stage)
        _write_launchers(stage)
        files = [
            {"path": path.relative_to(stage).as_posix(), "bytes": path.stat().st_size, "sha256": sha256(path)}
            for path in sorted(p for p in stage.rglob("*") if p.is_file())
        ]
        manifest = {
            "product": "FitzSight",
            "version": "0.13.0",
            "purpose": "portable_final_presentation_machine_kit",
            "source_scope": "explicit_allowlist",
            "excluded_classes": [".venv", "cache", "data/generated", "work", "old decks", "temporary output"],
            "external_submission_performed": False,
            "email_access_performed": False,
            "network_actions_performed_during_build": False,
            "deepseek_live_validation_is_explicit_opt_in": True,
            "files": files,
        }
        (stage / "FINAL_MACHINE_KIT_MANIFEST.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        if output.exists():
            output.unlink()
        with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
            for path in sorted(p for p in stage.rglob("*") if p.is_file()):
                archive.write(path, path.relative_to(stage_parent).as_posix())
    with zipfile.ZipFile(output) as archive:
        if archive.testzip() is not None:
            raise RuntimeError("Final-machine kit failed ZIP integrity check.")
        names = set(archive.namelist())
        prefix = "FitzSight_Final_Machine_Kit/"
        required = {
            prefix + "RUN_FINAL_CHECKS.bat",
            prefix + "START_DEMO.sh",
            prefix + "FINAL_MACHINE_KIT_MANIFEST.json",
            prefix + "submission/FitzSight_GOAI_初赛方案_CN.pdf",
            prefix + "docs/PROJFITZGERALD_PROGRESS_SNAPSHOT.md",
        }
        if required - names:
            raise RuntimeError(f"Final-machine kit missing: {sorted(required - names)}")
        forbidden = ("/.git/", "/.venv/", "/__pycache__/", "/data/generated/", ".pptx")
        if any(any(marker in name for marker in forbidden) for name in names):
            raise RuntimeError("Final-machine kit contains a forbidden path.")
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
    parser = argparse.ArgumentParser(description="Build an allowlisted local FitzSight final-machine kit.")
    parser.add_argument("--output", default=str(ROOT / "submission" / SELF_ARCHIVE_NAME))
    args = parser.parse_args()
    print(json.dumps(build_kit(Path(args.output)), indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
