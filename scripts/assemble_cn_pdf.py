from __future__ import annotations

import argparse
import json
from pathlib import Path

from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas


ROOT = Path(__file__).resolve().parents[1]
PAGE_WIDTH = 960
PAGE_HEIGHT = 540


def build_pdf(images_dir: Path, output: Path) -> dict[str, object]:
    images = sorted(images_dir.glob("slide-*.png"))
    if len(images) != 12:
        raise ValueError(f"Expected 12 rendered slides, found {len(images)}")
    output.parent.mkdir(parents=True, exist_ok=True)
    pdf = canvas.Canvas(str(output), pagesize=(PAGE_WIDTH, PAGE_HEIGHT), pageCompression=1)
    pdf.setTitle("FitzSight GOAI 初赛方案")
    pdf.setAuthor("FitzSight")
    pdf.setSubject("GOAI 2026 Boundless Agents · AI+金融")
    for image in images:
        pdf.drawImage(ImageReader(str(image)), 0, 0, width=PAGE_WIDTH, height=PAGE_HEIGHT)
        pdf.showPage()
    pdf.save()
    return {
        "product": "FitzSight",
        "version": "0.13.0",
        "output": str(output),
        "pages": len(images),
        "page_size_points": [PAGE_WIDTH, PAGE_HEIGHT],
        "language": "zh-CN",
        "source": "Playwright static renders of guizang-ppt-skill Swiss IKB HTML",
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Assemble the rendered Chinese deck into a 16:9 PDF.")
    parser.add_argument(
        "--images-dir",
        default=str(ROOT / "build" / "deck-cn-rendered"),
    )
    parser.add_argument(
        "--output",
        default=str(ROOT / "submission" / "FitzSight_GOAI_初赛方案_CN.pdf"),
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = build_pdf(Path(args.images_dir), Path(args.output))
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
