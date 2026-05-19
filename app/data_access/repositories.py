"""SQLAlchemy-реалізації репозиторіїв."""
from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.business_logic.dto import (
    CategoryCreateDto,
    CommentCreateDto,
    MediaCreateDto,
    PageCreateDto,
    PostCreateDto,
    TagCreateDto,
    UserCreateDto,
)
from app.data_access.interfaces import (
    ICategoryRepository,
    ICommentRepository,
    IMediaRepository,
    IPageRepository,
    IPostRepository,
    ITagRepository,
    IUserRepository,
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
# User
# ============================================================

class UserRepository(IUserRepository):
    def __init__(self, session: Session):
        self._session = session

    def get_by_email(self, email: str) -> Optional[User]:
        return self._session.execute(
            select(User).where(User.email == email)
        ).scalar_one_or_none()

    def create(self, dto: UserCreateDto) -> User:
        user = User(**dto.model_dump())
        self._session.add(user)
        self._session.flush()  # отримати user.id без commit
        return user

    def count(self) -> int:
        return self._session.execute(
            select(func.count()).select_from(User)
        ).scalar() or 0


# ============================================================
# Category
# ============================================================

class CategoryRepository(ICategoryRepository):
    def __init__(self, session: Session):
        self._session = session

    def get_by_slug(self, slug: str) -> Optional[Category]:
        return self._session.execute(
            select(Category).where(Category.slug == slug)
        ).scalar_one_or_none()

    def create(self, dto: CategoryCreateDto) -> Category:
        category = Category(**dto.model_dump())
        self._session.add(category)
        self._session.flush()
        return category

    def count(self) -> int:
        return self._session.execute(
            select(func.count()).select_from(Category)
        ).scalar() or 0


# ============================================================
# Tag
# ============================================================

class TagRepository(ITagRepository):
    def __init__(self, session: Session):
        self._session = session

    def get_by_slug(self, slug: str) -> Optional[Tag]:
        return self._session.execute(
            select(Tag).where(Tag.slug == slug)
        ).scalar_one_or_none()

    def create(self, dto: TagCreateDto) -> Tag:
        tag = Tag(**dto.model_dump())
        self._session.add(tag)
        self._session.flush()
        return tag

    def count(self) -> int:
        return self._session.execute(
            select(func.count()).select_from(Tag)
        ).scalar() or 0


# ============================================================
# Media
# ============================================================

class MediaRepository(IMediaRepository):
    def __init__(self, session: Session):
        self._session = session

    def get_by_url(self, url: str) -> Optional[Media]:
        return self._session.execute(
            select(Media).where(Media.url == url)
        ).scalar_one_or_none()

    def create(self, dto: MediaCreateDto) -> Media:
        media = Media(**dto.model_dump())
        self._session.add(media)
        self._session.flush()
        return media

    def count(self) -> int:
        return self._session.execute(
            select(func.count()).select_from(Media)
        ).scalar() or 0


# ============================================================
# Post
# ============================================================

class PostRepository(IPostRepository):
    def __init__(self, session: Session):
        self._session = session

    def get_by_slug(self, slug: str) -> Optional[Post]:
        return self._session.execute(
            select(Post).where(Post.slug == slug)
        ).scalar_one_or_none()

    def create(self, dto: PostCreateDto) -> Post:
        post = Post(**dto.model_dump())
        self._session.add(post)
        self._session.flush()
        return post

    def count(self) -> int:
        return self._session.execute(
            select(func.count()).select_from(Post)
        ).scalar() or 0


# ============================================================
# Page
# ============================================================

class PageRepository(IPageRepository):
    def __init__(self, session: Session):
        self._session = session

    def get_by_slug(self, slug: str) -> Optional[Page]:
        return self._session.execute(
            select(Page).where(Page.slug == slug)
        ).scalar_one_or_none()

    def create(self, dto: PageCreateDto) -> Page:
        page = Page(**dto.model_dump())
        self._session.add(page)
        self._session.flush()
        return page

    def count(self) -> int:
        return self._session.execute(
            select(func.count()).select_from(Page)
        ).scalar() or 0


# ============================================================
# Comment
# ============================================================

class CommentRepository(ICommentRepository):
    def __init__(self, session: Session):
        self._session = session

    def create(self, dto: CommentCreateDto) -> Comment:
        comment = Comment(**dto.model_dump())
        self._session.add(comment)
        self._session.flush()
        return comment

    def count(self) -> int:
        return self._session.execute(
            select(func.count()).select_from(Comment)
        ).scalar() or 0