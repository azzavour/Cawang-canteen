import sqlite3

DB_PATH = "sqlite_database.db"  

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

try:
    cursor.execute("ALTER TABLE employees ADD COLUMN token TEXT;")
    print("Kolom 'token' berhasil ditambahkan ke tabel employees.")
except Exception as e:
    print("Kolom 'token' mungkin sudah ada. Error:")
    print(e)

conn.commit()
conn.close()
print("Selesai.")
