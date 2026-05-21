"""Абстрактні базові класи (інтерфейси) для рівня доступу до даних."""
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Optional

from app.business_logic.dto import (
    CategoryCreateDto,
    CommentCreateDto,
    CsvRowDto,
    MediaCreateDto,
    PageCreateDto,
    PostCreateDto,
    PostUpdateDto,
    TagCreateDto,
    UserCreateDto,
)
from app.data_access.models import (
    Category,
    Comment,
    Media,
    Page,
    Post,
    Tag,
    User,
)


# ============================================================
# CSV reader
# ============================================================

class ICsvReader(ABC):
    """Контракт читача CSV-файлів."""

    @abstractmethod
    def read(self, path: Path) -> List[CsvRowDto]:
        ...


# ============================================================
# Repositories
# ============================================================

class IUserRepository(ABC):
    @abstractmethod
    def get_by_email(self, email: str) -> Optional[User]:
        ...

    @abstractmethod
    def get_by_id(self, user_id: int) -> Optional[User]:
        ...

    @abstractmethod
    def get_first(self) -> Optional[User]:
        """Повертає першого користувача (для дефолтного автора в UI)."""
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
    """Розширено для CRUD (Lab 3)."""

    @abstractmethod
    def get_by_id(self, post_id: int) -> Optional[Post]:
        ...

    @abstractmethod
    def get_by_slug(self, slug: str) -> Optional[Post]:
        ...

    @abstractmethod
    def list_all(self, limit: int = 50, offset: int = 0) -> List[Post]:
        ...

    @abstractmethod
    def create(self, dto: PostCreateDto) -> Post:
        ...

    @abstractmethod
    def update(self, post: Post, dto: PostUpdateDto) -> Post:
        ...

    @abstractmethod
    def delete(self, post: Post) -> None:
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
