from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.common.constants import DATABASE_URL

# check_same_thread=False — необхідно для SQLite + FastAPI
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False,  # True — побачиш кожен SQL у консолі (корисно для дебагу)
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """Спільна база для всіх ORM-моделей."""
    pass


def get_db():
    """
    FastAPI dependency: одна сесія на запит.
    Використовується через Depends(get_db).
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()