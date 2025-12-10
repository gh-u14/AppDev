#!/bin/bash

# Скрипт для запуска TaskIQ worker

echo "Запуск TaskIQ Worker..."

# Активируем виртуальное окружение, если оно существует
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Устанавливаем PYTHONPATH на текущую директорию для корректного импорта модулей
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Запускаем worker для обработки задач из очереди
taskiq worker app.scheduler:broker

