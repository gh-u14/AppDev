#!/bin/bash

# Скрипт для запуска проекта LR8

set -e

echo "Запуск проекта LR8..."

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
echo "Запускаю PostgreSQL, RabbitMQ и Redis контейнеры..."
docker-compose up -d postgres rabbitmq redis

# Ждем пока PostgreSQL, RabbitMQ и Redis будут готовы
echo "Ожидание готовности PostgreSQL, RabbitMQ и Redis..."
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

# Проверяем подключение к Redis
echo "Проверяю подключение к Redis..."
if python -c "import redis; r = redis.Redis(host='localhost', port=6379, db=0); r.ping(); print('Redis подключен успешно')" 2>/dev/null; then
    echo "✓ Redis подключен и готов к работе"
else
    echo "⚠ Предупреждение: Не удалось подключиться к Redis. Кэширование будет недоступно."
fi

# Запускаем приложение
echo ""
echo "Запускаю приложение..."
echo "Приложение будет доступно по адресу: http://localhost:8000"
echo "RabbitMQ Management UI доступен по адресу: http://localhost:15672 (guest/guest)"
echo "Redis доступен по адресу: localhost:6379"
echo ""
echo "ВАЖНО: Для обработки сообщений из RabbitMQ запустите в отдельном терминале:"
echo "  ./run_consumer.sh"
echo "  или"
echo "  source venv/bin/activate && python app/consumer_app.py"
echo ""
echo "Для проверки работы Redis можно запустить:"
echo "  python test_redis.py"
echo ""
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

