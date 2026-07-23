"""
GlucoGuard - Database Management Module
Handles SQLite operations for storing and fetching glucose records.
"""

import sqlite3
import os
import hashlib
import secrets
from datetime import datetime

# Database file location
DB_FILE = "glucoguard.db"


def init_db():
    """
    Initializes the database by creating the users, glucose_records, and training_files
    tables if they do not exist, then seeds the built-in demo accounts.
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Users table (stores a hashed password + per-user salt, never the plain password)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT,
            salt TEXT,
            name TEXT,
            role TEXT DEFAULT 'standard',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

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

    # Per-user file storage: raw uploads, sliding-window datasets, and algorithm
    # results all live here, distinguished by file_type. Content is stored directly
    # in the database (BLOB) so nothing depends on local disk paths at deploy time.
    # History is kept (no overwrite) — every save is a new row.
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            file_type TEXT NOT NULL,
            file_name TEXT NOT NULL,
            file_content BLOB NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    # Migration: add the authentication columns to an older users table that lacks them
    cursor.execute("PRAGMA table_info(users)")
    user_columns = [info[1] for info in cursor.fetchall()]
    for col_name, col_type in (("password_hash", "TEXT"), ("salt", "TEXT"), ("name", "TEXT")):
        if col_name not in user_columns:
            try:
                cursor.execute(f"ALTER TABLE users ADD COLUMN {col_name} {col_type}")
            except Exception:
                pass

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

    # Seed the built-in demo accounts so existing logins keep working (now DB-backed)
    _ensure_demo_user("admin", "123456", "Super Admin", "Administrator")
    _ensure_demo_user("user", "123456", "Normal User", "Standard User")


# ==================== AUTHENTICATION ====================

def _hash_password(password, salt):
    """Hash a password with the given hex salt using PBKDF2-HMAC-SHA256."""
    return hashlib.pbkdf2_hmac(
        "sha256", str(password).encode("utf-8"), bytes.fromhex(salt), 100000
    ).hex()


def _ensure_demo_user(username, password, name, role):
    """Create a demo account if missing, or backfill its password if it predates hashing."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT id, password_hash FROM users WHERE username = ?", (username,))
    row = cursor.fetchone()
    salt = secrets.token_hex(16)
    pw_hash = _hash_password(password, salt)
    if row is None:
        cursor.execute(
            "INSERT INTO users (username, password_hash, salt, name, role) VALUES (?, ?, ?, ?, ?)",
            (username, pw_hash, salt, name, role),
        )
    elif not row[1]:
        cursor.execute(
            "UPDATE users SET password_hash = ?, salt = ?, name = COALESCE(name, ?), role = COALESCE(role, ?) WHERE username = ?",
            (pw_hash, salt, name, role, username),
        )
    conn.commit()
    conn.close()


def register_user(username, password, name=None, role="standard"):
    """
    Register a new user with a securely hashed password.
    Returns a (success: bool, message: str) tuple.
    """
    username = (username or "").strip()
    if not username or not password:
        return False, "Username and password cannot be empty."

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
    if cursor.fetchone() is not None:
        conn.close()
        return False, "This username is already taken."

    salt = secrets.token_hex(16)
    pw_hash = _hash_password(password, salt)
    cursor.execute(
        "INSERT INTO users (username, password_hash, salt, name, role) VALUES (?, ?, ?, ?, ?)",
        (username, pw_hash, salt, name or username, role),
    )
    conn.commit()
    conn.close()
    return True, "Account created successfully."


def verify_user(username, password):
    """
    Verify login credentials against the database.
    Returns a user dict on success, or None on failure.
    """
    username = (username or "").strip()
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, username, password_hash, salt, name, role FROM users WHERE username = ?",
        (username,),
    )
    row = cursor.fetchone()
    conn.close()
    if row is None:
        return None

    user_id, uname, pw_hash, salt, name, role = row
    if not pw_hash or not salt:
        return None
    if _hash_password(password, salt) == pw_hash:
        return {"user_id": user_id, "username": uname, "name": name or uname, "role": role or "standard"}
    return None


def get_all_users():
    """Return all registered users (id, username, name, role, created_at) for the admin view."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id, username, name, role, created_at FROM users ORDER BY id ASC")
        rows = cursor.fetchall()
    except sqlite3.OperationalError:
        rows = []
    conn.close()
    return rows


# ==================== PER-USER FILE STORAGE ====================

def save_user_file(user_id, file_type, file_name, file_content):
    """
    Save a file's raw bytes into the database for a given user.
    file_type: one of 'raw_upload', '15min_data', '30min_data', '50min_data',
               'prediction_15min'/'30min'/'50min', 'metrics_15min'/'30min'/'50min'.
    Does NOT overwrite previous files of the same type — every call adds a new row,
    so a user's upload/training history is preserved.
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO user_files (user_id, file_type, file_name, file_content) VALUES (?, ?, ?, ?)",
        (int(user_id), str(file_type), str(file_name), sqlite3.Binary(bytes(file_content))),
    )
    conn.commit()
    conn.close()


def get_user_files(user_id, file_type=None):
    """
    Return a user's own files (id, file_type, file_name, created_at) — newest first.
    Does not return file_content (kept out to avoid loading large blobs for a list view);
    use get_user_file_content() to fetch one file's actual bytes.
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    if file_type:
        cursor.execute(
            "SELECT id, file_type, file_name, created_at FROM user_files "
            "WHERE user_id = ? AND file_type = ? ORDER BY id DESC",
            (user_id, file_type),
        )
    else:
        cursor.execute(
            "SELECT id, file_type, file_name, created_at FROM user_files "
            "WHERE user_id = ? ORDER BY id DESC",
            (user_id,),
        )
    rows = cursor.fetchall()
    conn.close()
    return rows


def get_all_user_files():
    """
    Admin view: every file from every user, joined with the owning username.
    Returns (id, username, file_type, file_name, created_at) — newest first.
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT user_files.id, users.username, user_files.file_type,
               user_files.file_name, user_files.created_at
        FROM user_files
        JOIN users ON users.id = user_files.user_id
        ORDER BY user_files.id DESC
    """)
    rows = cursor.fetchall()
    conn.close()
    return rows


def get_user_file_content(file_id):
    """Fetch one file's raw bytes + name by its row id (for download/preview)."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT file_name, file_content FROM user_files WHERE id = ?", (file_id,))
    row = cursor.fetchone()
    conn.close()
    if row is None:
        return None, None
    return row[0], row[1]


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