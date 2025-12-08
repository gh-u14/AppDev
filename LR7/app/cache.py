"""Утилита для работы с Redis кэшем"""

import json
import os
from typing import Any, Optional
from uuid import UUID

import redis
from dotenv import load_dotenv

load_dotenv()

# Подключение к Redis
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))

# Создаем клиент Redis
redis_client = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    db=0,
    decode_responses=True,
)


def get_redis_client() -> Optional[redis.Redis]:
    """Получить клиент Redis"""
    try:
        redis_client.ping()
        return redis_client
    except (redis.ConnectionError, redis.RedisError):
        return None


class CacheService:
    """Сервис для работы с кэшем Redis"""

    def __init__(self):
        self.client = get_redis_client()
        self._available = self.client is not None

    def get(self, key: str) -> Optional[str]:
        """Получить значение из кэша"""
        if not self._available:
            return None
        try:
            return self.client.get(key)
        except redis.RedisError:
            return None

    def set(self, key: str, value: str, ttl: int) -> bool:
        """Установить значение в кэш с TTL (в секундах)"""
        if not self._available:
            return False
        try:
            return self.client.setex(key, ttl, value)
        except redis.RedisError:
            return False

    def delete(self, key: str) -> bool:
        """Удалить значение из кэша"""
        if not self._available:
            return False
        try:
            return bool(self.client.delete(key))
        except redis.RedisError:
            return False

    def delete_pattern(self, pattern: str) -> int:
        """Удалить все ключи по паттерну"""
        if not self._available:
            return 0
        try:
            keys = self.client.keys(pattern)
            if keys:
                return self.client.delete(*keys)
            return 0
        except redis.RedisError:
            return 0

    def cache_user(self, user_id: UUID, user_data: dict) -> bool:
        """Кэшировать данные пользователя на 1 час (3600 секунд)"""
        key = f"user:{user_id}"
        value = json.dumps(user_data, default=str)
        return self.set(key, value, ttl=3600)

    def get_cached_user(self, user_id: UUID) -> Optional[dict]:
        """Получить закэшированные данные пользователя"""
        key = f"user:{user_id}"
        value = self.get(key)
        if value:
            return json.loads(value)
        return None

    def delete_cached_user(self, user_id: UUID) -> bool:
        """Удалить закэшированные данные пользователя"""
        key = f"user:{user_id}"
        return self.delete(key)

    def cache_product(self, product_id: UUID, product_data: dict) -> bool:
        """Кэшировать данные продукта на 10 минут (600 секунд)"""
        key = f"product:{product_id}"
        value = json.dumps(product_data, default=str)
        return self.set(key, value, ttl=600)

    def get_cached_product(self, product_id: UUID) -> Optional[dict]:
        """Получить закэшированные данные продукта"""
        key = f"product:{product_id}"
        value = self.get(key)
        if value:
            return json.loads(value)
        return None

    def update_cached_product(self, product_id: UUID, product_data: dict) -> bool:
        """Обновить закэшированные данные продукта"""
        return self.cache_product(product_id, product_data)

    def cache_products_list(
        self, page: int, count: int, products_data: list, total: int
    ) -> bool:
        """Кэшировать список продуктов на 10 минут (600 секунд)"""
        key = f"products:list:page:{page}:count:{count}"
        value = json.dumps({"products": products_data, "total": total}, default=str)
        return self.set(key, value, ttl=600)

    def get_cached_products_list(
        self, page: int, count: int
    ) -> Optional[dict]:
        """Получить закэшированный список продуктов"""
        key = f"products:list:page:{page}:count:{count}"
        value = self.get(key)
        if value:
            return json.loads(value)
        return None

    def invalidate_products_list(self) -> int:
        """Инвалидировать все кэшированные списки продуктов"""
        return self.delete_pattern("products:list:*")

