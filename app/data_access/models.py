"""SQLAlchemy ORM-моделі за Class Diagram з Lab 1."""
from __future__ import annotations
from datetime import datetime
from typing import List, Optional

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Table,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


# ============================================================
# Зв'язуючі таблиці для M:N — без власних ORM-класів
# ============================================================

post_categories = Table(
    "post_categories",
    Base.metadata,
    Column("post_id", ForeignKey("content.id", ondelete="CASCADE"), primary_key=True),
    Column("category_id", ForeignKey("categories.id", ondelete="CASCADE"), primary_key=True),
)

post_tags = Table(
    "post_tags",
    Base.metadata,
    Column("post_id", ForeignKey("content.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True),
)

content_media = Table(
    "content_media",
    Base.metadata,
    Column("content_id", ForeignKey("content.id", ondelete="CASCADE"), primary_key=True),
    Column("media_id", ForeignKey("media.id", ondelete="CASCADE"), primary_key=True),
)


# ============================================================
# User
# ============================================================

class User(Base):
    """Користувач системи. Автор контенту."""
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(32), default="author")

    # one-to-many: один автор -- багато контенту
    contents: Mapped[List["Content"]] = relationship(back_populates="author")

    def __repr__(self) -> str:
        return f"<User {self.username}>"


# ============================================================
# Content -- абстрактна база для Post і Page (STI)
# ============================================================

class Content(Base):
    """
    Базовий клас для Post і Page.
    Single Table Inheritance: одна таблиця 'content' з discriminator 'type'.
    """
    __tablename__ = "content"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="draft")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # FK на автора (асоціація User-Content)
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    author: Mapped["User"] = relationship(back_populates="contents")

    # M:N з Media (доступно і для Post, і для Page)
    media: Mapped[List["Media"]] = relationship(
        secondary=content_media, back_populates="contents"
    )

    # discriminator-колонка для STI
    type: Mapped[str] = mapped_column(String(16))

    __mapper_args__ = {
        "polymorphic_identity": "content",
        "polymorphic_on": "type",
    }

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} '{self.title}'>"


# ============================================================
# Post extends Content
# ============================================================

class Post(Content):
    """Запис у блог. Має дату публікації, коментарі, категорії, теги."""

    published_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    allow_comments: Mapped[Optional[bool]] = mapped_column(Boolean, default=True)

    # композиція: видалили пост -- каскадно видаляються коментарі
    comments: Mapped[List["Comment"]] = relationship(
        back_populates="post",
        cascade="all, delete-orphan",
    )

    # M:N з Category
    categories: Mapped[List["Category"]] = relationship(
        secondary=post_categories, back_populates="posts"
    )

    # M:N з Tag
    tags: Mapped[List["Tag"]] = relationship(
        secondary=post_tags, back_populates="posts"
    )

    __mapper_args__ = {
        "polymorphic_identity": "post",
    }


# ============================================================
# Page extends Content
# ============================================================

class Page(Content):
    """Статична сторінка (About, Contact). Має ієрархію через parent_page_id."""

    menu_order: Mapped[Optional[int]] = mapped_column(Integer, default=0)
    parent_page_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("content.id"), nullable=True
    )

    __mapper_args__ = {
        "polymorphic_identity": "page",
    }


# ============================================================
# Comment -- композиція з Post
# ============================================================

class Comment(Base):
    """Коментар до посту. Видалили пост -- каскадно видаляється."""
    __tablename__ = "comments"

    id: Mapped[int] = mapped_column(primary_key=True)
    author_name: Mapped[str] = mapped_column(String(128), nullable=False)
    author_email: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    approved: Mapped[bool] = mapped_column(Boolean, default=False)

    post_id: Mapped[int] = mapped_column(ForeignKey("content.id", ondelete="CASCADE"))
    post: Mapped["Post"] = relationship(back_populates="comments")

    def __repr__(self) -> str:
        return f"<Comment by {self.author_name}>"


# ============================================================
# Category -- M:N з Post
# ============================================================

class Category(Base):
    """Категорія постів."""
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    slug: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)

    posts: Mapped[List["Post"]] = relationship(
        secondary=post_categories, back_populates="categories"
    )

    def __repr__(self) -> str:
        return f"<Category {self.name}>"


# ============================================================
# Tag -- M:N з Post
# ============================================================

class Tag(Base):
    """Тег постів."""
    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    slug: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)

    posts: Mapped[List["Post"]] = relationship(
        secondary=post_tags, back_populates="tags"
    )

    def __repr__(self) -> str:
        return f"<Tag {self.name}>"


# ============================================================
# Media -- M:N з Content (Post і Page)
# ============================================================

class Media(Base):
    """Зображення/відео файли. Можуть бути в постах і сторінках."""
    __tablename__ = "media"

    id: Mapped[int] = mapped_column(primary_key=True)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    url: Mapped[str] = mapped_column(String(512), unique=True, nullable=False)
    mime_type: Mapped[str] = mapped_column(String(64), nullable=False)
    size: Mapped[int] = mapped_column(Integer, default=0)
    uploaded_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    contents: Mapped[List["Content"]] = relationship(
        secondary=content_media, back_populates="media"
    )

    def __repr__(self) -> str:
        return f"<Media {self.filename}>"