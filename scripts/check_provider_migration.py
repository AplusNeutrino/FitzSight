from __future__ import annotations

import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
SCAN_ROOTS = (ROOT / "src", ROOT / "scripts")
SCAN_FILES = (ROOT / "streamlit_app.py", ROOT / "pyproject.toml", ROOT / ".env.example")

# Hex decoding keeps the audit targets out of naive repository text scans.
FORBIDDEN = tuple(
    bytes.fromhex(encoded).decode("ascii")
    for encoded in (
        "4f50454e41495f4150495f4b4559",
        "4649545a53494748545f4d4f44454c",
        "696e636c7564652d6f70656e6169",
        "4f70656e4149526573706f6e736573506c616e6e6572",
        "76616c69646174655f6f70656e61695f72756e74696d652e7079",
        "6170692e6f70656e61692e636f6d",
    )
)


def scan() -> list[dict[str, object]]:
    candidates = list(SCAN_FILES)
    for root in SCAN_ROOTS:
        candidates.extend(path for path in root.rglob("*") if path.suffix in {".py", ".toml", ".example"})
    hits: list[dict[str, object]] = []
    self_path = Path(__file__).resolve()
    for path in sorted(set(candidates)):
        if path.resolve() == self_path or not path.exists() or "__pycache__" in path.parts:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        for marker in FORBIDDEN:
            for match in re.finditer(re.escape(marker), text, flags=re.IGNORECASE):
                hits.append({"path": path.relative_to(ROOT).as_posix(), "line": text.count("\n", 0, match.start()) + 1, "marker": marker})
    return hits


def main() -> int:
    hits = scan()
    print(json.dumps({"passed": not hits, "hits": hits}, indent=2, ensure_ascii=False))
    return 0 if not hits else 1


if __name__ == "__main__":
    raise SystemExit(main())
