from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import preflight_submission


def test_required_submission_file_list_is_pdf_only():
    assert "submission/FitzSight_GOAI_初赛方案_CN.pdf" in preflight_submission.REQUIRED_FILES
    assert not any(path.endswith(".pptx") for path in preflight_submission.REQUIRED_FILES)


def test_secret_scanner_has_deepseek_key_pattern():
    assert any("DEEPSEEK_API_KEY" in pattern.pattern for pattern in preflight_submission.SECRET_PATTERNS)


def test_current_submission_preflight_passes():
    report = preflight_submission.run_preflight(require_final_machine_kit=False)
    assert report["passed"] is True
    assert report["deepseek_live"] == "not_requested"
