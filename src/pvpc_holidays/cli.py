"""CLI for PVPC holidays."""

from __future__ import annotations

import argparse
from datetime import date
import logging
import sys

from .core import DEFAULT_CSV_URL, PVPCError, get_pvpc_holidays


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="pvpc-holidays",
        description="Calculate Spanish PVPC P3/valle holidays for one year.",
    )
    parser.add_argument("--year", type=int, default=date.today().year, help="Target year (default: current year)")
    parser.add_argument(
        "--source",
        choices=["csv", "python-holidays"],
        default="csv",
        help="Holiday source: Seguridad Social CSV or python-holidays",
    )
    parser.add_argument("--csv-url", default=DEFAULT_CSV_URL, help="CSV URL (optional with {year} placeholder)")
    parser.add_argument("--timeout", type=int, default=20, help="HTTP timeout in seconds")
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Log level",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    logging.basicConfig(level=getattr(logging, args.log_level), format="%(levelname)s: %(message)s")
    log = logging.getLogger("pvpc_holidays")

    try:
        result = get_pvpc_holidays(
            args.year,
            source=args.source,
            csv_url=args.csv_url,
            timeout=args.timeout,
            logger=log,
        )
    except PVPCError as exc:
        log.error("Abort: %s", exc)
        return 1

    print(f"PVPC P3/valle holidays {args.year}/{args.year + 1} ({len(result)} entries):")
    for holiday_day, description in result.items():
        print(f"{holiday_day.isoformat()} - {description}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
