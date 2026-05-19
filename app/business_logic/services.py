"""Реалізація сервісу seeding'у."""
from pathlib import Path
from typing import List, Optional

from app.business_logic.dto import (
    CategoryCreateDto,
    CommentCreateDto,
    CsvRowDto,
    MediaCreateDto,
    PostCreateDto,
    TagCreateDto,
    UserCreateDto,
)
from app.business_logic.interfaces import (
    IContentSeedingService,
    SeedingResult,
)
from app.common.logger import get_logger
from app.data_access.interfaces import (
    ICategoryRepository,
    ICommentRepository,
    ICsvReader,
    IMediaRepository,
    IPostRepository,
    ITagRepository,
    IUserRepository,
)
from app.data_access.models import Category, Media, Post, Tag, User

log = get_logger(__name__)


class ContentSeedingService(IContentSeedingService):
    """
    Заповнює БД даними з CSV.
    Залежить лише від інтерфейсів DAL -- не від конкретних реалізацій.
    """

    def __init__(
        self,
        csv_reader: ICsvReader,
        user_repo: IUserRepository,
        category_repo: ICategoryRepository,
        tag_repo: ITagRepository,
        media_repo: IMediaRepository,
        post_repo: IPostRepository,
        comment_repo: ICommentRepository,
    ):
        self._csv = csv_reader
        self._users = user_repo
        self._categories = category_repo
        self._tags = tag_repo
        self._media = media_repo
        self._posts = post_repo
        self._comments = comment_repo

    # ============================================================
    # Публічний API
    # ============================================================

    def seed(self, csv_path: Path) -> SeedingResult:
        log.info(f"Starting seed from {csv_path}")
        rows = self._csv.read(csv_path)

        for i, row in enumerate(rows, start=1):
            try:
                self._process_row(row)
            except Exception as e:
                log.error(f"Row {i} failed: {e}")

            if i % 100 == 0:
                log.info(f"Processed {i}/{len(rows)} rows")

        result = SeedingResult(
            users=self._users.count(),
            categories=self._categories.count(),
            tags=self._tags.count(),
            media=self._media.count(),
            posts=self._posts.count(),
            comments=self._comments.count(),
        )
        log.info(f"Seeding done: {result.model_dump()}")
        return result

    # ============================================================
    # Обробка одного рядка
    # ============================================================

    def _process_row(self, row: CsvRowDto) -> None:
        # 1. Автор (дедуплікація за email)
        user = self._get_or_create_user(row)

        # 2. Категорії та теги (дедуплікація за slug)
        categories = self._get_or_create_categories(row.categories)
        tags = self._get_or_create_tags(row.tags)

        # 3. Медіа (дедуплікація за url)
        media = self._get_or_create_media(row)

        # 4. Пост (дедуплікація за slug)
        post = self._get_or_create_post(row, author_id=user.id)

        # 5. Прив'язка M:N зв'язків
        self._attach_relationships(post, categories, tags, media)

        # 6. Коментар (якщо є)
        if row.comment_content:
            self._create_comment(row, post_id=post.id)

    # ============================================================
    # Helpers: find-or-create
    # ============================================================

    def _get_or_create_user(self, row: CsvRowDto) -> User:
        user = self._users.get_by_email(row.author_email)
        if user:
            return user
        return self._users.create(UserCreateDto(
            username=row.author_username,
            email=row.author_email,
            role=row.author_role,
        ))

    def _get_or_create_categories(self, raw: str) -> List[Category]:
        if not raw:
            return []
        result: List[Category] = []
        for name in raw.split("|"):
            name = name.strip()
            if not name:
                continue
            slug = self._slugify(name)
            cat = self._categories.get_by_slug(slug)
            if not cat:
                cat = self._categories.create(
                    CategoryCreateDto(name=name, slug=slug)
                )
            result.append(cat)
        return result

    def _get_or_create_tags(self, raw: str) -> List[Tag]:
        if not raw:
            return []
        result: List[Tag] = []
        for name in raw.split("|"):
            name = name.strip()
            if not name:
                continue
            slug = self._slugify(name)
            tag = self._tags.get_by_slug(slug)
            if not tag:
                tag = self._tags.create(TagCreateDto(name=name, slug=slug))
            result.append(tag)
        return result

    def _get_or_create_media(self, row: CsvRowDto) -> Optional[Media]:
        if not row.media_url or not row.media_filename:
            return None
        media = self._media.get_by_url(row.media_url)
        if media:
            return media
        return self._media.create(MediaCreateDto(
            filename=row.media_filename,
            url=row.media_url,
            mime_type=row.media_mime_type or "image/jpeg",
        ))

    def _get_or_create_post(self, row: CsvRowDto, author_id: int) -> Post:
        post = self._posts.get_by_slug(row.post_slug)
        if post:
            return post
        return self._posts.create(PostCreateDto(
            title=row.post_title,
            slug=row.post_slug,
            body=row.post_body,
            status=row.post_status,
            published_at=row.post_published_at,
            author_id=author_id,
        ))

    def _attach_relationships(
        self,
        post: Post,
        categories: List[Category],
        tags: List[Tag],
        media: Optional[Media],
    ) -> None:
        for c in categories:
            if c not in post.categories:
                post.categories.append(c)
        for t in tags:
            if t not in post.tags:
                post.tags.append(t)
        if media and media not in post.media:
            post.media.append(media)

    def _create_comment(self, row: CsvRowDto, post_id: int) -> None:
        self._comments.create(CommentCreateDto(
            author_name=row.comment_author_name or "Anonymous",
            author_email=row.comment_author_email or "anon@example.com",
            content=row.comment_content or "",
            post_id=post_id,
        ))

    # ============================================================
    # Utils
    # ============================================================

    @staticmethod
    def _slugify(name: str) -> str:
        """Перетворює 'Web Development' -> 'web-development'."""
        return (
            name.lower()
            .replace(" ", "-")
            .replace("_", "-")
            .replace("/", "-")
        )