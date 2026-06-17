import sqlite3
from pathlib import Path
import pandas as pd

DB_PATH = Path(__file__).parent / "glucoguard.db"


def get_connection():
    return sqlite3.connect(DB_PATH)


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        role TEXT DEFAULT 'standard',
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS glucose_records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        timestamp TEXT NOT NULL,
        glucose REAL NOT NULL,
        source TEXT DEFAULT 'manual',
        notes TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
    """)

    cursor.execute("""
    CREATE INDEX IF NOT EXISTS idx_glucose_user_time
    ON glucose_records(user_id, timestamp)
    """)

    cursor.execute("""
    INSERT OR IGNORE INTO users (id, username, role)
    VALUES (1, 'demo_user', 'standard')
    """)

    conn.commit()
    conn.close()


def add_glucose_record(user_id, timestamp, glucose, source="manual", notes=""):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO glucose_records (user_id, timestamp, glucose, source, notes)
    VALUES (?, ?, ?, ?, ?)
    """, (user_id, timestamp, glucose, source, notes))

    conn.commit()
    conn.close()


def get_glucose_records(user_id=1):
    conn = get_connection()

    df = pd.read_sql_query("""
    SELECT id, timestamp, glucose, source, notes, created_at
    FROM glucose_records
    WHERE user_id = ?
    ORDER BY timestamp ASC
    """, conn, params=(user_id,))

    conn.close()
    return df


def seed_demo_data():
    init_db()

    demo_records = [
        ("2026-06-17 08:00", 5.8, "historical", "demo breakfast"),
        ("2026-06-17 10:00", 6.4, "historical", "demo"),
        ("2026-06-17 12:00", 7.2, "historical", "after lunch"),
        ("2026-06-17 15:00", 6.1, "historical", "afternoon"),
        ("2026-06-17 18:00", 7.8, "historical", "after dinner"),
    ]

    for timestamp, glucose, source, notes in demo_records:
        add_glucose_record(1, timestamp, glucose, source, notes)


if __name__ == "__main__":
    seed_demo_data()
    print("Database initialized and demo data inserted.")
    print(get_glucose_records())