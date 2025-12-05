import sqlite3


def main() -> None:
    conn = sqlite3.connect("sqlite_database.db")
    cursor = conn.cursor()

    cursor.execute("PRAGMA table_info(employees)")
    columns = [row[1] for row in cursor.fetchall()]

    if "email" in columns:
        print("Kolom 'email' sudah ada, tidak perlu ditambahkan.")
        conn.close()
        return

    cursor.execute("ALTER TABLE employees ADD COLUMN email TEXT")
    conn.commit()
    conn.close()
    print("Kolom 'email' berhasil ditambahkan ke tabel employees.")


if __name__ == "__main__":
    main()
