from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_chinese_deck_uses_verified_runtime_metrics():
    text = (ROOT / "submission" / "deck-cn" / "index.html").read_text(encoding="utf-8")
    for expected in ("-7.53", "-1.21", "+29.15", "CRM-CHANGE-2026-0715#p1", "5/5", "8/8"):
        assert expected in text


def test_deck_build_is_html_to_pdf_only():
    builder = (ROOT / "scripts" / "build_cn_submission.py").read_text(encoding="utf-8")
    renderer = (ROOT / "scripts" / "render_cn_submission.mjs").read_text(encoding="utf-8")
    assert "index.html" in builder
    assert "Playwright" in renderer or "playwright" in renderer
    assert "pptx" not in builder.lower()
    assert "pptx" not in renderer.lower()
