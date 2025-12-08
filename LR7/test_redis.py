"""Тестовый скрипт для проверки подключения к Redis"""

import redis

# Подключение к локальному Redis
r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

# Проверка подключения
try:
    r.ping()
    print("Успешное подключение к Redis")
except redis.ConnectionError:
    print("Ошибка подключения к Redis")

# Работа со строками
print("\n=== Работа со строками ===")
r.set("user:name", "Иван")
name = r.get("user:name")
print(f"Имя пользователя: {name}")

# Установка с TTL
r.setex("session:123", 3600, "active")  # 1 час
print(f"Сессия: {r.get('session:123')}")

# Работа с числами
r.set("counter", 0)
r.incr("counter")  # Увеличить на 1
r.incrby("counter", 5)  # Увеличить на 5
r.decr("counter")  # Уменьшить на 1
print(f"Счетчик: {r.get('counter')}")

# Работа со списками
print("\n=== Работа со списками ===")
r.lpush("tasks", "task1", "task2")  # В начало
r.rpush("tasks", "task3", "task4")  # В конец
tasks = r.lrange("tasks", 0, -1)  # Все элементы
print(f"Все задачи: {tasks}")
first_task = r.lpop("tasks")  # Удалить и вернуть первый
last_task = r.rpop("tasks")  # Удалить и вернуть последний
print(f"Первая задача: {first_task}, Последняя задача: {last_task}")
length = r.llen("tasks")
print(f"Длина списка: {length}")

# Работа с множествами
print("\n=== Работа с множествами ===")
r.sadd("tags", "python", "redis", "database")
r.sadd("languages", "python", "java", "javascript")
is_member = r.sismember("tags", "python")  # True
print(f"Python в тегах: {is_member}")
all_tags = r.smembers("tags")
print(f"Все теги: {all_tags}")
intersection = r.sinter("tags", "languages")  # Пересечение
union = r.sunion("tags", "languages")  # Объединение
difference = r.sdiff("tags", "languages")  # Разность
print(f"Пересечение: {intersection}")
print(f"Объединение: {union}")
print(f"Разность: {difference}")

# Работа с хэшами
print("\n=== Работа с хэшами ===")
r.hset("user:1000", mapping={
    "name": "Иван",
    "age": "30",
    "city": "Москва"
})
name = r.hget("user:1000", "name")
all_data = r.hgetall("user:1000")
print(f"Имя: {name}")
print(f"Все данные: {all_data}")
exists = r.hexists("user:1000", "email")
print(f"Email существует: {exists}")
keys = r.hkeys("user:1000")
values = r.hvals("user:1000")
print(f"Ключи: {keys}")
print(f"Значения: {values}")

# Работа с упорядоченными множествами
print("\n=== Работа с упорядоченными множествами ===")
r.zadd("leaderboard", {
    "player1": 100,
    "player2": 200,
    "player3": 150
})
top_players = r.zrange("leaderboard", 0, 2, withscores=True)
print(f"Топ игроки: {top_players}")
players_by_score = r.zrangebyscore("leaderboard", 100, 200)
print(f"Игроки по очкам (100-200): {players_by_score}")
rank = r.zrank("leaderboard", "player1")
print(f"Ранг player1: {rank}")

print("\nВсе тесты выполнены успешно!")

