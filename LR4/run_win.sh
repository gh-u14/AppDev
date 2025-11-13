#!/bin/bash

# Скрипт для запуска проекта LR4 на Windows (Git Bash)

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
# Пробуем оба варианта команды (docker-compose или docker compose)
if ! docker-compose up -d postgres 2>/dev/null; then
    if ! docker compose up -d postgres 2>/dev/null; then
        echo "Ошибка при запуске PostgreSQL контейнера!"
        exit 1
    fi
fi

# Ждем пока PostgreSQL будет готов
echo "Ожидание готовности PostgreSQL..."
sleep 5

# Проверяем наличие виртуального окружения
if [ ! -d "venv" ]; then
    echo "Создаю виртуальное окружение..."
    python -m venv venv
fi

# Активируем виртуальное окружение (Windows путь в Git Bash)
echo "Активирую виртуальное окружение..."
source venv/Scripts/activate

# Устанавливаем зависимости
echo "Устанавливаю зависимости..."
# На Windows uvloop не поддерживается, поэтому устанавливаем без него
temp_requirements="requirements_temp_win.txt"
grep -v "^uvloop" requirements.txt > "$temp_requirements" || {
    echo "Ошибка при создании временного файла requirements!"
    exit 1
}

if ! pip install -q -r "$temp_requirements"; then
    echo "Ошибка при установке зависимостей!"
    rm -f "$temp_requirements"
    exit 1
fi
echo "Зависимости установлены успешно"

# Удаляем временный файл
rm -f "$temp_requirements"

# Загружаем переменные из .env
echo "Загружаю переменные окружения из .env..."
export $(grep -v '^#' .env | xargs)

# Обновляем DATABASE_URL для локального подключения (заменяем postgres на localhost)
if [[ "$DATABASE_URL" == *"postgres:5432"* ]]; then
    export DATABASE_URL="postgresql+psycopg2://postgres:pass@localhost:${POSTGRES_PORT:-5433}/labdb"
fi

# Выполняем миграции
echo "Выполняю миграции базы данных..."
if ! alembic upgrade head; then
    echo "Ошибка при выполнении миграций!"
    exit 1
fi
echo "Миграции выполнены успешно"

# Запускаем приложение
echo "Запускаю приложение..."
echo "Приложение будет доступно по адресу: http://localhost:8000"
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

