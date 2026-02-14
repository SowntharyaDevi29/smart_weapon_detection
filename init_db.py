import sqlite3

conn = sqlite3.connect("weapon.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS detections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    weapon_name TEXT,
    image TEXT,
    datetime TEXT
)
""")

conn.commit()
conn.close()

print("Database created successfully")
