"""Інтерфейси та допоміжні типи рівня бізнес-логіки."""
from abc import ABC, abstractmethod
from pathlib import Path

from pydantic import BaseModel


class SeedingResult(BaseModel):
    """Підсумок заповнення БД -- кількість записів у кожній таблиці."""
    users: int
    categories: int
    tags: int
    media: int
    posts: int
    comments: int


class IContentSeedingService(ABC):
    """Контракт сервісу заповнення БД даними з CSV."""

    @abstractmethod
    def seed(self, csv_path: Path) -> SeedingResult:
        """
        Читає CSV, дедуплікує сутності, зберігає в БД.
        Не комітить сам -- це робить caller (main.py).
        """
        ...