import streamlit as st
import pandas as pd
from finance_tracker import *

setup_db()

st.title("💰 Personal Finance Tracker")

menu = st.sidebar.selectbox(
    "Menu",
    [
        "Add Income",
        "Add Expense",
        "Summary",
        "Transactions",
        "Graph",
        "Budget Score"
    ]
)

# ADD INCOME
if menu == "Add Income":

    st.header("Add Income")

    name = st.text_input("Income Source")
    amount = st.number_input("Amount", min_value=0.0)
    category = st.text_input("Category")

    if st.button("Add Income"):

        conn, cursor = connect_db()

        cursor.execute(
            f"""
            INSERT INTO {DB_TABLE}
            (date,name,amount,category,type)
            VALUES (CURDATE(),%s,%s,%s,'Income')
            """,
            (name, amount, category)
        )

        conn.commit()

        cursor.close()
        conn.close()

        st.success("Income Added")

# ADD EXPENSE
elif menu == "Add Expense":

    st.header("Add Expense")

    name = st.text_input("Expense Name")
    amount = st.number_input("Amount", min_value=0.0)
    category = st.text_input("Category")

    if st.button("Add Expense"):

        conn, cursor = connect_db()

        cursor.execute(
            f"""
            INSERT INTO {DB_TABLE}
            (date,name,amount,category,type)
            VALUES (CURDATE(),%s,%s,%s,'Expense')
            """,
            (name, amount, category)
        )

        conn.commit()

        cursor.close()
        conn.close()

        st.success("Expense Added")

# SUMMARY
elif menu == "Summary":

    data = fetch_data()

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

    balance = total_income - total_expense

    st.metric("Balance", f"₹{balance:.2f}")
    st.metric("Income", f"₹{total_income:.2f}")
    st.metric("Expense", f"₹{total_expense:.2f}")

# TRANSACTIONS
elif menu == "Transactions":

    data = fetch_data()

    if data:

        df = pd.DataFrame(data)

        st.dataframe(df)

# GRAPH
elif menu == "Graph":

    data = fetch_data()

    expenses = [
        d for d in data
        if d["type"] == "Expense"
    ]

    category_totals = {}

    for e in expenses:

        cat = e["category"]

        category_totals[cat] = (
            category_totals.get(cat, 0)
            + float(e["amount"])
        )

    if category_totals:

        import matplotlib.pyplot as plt

        fig, ax = plt.subplots()

        ax.pie(
            category_totals.values(),
            labels=category_totals.keys(),
            autopct="%1.1f%%"
        )

        st.pyplot(fig)

# BUDGET SCORE
elif menu == "Budget Score":

    budget = st.number_input(
        "Monthly Budget",
        min_value=0.0
    )

    if st.button("Calculate Score"):

        data = fetch_data()

        total_expense = sum(
            float(d["amount"])
            for d in data
            if d["type"] == "Expense"
        )

        if total_expense == 0:

            score = 100

        elif total_expense <= budget:

            score = 100

        else:

            score = (budget / total_expense) * 100

        st.metric(
            "Budget Score",
            f"{score:.1f}/100"
        )