import sqlite3

db_path = "backend/data/fitmind.db"

conn = sqlite3.connect(db_path)
c = conn.cursor()

# Insert a known user
c.execute("INSERT OR IGNORE INTO users (email, hashed_password) VALUES ('backup_user@example.com', 'hash')")
c.execute("SELECT id FROM users WHERE email='backup_user@example.com'")
user_id = c.fetchone()[0]

# Insert a known progress entry
c.execute("INSERT INTO progress (user_id, weight_kg, recorded_at) VALUES (?, ?, '2026-08-19T10:00:00Z')", (user_id, 70.0))
conn.commit()
conn.close()

print("Populated known record successfully.")
