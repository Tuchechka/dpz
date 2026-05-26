# Архітектура: Strategy pattern

## Суть патерну (з GoF)

> "Define a family of algorithms, encapsulate each one, and make them
> interchangeable. Strategy lets the algorithm vary independently from
> clients that use it."

У нашому випадку "алгоритми" — це **способи виводу даних**:
консоль, файл, Kafka, Redis. Усі вони роблять одне й те саме
(пишуть `List[BudgetRecord]` кудись), але по-різному.

## Учасники патерну в нашому коді

| Роль (GoF) | Наш клас | Файл |
|---|---|---|
| **Strategy** (interface) | `IOutputStrategy` | `app/output/strategy.py` |
| **ConcreteStrategy** | `ConsoleOutputStrategy` | `app/output/console_strategy.py` |
| **ConcreteStrategy** | `FileOutputStrategy` | `app/output/file_strategy.py` |
| **ConcreteStrategy** | `KafkaOutputStrategy` | `app/output/kafka_strategy.py` |
| **ConcreteStrategy** | `RedisOutputStrategy` | `app/output/redis_strategy.py` |
| **Context** | `main.py` | `app/main.py` |
| **Factory** (вибір) | `OutputStrategyFactory` | `app/output/factory.py` |

## Відокремлення reader від writer

Вимога задачі:
> Код, який виводить рядки в консоль, має бути відділений від коду,
> що робить вичитку даних з файлу.

У нас:
- `app/reader/csv_reader.py` — **тільки читає** CSV, нічого не виводить
- `app/output/*.py` — **тільки пишуть** у сховище, нічого не читають з CSV

Зв'язок між ними — лише через **доменну модель** `BudgetRecord`.

## Перемикання БЕЗ змін у коді

Вимога задачі:
> ...дозволяти переключити вивід з консолі на запис у кафку та Redis з
> мінімальними змінами в коді (тобто без змін в самому коді, а лише з-за
> допомогою зміни в конфігураційних файлах).

Реалізація:

1. **Конфіг** (`config.yaml`):
   ```yaml
   output:
     strategy: console   # ← єдине, що змінюємо
   ```

2. **Фабрика** (`factory.py`) читає це поле і повертає конкретну реалізацію.

3. **main.py** не знає, яку саме реалізацію він отримав — працює лише з
   інтерфейсом `IOutputStrategy`.

Результат: щоб додати новий вивід (наприклад, у RabbitMQ або PostgreSQL),
треба:
1. Створити новий файл `app/output/rabbitmq_strategy.py` з класом, що реалізує `IOutputStrategy`
2. Додати один `if name == "rabbitmq": return ...` у фабрику

`main.py` чіпати **не потрібно**. Це і є відкритість для розширення (буква
**O** з SOLID — Open/Closed Principle).

## SOLID-принципи, реалізовані в коді

| Літера | Принцип | Як виконано |
|---|---|---|
| **S** | Single Responsibility | Кожна стратегія робить ОДНУ річ (один тип виводу) |
| **O** | Open / Closed | Новий вивід = новий файл; існуючі не чіпаємо |
| **L** | Liskov Substitution | Будь-яку стратегію можна підставити замість іншої |
| **I** | Interface Segregation | `IOutputStrategy` має лише `write()` — нічого зайвого |
| **D** | Dependency Inversion | `main.py` залежить від абстракції, не від реалізацій |

## Сценарій роботи

```
$ python -m app.main

[time] [INFO] [app.main] Loaded config. Output strategy: 'console'
[time] [INFO] [app.reader.csv_reader] Read 52 records from data/dallas_budget.csv
[time] [INFO] [app.main] Using strategy: ConsoleOutputStrategy
[time] [INFO] [app.output.console_strategy] === Writing 52 records to CONSOLE ===
[2023] Police Department | Salaries and Wages: budget=$234,500,000.00 actual=$231,245,000.00 variance=$-3,255,000.00
[2023] Police Department | Overtime Pay: budget=$18,500,000.00 actual=$21,340,000.00 variance=$2,840,000.00
...
[time] [INFO] [app.output.console_strategy] Done.
[time] [INFO] [app.main] All done.
```

Зміна `strategy: file` в `config.yaml` → той самий запуск, але дані летять у
`output/budget_records.jsonl` замість консолі.

## Чому Factory, а не switch у main?

Тому що Factory **інкапсулює знання про всі реалізації в одному місці**.
`main.py` не знає, що існують `KafkaOutputStrategy` чи `RedisOutputStrategy` —
він просить фабрику дати стратегію. Якщо потім фабрику переробити на
DI-контейнер, `main.py` все одно не зачепимо.
