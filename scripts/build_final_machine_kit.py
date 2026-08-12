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


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _ignore(directory: str, names: list[str]) -> set[str]:
    ignored: set[str] = set()
    directory_path = Path(directory)
    for name in names:
        if name in {"__pycache__", ".pytest_cache", ".git"} or name.endswith(".pyc"):
            ignored.add(name)
        if name in {SELF_ARCHIVE_NAME, "SHA256SUMS.txt", "REPOSITORY_MANIFEST.md",
                    "V0.12.1_SUBMISSION_PREFLIGHT.json", "V0.12.1_HANDOFF_READINESS.json",
                    "V0.12.1_FINAL_MACHINE_READINESS.json"}:
            ignored.add(name)
    if directory_path.name == "generated":
        for name in names:
            if name != ".gitkeep":
                ignored.add(name)
    return ignored


def _write_launchers(stage: Path) -> None:
    (stage / "RUN_FINAL_CHECKS.bat").write_text(
        "@echo off\r\npython scripts\\final_machine_check.py --output final_machine_report.json\r\npause\r\n",
        encoding="utf-8",
    )
    (stage / "START_DEMO.bat").write_text(
        "@echo off\r\npython scripts\\start_demo.py\r\n",
        encoding="utf-8",
    )
    (stage / "RUN_FINAL_CHECKS.sh").write_text(
        "#!/usr/bin/env sh\nset -eu\npython scripts/final_machine_check.py --output final_machine_report.json\n",
        encoding="utf-8",
    )
    (stage / "START_DEMO.sh").write_text(
        "#!/usr/bin/env sh\nset -eu\npython scripts/start_demo.py\n",
        encoding="utf-8",
    )


def build_kit(output: Path) -> dict[str, object]:
    essentials = (
        ROOT / "pyproject.toml",
        ROOT / "streamlit_app.py",
        ROOT / "src" / "fitzsight" / "__init__.py",
        ROOT / "scripts" / "final_machine_check.py",
        ROOT / "submission" / "FitzSight_Manual_Handoff.zip",
        ROOT / "submission" / "FitzSight_Offline_Demo_Backup.mp4",
    )
    missing = [str(path.relative_to(ROOT)) for path in essentials if not path.exists()]
    if missing:
        raise FileNotFoundError(f"Missing final-machine essentials: {', '.join(missing)}")

    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="fitzsight_final_machine_") as tmp:
        stage_parent = Path(tmp)
        stage = stage_parent / "FitzSight_Final_Machine_Kit"
        shutil.copytree(ROOT, stage, ignore=_ignore)
        _write_launchers(stage)

        files_meta = []
        for path in sorted(p for p in stage.rglob("*") if p.is_file()):
            files_meta.append(
                {
                    "path": path.relative_to(stage).as_posix(),
                    "bytes": path.stat().st_size,
                    "sha256": sha256(path),
                }
            )
        manifest = {
            "product": "FitzSight",
            "version": "0.12.1",
            "purpose": "portable_final_presentation_machine_kit",
            "source_scope": "full_local_repository_snapshot_excluding_caches_generated_csv_and_self_archive",
            "external_submission_performed": False,
            "gmail_or_email_access_performed": False,
            "network_actions_performed_during_build": False,
            "openai_live_validation_is_explicit_opt_in": True,
            "files": files_meta,
        }
        (stage / "FINAL_MACHINE_KIT_MANIFEST.json").write_text(
            json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )

        if output.exists():
            output.unlink()
        with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
            for path in sorted(p for p in stage.rglob("*") if p.is_file()):
                archive.write(path, path.relative_to(stage_parent).as_posix())

    with zipfile.ZipFile(output) as archive:
        bad = archive.testzip()
        if bad is not None:
            raise RuntimeError(f"Corrupt final-machine kit entry: {bad}")
        names = set(archive.namelist())
        prefix = "FitzSight_Final_Machine_Kit/"
        required = {
            prefix + "RUN_FINAL_CHECKS.bat",
            prefix + "RUN_FINAL_CHECKS.sh",
            prefix + "START_DEMO.bat",
            prefix + "START_DEMO.sh",
            prefix + "FINAL_MACHINE_KIT_MANIFEST.json",
            prefix + "submission/FitzSight_Offline_Demo_Backup.mp4",
            prefix + "submission/FitzSight_Manual_Handoff.zip",
            prefix + "submission/FitzSight_GOAI_Upload_Bundle.zip",
            prefix + "scripts/final_machine_check.py",
            prefix + "scripts/preflight_submission.py",
            prefix + "src/fitzsight/__init__.py",
        }
        missing_names = required - names
        if missing_names:
            raise RuntimeError(f"Final-machine kit missing: {', '.join(sorted(missing_names))}")
        if any(name.endswith("/submission/FitzSight_Final_Machine_Kit.zip") for name in names):
            raise RuntimeError("Final-machine kit recursively contains itself")

    return {
        "product": "FitzSight",
        "version": "0.12.1",
        "output": str(output),
        "bytes": output.stat().st_size,
        "sha256": sha256(output),
        "integrity": "PASS",
        "external_submission_performed": False,
        "network_actions_performed": False,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build a portable FitzSight final-machine kit. No external account actions are performed.")
    parser.add_argument(
        "--output",
        default=str(ROOT / "submission" / SELF_ARCHIVE_NAME),
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = build_kit(Path(args.output))
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
