"""Pydantic DTOs для передачі даних між шарами."""
from __future__ import annotations
from datetime import datetime
from typing import Optional

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

    # Post fields
    post_external_id: str
    post_title: str
    post_slug: str
    post_body: str
    post_status: str = "published"
    post_published_at: Optional[datetime] = None

    # Author fields
    author_username: str
    author_email: str
    author_role: str = "author"

    # Categories and tags (pipe-separated, наприклад "Tech|Programming")
    categories: str = ""
    tags: str = ""

    # Media (одне медіа на рядок; необов'язково)
    media_filename: Optional[str] = None
    media_url: Optional[str] = None
    media_mime_type: Optional[str] = None

    # Comment (необов'язково)
    comment_author_name: Optional[str] = None
    comment_author_email: Optional[str] = None
    comment_content: Optional[str] = None


# ============================================================
# DTOs для створення сутностей у БД
# ============================================================

class UserCreateDto(BaseModel):
    username: str
    email: str
    password_hash: str = "stub_hash"  # реальне хешування -- не фокус лаби
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