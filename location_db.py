import sqlite3

DB_NAME = "users.db"

def create_location_table():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS locations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            method TEXT,
            latitude REAL,
            longitude REAL,
            timestamp TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def save_location(method, lat, lon):
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO locations (method, latitude, longitude) VALUES (?, ?, ?)", (method, lat, lon))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error saving location: {e}")
        return False

def get_last_saved_location():
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT latitude, longitude FROM locations ORDER BY id DESC LIMIT 1")
        result = cursor.fetchone()
        conn.close()
        return result if result else (None, None)
    except Exception as e:
        print(f"Error getting location: {e}")
        return None, None
