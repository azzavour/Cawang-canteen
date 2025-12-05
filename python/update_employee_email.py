import os
import sqlite3
from typing import Dict

import pyodbc
from dotenv import load_dotenv

from src.sqlite_database import get_db_connection


DUMMY_EMAILS: Dict[str, str] = {
    "34283": "annisafitriana38@gmail.com",
    "34283": "izzynisa.26@gmail.com",
    # Tambahkan mapping dummy lain di sini jika diperlukan.
}


def update_dummy_emails(conn: sqlite3.Connection) -> int:
    """
    Update kolom email untuk beberapa employee_id secara hardcoded (dummy/testing).
    Mengembalikan jumlah row yang diupdate.
    """
    updated_rows = 0
    cursor = conn.cursor()
    for employee_id, email in DUMMY_EMAILS.items():
        cursor.execute(
            "UPDATE employees SET email = ? WHERE employee_id = ?",
            (email, employee_id),
        )
        updated_rows += cursor.rowcount
    return updated_rows


def sync_emails_from_portal(conn: sqlite3.Connection) -> int:
    """
    Sinkronisasi email dari database portal ke tabel employees (SQLite).
    Mengembalikan jumlah row yang berhasil diupdate.
    """
    driver = os.getenv("PORTAL_DB_DRIVER")
    host = os.getenv("PORTAL_DB_HOST")
    port = os.getenv("PORTAL_DB_PORT", "1433")
    db_name = os.getenv("PORTAL_DB_NAME")
    user = os.getenv("PORTAL_DB_USER")
    password = os.getenv("PORTAL_DB_PASSWORD")
    table = os.getenv("PORTAL_DB_TABLE", "PortalEmployees")

    if not all([driver, host, db_name, user, password]):
        print("Portal DB configuration is incomplete. Skipping portal sync.")
        return 0

    conn_str = (
        f"DRIVER={{{driver}}};"
        f"SERVER={host},{port};"
        f"DATABASE={db_name};"
        f"UID={user};"
        f"PWD={password};"
    )

    try:
        portal_conn = pyodbc.connect(conn_str)
    except Exception as exc:
        print(f"Failed to connect to portal database: {exc}")
        return 0

    updated_rows = 0
    try:
        portal_cursor = portal_conn.cursor()
        portal_cursor.execute(
            f"""
            SELECT employee_id, email
            FROM {table}
            WHERE email IS NOT NULL
              AND email <> ''
            """
        )
        sqlite_cursor = conn.cursor()
        for employee_id, email in portal_cursor.fetchall():
            sqlite_cursor.execute(
                "UPDATE employees SET email = ? WHERE employee_id = ?",
                (email, employee_id),
            )
            updated_rows += sqlite_cursor.rowcount
    except Exception as exc:
        print(f"Failed to sync emails from portal: {exc}")
    finally:
        portal_conn.close()

    return updated_rows


def main() -> None:
    load_dotenv()
    conn = get_db_connection()
    try:
        dummy_updated = update_dummy_emails(conn)
        portal_updated = sync_emails_from_portal(conn)
        conn.commit()
    finally:
        conn.close()

    print(f"Dummy emails updated: {dummy_updated}")
    print(f"Portal emails updated: {portal_updated}")
    print(f"Total employees updated: {dummy_updated + portal_updated}")


if __name__ == "__main__":
    main()
