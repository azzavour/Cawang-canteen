import random
import string
from typing import Set

from src.sqlite_database import get_db_connection

TOKEN_LENGTH = 6


def generate_unique_token(existing_tokens: Set[str]) -> str:
    characters = string.ascii_uppercase + string.digits
    while True:
        token = "".join(random.choices(characters, k=TOKEN_LENGTH))
        if token not in existing_tokens:
            return token


def ensure_token_column(cursor) -> None:
    cursor.execute("PRAGMA table_info(employees)")
    columns = {row["name"] for row in cursor.fetchall()}
    if "token" not in columns:
        print("Kolom token belum ada, menambahkan kolom token ke tabel employees...")
        cursor.execute("ALTER TABLE employees ADD COLUMN token TEXT")
    else:
        print("Kolom token sudah ada, lanjut generate token.")


def main() -> None:
    conn = get_db_connection()
    cursor = conn.cursor()

    ensure_token_column(cursor)

    cursor.execute("SELECT token FROM employees WHERE token IS NOT NULL AND token != ''")
    existing_tokens: Set[str] = {
        row["token"]
        for row in cursor.fetchall()
        if row["token"]
    }

    cursor.execute(
        "SELECT id, employee_id FROM employees WHERE token IS NULL OR token = ''"
    )
    employees_without_token = cursor.fetchall()

    if not employees_without_token:
        print("Semua karyawan sudah memiliki token.")
        conn.close()
        return

    for row in employees_without_token:
        token = generate_unique_token(existing_tokens)
        existing_tokens.add(token)
        cursor.execute(
            "UPDATE employees SET token = ? WHERE id = ?",
            (token, row["id"]),
        )
        print(f"Set token {token} for employee_id {row['employee_id']}")

    conn.commit()
    conn.close()
    print("Done generating tokens.")


if __name__ == "__main__":
    main()
