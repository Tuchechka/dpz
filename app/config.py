"""Завантажує config.yaml і валідує його через Pydantic."""
from pathlib import Path

import yaml
from pydantic import BaseModel


class FileStrategyConfig(BaseModel):
    path: str = "./output/budget_records.jsonl"


class KafkaStrategyConfig(BaseModel):
    bootstrap_servers: str = "localhost:9092"
    topic: str = "dallas-budget"


class RedisStrategyConfig(BaseModel):
    host: str = "localhost"
    port: int = 6379
    db: int = 0
    key_prefix: str = "budget:"


class OutputConfig(BaseModel):
    strategy: str = "console"
    file: FileStrategyConfig = FileStrategyConfig()
    kafka: KafkaStrategyConfig = KafkaStrategyConfig()
    redis: RedisStrategyConfig = RedisStrategyConfig()


class ReaderConfig(BaseModel):
    csv_path: str = "./data/dallas_budget.csv"


class AppConfig(BaseModel):
    reader: ReaderConfig = ReaderConfig()
    output: OutputConfig = OutputConfig()


def load_config(path: str = "config.yaml") -> AppConfig:
    """Зчитує YAML, валідує через Pydantic, повертає типизований конфіг."""
    config_path = Path(path)
    if not config_path.exists():
        # Якщо файлу немає -- беремо все з дефолтів
        return AppConfig()

    with open(config_path, "r", encoding="utf-8") as f:
        raw = yaml.safe_load(f) or {}

    return AppConfig.model_validate(raw)
