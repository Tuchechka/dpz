
from fastapi import APIRouter, HTTPException, status

router = APIRouter()


def _not_implemented():
    """Уніфікована заглушка для всіх endpoint'ів."""
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Not implemented in Lab 2 (presentation layer is interfaces-only)",
    )


# ============================================================
# Health -- працює, потрібен для перевірки що сервер живий
# ============================================================

@router.get("/health", status_code=status.HTTP_200_OK)
def health_check():
    """Перевірка, що сервер живий."""
    return {"status": "ok"}


# ============================================================
# Posts
# ============================================================

@router.get("/posts")
def list_posts():
    """Повернути список постів."""
    _not_implemented()


@router.get("/posts/{slug}")
def get_post(slug: str):
    """Повернути один пост за slug."""
    _not_implemented()


@router.post("/posts")
def create_post():
    """Створити новий пост."""
    _not_implemented()


# ============================================================
# Comments
# ============================================================

@router.get("/posts/{post_id}/comments")
def list_comments(post_id: int):
    """Повернути коментарі поста."""
    _not_implemented()


@router.post("/posts/{post_id}/comments")
def create_comment(post_id: int):
    """Додати коментар до поста."""
    _not_implemented()


# ============================================================
# Categories / Tags / Media
# ============================================================

@router.get("/categories")
def list_categories():
    """Повернути всі категорії."""
    _not_implemented()


@router.get("/tags")
def list_tags():
    """Повернути всі теги."""
    _not_implemented()


@router.get("/media")
def list_media():
    """Повернути всі медіа-файли."""
    _not_implemented()


# ============================================================
# Users
# ============================================================

@router.get("/users")
def list_users():
    """Повернути всіх користувачів."""
    _not_implemented()


@router.get("/users/{user_id}")
def get_user(user_id: int):
    """Повернути одного користувача."""
    _not_implemented()