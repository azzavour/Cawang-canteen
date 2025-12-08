import sqlite3
from typing import Dict, Optional

from src.sqlite_database import get_db_connection

# Mapping dummy untuk testing lokal / sementara.
DUMMY_EMAILS: Dict[str, str] = {
    "34283": "annisafitriana38@gmail.com",
}


def update_employee_email(employee_id: str) -> Optional[str]:
    """
    Dipakai di runtime.
    1. Cek email di tabel employees (SQLite).
    2. Kalau sudah ada, return.
    3. Kalau kosong, cek DUMMY_EMAILS. Jika ada, update DB dan return.
    4. Kalau tidak punya email sama sekali, return None.
    """
    employee_id = (employee_id or "").strip()
    if not employee_id:
        return None

    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT email
            FROM employees
            WHERE employee_id = ?
            """,
            (employee_id,),
        )
        row = cursor.fetchone()
        if row:
            existing_email = (row["email"] or "").strip()
            if existing_email:
                return existing_email

        dummy_email = DUMMY_EMAILS.get(employee_id)
        if dummy_email:
            cursor.execute(
                """
                UPDATE employees
                SET email = ?
                WHERE employee_id = ?
                """,
                (dummy_email, employee_id),
            )
            conn.commit()
            return dummy_email
        return None
    finally:
        conn.close()


def update_dummy_emails() -> int:
    """
    Jalankan saat script dipanggil langsung.
    Mengisi email berdasarkan DUMMY_EMAILS.
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        updated_rows = 0
        for employee_id, email in DUMMY_EMAILS.items():
            cursor.execute(
                """
                UPDATE employees
                SET email = ?
                WHERE employee_id = ?
                """,
                (email, employee_id),
            )
            updated_rows += cursor.rowcount
        conn.commit()
        return updated_rows
    finally:
        conn.close()


if __name__ == "__main__":
    updated = update_dummy_emails()
    print(f"Dummy emails applied to SQLite employees table: {updated}")
