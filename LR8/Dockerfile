FROM python:3.11-slim

WORKDIR /app

# Установка системных зависимостей для PostgreSQL и netcat
RUN apt-get update && apt-get install -y \
    postgresql-client \
    netcat-openbsd \
    gcc \
    python3-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Установка зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование приложения
COPY . .

# Настройка миграций
RUN chmod +x entrypoint.sh

ENTRYPOINT ["./entrypoint.sh"]

