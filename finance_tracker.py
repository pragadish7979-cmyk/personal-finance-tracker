import mysql.connector
from datetime import date
import matplotlib.pyplot as plt

# ---------------- CONFIGURATION ----------------

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "Prawin2425"
}

DB_NAME = "finance_tracker"
DB_TABLE = "transactions"

# ---------------- DATABASE UTILITIES ----------------

def create_database_if_not_exists():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()

        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")

        conn.commit()
        cursor.close()
        conn.close()

    except mysql.connector.Error as err:
        print(f"❌ Error connecting to MySQL Server: {err}")
        print("💡 Hint: Is MySQL running?")


def connect_db():
    try:
        config_with_db = DB_CONFIG.copy()
        config_with_db["database"] = DB_NAME

        conn = mysql.connector.connect(**config_with_db)
        cursor = conn.cursor(dictionary=True)

        return conn, cursor

    except mysql.connector.Error as err:
        print(f"❌ MySQL Connection Error: {err}")
        return None, None


def setup_db():
    create_database_if_not_exists()

    conn, cursor = connect_db()

    if conn is None:
        return

    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {DB_TABLE} (
            id INT AUTO_INCREMENT PRIMARY KEY,
            date DATE NOT NULL,
            name VARCHAR(100) NOT NULL,
            amount DECIMAL(10,2) NOT NULL,
            category VARCHAR(50) NOT NULL,
            type ENUM('Income','Expense') NOT NULL
        )
    """)

    conn.commit()
    cursor.close()
    conn.close()

    print("✅ Database and Tables are ready.")

# ---------------- TRANSACTION FUNCTIONS ----------------

def get_transaction_input(trans_type):

    print(f"\n--- Add {trans_type} ---")

    while True:
        try:
            name = input(
                f"Enter {trans_type} Name/Source: "
            ).strip()

            if not name:
                print("❗ Name cannot be empty.")
                continue

            amount = float(
                input(
                    f"Enter {trans_type} Amount: "
                )
            )

            category = input(
                f"Enter {trans_type} Category: "
            ).strip()

            if amount <= 0:
                print("❗ Amount must be positive.")
                continue

            if not category:
                print("❗ Category cannot be empty.")
                continue

            return name, amount, category

        except ValueError:
            print("❗ Enter a valid number for amount.")


def add_transaction(trans_type):

    name, amount, category = get_transaction_input(
        trans_type
    )

    today = date.today()

    conn, cursor = connect_db()

    if conn is None:
        return

    try:

        cursor.execute(
            f"""
            INSERT INTO {DB_TABLE}
            (date, name, amount, category, type)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (
                today,
                name,
                amount,
                category,
                trans_type
            )
        )

        conn.commit()

        print(
            f"✅ {trans_type} added successfully."
        )

    except mysql.connector.Error as err:
        print(
            f"❌ Error adding transaction: {err}"
        )

    finally:
        if cursor:
            cursor.close()

        if conn:
            conn.close()

# ---------------- FETCH DATA ----------------

def fetch_data(where_clause=""):

    conn, cursor = connect_db()

    if conn is None:
        return []

    try:

        cursor.execute(
            f"""
            SELECT *
            FROM {DB_TABLE}
            {where_clause}
            ORDER BY date DESC
            """
        )

        return cursor.fetchall()

    except mysql.connector.Error as err:

        print(
            f"❌ Error fetching data: {err}"
        )

        return []

    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()

# ---------------- FILTER ----------------

def display_filtered_transactions():

    print("\n--- Filter Transactions ---")

    print("1. By Date Range")
    print("2. By Category")

    choice = input(
        "Enter choice (1/2): "
    )

    where = ""

    if choice == "1":

        start = input(
            "Start Date (YYYY-MM-DD): "
        ).strip()

        end = input(
            "End Date (YYYY-MM-DD): "
        ).strip()

        where = (
            f"WHERE date BETWEEN "
            f"'{start}' AND '{end}'"
        )

    elif choice == "2":

        cat = input(
            "Enter Category: "
        ).strip()

        where = (
            f"WHERE category = '{cat}'"
        )

    else:
        print("❌ Invalid choice.")
        return

    data = fetch_data(where)

    if not data:
        print("\nNo matching records found.")
        return

    print("\n--- FILTERED RESULTS ---")

    for row in data:

        print(
            f"{row['date']} | "
            f"{row['name']} | "
            f"{row['type']} | "
            f"{row['amount']} | "
            f"{row['category']}"
        )

    print("-" * 50)

# ---------------- SUMMARY ----------------

def display_details_summary():

    data = fetch_data()

    if not data:
        print("No data available.")
        return

    total_income = sum(
        float(d["amount"])
        for d in data
        if d["type"] == "Income"
    )

    total_expense = sum(
        float(d["amount"])
        for d in data
        if d["type"] == "Expense"
    )

    net = total_income - total_expense

    print(
        f"\n💰 Net Balance: ₹{net:.2f}"
    )

    print(
        f"Income: ₹{total_income:.2f} | "
        f"Expense: ₹{total_expense:.2f}"
    )

    print("-" * 50)

    monthly = {}

    for row in data:

        month_key = row["date"].strftime(
            "%Y-%m"
        )

        if month_key not in monthly:

            monthly[month_key] = {
                "Income": 0,
                "Expense": 0
            }

        monthly[month_key][
            row["type"]
        ] += float(row["amount"])

    print(
        "\n📅 Monthly Summary "
        "(Last 3 Months):"
    )

    for m in sorted(
        list(monthly.keys())
    )[-3:]:

        inc = monthly[m]["Income"]
        exp = monthly[m]["Expense"]

        print(
            f"{m} -> "
            f"Income: ₹{inc:.0f}, "
            f"Expense: ₹{exp:.0f}"
        )

# ---------------- GRAPH ----------------

def show_category_graph():

    data = fetch_data()

    expenses = [
        d for d in data
        if d["type"] == "Expense"
    ]

    if not expenses:
        print("No expenses to display.")
        return

    category_totals = {}

    for e in expenses:

        cat = e["category"]

        amt = float(
            e["amount"]
        )

        category_totals[cat] = (
            category_totals.get(cat, 0)
            + amt
        )

    plt.figure(figsize=(6, 6))

    plt.pie(
        list(category_totals.values()),
        labels=list(category_totals.keys()),
        autopct="%1.1f%%"
    )

    plt.title("Expense Breakdown")
    plt.show()

# ---------------- BUDGET SCORE ----------------

def calculate_budget_score():

    try:

        budget = float(
            input(
                "Enter your monthly expense budget: "
            )
        )

    except ValueError:

        print("Invalid number.")
        return

    data = fetch_data()

    today_month = date.today().strftime(
        "%Y-%m"
    )

    month_exp = sum(
        float(d["amount"])
        for d in data
        if d["type"] == "Expense"
        and d["date"].strftime("%Y-%m")
        == today_month
    )

    print(
        f"\nBudget: ₹{budget:.2f}"
    )

    print(
        f"Actual Expenses "
        f"({today_month}): "
        f"₹{month_exp:.2f}"
    )

    if month_exp == 0:

        print("Score: 100/100")

    elif month_exp <= budget:

        print(
            "Score: 100/100 "
            "(Within Budget)"
        )

    else:

        score = (
            budget / month_exp
        ) * 100

        print(
            f"Score: {score:.1f}/100"
        )

# ---------------- MAIN MENU ----------------

def main_menu():

    setup_db()

    while True:

        print(
            "\n===== PERSONAL FINANCE TRACKER ====="
        )

        print(
            "1. Add Income"
        )

        print(
            "2. Add Expense"
        )

        print(
            "3. Summary"
        )

        print(
            "4. Filter"
        )

        print(
            "5. Graph"
        )

        print(
            "6. Budget Score"
        )

        print(
            "7. Exit"
        )

        ch = input(
            "Enter choice: "
        ).strip()

        if ch == "1":

            add_transaction("Income")

        elif ch == "2":

            add_transaction("Expense")

        elif ch == "3":

            display_details_summary()

        elif ch == "4":

            display_filtered_transactions()

        elif ch == "5":

            show_category_graph()

        elif ch == "6":

            calculate_budget_score()

        elif ch == "7":

            break

        else:

            print(
                "Invalid choice."
            )


if __name__ == "__main__":
    main_menu()