import sqlite3

conn = sqlite3.connect("cash.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS shifts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    admin_id INTEGER,
    start_cash REAL,
    end_cash REAL,
    is_open INTEGER
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    shift_id INTEGER,
    amount REAL,
    comment TEXT
)
""")

conn.commit()
