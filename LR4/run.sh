#!/bin/bash

# Скрипт для запуска проекта LR4

set -e

echo "Запуск проекта LR4..."

# Проверяем наличие .env файла
if [ ! -f .env ]; then
    echo "Файл .env не найден!"
    exit 1
fi

echo "Файл .env найден"

# Запускаем docker-compose
echo "Запускаю PostgreSQL контейнер..."
docker-compose up -d postgres

# Ждем пока PostgreSQL будет готов
echo "Ожидание готовности PostgreSQL..."
sleep 5

# Проверяем наличие виртуального окружения
if [ ! -d "venv" ]; then
    echo "Создаю виртуальное окружение..."
    python3 -m venv venv
fi

# Активируем виртуальное окружение
echo "Активирую виртуальное окружение..."
source venv/bin/activate

# Устанавливаем зависимости
echo "Устанавливаю зависимости..."
pip install -q -r requirements.txt

# Загружаем переменные из .env
export $(grep -v '^#' .env | xargs)

# Обновляем DATABASE_URL для локального подключения (заменяем postgres на localhost)
if [[ "$DATABASE_URL" == *"postgres:5432"* ]]; then
    export DATABASE_URL="postgresql+psycopg2://postgres:pass@localhost:${POSTGRES_PORT:-5433}/labdb"
fi

# Выполняем миграции
echo "Выполняю миграции базы данных..."
alembic upgrade head

# Запускаем приложение
echo "Запускаю приложение..."
echo "Приложение будет доступно по адресу: http://localhost:8000"
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

