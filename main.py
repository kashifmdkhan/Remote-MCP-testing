from fastmcp import FastMCP
import os
import sqlite3
from contextlib import closing

# Writable location inside the container. Override with the EXPENSE_DB_PATH
# environment variable, e.g. /data/expense.db when a persistent volume is mounted.
DB_PATH = os.environ.get("EXPENSE_DB_PATH", "/tmp/expense.db")

mcp = FastMCP("ExpenseTracker")


def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    with closing(sqlite3.connect(DB_PATH)) as conn:
        with conn:  # commits on success
            conn.execute("""
                CREATE TABLE IF NOT EXISTS expenses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT NOT NULL,
                    amount REAL NOT NULL,
                    category TEXT NOT NULL,
                    subcategory TEXT DEFAULT '',
                    note TEXT DEFAULT ''
                )
            """)


init_db()


@mcp.tool
def add_expense(date: str, amount: float, category: str, subcategory: str = "", note: str = ""):
    """Add a new expense entry to the database. Date format: YYYY-MM-DD."""
    with closing(sqlite3.connect(DB_PATH)) as conn:
        with conn:
            cur = conn.execute(
                "INSERT INTO expenses (date, amount, category, subcategory, note) VALUES (?, ?, ?, ?, ?)",
                (date, amount, category, subcategory, note),
            )
            return {"status": "ok", "id": cur.lastrowid}


@mcp.tool
def list_expenses(start_date: str, end_date: str):
    """Retrieves list of all expense entries between start_date and end_date (YYYY-MM-DD)."""
    with closing(sqlite3.connect(DB_PATH)) as conn:
        cur = conn.execute(
            "SELECT id, date, amount, category, subcategory, note FROM expenses "
            "WHERE date BETWEEN ? AND ? ORDER BY id ASC",
            (start_date, end_date),
        )
        cols = [d[0] for d in cur.description]
        return [dict(zip(cols, r)) for r in cur.fetchall()]


if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=8000)