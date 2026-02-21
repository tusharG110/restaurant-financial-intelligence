import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from sklearn.linear_model import LinearRegression

# ==============================
# PAGE CONFIG
# ==============================
st.set_page_config(
    page_title="Restaurant Financial Intelligence",
    layout="wide"
)

# ==============================
# LOAD DATA
# ==============================
df = pd.read_csv("final_complete_restaurant_dataset.csv")
df["Date"] = pd.to_datetime(df["Date"])

# ==============================
# GLOBAL STYLING (ELITE UI)
# ==============================
st.markdown("""
<style>
.stApp {
    background-color: #0E1117;
    color: white;
}

.block-container {
    border: 1px solid #2A2F3A;
    border-radius: 15px;
    padding: 2rem;
    margin-top: 1rem;
}

.kpi-card {
    background: linear-gradient(135deg, #161A23, #1F2633);
    padding: 25px;
    border-radius: 15px;
    border: 1px solid #2A2F3A;
    box-shadow: 0 4px 20px rgba(0,0,0,0.4);
}

.section-card {
    background-color: #161A23;
    padding: 20px;
    border-radius: 12px;
    border: 1px solid #2A2F3A;
    margin-top: 20px;
}
</style>
""", unsafe_allow_html=True)

# ==============================
# HELPER FUNCTIONS
# ==============================

def calculate_risk_index(data):
    revenue_vol = data["Revenue_Generated"].std()
    margin_vol = data["Net_Profit_Margin_%"].std()
    expense_growth = data["Expense_Allocated"].pct_change().mean()

    score = 100 - (revenue_vol * 0.01 + margin_vol * 2 + expense_growth * 50)
    score = max(0, min(100, score))
    return round(score, 2)

def detect_anomalies(daily):
    mean = daily["Revenue_Generated"].mean()
    std = daily["Revenue_Generated"].std()
    daily["Z"] = (daily["Revenue_Generated"] - mean) / std
    anomalies = daily[abs(daily["Z"]) > 2]
    return anomalies

def abc_classification(data):
    data = data.sort_values(by="Revenue_Generated", ascending=False)
    data["Cum%"] = data["Revenue_Generated"].cumsum() / data["Revenue_Generated"].sum() * 100
    data["Class"] = data["Cum%"].apply(
        lambda x: "A" if x <= 70 else ("B" if x <= 90 else "C")
    )
    return data

# ==============================
# HEADER
# ==============================
st.markdown("## 📊 Restaurant Financial Intelligence Platform")

page = st.radio(
    "",
    ["Executive Overview",
     "KPI Dashboard",
     "Product Analytics",
     "Forecasting",
     "Scenario Simulator"],
    horizontal=True
)

st.divider()

# ==============================
# EXECUTIVE OVERVIEW
# ==============================
if page == "Executive Overview":

    total_revenue = df["Revenue_Generated"].sum()
    total_expense = df["Expense_Allocated"].sum()
    net_profit = df["Net_Profit_After_Expense"].sum()
    avg_margin = df["Net_Profit_Margin_%"].mean()

    monthly = df.groupby(df["Date"].dt.to_period("M"))[
        ["Revenue_Generated", "Net_Profit_After_Expense"]
    ].sum()

    if len(monthly) > 1:
        rev_growth = ((monthly.iloc[-1, 0] - monthly.iloc[-2, 0]) /
                      monthly.iloc[-2, 0]) * 100
        prof_growth = ((monthly.iloc[-1, 1] - monthly.iloc[-2, 1]) /
                       monthly.iloc[-2, 1]) * 100
    else:
        rev_growth = prof_growth = 0

    col1, col2, col3, col4 = st.columns(4)

    col1.markdown(f'<div class="kpi-card"><h4>Total Revenue</h4><h2>₹{total_revenue:,.0f}</h2></div>', unsafe_allow_html=True)
    col2.markdown(f'<div class="kpi-card"><h4>Total Expense</h4><h2>₹{total_expense:,.0f}</h2></div>', unsafe_allow_html=True)
    col3.markdown(f'<div class="kpi-card"><h4>Net Profit</h4><h2>₹{net_profit:,.0f}</h2></div>', unsafe_allow_html=True)
    col4.markdown(f'<div class="kpi-card"><h4>Avg Margin</h4><h2>{avg_margin:.2f}%</h2></div>', unsafe_allow_html=True)

    # Risk Index
    risk_score = calculate_risk_index(df)

    if risk_score > 70:
        risk_label = "🟢 Low Risk"
    elif risk_score > 40:
        risk_label = "🟡 Moderate Risk"
    else:
        risk_label = "🔴 High Risk"

    st.markdown(f'<div class="section-card"><h4>Risk Index: {risk_score}/100</h4>{risk_label}</div>', unsafe_allow_html=True)

    # Waterfall Chart
    fig = go.Figure(go.Waterfall(
        name="Financial Breakdown",
        orientation="v",
        measure=["relative", "relative", "total"],
        x=["Revenue", "Expense", "Net Profit"],
        y=[total_revenue, -total_expense, net_profit]
    ))
    fig.update_layout(template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)

    # AI Insight
    insight = f"""
    📌 Executive Insight:

    Revenue growth stands at {rev_growth:.2f}% MoM.
    Profit growth at {prof_growth:.2f}%.
    Current margin: {avg_margin:.2f}%.
    Risk level: {risk_label}.
    """
    st.markdown(f'<div class="section-card">{insight}</div>', unsafe_allow_html=True)

# ==============================
# KPI DASHBOARD
# ==============================
elif page == "KPI Dashboard":

    daily = df.groupby("Date")["Revenue_Generated"].sum().reset_index()
    daily["MA_7"] = daily["Revenue_Generated"].rolling(7).mean()

    fig = px.line(daily, x="Date",
                  y=["Revenue_Generated", "MA_7"],
                  template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)

    # Anomaly Detection
    anomalies = detect_anomalies(daily)
    if not anomalies.empty:
        st.warning("⚠ Revenue anomalies detected:")
        st.dataframe(anomalies[["Date", "Revenue_Generated"]])

    # Calendar Heatmap
    daily["Day"] = daily["Date"].dt.day
    daily["Month"] = daily["Date"].dt.month

    pivot = daily.pivot_table(
        values="Revenue_Generated",
        index="Month",
        columns="Day",
        aggfunc="sum"
    )

    fig2 = px.imshow(pivot, template="plotly_dark",
                     title="Revenue Calendar Heatmap",
                     aspect="auto")
    st.plotly_chart(fig2, use_container_width=True)

# ==============================
# PRODUCT ANALYTICS
# ==============================
elif page == "Product Analytics":

    product_summary = df.groupby("Product_Name")[
        ["Revenue_Generated", "Net_Profit_After_Expense"]
    ].sum().reset_index()

    product_summary = abc_classification(product_summary)

    fig = px.bar(product_summary,
                 x="Product_Name",
                 y="Revenue_Generated",
                 color="Class",
                 template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)

    st.dataframe(product_summary)

# ==============================
# FORECASTING
# ==============================
elif page == "Forecasting":

    daily = df.groupby("Date")["Revenue_Generated"].sum().reset_index()
    daily["Date_Ordinal"] = daily["Date"].map(pd.Timestamp.toordinal)

    model = LinearRegression()
    model.fit(daily[["Date_Ordinal"]],
              daily["Revenue_Generated"])

    future_dates = pd.date_range(daily["Date"].max(), periods=15)[1:]
    future_ord = future_dates.map(pd.Timestamp.toordinal)
    preds = model.predict(np.array(future_ord).reshape(-1, 1))

    residuals = daily["Revenue_Generated"] - \
        model.predict(daily[["Date_Ordinal"]])
    std = np.std(residuals)

    upper = preds + 1.96 * std
    lower = preds - 1.96 * std

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=daily["Date"],
        y=daily["Revenue_Generated"],
        name="Actual"
    ))
    fig.add_trace(go.Scatter(
        x=future_dates, y=preds, name="Forecast"
    ))
    fig.add_trace(go.Scatter(
        x=future_dates, y=upper,
        line=dict(width=0), showlegend=False
    ))
    fig.add_trace(go.Scatter(
        x=future_dates, y=lower,
        fill="tonexty",
        name="Confidence Interval"
    ))
    fig.update_layout(template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)

# ==============================
# SCENARIO SIMULATOR
# ==============================
elif page == "Scenario Simulator":

    rev = st.slider("Revenue Growth %", 0, 50, 5)
    exp = st.slider("Expense Growth %", 0, 50, 10)

    adj_rev = df["Revenue_Generated"] * (1 + rev/100)
    adj_exp = df["Expense_Allocated"] * (1 + exp/100)
    adj_profit = adj_rev - adj_exp

    new_margin = (adj_profit.sum() / adj_rev.sum()) * 100

    st.metric("Projected Net Profit",
              f"₹{adj_profit.sum():,.0f}")
    st.metric("Projected Margin",
              f"{new_margin:.2f}%")
