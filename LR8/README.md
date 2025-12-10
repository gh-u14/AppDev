# LR8 — Основы работы с планировщиками

## Быстрый запуск

### Автоматический запуск (рекомендуется)

После клонирования репозитория:

```bash
cd LR8
chmod +x run.sh
./run.sh
```

**После клонирования с GitHub:**
Файл `.env` уже включён в репозиторий (т.к. это учебный проект), поэтому просто выполняем `./run.sh`.

Скрипт автоматически:
- Запустит PostgreSQL, RabbitMQ и Redis в Docker контейнерах
- Создаст виртуальное окружение (если его нет)
- Установит зависимости
- Выполнит миграции базы данных (через Alembic)
- Запустит приложение

Приложение будет доступно по адресу: http://localhost:8000
RabbitMQ Management UI доступен по адресу: http://localhost:15672 (логин/пароль: guest/guest)

### Ручной запуск (без скрипта)

1. Поднимите PostgreSQL и RabbitMQ контейнеры:
   ```bash
   docker-compose up -d postgres rabbitmq
   ```
2. Создайте и активируйте виртуальное окружение:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
3. Установите зависимости:
   ```bash
   pip install -r requirements.txt
   ```
4. Выполните миграции:
   ```bash
   alembic upgrade head
   ```
5. Запустите приложение:
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

## API Endpoints

После запуска приложения доступны следующие endpoints:

### Пользователи
- `GET /users` - Получить список всех пользователей
- `GET /users/{user_id}` - Получить пользователя по ID
- `POST /users` - Создать нового пользователя
- `PUT /users/{user_id}` - Обновить пользователя
- `DELETE /users/{user_id}` - Удалить пользователя

### Продукты
- `GET /products` - Получить список всех продуктов (с пагинацией: ?count=10&page=1)
- `GET /products/{product_id}` - Получить продукт по ID

### Заказы
- `GET /orders` - Получить список всех заказов (с пагинацией: ?count=10&page=1)
- `GET /orders/{order_id}` - Получить заказ по ID

### Отчеты
- `GET /report?date=YYYY-MM-DD` - Получить отчет по заказам за конкретную дату

## RabbitMQ

Приложение использует RabbitMQ для асинхронной обработки сообщений через очереди.

### Краткая инструкция

1. **Запуск RabbitMQ**: `docker-compose up -d rabbitmq`
2. **Запуск Consumer**: `./run_consumer.sh` (в отдельном терминале)
3. **Отправка сообщений**: `python producer.py` или `python demo.py`
4. **Проверка очередей**: http://localhost:15672 (guest/guest)

### Очереди

- **`product`** - очередь для обработки операций с продуктами:
  - Создание продукта: `{"name": "Название", "price": 1000.0, "stock_quantity": 10}`
  - Обновление продукта: `{"id": "uuid", "name": "Новое название", "price": 1500.0}`
  - Отметка как закончившегося: `{"id": "uuid", "out_of_stock": true}`

- **`order`** - очередь для обработки операций с заказами:
  - Создание заказа: `{"user_id": "uuid", "address_id": "uuid", "status": "pending", "items": [{"product_id": "uuid", "quantity": 2}]}`
  - Обновление статуса: `{"id": "uuid", "status": "completed"}`

### Запуск Consumer

Для обработки сообщений из очередей необходимо запустить отдельный процесс в новом терминале:

**Вариант 1 (рекомендуется):** Используйте скрипт:
```bash
./run_consumer.sh
```

**Вариант 2:** Активируйте виртуальное окружение вручную:
```bash
source venv/bin/activate
python app/consumer_app.py
```

### Отправка сообщений (Producer)

Для отправки тестовых данных в очереди используйте скрипт:

```bash
python producer.py
```

Скрипт создаст 5 продуктов и 3 заказа через очереди RabbitMQ.

## TaskIQ Планировщик

Приложение использует TaskIQ для планирования и выполнения периодических задач (формирование отчетов по заказам).

### Запуск планировщика и worker

Для работы планировщика необходимо запустить **два процесса** в отдельных терминалах:

**Терминал 1 - Планировщик:**
```bash
./run_scheduler.sh
```

**Терминал 2 - Worker:**
```bash
./run_worker.sh
```

### Как это работает

1. **Планировщик** (`run_scheduler.sh`) - отправляет задачи в очередь RabbitMQ каждую минуту по расписанию cron (`*/1 * * * *`)
2. **Worker** (`run_worker.sh`) - обрабатывает задачи из очереди и формирует отчеты по заказам
3. Отчеты сохраняются в таблицу `reports` в базе данных
4. Получить отчеты можно через API: `GET /report?date=YYYY-MM-DD`

### Полная схема запуска

Для полной работы системы необходимо запустить **4 процесса**:

1. **Основное приложение** - `./run.sh`
2. **Consumer** - `./run_consumer.sh` - для обработки заказов из RabbitMQ
3. **Планировщик** - `./run_scheduler.sh` - для отправки задач
4. **Worker** - `./run_worker.sh` - для обработки задач

## Заполнение базы данных тестовыми данными

Для заполнения базы данных тестовыми данными используйте скрипт `fill_full_db.py`:

```bash
docker-compose up -d postgres
source venv/bin/activate
python fill_full_db.py
```

## Тестирование

В проекте настроен тестовый стенд на SQLite и написаны модульные и интеграционные тесты для репозиториев, сервисного слоя и HTTP‑эндпоинтов.

Запуск всех тестов:

```bash
pytest
```

Отдельные группы:
- Unit/интеграционные тесты репозиториев и сервисов:
  ```bash
  pytest tests/test_user_repository.py tests/test_product_repository.py tests/test_order_repository.py tests/test_user_service.py tests/test_order_service.py
  ```
- Тестирование REST API:
  ```bash
  pytest tests/test_user_routes.py
  ```

Дополнительно:
- Отчёт о покрытии: `pytest --cov=app --cov-report=html`

## Линтеры и форматеры

В проекте настроены инструменты для проверки качества кода: **pre-commit**, **pylint**, **black** и **isort**.

### Запуск проверок вручную

```bash
source venv/bin/activate
pre-commit run --all-files
```

### Автоматический запуск при коммитах (опционально)

Для запуска проверки автоматически при каждом `git commit`, установите pre-commit хуки:

```bash
source venv/bin/activate
pre-commit install
```

### Что проверяется

- **Black** — автоматическое форматирование кода согласно стандартам PEP 8
- **isort** — сортировка и организация импортов
- **pylint** — статический анализ кода на наличие ошибок и проблем стиля

Конфигурация инструментов находится в:
- `.pre-commit-config.yaml` — настройки pre-commit хуков
- `.pylintrc` — конфигурация pylint
- `pyproject.toml` — настройки black и isort
