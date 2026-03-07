import os
import random
from datetime import datetime, timedelta
from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, DateTime, Text, text
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from faker import Faker
from dotenv import load_dotenv

load_dotenv()

Base = declarative_base()
faker = Faker()

# --- Hyper-Complex Schema Definition ---

class Category(Base):
    __tablename__ = 'categories'
    category_id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)

class Supplier(Base):
    __tablename__ = 'suppliers'
    supplier_id = Column(Integer, primary_key=True)
    company_name = Column(String(200), nullable=False)
    contact_name = Column(String(100))
    city = Column(String(100))
    country = Column(String(100))

class Shipper(Base):
    __tablename__ = 'shippers'
    shipper_id = Column(Integer, primary_key=True)
    company_name = Column(String(100), nullable=False)
    phone = Column(String(24))

class Product(Base):
    __tablename__ = 'products'
    product_id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    category_id = Column(Integer, ForeignKey('categories.category_id'))
    supplier_id = Column(Integer, ForeignKey('suppliers.supplier_id'))
    unit_price = Column(Float, nullable=False)
    units_in_stock = Column(Integer, default=0)
    
    category = relationship("Category")
    supplier = relationship("Supplier")

class Customer(Base):
    __tablename__ = 'customers'
    customer_id = Column(Integer, primary_key=True)
    full_name = Column(String(200), nullable=False)
    email = Column(String(200), unique=True)
    city = Column(String(100))
    country = Column(String(100))
    registration_date = Column(DateTime, default=datetime.utcnow)

class Employee(Base):
    __tablename__ = 'employees'
    employee_id = Column(Integer, primary_key=True)
    first_name = Column(String(100))
    last_name = Column(String(100))
    title = Column(String(100))
    hire_date = Column(DateTime)
    reports_to = Column(Integer, ForeignKey('employees.employee_id'), nullable=True)

class Order(Base):
    __tablename__ = 'orders'
    order_id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey('customers.customer_id'))
    employee_id = Column(Integer, ForeignKey('employees.employee_id'))
    shipper_id = Column(Integer, ForeignKey('shippers.shipper_id'))
    order_date = Column(DateTime, default=datetime.utcnow)
    shipped_date = Column(DateTime)
    ship_city = Column(String(100))
    ship_country = Column(String(100))
    freight = Column(Float, default=0.0)
    
    customer = relationship("Customer")
    employee = relationship("Employee")
    shipper = relationship("Shipper")

class OrderDetail(Base):
    __tablename__ = 'order_details'
    order_detail_id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey('orders.order_id'))
    product_id = Column(Integer, ForeignKey('products.product_id'))
    unit_price = Column(Float, nullable=False)
    quantity = Column(Integer, nullable=False)
    discount = Column(Float, default=0.0)
    
    order = relationship("Order")
    product = relationship("Product")

class ProductReview(Base):
    __tablename__ = 'product_reviews'
    review_id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey('products.product_id'))
    customer_id = Column(Integer, ForeignKey('customers.customer_id'))
    rating = Column(Integer) # 1-5
    review_text = Column(Text)
    review_date = Column(DateTime, default=datetime.utcnow)
    
    product = relationship("Product")
    customer = relationship("Customer")

# --- Scaling Logic ---

def setup_database():
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("[!] ERROR: DATABASE_URL not found in .env")
        return

    print(f"[*] Hyper-Scaling Database: Connecting to {db_url}...")
    engine = create_engine(db_url)
    
    # Fresh start
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    
    Session = sessionmaker(bind=engine)
    session = Session()

    print("[*] Seeding 10 categories...")
    categories = [Category(name=c, description=f"Detailed category for {c}") for c in 
                  ["Electronics", "Clothing", "Home", "Books", "Beauty", "Garden", "Toys", "Fitness", "Automotive", "Grocery"]]
    session.add_all(categories)
    session.commit()

    print("[*] Seeding 20 suppliers...")
    suppliers = [Supplier(company_name=faker.company(), contact_name=faker.name(), city=faker.city(), country=faker.country()) for _ in range(20)]
    session.add_all(suppliers)
    session.commit()

    print("[*] Seeding 3 shippers...")
    shippers = [
        Shipper(company_name="Speedy Express", phone="(503) 555-9831"),
        Shipper(company_name="Global Parcel", phone="(503) 555-3199"),
        Shipper(company_name="Federal Shipping", phone="(503) 555-9931")
    ]
    session.add_all(shippers)
    session.commit()

    print("[*] Seeding 200 products...")
    products = []
    for _ in range(200):
        products.append(Product(
            name=faker.catch_phrase(),
            category_id=random.choice(categories).category_id,
            supplier_id=random.choice(suppliers).supplier_id,
            unit_price=round(random.uniform(5.0, 5000.0), 2),
            units_in_stock=random.randint(0, 1000)
        ))
    session.add_all(products)
    session.commit()

    print("[*] Seeding 1,000 customers...")
    customers = []
    for _ in range(1000):
        customers.append(Customer(
            full_name=faker.name(),
            email=faker.unique.email(),
            city=faker.city(),
            country=faker.country(),
            registration_date=faker.date_between(start_date='-5y', end_date='today')
        ))
    session.add_all(customers)
    session.commit()

    print("[*] Seeding 5,000 orders and ~15,000 details...")
    all_employees = session.query(Employee).all()
    if not all_employees:
        # Create a few if they don't exist (e.g. fresh run)
        manager = Employee(first_name="Alice", last_name="Boss", title="Director")
        session.add(manager)
        session.commit()
        for _ in range(15):
            session.add(Employee(first_name=faker.first_name(), last_name=faker.last_name(), title="Associate", reports_to=manager.employee_id))
        session.commit()
        all_employees = session.query(Employee).all()

    for i in range(5000):
        cust = random.choice(customers)
        emp = random.choice(all_employees)
        ship = random.choice(shippers)
        order_date = faker.date_time_between(start_date='-2y', end_date='now')
        
        order = Order(
            customer_id=cust.customer_id,
            employee_id=emp.employee_id,
            shipper_id=ship.shipper_id,
            order_date=order_date,
            shipped_date=order_date + timedelta(days=random.randint(1, 7)),
            ship_city=cust.city,
            ship_country=cust.country,
            freight=round(random.uniform(5.0, 100.0), 2)
        )
        session.add(order)
        if i % 500 == 0: session.flush() # Keep session manageable
        
        # 1-6 items per order
        for _ in range(random.randint(1, 6)):
            prod = random.choice(products)
            session.add(OrderDetail(
                order=order,
                product_id=prod.product_id,
                unit_price=prod.unit_price,
                quantity=random.randint(1, 15),
                discount=random.choice([0.0, 0.05, 0.1, 0.15, 0.2])
            ))
            
    session.commit()

    print("[*] Seeding 2,000 product reviews...")
    for _ in range(2000):
        session.add(ProductReview(
            product_id=random.choice(products).product_id,
            customer_id=random.choice(customers).customer_id,
            rating=random.randint(1, 5),
            review_text=faker.paragraph(nb_sentences=3),
            review_date=faker.date_time_between(start_date='-1y', end_date='now')
        ))

    session.commit()
    print(f"[+] Hyper-Scale Transition Complete! Generated 25,000+ total record items.")
    session.close()

if __name__ == "__main__":
    setup_database()
