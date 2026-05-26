"""Reader -- відокремлений від коду виводу за вимогою задачі.

Цей файл займається ЛИШЕ читанням CSV. Він НЕ знає, куди підуть дані --
це справа стратегії виводу.
"""
import csv
from pathlib import Path
from typing import List

from app.logger import get_logger
from app.models import BudgetRecord

log = get_logger(__name__)


class CsvBudgetReader:
    """Читає CSV-файл, повертає список BudgetRecord."""

    def __init__(self, csv_path: str):
        self._path = Path(csv_path)

    def read(self) -> List[BudgetRecord]:
        if not self._path.exists():
            raise FileNotFoundError(f"CSV not found: {self._path}")

        records: List[BudgetRecord] = []
        with open(self._path, "r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            for row_num, row in enumerate(reader, start=2):
                try:
                    records.append(self._row_to_record(row))
                except Exception as e:
                    log.warning(f"Row {row_num} skipped: {e}")

        log.info(f"Read {len(records)} records from {self._path}")
        return records

    def _row_to_record(self, row: dict) -> BudgetRecord:
        budget = float(row.get("budget_amount", 0) or 0)
        actual = float(row.get("actual_amount", 0) or 0)
        return BudgetRecord(
            fiscal_year=int(row.get("fiscal_year", 0) or 0),
            department=row.get("department", "").strip(),
            account_code=row.get("account_code", "").strip(),
            account_description=row.get("account_description", "").strip(),
            budget_amount=budget,
            actual_amount=actual,
            variance=actual - budget,
        )
