from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker, selectinload
from models import User

# подключение к базе
engine = create_engine("postgresql+psycopg2://postgres:pass@localhost:5432/labdb")
Session = sessionmaker(bind=engine)
session = Session()

# делаем запрос всех пользователей с их адресами
stmt = select(User).options(selectinload(User.addresses))
results = session.execute(stmt).scalars().all()

for user in results:
    print(f"User: {user.username} ({user.email})")
    for addr in user.addresses:
        print(f"  Address: {addr.street}, {addr.city}, {addr.country} (primary={addr.is_primary})")

session.close()
