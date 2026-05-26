# Архітектура

## Три рівні

### 1. Data Access Layer (`app/data_access/`)

Відповідальність: робота з джерелами даних (БД та CSV).

- `models.py` — SQLAlchemy ORM-моделі за Class Diagram з Lab 1
- `interfaces.py` — абстрактні базові класи репозиторіїв (`IUserRepository`, 
  `IPostRepository`, `ICsvReader`, ...)
- `repositories.py` — реалізації через SQLAlchemy
- `csv_reader.py` — реалізація читача CSV

### 2. Business Logic Layer (`app/business_logic/`)

Відповідальність: бізнес-операції. Не знає про SQLAlchemy чи CSV — 
працює тільки з інтерфейсами DAL.

- `interfaces.py` — `IContentSeedingService`
- `services.py` — `ContentSeedingService`: читає CSV, дедуплікує, зберігає
- `dto.py` — Pydantic-схеми для передачі даних між шарами

### 3. Presentation Layer (`app/presentation/`)

Відповідальність: HTTP-інтерфейс. На цьому етапі — лише заглушки, 
повертають 501 Not Implemented.

- `routers.py` — FastAPI роутери

## Dependency Injection

Конкретні реалізації не створюються всередині залежних класів — 
вони підставляються через конструктор. Це робить код тестованим 
і дозволяє замінити реалізацію без зміни залежних класів 
(принцип Dependency Inversion з SOLID).

```python
# Погано — жорсткий зв'язок з реалізацією:
class ContentSeedingService:
    def __init__(self):
        self._csv = CsvReader()                
        self._users = SqlAlchemyUserRepo()     

# Добре — залежність від абстракції:
class ContentSeedingService:
    def __init__(self, csv: ICsvReader, users: IUserRepository):
        self._csv = csv
        self._users = users
```

Реальні залежності збираються у `app/main.py` і передаються в роутери через `Depends`.

## CSV-формат

Денормалізована плоска таблиця. Кожен рядок описує "повний контекст 
однієї одиниці контенту" — пост + автор + категорії + теги + медіа + коментар.

Дублікати одних і тих самих сутностей в різних рядках допустимі — 
DAL дедуплікує за natural key (email, slug, url).