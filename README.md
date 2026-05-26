# documentation-lab-4

**Variant:** 10 — City of Dallas Expenses Budget vs Actual
**Dataset:** [dallasopendata.com/.../nr4f-efb3](https://www.dallasopendata.com/Budget-Finance/CoD-Expenses-Budget-vs-Actual/nr4f-efb3)
**Pattern:** GoF Strategy
**Tech stack:** Python · Pydantic · PyYAML · kafka-python · redis-py

Реалізація патерну **Strategy** для виводу даних із датасету у різні сховища
(консоль / файл / Kafka / Redis) з перемиканням лише через конфіг.

## Структура

```
documentation-lab-4/
├── config.yaml                       ← єдине місце вибору стратегії
├── data/dallas_budget.csv            ← датасет
├── docker-compose.yml                ← Kafka + Redis для демо
└── app/
    ├── main.py                       ← entry point
    ├── config.py                     ← Pydantic-валідація YAML
    ├── models.py                     ← BudgetRecord
    ├── logger.py
    ├── reader/
    │   └── csv_reader.py             ← окремий клас читання (вимога задачі)
    └── output/
        ├── strategy.py               ← IOutputStrategy (контракт)
        ├── console_strategy.py
        ├── file_strategy.py
        ├── kafka_strategy.py
        ├── redis_strategy.py
        └── factory.py                ← обирає реалізацію за конфігом
```

## Як працює Strategy у нашому коді

```
main.py:
   config = load_config()
   reader = CsvBudgetReader(...)
   records = reader.read()
   strategy = OutputStrategyFactory.create(config.output)   ← Console / File / Kafka / Redis
   strategy.write(records)
```

`main.py` залежить ЛИШЕ від інтерфейсу `IOutputStrategy`. Конкретна реалізація
підставляється фабрикою на основі поля `output.strategy` у `config.yaml`.

## Запуск

```bash
python -m venv .venv
.venv\Scripts\Activate.ps1            # Windows
# або: source .venv/bin/activate     # Linux/Mac

pip install -r requirements.txt
python -m app.main
```

Стандартно виводить у консоль (`strategy: console` в `config.yaml`).

## Перемикання стратегій

Відредагуй `config.yaml`:

```yaml
output:
  strategy: console   # ← поміняй на: file | kafka | redis
```

Перезапусти `python -m app.main` — **в коді нічого не міняй**.

### Для Kafka / Redis потрібен Docker

```bash
docker-compose up -d
python -m app.main      # тепер з config.yaml strategy: kafka або redis
```

Перевірка результатів:

```bash
# Redis -- подивитись усі ключі
docker exec lab4-redis redis-cli KEYS 'budget:*' | head

# Kafka -- прочитати повідомлення з топіку
docker exec lab4-kafka kafka-console-consumer.sh \
  --bootstrap-server localhost:9092 \
  --topic dallas-budget --from-beginning --max-messages 5
```

## Опційно: оновити датасет з API

```bash
python scripts/fetch_data.py
```
