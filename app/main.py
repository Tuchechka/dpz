"""FastAPI entry point: DI wiring + startup seeding."""
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.business_logic.services import ContentSeedingService
from app.common.constants import CSV_FILE_PATH
from app.common.logger import get_logger
from app.data_access import models  # noqa: F401 -- щоб таблиці зареєструвались
from app.data_access.csv_reader import CsvReader
from app.data_access.repositories import (
    CategoryRepository,
    CommentRepository,
    MediaRepository,
    PostRepository,
    TagRepository,
    UserRepository,
)
from app.database import Base, SessionLocal, engine
from app.presentation.routers import router

log = get_logger(__name__)


# ============================================================
# Seeding -- збирання DI-графа і запуск
# ============================================================

def _seed_database() -> None:
    """Інстанціює всі реалізації, передає їх у сервіс, викликає seed."""
    if not CSV_FILE_PATH.exists():
        log.warning(f"CSV not found: {CSV_FILE_PATH}")
        log.warning("Run: python -m generators.generate_csv")
        return

    db = SessionLocal()
    try:
        # === DI: підставляємо конкретні реалізації в інтерфейси ===
        service = ContentSeedingService(
            csv_reader=CsvReader(),
            user_repo=UserRepository(db),
            category_repo=CategoryRepository(db),
            tag_repo=TagRepository(db),
            media_repo=MediaRepository(db),
            post_repo=PostRepository(db),
            comment_repo=CommentRepository(db),
        )
        # === Викликаємо бізнес-операцію ===
        result = service.seed(CSV_FILE_PATH)
        db.commit()
        log.info(f"Seed completed: {result.model_dump()}")
    except Exception as e:
        db.rollback()
        log.error(f"Seed failed: {e}")
        raise
    finally:
        db.close()


# ============================================================
# Lifespan -- запускається при старті/зупинці серверу
# ============================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    log.info("Starting up...")

    # 1. Створюємо таблиці (якщо їх немає)
    Base.metadata.create_all(engine)

    # 2. Заповнюємо БД -- але лише якщо ще не заповнена
    db = SessionLocal()
    try:
        existing = UserRepository(db).count()
    finally:
        db.close()

    if existing == 0:
        log.info("Database is empty, running seed...")
        _seed_database()
    else:
        log.info(f"Database already has {existing} users, skipping seed")

    yield
    log.info("Shutting down...")


# ============================================================
# FastAPI app
# ============================================================

app = FastAPI(
    title="WordPress Documentation Lab",
    description="Variant 10 -- Lab 2 (трирівнева архітектура з DI)",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(router)