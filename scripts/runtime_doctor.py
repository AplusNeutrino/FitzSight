from __future__ import annotations

import argparse
import importlib.util
import json
import os
from pathlib import Path
import platform
import sys

ROOT = Path(__file__).resolve().parents[1]


def module_available(name: str) -> bool:
    return importlib.util.find_spec(name) is not None


def build_report(data_dir: Path) -> dict[str, object]:
    required_csv = (
        "customers.csv",
        "sales_activity.csv",
        "deposits.csv",
        "withdrawals.csv",
        "trades.csv",
        "business_events.csv",
    )
    checks = {
        "python": {
            "ok": sys.version_info >= (3, 11),
            "detail": platform.python_version(),
        },
        "fitzsight_source": {
            "ok": (ROOT / "src" / "fitzsight").is_dir(),
            "detail": str(ROOT / "src" / "fitzsight"),
        },
        "duckdb": {
            "ok": module_available("duckdb"),
            "detail": "installed" if module_available("duckdb") else "not installed in this environment",
        },
        "streamlit": {
            "ok": module_available("streamlit"),
            "detail": "installed" if module_available("streamlit") else "install with pip install -e \".[ui]\"",
        },
        "openai_sdk": {
            "ok": module_available("openai"),
            "detail": "installed" if module_available("openai") else "install with pip install -e \".[openai]\"",
        },
        "openai_api_key": {
            "ok": bool(os.getenv("OPENAI_API_KEY")),
            "detail": "configured" if os.getenv("OPENAI_API_KEY") else "not configured",
        },
        "fitzsight_model": {
            "ok": bool(os.getenv("FITZSIGHT_MODEL")),
            "detail": os.getenv("FITZSIGHT_MODEL") or "not configured",
        },
        "data_directory": {
            "ok": data_dir.exists(),
            "detail": str(data_dir.resolve()),
        },
        "generated_dataset": {
            "ok": all((data_dir / name).exists() for name in required_csv),
            "detail": "complete" if all((data_dir / name).exists() for name in required_csv) else "will be generated automatically by the runtime",
        },
        "presentation_assets": {
            "ok": all(
                path.exists()
                for path in (
                    ROOT / "submission" / "FitzSight_GOAI_Initial_Round.pptx",
                    ROOT / "submission" / "FitzSight_GOAI_Initial_Round.pdf",
                )
            ),
            "detail": "PPTX/PDF present",
        },
    }
    return {
        "product": "FitzSight",
        "runtime_doctor_version": "0.9",
        "checks": checks,
        "core_demo_ready": checks["python"]["ok"] and checks["fitzsight_source"]["ok"],
        "streamlit_live_ready": checks["streamlit"]["ok"],
        "openai_live_ready": checks["openai_sdk"]["ok"] and checks["openai_api_key"]["ok"] and checks["fitzsight_model"]["ok"],
        "secrets_disclosed": False,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Inspect FitzSight demo/runtime readiness without exposing secrets.")
    parser.add_argument("--data-dir", default=str(ROOT / "data" / "generated"))
    parser.add_argument("--output", default=None)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = build_report(Path(args.data_dir))
    rendered = json.dumps(report, indent=2, ensure_ascii=False)
    print(rendered)
    if args.output:
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(rendered + "\n", encoding="utf-8")
    return 0 if report["core_demo_ready"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
