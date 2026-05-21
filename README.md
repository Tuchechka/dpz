# documentation-lab-3

**Variant:** 10 — WordPress  
**Pattern:** MVC over the 3-layer architecture from Lab 2  
**Tech stack:** Python · FastAPI · SQLAlchemy 2.x · Pydantic v2 · Jinja2 · Bootstrap 5 · SQLite

Lab 3 — веб-додаток з MVC-структурою, що реалізує CRUD на сутності **Post**.

## MVC у проекті

- **Model** — ORM-моделі (`app/data_access/models.py`) + сервіси (`app/business_logic/services.py`)
- **View** — Jinja2-шаблони (`app/presentation/templates/`)
- **Controller** — FastAPI-роутер (`app/presentation/controllers.py`)

Архітектура трирівнева (з Lab 2): Data Access → Business Logic → Presentation,
з інверсією залежностей через інтерфейси (ABC) і DI у `main.py`.

## Основна сутність — Post

CRUD-операції доступні через UI:

| URL | Метод | Дія |
|---|---|---|
| `/posts` | GET | Список постів |
| `/posts/{id}` | GET | Перегляд посту |
| `/posts/new` | GET | Форма створення |
| `/posts/new` | POST | Створення |
| `/posts/{id}/edit` | GET | Форма редагування |
| `/posts/{id}/edit` | POST | Збереження змін |
| `/posts/{id}/delete` | GET | Підтвердження видалення |
| `/posts/{id}/delete` | POST | Видалення |

## Запуск

```bash
python -m venv .venv
.venv\Scripts\Activate.ps1            # Windows
# або: source .venv/bin/activate     # Linux/Mac

pip install -r requirements.txt

python -m generators.generate_csv     # створює wordpress_data.csv
uvicorn app.main:app --reload         # сервер + сід БД
```

Відкрити: http://localhost:8000/posts
