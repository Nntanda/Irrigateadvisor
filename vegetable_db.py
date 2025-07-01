import sqlite3
from datetime import datetime

DB_NAME = "users.db"

def create_vegetable_table():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS vegetableSelections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vegetable TEXT,
            growthStage TEXT,
            timestamp TEXT
        )
    ''')
    conn.commit()
    conn.close()

def save_vegetable_selection(vegetable, growth_stage):
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        timestamp = datetime.now().isoformat()
        cursor.execute("INSERT INTO vegetableSelections (vegetable, growthStage, timestamp) VALUES (?, ?, ?)",
                       (vegetable, growth_stage, timestamp))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error saving vegetable selection: {e}")
        return False

def get_latest_vegetable_selection():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT vegetable, growthStage FROM vegetableSelections ORDER BY timestamp DESC LIMIT 1")
    row = cursor.fetchone()
    conn.close()
    if row:
        return row[0], row[1]
    return None, None
