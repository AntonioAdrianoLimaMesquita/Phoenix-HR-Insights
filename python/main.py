"""Command-line entry point for Phoenix HR Insights."""
from __future__ import annotations

import argparse
from datetime import date
from pathlib import Path
import sys

from config import DEFAULT_OUTPUT_DIR, DEFAULT_SQL_DIR, DEFAULT_SEED, Settings
from dimensions import build_dimensions
from facts import build_facts
from export_sql import write_csv_tables, write_ddl, write_run_summary


def parse_date(value: str) -> date:
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("Dates must use YYYY-MM-DD.") from exc


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate synthetic data for Phoenix HR Insights.")
    parser.add_argument("--employees", type=int, default=15_000, help="Number of synthetic employees (default: 15000).")
    parser.add_argument("--start", type=parse_date, default=date(2024, 1, 1), help="Snapshot start date.")
    parser.add_argument("--end", type=parse_date, default=date(2026, 6, 30), help="Snapshot end date.")
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED, help="Random seed for reproducible output.")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR, help="CSV output directory.")
    parser.add_argument("--sql-dir", type=Path, default=DEFAULT_SQL_DIR, help="SQL DDL output directory.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    settings = Settings(employee_count=args.employees, start_date=args.start, end_date=args.end, seed=args.seed,
                        output_dir=args.output_dir, sql_dir=args.sql_dir)
    settings.validate()
    print(f"Generating {settings.employee_count:,} fully synthetic employees...")
    dimensions = build_dimensions(settings)
    facts = build_facts(settings, dimensions)
    tables = {**dimensions, **facts}
    counts = write_csv_tables(tables, settings.output_dir)
    ddl = write_ddl(tables, settings.sql_dir)
    summary = write_run_summary(counts, settings.output_dir)
    print("Generation complete.")
    for table, count in counts.items():
        print(f"  {table}: {count:,} rows")
    print(f"CSV output: {settings.output_dir}")
    print(f"SQL DDL:    {ddl}")
    print(f"Summary:    {summary}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
