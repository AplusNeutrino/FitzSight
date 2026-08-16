from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
import time
from urllib.error import URLError
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]


def streamlit_available() -> bool:
    return importlib.util.find_spec("streamlit") is not None


def free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def build_command(port: int) -> list[str]:
    return [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        str(ROOT / "streamlit_app.py"),
        "--global.developmentMode=false",
        "--server.headless=true",
        "--server.address=127.0.0.1",
        f"--server.port={port}",
        "--browser.gatherUsageStats=false",
    ]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Launch FitzSight Streamlit headlessly and verify its local health endpoint.")
    parser.add_argument("--port", type=int, default=0)
    parser.add_argument("--timeout", type=float, default=30.0)
    parser.add_argument("--output", default=None)
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    port = args.port or free_port()
    command = build_command(port)
    report: dict[str, object] = {
        "product": "FitzSight",
        "runtime": "streamlit",
        "port": port,
        "command": command,
        "health_url": f"http://127.0.0.1:{port}/_stcore/health",
        "passed": False,
    }

    if args.dry_run:
        report["status"] = "dry_run"
        code = 0
    elif not streamlit_available():
        report["status"] = "not_run_dependency_missing"
        report["message"] = 'Streamlit is not installed; install with pip install -e ".[ui]".'
        code = 2
    else:
        started = time.perf_counter()
        with tempfile.NamedTemporaryFile(mode="w+", encoding="utf-8", delete=True) as log:
            process = subprocess.Popen(
                command,
                cwd=ROOT,
                stdout=log,
                stderr=subprocess.STDOUT,
                text=True,
            )
            try:
                deadline = time.monotonic() + args.timeout
                last_error = ""
                while time.monotonic() < deadline:
                    if process.poll() is not None:
                        last_error = f"Streamlit exited early with code {process.returncode}"
                        break
                    try:
                        with urlopen(report["health_url"], timeout=1.0) as response:  # noqa: S310 - localhost only
                            body = response.read().decode("utf-8", errors="replace").strip()
                            if response.status == 200:
                                report.update(
                                    {
                                        "status": "passed",
                                        "passed": True,
                                        "http_status": response.status,
                                        "health_body": body[:200],
                                        "startup_seconds": time.perf_counter() - started,
                                    }
                                )
                                break
                    except (URLError, TimeoutError, OSError) as exc:
                        last_error = str(exc)
                    time.sleep(0.25)
                else:
                    last_error = "Timed out waiting for Streamlit health endpoint"

                if not report["passed"]:
                    report["status"] = "failed"
                    report["message"] = last_error
                    log.seek(0)
                    report["log_tail"] = log.read()[-4000:]
            finally:
                if process.poll() is None:
                    process.terminate()
                    try:
                        process.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        process.kill()
                        process.wait(timeout=5)
        code = 0 if report["passed"] else 1

    rendered = json.dumps(report, indent=2, ensure_ascii=False)
    print(rendered)
    if args.output:
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(rendered + "\n", encoding="utf-8")
    return code


if __name__ == "__main__":
    raise SystemExit(main())
