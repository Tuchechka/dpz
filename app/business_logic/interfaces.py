"""Інтерфейси та допоміжні типи рівня бізнес-логіки."""
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Optional

from pydantic import BaseModel

from app.business_logic.dto import (
    PostCreateDto,
    PostDetailDto,
    PostReadDto,
    PostUpdateDto,
)


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


class IPostService(ABC):
    """Контракт сервісу для CRUD-операцій з постами (Lab 3)."""

    @abstractmethod
    def list_posts(self, limit: int = 50, offset: int = 0) -> List[PostReadDto]:
        """Повернути список постів (для list view)."""
        ...

    @abstractmethod
    def get_post(self, post_id: int) -> Optional[PostDetailDto]:
        """Повернути деталі одного посту (для detail view)."""
        ...

    @abstractmethod
    def count_posts(self) -> int:
        """Загальна кількість постів."""
        ...

    @abstractmethod
    def create_post(self, dto: PostCreateDto) -> int:
        """Створити новий пост, повернути id."""
        ...

    @abstractmethod
    def update_post(self, post_id: int, dto: PostUpdateDto) -> bool:
        """Оновити пост. True якщо знайдено і оновлено."""
        ...

    @abstractmethod
    def delete_post(self, post_id: int) -> bool:
        """Видалити пост. True якщо знайдено і видалено."""
        ...
