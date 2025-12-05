import sqlite3
from pathlib import Path


DB_PATH = Path(__file__).parent.parent / "data" / "canteen.db"

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

cur.execute("PRAGMA table_info(preorders);")
columns = [row[1] for row in cur.fetchall()]
print("Existing columns in preorders:", columns)

if "ticket_number" not in columns:
    print("Adding ticket_number column...")
    cur.execute("ALTER TABLE preorders ADD COLUMN ticket_number TEXT;")
    conn.commit()
    print("ticket_number column added.")
else:
    print("ticket_number column already exists, nothing to do.")

conn.close()
