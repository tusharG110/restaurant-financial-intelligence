import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sklearn.linear_model import LinearRegression

# ================= PAGE CONFIG =================
st.set_page_config(
    page_title="Restaurant Financial Intelligence",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ================= LOAD DATA =================
df = pd.read_csv("final_complete_restaurant_dataset.csv")
df["Date"] = pd.to_datetime(df["Date"])

# ================= THEME TOGGLE =================
theme = st.toggle("🌗 Dark Mode", value=True)

if not theme:
    st.markdown(
        """
        <style>
        body {background-color: white; color: black;}
        </style>
        """,
        unsafe_allow_html=True
    )

# ================= NAVBAR =================
st.markdown("## 📊 Restaurant Financial Intelligence Platform")

page = st.radio(
    "",
    ["Executive Overview", "KPI Dashboard", "Product Analytics",
     "Forecasting", "Scenario Simulator"],
    horizontal=True
)

st.divider()

# ================= EXECUTIVE OVERVIEW =================
if page == "Executive Overview":

    total_revenue = df["Revenue_Generated"].sum()
    total_expense = df["Expense_Allocated"].sum()
    net_profit = df["Net_Profit_After_Expense"].sum()
    avg_margin = df["Net_Profit_Margin_%"].mean()

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Revenue", f"₹{total_revenue:,.0f}")
    col2.metric("Total Expense", f"₹{total_expense:,.0f}")
    col3.metric("Net Profit", f"₹{net_profit:,.0f}")
    col4.metric("Avg Net Margin", f"{avg_margin:.2f}%")

    st.markdown("### 📌 Strategic Insight")

    if avg_margin > 40:
        st.success("Margins are strong and healthy.")
    elif avg_margin > 30:
        st.warning("Margins are moderate. Cost optimization advised.")
    else:
        st.error("Margins are weak. Immediate pricing or cost action required.")

# ================= KPI DASHBOARD =================
elif page == "KPI Dashboard":

    monthly = df.groupby(df["Date"].dt.to_period("M"))[
        ["Revenue_Generated", "Expense_Allocated", "Net_Profit_After_Expense"]
    ].sum().reset_index()

    monthly["Date"] = monthly["Date"].astype(str)

    fig = px.line(monthly,
                  x="Date",
                  y=["Revenue_Generated",
                     "Expense_Allocated",
                     "Net_Profit_After_Expense"],
                  title="Monthly Financial Trend")

    st.plotly_chart(fig, use_container_width=True)

# ================= PRODUCT ANALYTICS =================
elif page == "Product Analytics":

    product_summary = df.groupby("Product_Name")[
        "Net_Profit_After_Expense"
    ].sum().reset_index()

    fig = px.bar(product_summary,
                 x="Product_Name",
                 y="Net_Profit_After_Expense",
                 title="Net Profit by Product")

    st.plotly_chart(fig, use_container_width=True)

    top3 = product_summary.sort_values(
        by="Net_Profit_After_Expense", ascending=False
    ).head(3)

    bottom3 = product_summary.sort_values(
        by="Net_Profit_After_Expense"
    ).head(3)

    col1, col2 = st.columns(2)
    col1.dataframe(top3, use_container_width=True)
    col2.dataframe(bottom3, use_container_width=True)

# ================= FORECASTING =================
elif page == "Forecasting":

    daily = df.groupby("Date")["Revenue_Generated"].sum().reset_index()
    daily["Date_Ordinal"] = daily["Date"].map(pd.Timestamp.toordinal)

    model = LinearRegression()
    model.fit(daily[["Date_Ordinal"]], daily["Revenue_Generated"])

    future_dates = pd.date_range(
        daily["Date"].max(), periods=8
    )[1:]

    future_df = pd.DataFrame(
        {"Date_Ordinal": future_dates.map(pd.Timestamp.toordinal)}
    )

    predictions = model.predict(future_df)

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=daily["Date"],
        y=daily["Revenue_Generated"],
        name="Actual"
    ))
    fig.add_trace(go.Scatter(
        x=future_dates,
        y=predictions,
        name="Forecast"
    ))

    st.plotly_chart(fig, use_container_width=True)

# ================= SCENARIO SIMULATOR =================
elif page == "Scenario Simulator":

    cost_increase = st.slider(
        "Increase Expenses (%)", 0, 50, 10
    )

    adjusted_expense = df["Expense_Allocated"] * (
        1 + cost_increase / 100
    )
    adjusted_profit = df["Revenue_Generated"] - adjusted_expense

    st.metric(
        "Projected Net Profit",
        f"₹{adjusted_profit.sum():,.0f}"
    )

# ================= DOWNLOAD REPORT =================
st.divider()
st.download_button(
    "⬇ Download Full Dataset",
    df.to_csv(index=False),
    file_name="restaurant_financial_report.csv"
)
