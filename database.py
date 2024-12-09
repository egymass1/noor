import sqlite3
from sqlite3 import Error
import os

def create_connection():
    """Create a database connection to SQLite database"""
    conn = None
    try:
        conn = sqlite3.connect('noor_alislam.db')
        return conn
    except Error as e:
        print(e)
    return conn

def create_tables(conn):
    """Create all required tables in the database"""
    try:
        cursor = conn.cursor()
        
        # Create products table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                product_id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_name TEXT NOT NULL,
                description TEXT,
                unit_type TEXT,
                min_stock_level INTEGER NOT NULL,
                current_stock INTEGER DEFAULT 0
            )
        ''')

        # Create suppliers table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS suppliers (
                supplier_id INTEGER PRIMARY KEY AUTOINCREMENT,
                supplier_name TEXT NOT NULL,
                contact_details TEXT
            )
        ''')

        # Create supplier_products table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS supplier_products (
                supplier_id INTEGER,
                product_id INTEGER,
                supply_price DECIMAL(10, 2),
                supply_date DATE,
                PRIMARY KEY (supplier_id, product_id),
                FOREIGN KEY (supplier_id) REFERENCES suppliers(supplier_id),
                FOREIGN KEY (product_id) REFERENCES products(product_id)
            )
        ''')

        # Create warehouses table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS warehouses (
                warehouse_id INTEGER PRIMARY KEY AUTOINCREMENT,
                warehouse_name TEXT,
                location TEXT,
                contact_details TEXT
            )
        ''')

        # Create warehouse_products table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS warehouse_products (
                warehouse_id INTEGER,
                product_id INTEGER,
                quantity INTEGER DEFAULT 0,
                PRIMARY KEY (warehouse_id, product_id),
                FOREIGN KEY (warehouse_id) REFERENCES warehouses(warehouse_id),
                FOREIGN KEY (product_id) REFERENCES products(product_id)
            )
        ''')

        # Create customers table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS customers (
                customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_name TEXT NOT NULL,
                address TEXT,
                phone_number TEXT,
                discount_percentage DECIMAL(5, 2) DEFAULT 0
            )
        ''')

        # Create orders table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS orders (
                order_id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id INTEGER,
                order_date DATE NOT NULL,
                total_price DECIMAL(10, 2),
                FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
            )
        ''')

        # Create order_details table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS order_details (
                order_detail_id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id INTEGER,
                product_id INTEGER,
                quantity INTEGER NOT NULL,
                sale_price DECIMAL(10, 2),
                price_type TEXT,
                FOREIGN KEY (order_id) REFERENCES orders(order_id),
                FOREIGN KEY (product_id) REFERENCES products(product_id)
            )
        ''')

        # Create invoices table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS invoices (
                invoice_id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id INTEGER,
                total_amount DECIMAL(10, 2),
                profit DECIMAL(10, 2),
                invoice_date DATE,
                FOREIGN KEY (order_id) REFERENCES orders(order_id)
            )
        ''')

        # Create stock_alerts table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS stock_alerts (
                alert_id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER,
                current_stock INTEGER,
                alert_threshold INTEGER,
                alert_status INTEGER DEFAULT 0,
                FOREIGN KEY (product_id) REFERENCES products(product_id)
            )
        ''')

        # Create users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                user_type TEXT
            )
        ''')

        # Create permissions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS permissions (
                permission_id INTEGER PRIMARY KEY AUTOINCREMENT,
                permission_name TEXT
            )
        ''')

        # Create user_permissions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_permissions (
                user_id INTEGER,
                permission_id INTEGER,
                PRIMARY KEY (user_id, permission_id),
                FOREIGN KEY (user_id) REFERENCES users(user_id),
                FOREIGN KEY (permission_id) REFERENCES permissions(permission_id)
            )
        ''')

        # Create activity_logs table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS activity_logs (
                log_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                action_type TEXT,
                action_details TEXT,
                action_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        ''')

        # Create reports table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS reports (
                report_id INTEGER PRIMARY KEY AUTOINCREMENT,
                report_type TEXT,
                report_date DATE,
                report_content TEXT
            )
        ''')

        # Create notifications table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS notifications (
                notification_id INTEGER PRIMARY KEY AUTOINCREMENT,
                notification_type TEXT,
                notification_content TEXT,
                is_read INTEGER DEFAULT 0,
                notification_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        conn.commit()
        print("All tables created successfully!")
        
    except Error as e:
        print(f"Error creating tables: {e}")

def initialize_database():
    """Initialize the database and create all tables"""
    conn = create_connection()
    if conn is not None:
        create_tables(conn)
        conn.close()
    else:
        print("Error! Cannot create the database connection.")
