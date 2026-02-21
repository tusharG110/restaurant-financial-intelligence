import streamlit as st
import pandas as pd
import plotly.express as px

st.title("📦 Product Analytics")

df = pd.read_csv("final_complete_restaurant_dataset.csv")

product_summary = df.groupby("Product_Name")["Net_Profit_After_Expense"].sum().reset_index()

fig = px.bar(product_summary,
             x="Product_Name",
             y="Net_Profit_After_Expense",
             title="Net Profit by Product")

st.plotly_chart(fig, use_container_width=True)

top3 = product_summary.sort_values(by="Net_Profit_After_Expense", ascending=False).head(3)
bottom3 = product_summary.sort_values(by="Net_Profit_After_Expense").head(3)

st.subheader("🏆 Top 3 Products")
st.dataframe(top3)

st.subheader("⚠️ Bottom 3 Products")
st.dataframe(bottom3)
