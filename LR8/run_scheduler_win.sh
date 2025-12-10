#!/bin/bash

# Скрипт для запуска планировщика TaskIQ на Windows (Git Bash)

echo "Запуск планировщика TaskIQ..."

# Активируем виртуальное окружение (Windows путь в Git Bash)
if [ -d "venv" ]; then
    source venv/Scripts/activate
fi

# Устанавливаем PYTHONPATH на текущую директорию для корректного импорта модулей
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Запускаем планировщик
taskiq scheduler app.scheduler:scheduler --skip-first-run

