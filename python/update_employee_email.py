
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "data" / "canteen.db"

EMPLOYEE_ID = "34283"  
NEW_EMAIL = "annisafitriana38@gmail.com"  


def main():
    print(f"Using database: {DB_PATH}")
    conn = sqlite3.connect(str(DB_PATH))
    cur = conn.cursor()

    cur.execute(
        "UPDATE employees SET email = ? WHERE employee_id = ?",
        (NEW_EMAIL, EMPLOYEE_ID),
    )
    conn.commit()

    cur.execute(
        "SELECT employee_id, name, email FROM employees WHERE employee_id = ?",
        (EMPLOYEE_ID,),
    )
    row = cur.fetchone()
    print("Updated row:", row)

    conn.close()


if __name__ == "__main__":
    main()
