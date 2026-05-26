"""Точка входу додатку.

Послідовність:
1. Завантажуємо config.yaml (з валідацією через Pydantic)
2. Читач (відокремлений від коду виводу!) дістає записи з CSV
3. Фабрика обирає потрібну стратегію виводу за конфігом
4. Викликаємо strategy.write(records) -- main.py НЕ знає, куди саме йдуть дані

Перемикання Console -> File -> Kafka -> Redis -- тільки через config.yaml,
БЕЗ змін у коді цього файлу.
"""
from app.config import load_config
from app.logger import get_logger
from app.output.factory import OutputStrategyFactory
from app.reader.csv_reader import CsvBudgetReader

log = get_logger(__name__)


def main():
    # 1. Конфіг
    config = load_config("config.yaml")
    log.info(f"Loaded config. Output strategy: '{config.output.strategy}'")

    # 2. Reader (окремий від коду виводу за вимогою задачі)
    reader = CsvBudgetReader(config.reader.csv_path)
    records = reader.read()

    # 3. Стратегія виводу (за конфігом, через фабрику)
    strategy = OutputStrategyFactory.create(config.output)
    log.info(f"Using strategy: {strategy.__class__.__name__}")

    # 4. Запис -- main.py НЕ знає, куди саме
    strategy.write(records)
    log.info("All done.")


if __name__ == "__main__":
    main()
