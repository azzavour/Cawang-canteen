import sys
from pathlib import Path

# Ensure src directory is on the Python path so we can import email_service.
BASE_DIR = Path(__file__).resolve().parent
SRC_DIR = BASE_DIR / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from src.sqlite_database import get_db_connection
from email_service import send_employee_token_email


def main() -> None:
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            SELECT employee_id, name, email, token
            FROM employees
            WHERE email IS NOT NULL
              AND TRIM(email) != ''
              AND token IS NOT NULL
              AND TRIM(token) != ''
            """
        )
        employees = cursor.fetchall()

        total = len(employees)
        sent_count = 0
        failed_count = 0

        for employee in employees:
            try:
                send_employee_token_email(
                    to_email=employee["email"],
                    employee_name=employee["name"],
                    employee_id=employee["employee_id"],
                    token=employee["token"],
                )
                sent_count += 1
            except Exception as exc:
                failed_count += 1
                print(
                    f"Failed to send token email to {employee['email']} "
                    f"({employee['employee_id']}): {exc}"
                )

        print(
            f"Attempted to send token emails to {total} employees "
            f"(success: {sent_count}, failed: {failed_count})"
        )
    finally:
        conn.close()


if __name__ == "__main__":
    main()
