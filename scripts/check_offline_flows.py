"""Exercise the actual CLI for five approved synthetic demos on both backends.

No model planner is selected. Output is execution evidence, not an independent
numerical correctness evaluation or a production/AI benefit measurement.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parents[1]
CASES = (
    ('crm_routing_ftd_investigation', 'Why did European FTD conversion deteriorate after July 15?'),
    ('net_deposit_anomaly_investigation', 'Why did European net deposits fall in the week starting August 3?'),
    ('customer_intelligence_segmentation', 'How are European customer segments distributed by behavioral value, and which segment contributes most to deposits?'),
    ('marketing_lead_quality_investigation', 'Why did Americas lead volume rise while FTD conversion fell after June 15?'),
    ('false_correlation_guardrail_investigation', 'Why did Asia FTD conversion fall after July 20, and is the nearby office relocation the cause?'),
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    runs = []
    # Always start from a new disposable synthetic-data directory; never reuse
    # or overwrite a user's imported data. The runtime's legacy demo generator
    # uses GeneratorConfig defaults (seed 20260811, 20,000 customers).
    with tempfile.TemporaryDirectory(prefix='fitzsight-offline-') as temporary:
        data_dir = Path(temporary) / 'data'
        for backend in ('sqlite', 'duckdb'):
            for intent, question in CASES:
                started = time.perf_counter()
                command = [sys.executable, str(ROOT / 'scripts/agent_investigate.py'),
                           '--planner', 'deterministic', '--backend', backend,
                           '--data-dir', str(data_dir), '--question', question]
                row = {'backend': backend, 'intent': intent, 'question': question}
                try:
                    result = subprocess.run(command, cwd=ROOT, capture_output=True,
                                            text=True, timeout=120)
                    row.update(returncode=result.returncode, stderr=result.stderr)
                    payload = json.loads(result.stdout) if result.returncode == 0 else {}
                    row['passed'] = bool(
                        result.returncode == 0
                        and payload.get('runtime', {}).get('backend') == backend
                        and payload.get('plan', {}).get('intent') == intent
                        and payload.get('verification', {}).get('passed') is True
                        and payload.get('final_answer', {}).get('status') == 'verified'
                        and payload.get('audit_evidence')
                    )
                    row['verification'] = payload.get('verification')
                    row['diagnosis'] = payload.get('investigation', {}).get('diagnosis')
                    row['evidence_count'] = len(payload.get('audit_evidence', []))
                except (subprocess.TimeoutExpired, ValueError) as exc:
                    row.update(passed=False, error=str(exc))
                row['elapsed_seconds'] = round(time.perf_counter() - started, 3)
                runs.append(row)
    report = {'scope': 'synthetic deterministic CLI smoke checks; not numerical truth validation',
              'seed': 20260811, 'n_customers': 20000,
              'passed': sum(r['passed'] for r in runs), 'total': len(runs), 'runs': runs}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f"{report['passed']}/{report['total']} offline flows passed; {args.output}")
    return 0 if report['passed'] == report['total'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
