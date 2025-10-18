from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, User, Address
from uuid import uuid4

# подключение к базе
engine = create_engine("postgresql+psycopg2://postgres:pass@localhost:5432/labdb")

# создаём сессию
Session = sessionmaker(bind=engine)
session = Session()

user = User(username=f"Ivan",email=f"ivan@example.com")
user.addresses = [Address(street=f"Mira 19", city="Yekaterinburg", country="Russia", is_primary=True)]
session.add(user)

user = User(username=f"Petr",email=f"petr@example.com")
user.addresses = [Address(street=f"Lenina 1", city="Moscow", country="Russia", is_primary=True)]
session.add(user)

user = User(username=f"Vasiliy",email=f"vasiliy@example.com")
user.addresses = [Address(street=f"Nevsky Prospekt 123", city="Saint Petersburg", country="Russia", is_primary=True)]
session.add(user)

user = User(username=f"Nikolaii",email=f"nikolaii@example.com")
user.addresses = [Address(street=f"Lenina 22", city="Yekaterinburg", country="Russia", is_primary=True)]
session.add(user)

user = User(username=f"Anatoly",email=f"anatoly@example.com")
user.addresses = [Address(street=f"Tverskaya 15", city="Moscow", country="Russia", is_primary=True)]
session.add(user)
session.commit()


# проверяем
for user in session.query(User).all():
    print(f"{user.username} ({user.email}):")
    for addr in user.addresses:
        print(f"  - {addr.street}, {addr.city}, {addr.country} (primary={addr.is_primary})")

session.close()


