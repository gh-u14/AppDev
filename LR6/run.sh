#!/bin/bash

# Скрипт для запуска проекта LR6

set -e

echo "Запуск проекта LR6..."

# Проверяем наличие .env файла
if [ ! -f .env ]; then
    echo "Файл .env не найден!"
    exit 1
fi

echo "Файл .env найден"

# Проверяем, что Docker запущен
if ! docker info > /dev/null 2>&1; then
    echo "ОШИБКА: Docker daemon не запущен!"
    echo "Пожалуйста, запустите Docker Desktop или Docker daemon и попробуйте снова."
    exit 1
fi

# Запускаем docker-compose
echo "Запускаю PostgreSQL и RabbitMQ контейнеры..."
docker-compose up -d postgres rabbitmq

# Ждем пока PostgreSQL и RabbitMQ будут готовы
echo "Ожидание готовности PostgreSQL и RabbitMQ..."
sleep 2

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
echo "RabbitMQ Management UI доступен по адресу: http://localhost:15672 (guest/guest)"
echo ""
echo "ВАЖНО: Для обработки сообщений из RabbitMQ запустите в отдельном терминале:"
echo "  ./run_consumer.sh"
echo "  или"
echo "  source venv/bin/activate && python app/consumer_app.py"
echo ""
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

