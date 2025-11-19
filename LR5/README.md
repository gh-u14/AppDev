# LR5 — Тестирование бекенд‑приложения на Litestar

## Быстрый запуск

### Автоматический запуск (рекомендуется)

После клонирования репозитория:

```bash
cd LR5
chmod +x run.sh
./run.sh
```

**После клонирования с GitHub:**
Файл `.env` уже включён в репозиторий (т.к. это учебный проект), поэтому просто выполняем `./run.sh`.

Скрипт автоматически:
- Запустит PostgreSQL в Docker контейнере
- Создаст виртуальное окружение (если его нет)
- Установит зависимости
- Выполнит миграции базы данных (через Alembic)
- Запустит приложение

Приложение будет доступно по адресу: http://localhost:8000

### Ручной запуск (без скрипта)

1. Поднимите PostgreSQL контейнер:
   ```bash
   docker-compose up -d postgres
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

- `GET /users` - Получить список всех пользователей
- `GET /users/{user_id}` - Получить пользователя по ID
- `POST /users` - Создать нового пользователя
- `PUT /users/{user_id}` - Обновить пользователя
- `DELETE /users/{user_id}` - Удалить пользователя

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
