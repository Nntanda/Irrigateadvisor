import sqlite3
import hashlib
import re

DB_NAME = "users.db"

def create_user_table():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE,
            password_hash TEXT
        )
    ''')
    conn.commit()
    conn.close()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def is_valid_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)

def add_user(email, password):
    if not is_valid_email(email):
        return "invalid_email"
    if len(password) < 6:
        return "weak_password"

    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        password_hash = hash_password(password)
        cursor.execute("INSERT INTO users (email, password_hash) VALUES (?, ?)", (email, password_hash))
        conn.commit()
        conn.close()
        return "success"
    except sqlite3.IntegrityError:
        return "exists"

def validate_user(email, password):
    password_hash = hash_password(password)
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email = ? AND password_hash = ?", (email, password_hash))
    result = cursor.fetchone()
    conn.close()
    return result is not None
