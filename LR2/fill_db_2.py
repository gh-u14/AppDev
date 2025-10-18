from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, selectinload
from models import User, Address, Product, Order
from uuid import uuid4


engine = create_engine("postgresql+psycopg2://postgres:pass@localhost:5432/labdb")


Session = sessionmaker(bind=engine)
session = Session()


products = [
    Product(name="Laptop", price=1200.0),
    Product(name="Mouse", price=25.0),
    Product(name="Keyboard", price=50.0),
    Product(name="Monitor", price=300.0),
    Product(name="Headphones", price=80.0),
]
session.add_all(products)
session.commit()


users = session.query(User).all()
orders = [
    Order(user_id=users[0].id, address_id=users[0].addresses[0].id, product_id=products[0].id, quantity=1),
    Order(user_id=users[1].id, address_id=users[1].addresses[0].id, product_id=products[1].id, quantity=2),
    Order(user_id=users[2].id, address_id=users[2].addresses[0].id, product_id=products[2].id, quantity=1),
    Order(user_id=users[3].id, address_id=users[3].addresses[0].id, product_id=products[3].id, quantity=3),
    Order(user_id=users[4].id, address_id=users[4].addresses[0].id, product_id=products[4].id, quantity=2),
]

session.add_all(orders)
session.commit()

# проверка
for order in session.query(Order).options(
    selectinload(Order.user),
    selectinload(Order.address),
    selectinload(Order.product)
):
    print(f"{order.user.username} заказал {order.product.name} x{order.quantity} на {order.address.street}")

session.close()
