
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sklearn.linear_model import LinearRegression

st.set_page_config(page_title="Restaurant Financial Intelligence", layout="wide")

# ---------------- LOAD DATA ----------------
pd.read_csv("final_complete_restaurant_dataset.csv")
df["Date"] = pd.to_datetime(df["Date"])
df.dropna(inplace=True)

# ---------------- KPI CALCULATIONS ----------------
total_revenue = df["Revenue_Generated"].sum()
total_expense = df["Expense_Allocated"].sum()
total_net_profit = df["Net_Profit_After_Expense"].sum()
avg_margin = df["Net_Profit_Margin_%"].mean()

# ---------------- SIDEBAR ----------------
st.sidebar.title("📊 Filters")

product_list = df["Product_Name"].unique()
selected_product = st.sidebar.selectbox("Select Product", product_list)

st.sidebar.markdown("---")
st.sidebar.write("Dataset Version: v2.0")

# ---------------- TITLE ----------------
st.title("📈 Restaurant Financial Intelligence Dashboard")

# ---------------- KPI SECTION ----------------
col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Revenue", f"₹{total_revenue:,.0f}")
col2.metric("Total Expense", f"₹{total_expense:,.0f}")
col3.metric("Net Profit", f"₹{total_net_profit:,.0f}")
col4.metric("Avg Net Margin", f"{avg_margin:.2f}%")

st.markdown("---")

# ---------------- FILTERED DATA ----------------
filtered_df = df[df["Product_Name"] == selected_product]

# ---------------- DAILY FINANCIAL TREND ----------------
daily_summary = filtered_df.groupby("Date")[[
    "Revenue_Generated",
    "Expense_Allocated",
    "Net_Profit_After_Expense"
]].sum().reset_index()

fig1 = go.Figure()

fig1.add_trace(go.Scatter(
    x=daily_summary["Date"],
    y=daily_summary["Revenue_Generated"],
    mode='lines',
    name='Revenue'
))

fig1.add_trace(go.Scatter(
    x=daily_summary["Date"],
    y=daily_summary["Expense_Allocated"],
    mode='lines',
    name='Expense'
))

fig1.add_trace(go.Scatter(
    x=daily_summary["Date"],
    y=daily_summary["Net_Profit_After_Expense"],
    mode='lines',
    name='Net Profit'
))

fig1.update_layout(title=f"Daily Financial Trend - {selected_product}")

st.plotly_chart(fig1, use_container_width=True)

# ---------------- PRODUCT PERFORMANCE ----------------
st.subheader("📦 Product Performance Overview")

product_summary = df.groupby("Product_Name")[[
    "Revenue_Generated",
    "Net_Profit_After_Expense"
]].sum().reset_index()

fig2 = px.bar(
    product_summary,
    x="Product_Name",
    y="Revenue_Generated",
    title="Revenue by Product"
)

st.plotly_chart(fig2, use_container_width=True)

# ---------------- FORECASTING ----------------
st.subheader("📅 Revenue Forecast (Next 7 Days)")

daily_total = df.groupby("Date")["Revenue_Generated"].sum().reset_index()
daily_total["Date_Ordinal"] = daily_total["Date"].map(pd.Timestamp.toordinal)

model = LinearRegression()
model.fit(daily_total[["Date_Ordinal"]], daily_total["Revenue_Generated"])

last_date = daily_total["Date"].max()
future_dates = [last_date + pd.Timedelta(days=i) for i in range(1,8)]

future_df = pd.DataFrame({
    "Date_Ordinal": [d.toordinal() for d in future_dates]
})

predictions = model.predict(future_df)

forecast_df = pd.DataFrame({
    "Date": future_dates,
    "Predicted_Revenue": predictions
})

fig3 = go.Figure()

fig3.add_trace(go.Scatter(
    x=daily_total["Date"],
    y=daily_total["Revenue_Generated"],
    mode='lines',
    name='Actual'
))

fig3.add_trace(go.Scatter(
    x=forecast_df["Date"],
    y=forecast_df["Predicted_Revenue"],
    mode='lines',
    name='Forecast'
))

st.plotly_chart(fig3, use_container_width=True)

# ---------------- RECOMMENDATIONS ----------------
st.subheader("📌 Strategic Recommendations")

recommendations = []

if avg_margin < 20:
    recommendations.append("⚠ Profit margins are low. Immediate cost optimization required.")
elif avg_margin < 35:
    recommendations.append("⚠ Margins are moderate. Improve pricing or reduce expenses.")
else:
    recommendations.append("✅ Margins are healthy and stable.")

top_product = product_summary.sort_values(
    by="Revenue_Generated", ascending=False
).iloc[0]["Product_Name"]

lowest_product = product_summary.sort_values(
    by="Revenue_Generated"
).iloc[0]["Product_Name"]

recommendations.append(f"🎯 Focus marketing on high-performing product: {top_product}.")
recommendations.append(f"🔍 Review profitability strategy for: {lowest_product}.")

if total_expense > total_revenue * 0.7:
    recommendations.append("🚨 Expenses are consuming more than 70% of revenue. Reduce operational costs.")

for r in recommendations:
    st.write(r)
