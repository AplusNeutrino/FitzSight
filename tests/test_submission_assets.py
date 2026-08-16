from pathlib import Path

from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
PDF = ROOT / "submission" / "FitzSight_GOAI_初赛方案_CN.pdf"
HTML = ROOT / "submission" / "deck-cn" / "index.html"


def test_chinese_pdf_only_submission_exists():
    assert PDF.exists() and PDF.stat().st_size > 10_000
    assert PDF.read_bytes()[:5] == b"%PDF-"
    assert not list((ROOT / "submission").glob("*.pptx"))


def test_submission_pdf_has_twelve_widescreen_pages():
    reader = PdfReader(PDF)
    assert len(reader.pages) == 12
    for page in reader.pages:
        width = float(page.mediabox.width)
        height = float(page.mediabox.height)
        assert abs(width / height - 16 / 9) < 0.01


def test_reproducible_html_has_chinese_and_no_legacy_brand():
    text = HTML.read_text(encoding="utf-8")
    assert "FitzSight" in text
    assert "DeepSeek" in text
    assert "欧洲" in text
    assert "FinSight" not in text
    assert "FIN SIGHT" not in text
    assert text.count("data-slide-id=") == 12
