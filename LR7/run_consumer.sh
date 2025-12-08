#!/bin/bash

# Скрипт для запуска RabbitMQ consumer

set -e

echo "Запуск RabbitMQ Consumer..."

# Проверяем наличие виртуального окружения
if [ ! -d "venv" ]; then
    echo "ОШИБКА: Виртуальное окружение не найдено!"
    echo "Сначала запустите ./run.sh для создания окружения и установки зависимостей."
    exit 1
fi

# Активируем виртуальное окружение
echo "Активирую виртуальное окружение..."
source venv/bin/activate

# Запускаем consumer
echo "Запускаю RabbitMQ Consumer..."
echo "Consumer будет обрабатывать сообщения из очередей 'order' и 'product'"
echo ""
# Устанавливаем PYTHONPATH на текущую директорию для корректного импорта модулей
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
python -m app.consumer_app

