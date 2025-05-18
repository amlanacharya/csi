"""
Database operations for the attendance tracking system.
"""
import os
import sqlite3
import pandas as pd
from datetime import datetime
import config
from passlib.hash import pbkdf2_sha256
import pytz

# Ensure data directory exists
os.makedirs(os.path.dirname(config.DB_PATH), exist_ok=True)

def get_db_connection():
    """Create a database connection and return the connection object."""
    conn = sqlite3.connect(config.DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize the database with required tables."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Create users table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        department TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # Create attendance table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS attendance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        date DATE NOT NULL,
        check_in_time TIMESTAMP,
        check_out_time TIMESTAMP,
        status TEXT,
        notes TEXT,
        FOREIGN KEY (user_id) REFERENCES users (id),
        UNIQUE(user_id, date)
    )
    ''')

    # Create departments table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS departments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL
    )
    ''')

    # Insert default admin user if not exists
    cursor.execute("SELECT * FROM users WHERE username = 'admin'")
    if not cursor.fetchone():
        hash_password = pbkdf2_sha256.hash("admin123")
        cursor.execute(
            "INSERT INTO users (username, password_hash, role, name, email) VALUES (?, ?, ?, ?, ?)",
            ("admin", hash_password, "admin", "Administrator", "admin@example.com")
        )

    # Insert default departments if not exists
    default_departments = ["IT", "HR", "Finance", "Marketing", "Operations"]
    for dept in default_departments:
        cursor.execute("SELECT * FROM departments WHERE name = ?", (dept,))
        if not cursor.fetchone():
            cursor.execute("INSERT INTO departments (name) VALUES (?)", (dept,))

    conn.commit()
    conn.close()

# User operations
def add_user(username, password, role, name, email, department=None):
    """Add a new user to the database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    hash_password = pbkdf2_sha256.hash(password)

    try:
        cursor.execute(
            "INSERT INTO users (username, password_hash, role, name, email, department) VALUES (?, ?, ?, ?, ?, ?)",
            (username, hash_password, role, name, email, department)
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def verify_user(username, password):
    """Verify user credentials and return user data if valid."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()

    if user and pbkdf2_sha256.verify(password, user['password_hash']):
        return dict(user)
    return None

def get_user(user_id):
    """Get user by ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()

    return dict(user) if user else None

def get_all_users(role=None):
    """Get all users, optionally filtered by role."""
    conn = get_db_connection()
    cursor = conn.cursor()

    if role:
        cursor.execute("SELECT * FROM users WHERE role = ?", (role,))
    else:
        cursor.execute("SELECT * FROM users")

    users = [dict(row) for row in cursor.fetchall()]
    conn.close()

    return users

def update_user(user_id, name=None, email=None, department=None):
    """Update user information."""
    conn = get_db_connection()
    cursor = conn.cursor()

    update_fields = []
    params = []

    if name:
        update_fields.append("name = ?")
        params.append(name)
    if email:
        update_fields.append("email = ?")
        params.append(email)
    if department:
        update_fields.append("department = ?")
        params.append(department)

    if update_fields:
        query = f"UPDATE users SET {', '.join(update_fields)} WHERE id = ?"
        params.append(user_id)
        cursor.execute(query, params)
        conn.commit()
        success = True
    else:
        success = False

    conn.close()
    return success

def change_password(user_id, new_password):
    """Change user password."""
    conn = get_db_connection()
    cursor = conn.cursor()
    hash_password = pbkdf2_sha256.hash(new_password)

    cursor.execute("UPDATE users SET password_hash = ? WHERE id = ?", (hash_password, user_id))
    conn.commit()
    conn.close()
    return True

# Attendance operations
def record_check_in(user_id, date=None, time=None):
    """Record check-in time for a user."""
    # Get current time in India (GMT+5:30)
    india_tz = pytz.timezone('Asia/Kolkata')
    now = datetime.now(pytz.UTC).astimezone(india_tz)

    if date is None:
        date = now.strftime("%Y-%m-%d")
    if time is None:
        time = now.strftime("%Y-%m-%d %H:%M:%S")

    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if an entry already exists for this user and date
    cursor.execute("SELECT * FROM attendance WHERE user_id = ? AND date = ?", (user_id, date))
    existing = cursor.fetchone()

    if existing:
        # Update existing entry
        cursor.execute(
            "UPDATE attendance SET check_in_time = ? WHERE user_id = ? AND date = ?",
            (time, user_id, date)
        )
    else:
        # Create new entry
        cursor.execute(
            "INSERT INTO attendance (user_id, date, check_in_time, status) VALUES (?, ?, ?, ?)",
            (user_id, date, time, determine_status(time))
        )

    conn.commit()
    conn.close()
    return True

def record_check_out(user_id, date=None, time=None):
    """Record check-out time for a user."""
    # Get current time in India (GMT+5:30)
    india_tz = pytz.timezone('Asia/Kolkata')
    now = datetime.now(pytz.UTC).astimezone(india_tz)

    if date is None:
        date = now.strftime("%Y-%m-%d")
    if time is None:
        time = now.strftime("%Y-%m-%d %H:%M:%S")

    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if an entry exists for this user and date
    cursor.execute("SELECT * FROM attendance WHERE user_id = ? AND date = ?", (user_id, date))
    existing = cursor.fetchone()

    if existing:
        # Update existing entry
        cursor.execute(
            "UPDATE attendance SET check_out_time = ? WHERE user_id = ? AND date = ?",
            (time, user_id, date)
        )
        conn.commit()
        success = True
    else:
        # No check-in record found
        success = False

    conn.close()
    return success

def determine_status(check_in_time):
    """Determine attendance status based on check-in time."""
    india_tz = pytz.timezone('Asia/Kolkata')

    if isinstance(check_in_time, str):
        # Parse the string time and make it timezone-aware
        check_in_time = datetime.strptime(check_in_time, "%Y-%m-%d %H:%M:%S")
        check_in_time = india_tz.localize(check_in_time)

    # Create work start time with the same date as check-in time
    work_start_str = f"{check_in_time.strftime('%Y-%m-%d')} {config.WORK_START_TIME}:00"
    work_start = datetime.strptime(work_start_str, "%Y-%m-%d %H:%M:%S")
    work_start = india_tz.localize(work_start)

    # If check-in is later than threshold, mark as late
    if check_in_time > work_start:
        minutes_late = (check_in_time - work_start).seconds // 60
        if minutes_late > config.LATE_THRESHOLD:
            return config.STATUS_LATE

    return config.STATUS_PRESENT

def get_attendance(user_id, start_date=None, end_date=None):
    """Get attendance records for a user within a date range."""
    conn = get_db_connection()
    cursor = conn.cursor()

    query = "SELECT * FROM attendance WHERE user_id = ?"
    params = [user_id]

    if start_date:
        query += " AND date >= ?"
        params.append(start_date)
    if end_date:
        query += " AND date <= ?"
        params.append(end_date)

    query += " ORDER BY date DESC"
    cursor.execute(query, params)

    attendance = [dict(row) for row in cursor.fetchall()]
    conn.close()

    return attendance

def get_all_attendance(start_date=None, end_date=None, department=None):
    """Get all attendance records within a date range, optionally filtered by department."""
    conn = get_db_connection()
    cursor = conn.cursor()

    query = """
    SELECT a.*, u.name, u.username, u.department
    FROM attendance a
    JOIN users u ON a.user_id = u.id
    WHERE 1=1
    """
    params = []

    if start_date:
        query += " AND a.date >= ?"
        params.append(start_date)
    if end_date:
        query += " AND a.date <= ?"
        params.append(end_date)
    if department:
        query += " AND u.department = ?"
        params.append(department)

    query += " ORDER BY a.date DESC, u.name"
    cursor.execute(query, params)

    attendance = [dict(row) for row in cursor.fetchall()]
    conn.close()

    return attendance

def get_departments():
    """Get all departments."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM departments ORDER BY name")
    departments = [dict(row) for row in cursor.fetchall()]
    conn.close()

    return departments

def add_department(name):
    """Add a new department."""
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("INSERT INTO departments (name) VALUES (?)", (name,))
        conn.commit()
        success = True
    except sqlite3.IntegrityError:
        success = False

    conn.close()
    return success

# Initialize the database
init_db()
