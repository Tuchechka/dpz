"""Абстрактні базові класи (інтерфейси) для рівня доступу до даних."""
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Optional

from app.data_access.models import (
    Category,
    Comment,
    Media,
    Page,
    Post,
    Tag,
    User,
)
from app.business_logic.dto import (
    CategoryCreateDto,
    CommentCreateDto,
    CsvRowDto,
    MediaCreateDto,
    PageCreateDto,
    PostCreateDto,
    TagCreateDto,
    UserCreateDto,
)


# ============================================================
# CSV reader
# ============================================================

class ICsvReader(ABC):
    """Контракт читача CSV-файлів."""

    @abstractmethod
    def read(self, path: Path) -> List[CsvRowDto]:
        """Зчитує файл, повертає список валідованих DTO."""
        ...


# ============================================================
# Repositories
# ============================================================

class IUserRepository(ABC):
    """Контракт репозиторію користувачів."""

    @abstractmethod
    def get_by_email(self, email: str) -> Optional[User]:
        ...

    @abstractmethod
    def create(self, dto: UserCreateDto) -> User:
        ...

    @abstractmethod
    def count(self) -> int:
        ...


class ICategoryRepository(ABC):
    @abstractmethod
    def get_by_slug(self, slug: str) -> Optional[Category]:
        ...

    @abstractmethod
    def create(self, dto: CategoryCreateDto) -> Category:
        ...

    @abstractmethod
    def count(self) -> int:
        ...


class ITagRepository(ABC):
    @abstractmethod
    def get_by_slug(self, slug: str) -> Optional[Tag]:
        ...

    @abstractmethod
    def create(self, dto: TagCreateDto) -> Tag:
        ...

    @abstractmethod
    def count(self) -> int:
        ...


class IMediaRepository(ABC):
    @abstractmethod
    def get_by_url(self, url: str) -> Optional[Media]:
        ...

    @abstractmethod
    def create(self, dto: MediaCreateDto) -> Media:
        ...

    @abstractmethod
    def count(self) -> int:
        ...


class IPostRepository(ABC):
    @abstractmethod
    def get_by_slug(self, slug: str) -> Optional[Post]:
        ...

    @abstractmethod
    def create(self, dto: PostCreateDto) -> Post:
        ...

    @abstractmethod
    def count(self) -> int:
        ...


class IPageRepository(ABC):
    @abstractmethod
    def get_by_slug(self, slug: str) -> Optional[Page]:
        ...

    @abstractmethod
    def create(self, dto: PageCreateDto) -> Page:
        ...

    @abstractmethod
    def count(self) -> int:
        ...


class ICommentRepository(ABC):
    @abstractmethod
    def create(self, dto: CommentCreateDto) -> Comment:
        ...

    @abstractmethod
    def count(self) -> int:
        ...