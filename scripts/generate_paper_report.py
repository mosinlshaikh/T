from __future__ import annotations

import argparse
from dataclasses import asdict
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from trading_os.reports.paper_logbook import export_daily_paper_report


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate a paper trading daily report.")
    parser.add_argument("--day", default=None, help="Report date in YYYY-MM-DD format.")
    parser.add_argument("--output-dir", default="reports/paper/daily")
    parser.add_argument("--logbook", default="docs/PAPER_TRADING_LOGBOOK.md")
    args = parser.parse_args()

    result = export_daily_paper_report(
        day=args.day,
        output_dir=args.output_dir,
        logbook_path=args.logbook,
    )
    print(json.dumps(asdict(result), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
