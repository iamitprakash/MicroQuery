import sqlite3
import os

def seed_database():
    db_path = "mock_data.db"
    
    # Remove existing to start fresh
    if os.path.exists(db_path):
        os.remove(db_path)
        
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print(f"[*] Creating mock database at {db_path}...")
    
    # Create Tables
    cursor.execute("""
    CREATE TABLE Products (
        ProductID INTEGER PRIMARY KEY,
        ProductName TEXT,
        Category TEXT,
        UnitPrice REAL,
        UnitsInStock INTEGER
    )
    """)
    
    cursor.execute("""
    CREATE TABLE Customers (
        CustomerID INTEGER PRIMARY KEY,
        ContactName TEXT,
        City TEXT,
        Country TEXT
    )
    """)
    
    cursor.execute("""
    CREATE TABLE Orders (
        OrderID INTEGER PRIMARY KEY,
        CustomerID INTEGER,
        OrderDate TEXT,
        TotalAmount REAL,
        FOREIGN KEY(CustomerID) REFERENCES Customers(CustomerID)
    )
    """)
    
    # Insert Data
    products = [
        (1, 'Laptop', 'Electronics', 1200.00, 50),
        (2, 'Mouse', 'Electronics', 25.00, 150),
        (3, 'Desk Chair', 'Furniture', 200.00, 20),
        (4, 'Keyboard', 'Electronics', 75.00, 80),
        (5, 'Monitor', 'Electronics', 300.00, 40)
    ]
    cursor.executemany("INSERT INTO Products VALUES (?,?,?,?,?)", products)
    
    customers = [
        (1, 'Alice Smith', 'New York', 'USA'),
        (2, 'Bob Jones', 'London', 'UK'),
        (3, 'Charlie Brown', 'Paris', 'France')
    ]
    cursor.executemany("INSERT INTO Customers VALUES (?,?,?,?)", customers)
    
    orders = [
        (1, 1, '2024-03-01', 1225.00),
        (2, 2, '2024-03-05', 25.00),
        (3, 1, '2024-03-07', 300.00)
    ]
    cursor.executemany("INSERT INTO Orders VALUES (?,?,?,?)", orders)
    
    conn.commit()
    conn.close()
    print("[+] Mock database seeded successfully!")

if __name__ == "__main__":
    seed_database()
