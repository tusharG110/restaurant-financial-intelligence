import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score

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

# ================= THEME STATE =================
if "theme" not in st.session_state:
    st.session_state.theme = "Dark"

def toggle_theme():
    st.session_state.theme = (
        "Light" if st.session_state.theme == "Dark" else "Dark"
    )

col1, col2 = st.columns([10,1])
with col2:
    st.button("🌗", on_click=toggle_theme)

if st.session_state.theme == "Dark":
    bg_color = "#0E1117"
    card_bg = "#161A23"
    border_color = "#2A2F3A"
    text_color = "#FFFFFF"
    plotly_template = "plotly_dark"
else:
    bg_color = "#F4F6F9"
    card_bg = "#FFFFFF"
    border_color = "#E0E0E0"
    text_color = "#000000"
    plotly_template = "plotly"

# ================= UI CSS =================
st.markdown(f"""
<style>
.stApp {{
    background-color: {bg_color};
}}

.kpi-card {{
    background-color: {card_bg};
    padding: 25px;
    border-radius: 15px;
    border: 1px solid {border_color};
    box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    transition: 0.3s;
}}
.kpi-card:hover {{
    transform: translateY(-5px);
}}

.section-card {{
    background-color: {card_bg};
    padding: 20px;
    border-radius: 15px;
    border: 1px solid {border_color};
    margin-top: 20px;
}}

h1,h2,h3,h4,h5,h6 {{
    color: {text_color};
}}
</style>
""", unsafe_allow_html=True)

# ================= HEADER =================
st.markdown("## 📊 Restaurant Financial Intelligence Platform")

page = st.radio(
    "",
    ["Executive Overview", "KPI Dashboard",
     "Product Analytics", "Forecasting",
     "Scenario Simulator"],
    horizontal=True
)

st.divider()

# ================= EXECUTIVE OVERVIEW =================
if page == "Executive Overview":

    total_revenue = df["Revenue_Generated"].sum()
    total_expense = df["Expense_Allocated"].sum()
    net_profit = df["Net_Profit_After_Expense"].sum()
    avg_margin = df["Net_Profit_Margin_%"].mean()

    # Growth Calculation
    monthly = df.groupby(df["Date"].dt.to_period("M"))[
        ["Revenue_Generated","Net_Profit_After_Expense"]
    ].sum()

    if len(monthly) > 1:
        revenue_growth = ((monthly.iloc[-1,0] - monthly.iloc[-2,0]) /
                           monthly.iloc[-2,0]) * 100
        profit_growth = ((monthly.iloc[-1,1] - monthly.iloc[-2,1]) /
                          monthly.iloc[-2,1]) * 100
    else:
        revenue_growth = 0
        profit_growth = 0

    col1, col2, col3, col4 = st.columns(4)

    col1.markdown(f"""
    <div class="kpi-card">
        <h4>Total Revenue</h4>
        <h2>₹{total_revenue:,.0f}</h2>
        <p>Growth: {revenue_growth:.2f}%</p>
    </div>
    """, unsafe_allow_html=True)

    col2.markdown(f"""
    <div class="kpi-card">
        <h4>Total Expense</h4>
        <h2>₹{total_expense:,.0f}</h2>
    </div>
    """, unsafe_allow_html=True)

    col3.markdown(f"""
    <div class="kpi-card">
        <h4>Net Profit</h4>
        <h2>₹{net_profit:,.0f}</h2>
        <p>Growth: {profit_growth:.2f}%</p>
    </div>
    """, unsafe_allow_html=True)

    col4.markdown(f"""
    <div class="kpi-card">
        <h4>Avg Net Margin</h4>
        <h2>{avg_margin:.2f}%</h2>
    </div>
    """, unsafe_allow_html=True)

    # Gauge Chart
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=avg_margin,
        title={'text': "Profitability Score"},
        gauge={'axis': {'range': [0,100]}}
    ))
    fig.update_layout(template=plotly_template)
    st.plotly_chart(fig, use_container_width=True)

    # Executive Insight
    insight = f"""
    Revenue grew {revenue_growth:.2f}% last month.
    Profit margin currently stands at {avg_margin:.2f}%.
    """
    st.markdown(f'<div class="section-card">{insight}</div>', unsafe_allow_html=True)

# ================= KPI DASHBOARD =================
elif page == "KPI Dashboard":

    daily = df.groupby("Date")["Revenue_Generated"].sum().reset_index()

    # Moving Average
    daily["MA_7"] = daily["Revenue_Generated"].rolling(7).mean()

    fig = px.line(daily, x="Date",
                  y=["Revenue_Generated","MA_7"],
                  title="Daily Revenue & 7-Day Moving Avg")
    fig.update_layout(template=plotly_template)
    st.plotly_chart(fig, use_container_width=True)

    # Cumulative Revenue
    daily["Cumulative"] = daily["Revenue_Generated"].cumsum()
    fig2 = px.line(daily, x="Date",
                   y="Cumulative",
                   title="Cumulative Revenue")
    fig2.update_layout(template=plotly_template)
    st.plotly_chart(fig2, use_container_width=True)

    best_day = daily.loc[daily["Revenue_Generated"].idxmax()]
    worst_day = daily.loc[daily["Revenue_Generated"].idxmin()]

    st.success(f"Peak Revenue Day: {best_day['Date'].date()} (₹{best_day['Revenue_Generated']:,.0f})")
    st.error(f"Worst Revenue Day: {worst_day['Date'].date()} (₹{worst_day['Revenue_Generated']:,.0f})")

# ================= PRODUCT ANALYTICS =================
elif page == "Product Analytics":

    product_summary = df.groupby("Product_Name")[
        ["Revenue_Generated","Net_Profit_After_Expense"]
    ].sum().reset_index()

    product_summary["Margin_%"] = (
        product_summary["Net_Profit_After_Expense"] /
        product_summary["Revenue_Generated"] * 100
    )

    fig = px.bar(product_summary,
                 x="Product_Name",
                 y="Net_Profit_After_Expense",
                 title="Net Profit by Product")
    fig.update_layout(template=plotly_template)
    st.plotly_chart(fig, use_container_width=True)

    # Revenue Contribution
    fig2 = px.pie(product_summary,
                  names="Product_Name",
                  values="Revenue_Generated",
                  title="Revenue Contribution")
    fig2.update_layout(template=plotly_template)
    st.plotly_chart(fig2, use_container_width=True)

    # Margin Chart
    fig3 = px.bar(product_summary,
                  x="Product_Name",
                  y="Margin_%",
                  title="Profit Margin by Product")
    fig3.update_layout(template=plotly_template)
    st.plotly_chart(fig3, use_container_width=True)

    top3 = product_summary.sort_values(
        by="Net_Profit_After_Expense",
        ascending=False).head(3)

    bottom3 = product_summary.sort_values(
        by="Net_Profit_After_Expense").head(3)

    c1, c2 = st.columns(2)
    c1.dataframe(top3, use_container_width=True)
    c2.dataframe(bottom3, use_container_width=True)

# ================= FORECASTING =================
elif page == "Forecasting":

    daily = df.groupby("Date")["Revenue_Generated"].sum().reset_index()
    daily["Date_Ordinal"] = daily["Date"].map(pd.Timestamp.toordinal)

    model = LinearRegression()
    model.fit(daily[["Date_Ordinal"]], daily["Revenue_Generated"])

    predictions_train = model.predict(daily[["Date_Ordinal"]])
    r2 = r2_score(daily["Revenue_Generated"], predictions_train)

    future_dates = pd.date_range(daily["Date"].max(), periods=8)[1:]
    future_ord = future_dates.map(pd.Timestamp.toordinal)
    predictions = model.predict(np.array(future_ord).reshape(-1,1))

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=daily["Date"],
                             y=daily["Revenue_Generated"],
                             name="Actual"))
    fig.add_trace(go.Scatter(x=future_dates,
                             y=predictions,
                             name="Forecast"))

    fig.update_layout(template=plotly_template)
    st.plotly_chart(fig, use_container_width=True)

    st.info(f"Model Accuracy (R² Score): {r2:.4f}")

# ================= SCENARIO SIMULATOR =================
elif page == "Scenario Simulator":

    revenue_growth = st.slider("Revenue Growth %", 0, 50, 5)
    expense_growth = st.slider("Expense Growth %", 0, 50, 10)

    adjusted_revenue = df["Revenue_Generated"] * (1 + revenue_growth/100)
    adjusted_expense = df["Expense_Allocated"] * (1 + expense_growth/100)

    adjusted_profit = adjusted_revenue - adjusted_expense
    new_margin = (adjusted_profit.sum() /
                  adjusted_revenue.sum()) * 100

    st.metric("Projected Net Profit",
              f"₹{adjusted_profit.sum():,.0f}")
    st.metric("Projected Margin",
              f"{new_margin:.2f}%")

    break_even_revenue = adjusted_expense.sum()
    st.warning(f"Break-even Revenue Required: ₹{break_even_revenue:,.0f}")

st.divider()
st.download_button(
    "⬇ Download Full Dataset",
    df.to_csv(index=False),
    file_name="restaurant_financial_report.csv"
)
