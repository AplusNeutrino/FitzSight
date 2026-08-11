from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import preflight_submission


def test_required_submission_file_list_contains_both_deck_formats():
    assert "submission/FitzSight_GOAI_Initial_Round.pptx" in preflight_submission.REQUIRED_FILES
    assert "submission/FitzSight_GOAI_Initial_Round.pdf" in preflight_submission.REQUIRED_FILES


def test_secret_scanner_has_openai_key_pattern():
    assert any("OPENAI_API_KEY" in pattern.pattern for pattern in preflight_submission.SECRET_PATTERNS)
