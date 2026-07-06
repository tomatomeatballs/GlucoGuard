"""
GlucoGuard - Database Management Module
Handles SQLite operations for storing and fetching glucose records.
"""

import sqlite3
import os
from datetime import datetime

# Database file location
DB_FILE = "glucoguard.db"


def init_db():
    """
    Initializes the database by creating the glucose records table if it doesn't exist.
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Create table with modern schema
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS glucose_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            glucose_value REAL,
            timestamp TEXT NOT NULL,
            user_id INTEGER DEFAULT 1
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS training_files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_name TEXT NOT NULL,
            file_size INTEGER,
            upload_time TEXT NOT NULL
        )
    """)
    
    # Critical Migration: Check if column names match old variations
    cursor.execute("PRAGMA table_info(glucose_records)")
    columns = [info[1] for info in cursor.fetchall()]
    
    # If the database has an old column name layout, rename it on the fly
    if "glucose" in columns and "glucose_value" not in columns:
        try:
            cursor.execute("ALTER TABLE glucose_records RENAME COLUMN glucose TO glucose_value")
        except Exception:
            pass
            
    conn.commit()
    conn.close()


def add_glucose_record(*args):
    """
    Adaptive helper function to insert a record.
    Guarantees runtime insertion safely regardless of variable layout.
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    if len(args) == 2:
        timestamp_str = args[0]
        input_glucose = args[1]
        user_id = 1
    elif len(args) == 3:
        user_id = args[0]
        timestamp_str = args[1]
        input_glucose = args[2]
    else:
        conn.close()
        raise ValueError("Invalid number of arguments passed to add_glucose_record.")
        
    cursor.execute("""
        INSERT INTO glucose_records (glucose_value, timestamp, user_id)
        VALUES (?, ?, ?)
    """, (float(input_glucose), str(timestamp_str), int(user_id)))
    
    conn.commit()
    conn.close()


def get_glucose_records():
    """
    Fetches historical records and normalizes them into standard data frames.
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT id, glucose_value, timestamp, user_id FROM glucose_records ORDER BY timestamp ASC")
        records = cursor.fetchall()
    except sqlite3.OperationalError:
        records = []
        
    conn.close()
    return records

def save_training_file_to_db(file_name, file_size, dataframe=None):
    """
    Saves the uploaded training file metadata securely to the SQLite database.
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    cursor.execute("""
        INSERT INTO training_files (file_name, file_size, upload_time)
        VALUES (?, ?, ?)
    """, (str(file_name), int(file_size), current_time))
    
    conn.commit()
    conn.close()