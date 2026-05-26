"""Опційно: завантажує свіжі дані з Dallas Open Data API.

Використовується, якщо хочеш оновити sample-датасет до актуального.
Зверни увагу: реальні колонки Socrata можуть відрізнятися від наших --
тоді треба адаптувати CsvBudgetReader._row_to_record.
"""
import urllib.request
from pathlib import Path

DATASET_ID = "nr4f-efb3"  # CoD Expenses Budget vs Actual
URL = f"https://www.dallasopendata.com/resource/{DATASET_ID}.csv?$limit=1000"
OUTPUT = Path(__file__).resolve().parents[1] / "data" / "dallas_budget_fresh.csv"


def main():
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    print(f"Downloading from {URL}...")
    urllib.request.urlretrieve(URL, OUTPUT)
    print(f"Saved to {OUTPUT}")
    print(
        "Note: real Socrata columns may differ. "
        "Adjust CsvBudgetReader if needed."
    )


if __name__ == "__main__":
    main()
