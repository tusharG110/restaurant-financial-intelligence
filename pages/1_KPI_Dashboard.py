import streamlit as st
import pandas as pd
import plotly.express as px

st.title("📈 KPI Dashboard")

df = pd.read_csv("final_complete_restaurant_dataset.csv")
df["Date"] = pd.to_datetime(df["Date"])

total_revenue = df["Revenue_Generated"].sum()
total_expense = df["Expense_Allocated"].sum()
net_profit = df["Net_Profit_After_Expense"].sum()
avg_margin = df["Net_Profit_Margin_%"].mean()

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Revenue", f"₹{total_revenue:,.0f}")
col2.metric("Total Expense", f"₹{total_expense:,.0f}")
col3.metric("Net Profit", f"₹{net_profit:,.0f}")
col4.metric("Avg Net Margin", f"{avg_margin:.2f}%")

monthly = df.groupby(df["Date"].dt.to_period("M"))["Net_Profit_After_Expense"].sum().reset_index()
monthly["Date"] = monthly["Date"].astype(str)

fig = px.bar(monthly, x="Date", y="Net_Profit_After_Expense",
             title="Monthly Net Profit")

st.plotly_chart(fig, use_container_width=True)
