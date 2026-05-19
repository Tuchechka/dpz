# documentation-lab-2

**Variant:** 10 — WordPress  
**Tech stack:** Python · FastAPI · SQLAlchemy 2.x · Pydantic v2 · SQLite

Lab 2 — серверна частина з трирівневою архітектурою.

## Архітектура

- **data_access** — ORM-моделі, репозиторії, CSV-читач
- **business_logic** — сервіси та DTO; залежить лише від інтерфейсів DAL
- **presentation** — FastAPI роутери (поки заглушки)

Зв'язок між шарами реалізовано через абстрактні базові класи (`abc.ABC`) 
і ін'єкцію залежностей через FastAPI `Depends`. Детальніше — у [ARCHITECTURE.md](./ARCHITECTURE.md).

## Запуск

```bash
python -m venv .venv
.venv\Scripts\activate на Windows
pip install -r requirements.txt

python -m generators.generate_csv  
uvicorn app.main:app --reload     
```

Після запуску:
- API: http://localhost:8000
- Документація: http://localhost:8000/docs
- БД: `wordpress.db` (SQLite, у корені)