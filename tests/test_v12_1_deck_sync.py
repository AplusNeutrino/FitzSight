from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_chinese_deck_source_and_v013_docs_are_synchronized():
    source = (ROOT / "submission" / "deck-cn" / "index.html").read_text(encoding="utf-8")
    provider = (ROOT / "docs" / "MODEL_PROVIDER.md").read_text(encoding="utf-8")
    assert "v0.13.0" in source
    assert "DeepSeek V4" in source
    assert "Evidence ID" in source
    assert "deepseek-v4-flash" in provider
    assert "deepseek-v4-pro" in provider


def test_validation_records_deliberately_unrun_live_provider():
    text = (ROOT / "docs" / "V0.13_VALIDATION.md").read_text(encoding="utf-8")
    assert "deepseek_live: not_requested" in text
    assert "Mock" in text or "mock" in text
