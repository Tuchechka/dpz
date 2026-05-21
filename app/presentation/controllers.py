"""MVC Controllers -- CRUD для Post (Lab 3).

Це і є 'C' з MVC. Тут:
- маршрути HTTP-запитів обробляються
- викликається сервіс (бізнес-логіка)
- результат рендериться у Jinja2-шаблон (V) або робиться редірект
"""
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, Form, HTTPException, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

from app.business_logic.dto import PostCreateDto, PostUpdateDto
from app.business_logic.interfaces import IPostService
from app.business_logic.services import PostService
from app.common.logger import get_logger
from app.data_access.repositories import PostRepository, UserRepository
from app.database import get_db
from app.presentation.templates_setup import templates

log = get_logger(__name__)

router = APIRouter(prefix="/posts", tags=["posts"])


# ============================================================
# DI -- провайдер сервісу для роутерів
# ============================================================

def get_post_service(db: Session = Depends(get_db)) -> IPostService:
    """Збирає DI-граф для PostService на кожен запит."""
    return PostService(
        post_repo=PostRepository(db),
        user_repo=UserRepository(db),
        session=db,
    )


# ============================================================
# READ actions
# ============================================================

@router.get("", response_class=HTMLResponse)
def list_posts(
    request: Request,
    service: IPostService = Depends(get_post_service),
    limit: int = 50,
    offset: int = 0,
):
    """GET /posts -- список постів."""
    posts = service.list_posts(limit=limit, offset=offset)
    total = service.count_posts()
    return templates.TemplateResponse(
        request,
        "posts/list.html",
        {"posts": posts, "total": total},
    )


@router.get("/new", response_class=HTMLResponse)
def new_post_form(request: Request):
    """GET /posts/new -- порожня форма створення."""
    return templates.TemplateResponse(
        request,
        "posts/form.html",
        {"post": None, "action": "/posts/new", "mode": "create"},
    )


@router.get("/{post_id}", response_class=HTMLResponse)
def view_post(
    post_id: int,
    request: Request,
    service: IPostService = Depends(get_post_service),
):
    """GET /posts/{id} -- деталі посту."""
    post = service.get_post(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return templates.TemplateResponse(
        request,
        "posts/detail.html",
        {"post": post},
    )


@router.get("/{post_id}/edit", response_class=HTMLResponse)
def edit_post_form(
    post_id: int,
    request: Request,
    service: IPostService = Depends(get_post_service),
):
    """GET /posts/{id}/edit -- форма редагування."""
    post = service.get_post(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return templates.TemplateResponse(
        request,
        "posts/form.html",
        {"post": post, "action": f"/posts/{post_id}/edit", "mode": "edit"},
    )


@router.get("/{post_id}/delete", response_class=HTMLResponse)
def confirm_delete(
    post_id: int,
    request: Request,
    service: IPostService = Depends(get_post_service),
):
    """GET /posts/{id}/delete -- сторінка підтвердження."""
    post = service.get_post(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return templates.TemplateResponse(
        request,
        "posts/confirm_delete.html",
        {"post": post},
    )


# ============================================================
# WRITE actions
# ============================================================

@router.post("/new")
def create_post(
    db: Session = Depends(get_db),
    title: str = Form(...),
    slug: str = Form(...),
    body: str = Form(...),
    status_field: str = Form("draft", alias="status"),
    allow_comments: Optional[str] = Form(None),
    published_at: Optional[str] = Form(None),
):
    """POST /posts/new -- створення поста з HTML-форми."""
    service = PostService(
        post_repo=PostRepository(db),
        user_repo=UserRepository(db),
        session=db,
    )

    # Дефолтний автор -- перший з БД (для простоти, без auth)
    user_repo = UserRepository(db)
    default_user = user_repo.get_first()
    if not default_user:
        raise HTTPException(
            status_code=500,
            detail="No users in DB. Run generators/generate_csv.py first.",
        )

    dto = PostCreateDto(
        title=title,
        slug=slug,
        body=body,
        status=status_field,
        allow_comments=bool(allow_comments),
        published_at=_parse_datetime(published_at),
        author_id=default_user.id,
    )
    post_id = service.create_post(dto)
    return RedirectResponse(
        url=f"/posts/{post_id}",
        status_code=status.HTTP_303_SEE_OTHER,
    )


@router.post("/{post_id}/edit")
def update_post(
    post_id: int,
    service: IPostService = Depends(get_post_service),
    title: str = Form(...),
    slug: str = Form(...),
    body: str = Form(...),
    status_field: str = Form("draft", alias="status"),
    allow_comments: Optional[str] = Form(None),
    published_at: Optional[str] = Form(None),
):
    """POST /posts/{id}/edit -- збереження змін."""
    dto = PostUpdateDto(
        title=title,
        slug=slug,
        body=body,
        status=status_field,
        allow_comments=bool(allow_comments),
        published_at=_parse_datetime(published_at),
    )
    ok = service.update_post(post_id, dto)
    if not ok:
        raise HTTPException(status_code=404, detail="Post not found")
    return RedirectResponse(
        url=f"/posts/{post_id}",
        status_code=status.HTTP_303_SEE_OTHER,
    )


@router.post("/{post_id}/delete")
def delete_post(
    post_id: int,
    service: IPostService = Depends(get_post_service),
):
    """POST /posts/{id}/delete -- видалення."""
    ok = service.delete_post(post_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Post not found")
    return RedirectResponse(
        url="/posts",
        status_code=status.HTTP_303_SEE_OTHER,
    )


# ============================================================
# Helpers
# ============================================================

def _parse_datetime(value: Optional[str]) -> Optional[datetime]:
    """Парсить datetime з HTML-форми (<input type='datetime-local'>)."""
    if not value:
        return None
    try:
        return datetime.fromisoformat(value)
    except (ValueError, TypeError):
        return None
