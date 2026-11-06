from fastmcp import FastMCP
import os
import sqlite3

DB_PATH = os.path.join(os.path.dirname(__file__), "expense.db")

mcp = FastMCP("ExpenseTracker")

def init_db():
    with sqlite3.connect(DB_PATH) as c:
        c.execute("""
            CREATE TABLE IF NOT EXISTS expenses(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            amount REAL NOT NULL,
            CATEGORY TEXT NOT NULL,
            SUBCATEGORY TEXT DEFAULT '',
            NOTE TEXT DEFAULT ''
            )
""")

init_db()


@mcp.tool
def add_expense(date, amount, category, subcategory="", note=""):
    """Add a new expense entry to the database."""
    with sqlite3.connect(DB_PATH) as c:
        cur = c.execute(
            "INSERT INTO EXPENSES (DATE, AMOUNT, CATEGORY, SUBCATEGORY, NOTE) VALUES(?,?,?,?,?)",
            (date, amount, category, subcategory, note)
        )

        return {"status":"ok", "id": cur.lastrowid}

@mcp.tool
def list_expenses(start_date, end_date):
    """Retrieves List of all expense entries from database"""
    with sqlite3.connect(DB_PATH) as c:
        cur = c.execute(
            "SELECT id, date, amount, category, subcategory, note FROM EXPENSES " \
            "WHERE date BETWEEN ? AND ? "
            "ORDER BY id ASC",
            (start_date, end_date)
        )

        cols = [d[0] for d in cur.description]
        return [dict(zip(cols, r)) for r in cur.fetchall()]



if __name__=="__main__":
    mcp.run(transport="http", host="0.0.0.0", port=8000)