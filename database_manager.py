import sqlite3
from typing import List, Tuple, Optional, Dict
import datetime

class DatabaseManager:
    def __init__(self, db_path: str = "noor_alislam.db"):
        self.db_path = db_path

    def get_connection(self):
        return sqlite3.connect(self.db_path)

    def get_suppliers(self) -> List[Tuple]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT s.supplier_id, s.supplier_name, s.contact_details,
                       GROUP_CONCAT(p.product_name, ', ') as products,
                       COUNT(DISTINCT sp.product_id) as product_count
                FROM suppliers s
                LEFT JOIN supplier_products sp ON s.supplier_id = sp.supplier_id
                LEFT JOIN products p ON sp.product_id = p.product_id
                GROUP BY s.supplier_id
                ORDER BY s.supplier_name
            """)
            return cursor.fetchall()

    def get_products(self) -> List[Tuple]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT product_id, product_name FROM products ORDER BY product_name")
            return cursor.fetchall()

    def add_supplier(self, name: str, contact_details: str) -> int:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO suppliers (supplier_name, contact_details) VALUES (?, ?)",
                (name, contact_details)
            )
            conn.commit()
            return cursor.lastrowid

    def update_supplier(self, supplier_id: int, name: str, contact_details: str) -> bool:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE suppliers SET supplier_name = ?, contact_details = ? WHERE supplier_id = ?",
                (name, contact_details, supplier_id)
            )
            conn.commit()
            return cursor.rowcount > 0

    def delete_supplier(self, supplier_id: int) -> bool:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            # First delete from supplier_products
            cursor.execute("DELETE FROM supplier_products WHERE supplier_id = ?", (supplier_id,))
            # Then delete the supplier
            cursor.execute("DELETE FROM suppliers WHERE supplier_id = ?", (supplier_id,))
            conn.commit()
            return cursor.rowcount > 0

    def get_supplier_products(self, supplier_id: int) -> List[Tuple]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT p.product_id, p.product_name, sp.supply_price, sp.supply_date
                FROM supplier_products sp
                JOIN products p ON sp.product_id = p.product_id
                WHERE sp.supplier_id = ?
                ORDER BY p.product_name
            """, (supplier_id,))
            return cursor.fetchall()

    def add_supplier_product(self, supplier_id: int, product_id: int, 
                           supply_price: float, supply_date: Optional[str] = None) -> bool:
        if supply_date is None:
            supply_date = datetime.date.today().isoformat()
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("""
                    INSERT INTO supplier_products (supplier_id, product_id, supply_price, supply_date)
                    VALUES (?, ?, ?, ?)
                """, (supplier_id, product_id, supply_price, supply_date))
                conn.commit()
                return True
            except sqlite3.IntegrityError:
                return False

    def remove_supplier_product(self, supplier_id: int, product_id: int) -> bool:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                DELETE FROM supplier_products
                WHERE supplier_id = ? AND product_id = ?
            """, (supplier_id, product_id))
            conn.commit()
            return cursor.rowcount > 0

    def update_supplier_product(self, supplier_id: int, product_id: int, 
                              supply_price: float, supply_date: str) -> bool:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE supplier_products
                SET supply_price = ?, supply_date = ?
                WHERE supplier_id = ? AND product_id = ?
            """, (supply_price, supply_date, supplier_id, product_id))
            conn.commit()
            return cursor.rowcount > 0

    def get_products_with_details(self) -> List[Tuple]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    p.product_id,
                    p.product_name,
                    p.description,
                    p.unit_type,
                    p.min_stock_level,
                    COALESCE(wp.quantity, 0) as current_stock,
                    w.warehouse_name,
                    MIN(sp.supply_price) as min_supply_price,
                    GROUP_CONCAT(DISTINCT s.supplier_name) as suppliers,
                    (
                        SELECT MIN(od1.sale_price)
                        FROM order_details od1
                        WHERE od1.product_id = p.product_id
                        AND od1.price_type = 'wholesale'
                    ) as wholesale_price,
                    (
                        SELECT MIN(od2.sale_price)
                        FROM order_details od2
                        WHERE od2.product_id = p.product_id
                        AND od2.price_type = 'retail'
                    ) as retail_price,
                    w.warehouse_id
                FROM products p
                LEFT JOIN warehouse_products wp ON p.product_id = wp.product_id
                LEFT JOIN warehouses w ON wp.warehouse_id = w.warehouse_id
                LEFT JOIN supplier_products sp ON p.product_id = sp.product_id
                LEFT JOIN suppliers s ON sp.supplier_id = s.supplier_id
                GROUP BY p.product_id, w.warehouse_id
                ORDER BY p.product_name
            """)
            return cursor.fetchall()

    def get_warehouses(self) -> List[Tuple]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT warehouse_id, warehouse_name FROM warehouses ORDER BY warehouse_name")
            return cursor.fetchall()

    def add_warehouse(self, name: str, location: str = "", contact_details: str = "") -> int:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO warehouses (warehouse_name, location, contact_details)
                VALUES (?, ?, ?)
            """, (name, location, contact_details))
            conn.commit()
            return cursor.lastrowid

    def update_warehouse(self, warehouse_id: int, name: str, 
                        location: str = "", contact_details: str = "") -> bool:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE warehouses 
                SET warehouse_name = ?, location = ?, contact_details = ?
                WHERE warehouse_id = ?
            """, (name, location, contact_details, warehouse_id))
            conn.commit()
            return cursor.rowcount > 0

    def delete_warehouse(self, warehouse_id: int) -> bool:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            # First check if warehouse has any products
            cursor.execute("""
                SELECT COUNT(*) FROM warehouse_products 
                WHERE warehouse_id = ? AND quantity > 0
            """, (warehouse_id,))
            if cursor.fetchone()[0] > 0:
                return False
            
            # Delete warehouse associations and then warehouse
            cursor.execute("DELETE FROM warehouse_products WHERE warehouse_id = ?", (warehouse_id,))
            cursor.execute("DELETE FROM warehouses WHERE warehouse_id = ?", (warehouse_id,))
            conn.commit()
            return True

    def get_warehouse_details(self, warehouse_id: int) -> Tuple:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT warehouse_id, warehouse_name, location, contact_details
                FROM warehouses WHERE warehouse_id = ?
            """, (warehouse_id,))
            return cursor.fetchone()

    def get_warehouse_products(self, warehouse_id: int) -> List[Tuple]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT p.product_id, p.product_name, wp.quantity
                FROM warehouse_products wp
                JOIN products p ON wp.product_id = p.product_id
                WHERE wp.warehouse_id = ?
                ORDER BY p.product_name
            """, (warehouse_id,))
            return cursor.fetchall()

    def add_product(self, name: str, description: str, unit_type: str, 
                   min_stock: int, current_stock: int, warehouse_id: int,
                   suppliers: List[Dict], wholesale_price: float, retail_price: float) -> int:
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("BEGIN TRANSACTION")
                
                # Add product
                cursor.execute("""
                    INSERT INTO products (product_name, description, unit_type, 
                                        min_stock_level, current_stock)
                    VALUES (?, ?, ?, ?, ?)
                """, (name, description, unit_type, min_stock, current_stock))
                
                product_id = cursor.lastrowid

                # Add warehouse association
                if warehouse_id:
                    cursor.execute("""
                        INSERT INTO warehouse_products (warehouse_id, product_id, quantity)
                        VALUES (?, ?, ?)
                    """, (warehouse_id, product_id, current_stock))

                # Add supplier associations
                for supplier in suppliers:
                    cursor.execute("""
                        INSERT INTO supplier_products (supplier_id, product_id, supply_price)
                        VALUES (?, ?, ?)
                    """, (supplier['supplier_id'], product_id, supplier['supply_price']))

                # Add initial prices
                cursor.execute("""
                    INSERT INTO order_details (product_id, quantity, sale_price, price_type)
                    VALUES 
                        (?, 1, ?, 'wholesale'),
                        (?, 1, ?, 'retail')
                """, (product_id, wholesale_price, product_id, retail_price))

                conn.commit()
                return product_id
                
        except sqlite3.Error as e:
            conn.rollback()
            print(f"Database error: {e}")
            return None

    def update_product(self, product_id: int, name: str, description: str, 
                      unit_type: str, min_stock: int, current_stock: int,
                      warehouse_id: int, suppliers: List[Dict],
                      wholesale_price: float, retail_price: float) -> bool:
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                # Update product
                cursor.execute("""
                    UPDATE products 
                    SET product_name = ?, description = ?, unit_type = ?,
                        min_stock_level = ?, current_stock = ?
                    WHERE product_id = ?
                """, (name, description, unit_type, min_stock, current_stock, product_id))

                # Update warehouse association
                cursor.execute("DELETE FROM warehouse_products WHERE product_id = ?", (product_id,))
                if warehouse_id:
                    cursor.execute("""
                        INSERT INTO warehouse_products (warehouse_id, product_id, quantity)
                        VALUES (?, ?, ?)
                    """, (warehouse_id, product_id, current_stock))

                # Update supplier associations
                cursor.execute("DELETE FROM supplier_products WHERE product_id = ?", (product_id,))
                for supplier in suppliers:
                    cursor.execute("""
                        INSERT INTO supplier_products (supplier_id, product_id, supply_price)
                        VALUES (?, ?, ?)
                    """, (supplier['supplier_id'], product_id, supplier['supply_price']))

                # Update prices
                cursor.execute("""
                    INSERT OR REPLACE INTO order_details (product_id, quantity, sale_price, price_type)
                    VALUES 
                        (?, 1, ?, 'retail'),
                        (?, 1, ?, 'wholesale')
                """, (product_id, retail_price, product_id, wholesale_price))

                conn.commit()
                return True
        except sqlite3.Error:
            return False

    def delete_product(self, product_id: int) -> bool:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            # First delete from related tables
            cursor.execute("DELETE FROM supplier_products WHERE product_id = ?", (product_id,))
            cursor.execute("DELETE FROM warehouse_products WHERE product_id = ?", (product_id,))
            cursor.execute("DELETE FROM stock_alerts WHERE product_id = ?", (product_id,))
            # Then delete the product
            cursor.execute("DELETE FROM products WHERE product_id = ?", (product_id,))
            conn.commit()
            return cursor.rowcount > 0

    def update_product_warehouse(self, product_id: int, updates: list) -> bool:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("BEGIN TRANSACTION")
                
                total_stock = 0
                # تحديث كل مخزن
                for update in updates:
                    warehouse_id = update['warehouse_id']
                    quantity = update['quantity']
                    total_stock += quantity
                    
                    cursor.execute("""
                        INSERT OR REPLACE INTO warehouse_products 
                        (warehouse_id, product_id, quantity) 
                        VALUES (?, ?, ?)
                    """, (warehouse_id, product_id, quantity))
                
                # تحديث إجمالي المخزون في جدول المنتجات
                cursor.execute("""
                    UPDATE products 
                    SET current_stock = ? 
                    WHERE product_id = ?
                """, (total_stock, product_id))
                
                conn.commit()
                return True
                
            except sqlite3.Error:
                conn.rollback()
                return False

    def update_product_prices(self, product_id: int, supply_price: float, 
                            supplier_id: int, supply_date: str = None) -> bool:
        if supply_date is None:
            supply_date = datetime.date.today().isoformat()
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("""
                    INSERT INTO supplier_products (supplier_id, product_id, supply_price, supply_date)
                    VALUES (?, ?, ?, ?)
                    ON CONFLICT(supplier_id, product_id) 
                    DO UPDATE SET supply_price = ?, supply_date = ?
                """, (supplier_id, product_id, supply_price, supply_date, 
                      supply_price, supply_date))
                conn.commit()
                return True
            except sqlite3.Error:
                return False

    def get_warehouse_product_quantity(self, warehouse_id, product_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT quantity FROM warehouse_products 
                WHERE warehouse_id = ? AND product_id = ?
            """, (warehouse_id, product_id))
            result = cursor.fetchone()
            return result[0] if result else 0

    def get_product_details(self, product_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM products WHERE product_id = ?
            """, (product_id,))
            return cursor.fetchone()

    def get_customer_details(self, customer_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM customers WHERE customer_id = ?
            """, (customer_id,))
            return cursor.fetchone()

    def add_customer(self, name, address, phone, discount):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO customers (customer_name, address, phone_number, discount_percentage)
                VALUES (?, ?, ?, ?)
            """, (name, address, phone, discount))
            conn.commit()
            return cursor.lastrowid

    def create_order(self, customer_id, total_price, discount):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO orders (customer_id, order_date, total_price)
                VALUES (?, DATE('now'), ?)
            """, (customer_id, total_price))
            conn.commit()
            return cursor.lastrowid

    def add_order_detail(self, order_id, product_id, quantity, price):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO order_details (order_id, product_id, quantity, sale_price)
                VALUES (?, ?, ?, ?)
            """, (order_id, product_id, quantity, price))
            conn.commit()

    def create_invoice(self, order_id, total_amount):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO invoices (order_id, total_amount, invoice_date)
                VALUES (?, ?, DATE('now'))
            """, (order_id, total_amount))
            conn.commit()
            return cursor.lastrowid

    def get_customers(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT customer_id, customer_name, address, phone_number, 
                       discount_amount as discount
                FROM customers
                ORDER BY customer_name
            """)
            return cursor.fetchall()

    def update_customer(self, customer_id: int, name: str, address: str, 
                       phone: str, discount: float) -> bool:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("""
                    UPDATE customers 
                    SET customer_name = ?, address = ?, 
                        phone_number = ?, discount_amount = ?
                    WHERE customer_id = ?
                """, (name, address, phone, discount, customer_id))
                conn.commit()
                return True
            except sqlite3.Error:
                return False

    def delete_customer(self, customer_id: int) -> bool:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                # Check if customer has orders
                cursor.execute("SELECT COUNT(*) FROM orders WHERE customer_id = ?", 
                             (customer_id,))
                if cursor.fetchone()[0] > 0:
                    return False
                
                cursor.execute("DELETE FROM customers WHERE customer_id = ?", 
                             (customer_id,))
                conn.commit()
                return True
            except sqlite3.Error:
                return False
