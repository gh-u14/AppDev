#!/bin/bash

# Скрипт для запуска планировщика TaskIQ

echo "Запуск планировщика TaskIQ..."

# Активируем виртуальное окружение, если оно существует
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Устанавливаем PYTHONPATH на текущую директорию для корректного импорта модулей
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Запускаем планировщик
taskiq scheduler app.scheduler:scheduler --skip-first-run

