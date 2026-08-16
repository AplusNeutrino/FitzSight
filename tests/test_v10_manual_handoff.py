from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def _load_script(name: str):
    path = ROOT / "scripts" / name
    spec = importlib.util.spec_from_file_location(name.replace(".py", ""), path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_operator_boundary_is_explicit() -> None:
    text = (ROOT / "docs" / "OPERATOR_BOUNDARY.md").read_text(encoding="utf-8")
    lowered = text.lower()
    assert "user-manual only" in lowered
    assert "does not submit" in lowered
    assert "search, read, send" in lowered


def test_manual_handoff_zip_contains_required_assets(tmp_path: Path) -> None:
    module = _load_script("build_manual_handoff.py")
    output = tmp_path / "handoff.zip"
    report = module.build_packet(output)
    assert report["integrity"] == "PASS"
    assert report["external_submission_performed"] is False
    assert report["network_actions_performed"] is False

    with zipfile.ZipFile(output) as archive:
        names = set(archive.namelist())
        assert "START_HERE_MANUAL.md" in names
        assert "MANUAL_SUBMISSION_CHECKLIST.md" in names
        assert "FitzSight_GOAI_初赛方案_CN.pdf" in names
        assert not any(name.endswith(".pptx") for name in names)
        assert "FitzSight_Offline_Demo_Backup.mp4" in names
        manual = json.loads(archive.read("MANUAL_ACTIONS.json"))
        assert manual["execution_policy"] == "external_submission_user_manual_only"
        assert manual["automation_boundary"]["email_access"] is False
        assert manual["competition_upload_allowlist"] == ["FitzSight_GOAI_初赛方案_CN.pdf"]
        manifest = json.loads(archive.read("HANDOFF_MANIFEST.json"))
        assert manifest["external_submission_performed"] is False
        assert manifest["network_actions_performed"] is False


def test_preflight_reports_manual_submission_boundary() -> None:
    module = _load_script("preflight_submission.py")
    report = module.run_preflight()
    boundary = report["manual_submission_boundary"]
    assert boundary["mode"] == "user_manual_only"
    assert boundary["external_write_actions_performed"] is False
    assert boundary["portal_upload_or_submit_by_automation"] is False
    assert boundary["email_access_by_automation"] is False


def test_handoff_readiness_is_machine_readable() -> None:
    module = _load_script("handoff_readiness.py")
    report = module.readiness_report()
    assert report["external_write_actions_performed"] is False
    assert report["ready_for_user_takeover"] is True
    assert any("GOAI portal" in item for item in report["manual_user_actions_remaining"])


def test_upload_bundle_declares_no_external_submission(tmp_path: Path) -> None:
    module = _load_script("build_submission_bundle.py")
    assert module.DEFAULT_FILES == ("submission/FitzSight_GOAI_初赛方案_CN.pdf",)
    source_text = (ROOT / "scripts" / "build_submission_bundle.py").read_text(encoding="utf-8")
    assert '"external_submission_performed": False' in source_text
    assert '"network_actions_performed": False' in source_text
