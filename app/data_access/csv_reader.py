"""Реалізація читача CSV-файлів."""
import csv
from pathlib import Path
from typing import List

from app.business_logic.dto import CsvRowDto
from app.common.logger import get_logger
from app.data_access.interfaces import ICsvReader

log = get_logger(__name__)


class CsvReader(ICsvReader):
    """Читає денормалізовану CSV-таблицю, повертає список CsvRowDto."""

    def read(self, path: Path) -> List[CsvRowDto]:
        if not path.exists():
            raise FileNotFoundError(f"CSV file not found: {path}")

        rows: List[CsvRowDto] = []
        with open(path, "r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            for row_num, raw in enumerate(reader, start=2):
                # Порожні рядки викидаємо -- Pydantic підставить defaults
                cleaned = {k: v for k, v in raw.items() if v != ""}
                try:
                    rows.append(CsvRowDto.model_validate(cleaned))
                except Exception as e:
                    log.warning(f"Row {row_num} skipped: {e}")

        log.info(f"Read {len(rows)} rows from {path.name}")
        return rows