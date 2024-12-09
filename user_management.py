import sqlite3
import bcrypt
from sqlite3 import Error

def create_connection():
    """Create a database connection to SQLite database"""
    conn = None
    try:
        conn = sqlite3.connect('noor_alislam.db')
        return conn
    except Error as e:
        print(e)
    return conn

def add_user(username, password, user_type):
    """Add a new user to the database"""
    conn = create_connection()
    if conn is not None:
        try:
            cursor = conn.cursor()
            
            # Hash the password
            password_bytes = password.encode('utf-8')
            salt = bcrypt.gensalt()
            password_hash = bcrypt.hashpw(password_bytes, salt)
            
            # Insert user
            cursor.execute('''
                INSERT INTO users (username, password_hash, user_type)
                VALUES (?, ?, ?)
            ''', (username, password_hash, user_type))
            
            conn.commit()
            print(f"User {username} added successfully")
            return True
        except Error as e:
            print(f"Error adding user: {e}")
            return False
        finally:
            conn.close()
    return False

def verify_user(username, password):
    """Verify user credentials"""
    conn = create_connection()
    if conn is not None:
        try:
            cursor = conn.cursor()
            cursor.execute('SELECT password_hash, user_type FROM users WHERE username = ?', (username,))
            result = cursor.fetchone()
            
            if result:
                stored_hash = result[0]
                user_type = result[1]
                
                # Verify password
                if bcrypt.checkpw(password.encode('utf-8'), stored_hash):
                    return True, user_type
            return False, None
        finally:
            conn.close()
    return False, None
