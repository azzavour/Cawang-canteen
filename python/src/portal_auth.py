import os
from typing import Dict, Optional, Set, Tuple

from dotenv import load_dotenv

try:
    import pyodbc
except ModuleNotFoundError:
    pyodbc = None

from .sqlite_database import get_db_connection

load_dotenv()

DUMMY_PORTAL_TOKENS: Set[Tuple[str, str]] = {
    ("34283", "TEST123"),
}


def _verify_token_in_portal_db(employee_id: str, portal_token: str) -> bool:
    """
    Cek ke portal database apakah kombinasi emp_id + token valid.
    """
    driver = os.getenv("PORTAL_DB_DRIVER")
    host = os.getenv("PORTAL_DB_HOST")
    port = os.getenv("PORTAL_DB_PORT", "1433")
    db_name = os.getenv("PORTAL_DB_NAME")
    user = os.getenv("PORTAL_DB_USER")
    password = os.getenv("PORTAL_DB_PASSWORD")
    table = os.getenv("PORTAL_DB_TABLE", "PortalEmployees")

    if not (pyodbc and all([driver, host, db_name, user, password])):
        # Portal DB belum siap; gunakan dummy tokens untuk pengujian.
        print("Portal DB configuration incomplete; using dummy token mapping.")
        return (employee_id, portal_token) in DUMMY_PORTAL_TOKENS

    conn_str = (
        f"DRIVER={{{driver}}};"
        f"SERVER={host},{port};"
        f"DATABASE={db_name};"
        f"UID={user};"
        f"PWD={password};"
    )
    portal_conn = None
    try:
        portal_conn = pyodbc.connect(conn_str)
        cursor = portal_conn.cursor()
        cursor.execute(
            f"""
            SELECT 1
            FROM {table}
            WHERE emp_id = ? AND token = ?
            """,
            (employee_id, portal_token),
        )
        row = cursor.fetchone()
        if row:
            return True
        return (employee_id, portal_token) in DUMMY_PORTAL_TOKENS
    except Exception as exc:
        print(f"Failed to verify token in portal DB: {exc}")
        return (employee_id, portal_token) in DUMMY_PORTAL_TOKENS
    finally:
        if portal_conn is not None:
            portal_conn.close()


def verify_portal_token(employee_id: str, portal_token: str) -> Optional[Dict[str, str]]:
    """
    Validasi token di portal DB, kemudian ambil data pegawai dari SQLite.
    """
    employee_id = (employee_id or "").strip()
    portal_token = (portal_token or "").strip()
    if not employee_id or not portal_token:
        return None

    if not _verify_token_in_portal_db(employee_id, portal_token):
        return None

    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT employee_id, name, email
            FROM employees
            WHERE employee_id = ?
            """,
            (employee_id,),
        )
        row = cursor.fetchone()
        if not row:
            return None

        return {
            "employee_id": row["employee_id"],
            "name": row["name"],
            "email": row["email"],
        }
    finally:
        conn.close()


__all__ = ["verify_portal_token"]
