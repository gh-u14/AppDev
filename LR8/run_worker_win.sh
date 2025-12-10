#!/bin/bash

# Скрипт для запуска TaskIQ worker на Windows (Git Bash)

echo "Запуск TaskIQ Worker..."

# Активируем виртуальное окружение (Windows путь в Git Bash)
if [ -d "venv" ]; then
    source venv/Scripts/activate
fi

# Устанавливаем PYTHONPATH на текущую директорию для корректного импорта модулей
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Запускаем worker для обработки задач из очереди
taskiq worker app.scheduler:broker

