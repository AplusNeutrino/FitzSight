from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def _load_script(name: str):
    path = ROOT / "scripts" / name
    spec = importlib.util.spec_from_file_location(name.replace(".py", ""), path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_rehearsal_evaluation_boundaries() -> None:
    module = _load_script("rehearsal_assistant.py")
    assert module.evaluate("pitch", 390)["timing_passed"] is True
    assert module.evaluate("pitch", 490)["timing_passed"] is False
    assert module.evaluate("demo", 140)["timing_passed"] is True
    assert module.evaluate("demo", 181)["timing_passed"] is False
    assert module.evaluate("qa", 600)["timing_passed"] is True


def test_rehearsal_dry_run_has_no_external_action() -> None:
    completed = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "rehearsal_assistant.py"), "--mode", "demo", "--dry-run"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    payload = json.loads(completed.stdout)
    assert payload["status"] == "dry_run"
    assert payload["external_write_actions_performed"] is False


def test_final_machine_check_default_does_not_request_deepseek() -> None:
    module = _load_script("final_machine_check.py")
    report = module.build_report(attempt_streamlit=False, include_deepseek=False)
    assert report["local_core_ready"] is True
    assert report["deepseek_live"]["status"] == "not_requested"
    assert report["external_write_actions_performed"] is False
    assert report["portal_or_email_actions_performed"] is False


def test_final_machine_kit_builds_with_local_only_manifest(tmp_path: Path) -> None:
    module = _load_script("build_final_machine_kit.py")
    output = tmp_path / "kit.zip"
    report = module.build_kit(output)
    assert report["integrity"] == "PASS"
    assert report["external_submission_performed"] is False
    assert report["network_actions_performed"] is False
    with zipfile.ZipFile(output) as archive:
        assert archive.testzip() is None
        manifest = json.loads(archive.read("FitzSight_Final_Machine_Kit/FINAL_MACHINE_KIT_MANIFEST.json"))
        assert manifest["external_submission_performed"] is False
        assert manifest["email_access_performed"] is False
        assert manifest["deepseek_live_validation_is_explicit_opt_in"] is True
        names = set(archive.namelist())
        assert "FitzSight_Final_Machine_Kit/RUN_FINAL_CHECKS.bat" in names
        assert "FitzSight_Final_Machine_Kit/START_DEMO.sh" in names


def test_final_machine_docs_keep_submission_manual() -> None:
    text = (ROOT / "submission" / "FINAL_MACHINE_CHECKLIST.md").read_text(encoding="utf-8").lower()
    assert "goai" in text
    assert "人工" in text or "user-controlled" in text
    assert "--include-deepseek" in text
