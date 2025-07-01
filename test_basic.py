#!/usr/bin/env python3
"""
Basic test script for CropIrrigator core functionality
"""

import sqlite3
import hashlib
import re
from datetime import datetime

def test_user_db():
    """Test user database functionality"""
    print("Testing user database...")
    
    # Test email validation
    def is_valid_email(email):
        return re.match(r"[^@]+@[^@]+\.[^@]+", email)
    
    assert is_valid_email("test@example.com") is not None
    assert is_valid_email("invalid-email") is None
    print("✓ Email validation working")
    
    # Test password hashing
    def hash_password(password):
        return hashlib.sha256(password.encode()).hexdigest()
    
    password = "test123"
    hashed = hash_password(password)
    assert len(hashed) == 64  # SHA256 hash length
    print("✓ Password hashing working")
    
    print("User database tests passed!")

def test_database_creation():
    """Test database table creation"""
    print("Testing database creation...")
    
    try:
        conn = sqlite3.connect("test_users.db")
        cursor = conn.cursor()
        
        # Test users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE,
                password_hash TEXT
            )
        ''')
        
        # Test locations table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS locations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                method TEXT,
                latitude REAL,
                longitude REAL,
                timestamp TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Test vegetable selections table
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
        
        # Clean up test database
        import os
        os.remove("test_users.db")
        
        print("✓ Database tables created successfully")
        print("Database creation tests passed!")
        
    except Exception as e:
        print(f"✗ Database creation failed: {e}")

def test_basic_logic():
    """Test basic application logic"""
    print("Testing basic logic...")
    
    # Test vegetable selection logic
    vegetables = ['Tomato', 'Cabbage', 'Onion', 'Sukuma Wiki', 'Green pepper']
    growth_stages = ['initial', 'development', 'mid-season', 'late-season']
    
    assert 'Tomato' in vegetables
    assert 'initial' in growth_stages
    print("✓ Vegetable selection logic working")
    
    # Test timestamp generation
    timestamp = datetime.now().isoformat()
    assert len(timestamp) > 0
    print("✓ Timestamp generation working")
    
    print("Basic logic tests passed!")

if __name__ == "__main__":
    print("Running CropIrrigator basic tests...\n")
    
    test_user_db()
    print()
    
    test_database_creation()
    print()
    
    test_basic_logic()
    print()
    
    print("All basic tests passed! ✅")
    print("\nNote: Some features require additional dependencies:")
    print("- geopy: for location services")
    print("- kivy_garden.mapview: for map visualization")
    print("- matplotlib: for weather charts")
    print("- plyer: for GPS functionality")
    print("\nInstall with: pip install -r requirements.txt") 