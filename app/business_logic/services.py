"""Реалізації сервісів бізнес-логіки."""
from pathlib import Path
from typing import List, Optional

from sqlalchemy.orm import Session

from app.business_logic.dto import (
    CategoryCreateDto,
    CommentCreateDto,
    CommentReadDto,
    CsvRowDto,
    MediaCreateDto,
    PostCreateDto,
    PostDetailDto,
    PostReadDto,
    PostUpdateDto,
    TagCreateDto,
    UserCreateDto,
)
from app.business_logic.interfaces import (
    IContentSeedingService,
    IPostService,
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


# ============================================================
# ContentSeedingService (з Lab 2 -- без змін)
# ============================================================

class ContentSeedingService(IContentSeedingService):
    """Заповнює БД даними з CSV. Залежить лише від інтерфейсів DAL."""

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

    def _process_row(self, row: CsvRowDto) -> None:
        user = self._get_or_create_user(row)
        categories = self._get_or_create_categories(row.categories)
        tags = self._get_or_create_tags(row.tags)
        media = self._get_or_create_media(row)
        post = self._get_or_create_post(row, author_id=user.id)
        self._attach_relationships(post, categories, tags, media)
        if row.comment_content:
            self._create_comment(row, post_id=post.id)

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

    @staticmethod
    def _slugify(name: str) -> str:
        return (
            name.lower()
            .replace(" ", "-")
            .replace("_", "-")
            .replace("/", "-")
        )


# ============================================================
# PostService -- CRUD для постів (Lab 3)
# ============================================================

class PostService(IPostService):
    """Сервіс CRUD-операцій з постами для MVC controllers."""

    def __init__(
        self,
        post_repo: IPostRepository,
        user_repo: IUserRepository,
        session: Session,
    ):
        self._posts = post_repo
        self._users = user_repo
        self._session = session

    # ---- READ ----

    def list_posts(self, limit: int = 50, offset: int = 0) -> List[PostReadDto]:
        posts = self._posts.list_all(limit=limit, offset=offset)
        return [self._to_read_dto(p) for p in posts]

    def get_post(self, post_id: int) -> Optional[PostDetailDto]:
        post = self._posts.get_by_id(post_id)
        if not post:
            return None
        return self._to_detail_dto(post)

    def count_posts(self) -> int:
        return self._posts.count()

    # ---- WRITE ----

    def create_post(self, dto: PostCreateDto) -> int:
        post = self._posts.create(dto)
        self._session.commit()
        log.info(f"Created post id={post.id}, slug={post.slug}")
        return post.id

    def update_post(self, post_id: int, dto: PostUpdateDto) -> bool:
        post = self._posts.get_by_id(post_id)
        if not post:
            return False
        self._posts.update(post, dto)
        self._session.commit()
        log.info(f"Updated post id={post_id}")
        return True

    def delete_post(self, post_id: int) -> bool:
        post = self._posts.get_by_id(post_id)
        if not post:
            return False
        self._posts.delete(post)
        self._session.commit()
        log.info(f"Deleted post id={post_id}")
        return True

    # ---- mapping helpers (ORM -> DTO) ----

    def _to_read_dto(self, post: Post) -> PostReadDto:
        return PostReadDto(
            id=post.id,
            title=post.title,
            slug=post.slug,
            status=post.status,
            published_at=post.published_at,
            created_at=post.created_at,
            author_username=post.author.username if post.author else "(deleted)",
            comment_count=len(post.comments),
            category_names=[c.name for c in post.categories],
            tag_names=[t.name for t in post.tags],
        )

    def _to_detail_dto(self, post: Post) -> PostDetailDto:
        return PostDetailDto(
            id=post.id,
            title=post.title,
            slug=post.slug,
            body=post.body,
            status=post.status,
            published_at=post.published_at,
            created_at=post.created_at,
            updated_at=post.updated_at,
            allow_comments=post.allow_comments,
            author_username=post.author.username if post.author else "(deleted)",
            category_names=[c.name for c in post.categories],
            tag_names=[t.name for t in post.tags],
            comments=[
                CommentReadDto(
                    id=c.id,
                    author_name=c.author_name,
                    author_email=c.author_email,
                    content=c.content,
                    created_at=c.created_at,
                    approved=c.approved,
                )
                for c in sorted(
                    post.comments,
                    key=lambda c: c.created_at,
                    reverse=True,
                )
            ],
        )
