import streamlit as st
import pandas as pd

st.title("🧮 Scenario Simulator")

df = pd.read_csv("final_complete_restaurant_dataset.csv")

cost_increase = st.slider("Increase Expenses (%)", 0, 50, 10)

adjusted_expense = df["Expense_Allocated"] * (1 + cost_increase/100)
adjusted_profit = df["Revenue_Generated"] - adjusted_expense

st.metric("Projected Net Profit",
          f"₹{adjusted_profit.sum():,.0f}")
