from __future__ import annotations

from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def _slide_text() -> str:
    path = ROOT / "submission" / "FitzSight_GOAI_Initial_Round.pptx"
    with zipfile.ZipFile(path) as archive:
        return "\n".join(
            archive.read(name).decode("utf-8", errors="ignore")
            for name in sorted(archive.namelist())
            if name.startswith("ppt/slides/slide") and name.endswith(".xml")
        )


def test_formal_deck_and_source_are_synchronized():
    source = (ROOT / "docs" / "PITCH_DECK_CONTENT.md").read_text(encoding="utf-8")
    text = _slide_text()
    assert "v0.12.1 synchronized" in source
    assert "one CRM/FTD hero + one false-correlation refusal" in source
    assert "EvidenceClaimVerifier" in text
    assert "Human decision" in text


def test_final_reviewer_gate_preserves_live_runtime_boundaries():
    gate = (ROOT / "docs" / "V0.12.1_GOAI_REVIEWER_GATE.md").read_text(encoding="utf-8")
    assert "LIVE RUNTIME STILL UNVERIFIED" in gate
    assert "OpenAI Responses live planner" in gate
    assert "Portal" in gate or "portal" in gate
    assert "production blueprint" in gate.lower()
