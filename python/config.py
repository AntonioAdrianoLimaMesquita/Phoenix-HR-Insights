"""Central configuration for the Phoenix HR Insights synthetic warehouse."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from datetime import date


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "data" / "processed"
DEFAULT_SQL_DIR = PROJECT_ROOT / "sql"
DEFAULT_SEED = 20260718


@dataclass(frozen=True)
class Settings:
    employee_count: int = 15_000
    start_date: date = date(2024, 1, 1)
    end_date: date = date(2026, 6, 30)
    seed: int = DEFAULT_SEED
    company_name: str = "Phoenix Financial Group"
    output_dir: Path = DEFAULT_OUTPUT_DIR
    sql_dir: Path = DEFAULT_SQL_DIR

    def validate(self) -> None:
        if self.employee_count < 100:
            raise ValueError("employee_count must be at least 100.")
        if self.start_date >= self.end_date:
            raise ValueError("start_date must be before end_date.")
