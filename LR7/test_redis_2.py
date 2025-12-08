from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Product
import os
from dotenv import load_dotenv
from app.cache import CacheService

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql+psycopg2://postgres:pass@localhost:5433/labdb')
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

product = Product(name='Тестовый продукт', price=1000.0, stock_quantity=10)
session.add(product)
session.commit()
print(f'Продукт создан с ID: {product.id}')

# Инвалидируем кэш списков продуктов, чтобы новый продукт появился в списке
cache_service = CacheService()
cache_service.invalidate_products_list()
print('Кэш списков продуктов инвалидирован')

session.close()