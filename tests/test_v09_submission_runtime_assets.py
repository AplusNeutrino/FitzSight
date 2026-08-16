from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def test_offline_demo_contains_five_verified_workflows():
    payload = json.loads((ROOT / "submission" / "FitzSight_Offline_Demo.json").read_text(encoding="utf-8"))
    assert payload["scenario_count"] == 5
    assert payload["verified_runs"] == 5
    assert payload["evidence_records"] > 0
    html = (ROOT / "submission" / "FitzSight_Offline_Demo.html").read_text(encoding="utf-8")
    assert html.count("class='workflow'") == 5
    assert "Evidence preview" in html
    assert "No cloud model required" in html


def test_offline_backup_video_is_packaged_mp4():
    path = ROOT / "submission" / "FitzSight_Offline_Demo_Backup.mp4"
    raw = path.read_bytes()
    assert len(raw) > 100_000
    assert b"ftyp" in raw[:64]


def test_runtime_doctor_never_discloses_api_key(tmp_path: Path):
    env = dict(**__import__("os").environ)
    env["DEEPSEEK_API_KEY"] = "sk-test-secret-value-that-must-not-appear"
    completed = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "runtime_doctor.py"), "--data-dir", str(tmp_path)],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=True,
    )
    assert "sk-test-secret" not in completed.stdout
    report = json.loads(completed.stdout)
    assert report["checks"]["deepseek_api_key"]["detail"] == "configured"
    assert report["secrets_disclosed"] is False


def test_runtime_validation_scripts_have_safe_dry_runs():
    for script in ("validate_streamlit_runtime.py", "validate_deepseek_runtime.py"):
        completed = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / script), "--dry-run"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=True,
        )
        report = json.loads(completed.stdout)
        assert report["status"] == "dry_run"
        assert report["passed"] is False


def test_upload_bundle_is_integrity_checked(tmp_path: Path):
    output = tmp_path / "upload.zip"
    completed = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "build_submission_bundle.py"), "--output", str(output)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    report = json.loads(completed.stdout)
    assert report["integrity"] == "PASS"
    with zipfile.ZipFile(output) as archive:
        assert archive.testzip() is None
        names = set(archive.namelist())
        assert names == {"FitzSight_GOAI_初赛方案_CN.pdf"}
