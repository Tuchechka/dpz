"""Utility routes (health check etc). CRUD-роутери для постів -- у controllers.py."""
from fastapi import APIRouter, status

router = APIRouter()


@router.get("/health", status_code=status.HTTP_200_OK)
def health_check():
    """Перевірка, що сервер живий."""
    return {"status": "ok"}
