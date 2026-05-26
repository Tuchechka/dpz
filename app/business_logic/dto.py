"""Pydantic DTOs для передачі даних між шарами."""
from __future__ import annotations
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict


# ============================================================
# Raw CSV row -- читається з файлу як є
# ============================================================

class CsvRowDto(BaseModel):
    """
    Один рядок денормалізованого CSV.
    Містить повний контекст: пост + автор + категорії + теги + медіа + коментар.
    """
    model_config = ConfigDict(str_strip_whitespace=True)

    post_external_id: str
    post_title: str
    post_slug: str
    post_body: str
    post_status: str = "published"
    post_published_at: Optional[datetime] = None

    author_username: str
    author_email: str
    author_role: str = "author"

    categories: str = ""
    tags: str = ""

    media_filename: Optional[str] = None
    media_url: Optional[str] = None
    media_mime_type: Optional[str] = None

    comment_author_name: Optional[str] = None
    comment_author_email: Optional[str] = None
    comment_content: Optional[str] = None


# ============================================================
# DTOs для створення сутностей у БД
# ============================================================

class UserCreateDto(BaseModel):
    username: str
    email: str
    password_hash: str = "stub_hash"
    role: str = "author"


class CategoryCreateDto(BaseModel):
    name: str
    slug: str


class TagCreateDto(BaseModel):
    name: str
    slug: str


class PostCreateDto(BaseModel):
    title: str
    slug: str
    body: str
    status: str = "draft"
    published_at: Optional[datetime] = None
    allow_comments: bool = True
    author_id: int


class PageCreateDto(BaseModel):
    title: str
    slug: str
    body: str
    status: str = "draft"
    menu_order: int = 0
    parent_page_id: Optional[int] = None
    author_id: int


class CommentCreateDto(BaseModel):
    author_name: str
    author_email: str
    content: str
    approved: bool = False
    post_id: int


class MediaCreateDto(BaseModel):
    filename: str
    url: str
    mime_type: str
    size: int = 0


# ============================================================
# DTO для оновлення (Lab 3)
# ============================================================

class PostUpdateDto(BaseModel):
    """Для редагування посту через UI -- не змінює author_id."""
    title: str
    slug: str
    body: str
    status: str = "draft"
    allow_comments: bool = True
    published_at: Optional[datetime] = None


# ============================================================
# DTOs для читання (Lab 3) -- передаються у Jinja2 шаблони
# ============================================================

class CommentReadDto(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    author_name: str
    author_email: str
    content: str
    created_at: datetime
    approved: bool


class PostReadDto(BaseModel):
    """Для списку постів -- зведена інфо."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    slug: str
    status: str
    published_at: Optional[datetime] = None
    created_at: datetime
    author_username: str
    comment_count: int = 0
    category_names: List[str] = []
    tag_names: List[str] = []


class PostDetailDto(BaseModel):
    """Для деталі посту -- розширена інфо з коментарями."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    slug: str
    body: str
    status: str
    published_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    allow_comments: bool
    author_username: str
    category_names: List[str] = []
    tag_names: List[str] = []
    comments: List[CommentReadDto] = []
