import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from sklearn.linear_model import LinearRegression

# ================= PAGE CONFIG =================
st.set_page_config(
    page_title="Restaurant Financial Intelligence",
    page_icon="📊",
    layout="wide"
)

# ================= LOAD DATA =================
df = pd.read_csv("final_complete_restaurant_dataset.csv")
df["Date"] = pd.to_datetime(df["Date"])

# ================= GLOBAL STYLING =================
st.markdown("""
<style>
.stApp {
    background-color: #0E1117;
    color: white;
}

.block-container {
    border: 1px solid #2A2F3A;
    border-radius: 12px;
    padding: 2rem;
    margin-top: 1rem;
}

.section-card {
    background-color: #161A23;
    padding: 20px;
    border-radius: 12px;
    border: 1px solid #2A2F3A;
    margin-top: 20px;
}

.kpi-card {
    background-color: #161A23;
    padding: 25px;
    border-radius: 15px;
    border: 1px solid #2A2F3A;
    box-shadow: 0 4px 10px rgba(0,0,0,0.4);
    transition: 0.3s;
}
.kpi-card:hover {
    transform: translateY(-5px);
}

h1,h2,h3,h4,h5,h6 {
    color: white;
}
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

    col1, col2, col3, col4 = st.columns(4)

    col1.markdown(f"""
    <div class="kpi-card">
        <h4>Total Revenue</h4>
        <h2>₹{total_revenue:,.0f}</h2>
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
    </div>
    """, unsafe_allow_html=True)

    col4.markdown(f"""
    <div class="kpi-card">
        <h4>Avg Net Margin</h4>
        <h2>{avg_margin:.2f}%</h2>
    </div>
    """, unsafe_allow_html=True)

    # ================= AI INSIGHT GENERATOR =================
    revenue_by_product = df.groupby("Product_Name")["Revenue_Generated"].sum()
    top_product = revenue_by_product.idxmax()
    top_value = revenue_by_product.max()

    insight = f"""
    🔍 AI Strategic Insight:

    • {top_product} is the highest revenue contributor (₹{top_value:,.0f}).  
    • Current profit margin stands at {avg_margin:.2f}%.  
    • Total operational expense accounts for {(total_expense/total_revenue)*100:.2f}% of revenue.  
    """

    st.markdown(f'<div class="section-card">{insight}</div>', unsafe_allow_html=True)

# ================= KPI DASHBOARD =================
elif page == "KPI Dashboard":

    daily = df.groupby("Date")["Revenue_Generated"].sum().reset_index()
    daily["Month"] = daily["Date"].dt.month

    # Moving Average
    daily["MA_7"] = daily["Revenue_Generated"].rolling(7).mean()

    fig = px.line(daily, x="Date",
                  y=["Revenue_Generated", "MA_7"],
                  title="Daily Revenue & 7-Day Moving Average",
                  template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)

    # Cumulative Revenue
    daily["Cumulative"] = daily["Revenue_Generated"].cumsum()
    fig2 = px.line(daily, x="Date",
                   y="Cumulative",
                   title="Cumulative Revenue Growth",
                   template="plotly_dark")
    st.plotly_chart(fig2, use_container_width=True)

    # ================= SEASONAL HEATMAP =================
    heatmap_data = df.copy()
    heatmap_data["Month"] = heatmap_data["Date"].dt.month
    heatmap_data["Weekday"] = heatmap_data["Date"].dt.day_name()

    pivot = heatmap_data.pivot_table(
        values="Revenue_Generated",
        index="Weekday",
        columns="Month",
        aggfunc="sum"
    )

    fig3 = px.imshow(
        pivot,
        title="Seasonal Revenue Heatmap (Weekday vs Month)",
        template="plotly_dark",
        aspect="auto"
    )

    st.plotly_chart(fig3, use_container_width=True)

# ================= PRODUCT ANALYTICS =================
elif page == "Product Analytics":

    product_summary = df.groupby("Product_Name")[
        ["Revenue_Generated","Net_Profit_After_Expense"]
    ].sum().reset_index()

    # ABC Classification
    product_summary = product_summary.sort_values(
        by="Revenue_Generated", ascending=False)
    product_summary["Cumulative_%"] = (
        product_summary["Revenue_Generated"].cumsum() /
        product_summary["Revenue_Generated"].sum()) * 100

    def classify(x):
        if x <= 70:
            return "A"
        elif x <= 90:
            return "B"
        else:
            return "C"

    product_summary["Class"] = product_summary["Cumulative_%"].apply(classify)

    fig = px.bar(product_summary,
                 x="Product_Name",
                 y="Revenue_Generated",
                 color="Class",
                 title="Revenue by Product with ABC Classification",
                 template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)

    st.dataframe(product_summary, use_container_width=True)

# ================= FORECASTING =================
elif page == "Forecasting":

    daily = df.groupby("Date")["Revenue_Generated"].sum().reset_index()
    daily["Date_Ordinal"] = daily["Date"].map(pd.Timestamp.toordinal)

    model = LinearRegression()
    model.fit(daily[["Date_Ordinal"]], daily["Revenue_Generated"])

    future_dates = pd.date_range(daily["Date"].max(), periods=15)[1:]
    future_ord = future_dates.map(pd.Timestamp.toordinal)

    predictions = model.predict(np.array(future_ord).reshape(-1,1))

    # Confidence Interval
    residuals = daily["Revenue_Generated"] - \
                model.predict(daily[["Date_Ordinal"]])
    std_dev = np.std(residuals)

    upper = predictions + 1.96 * std_dev
    lower = predictions - 1.96 * std_dev

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

    fig.add_trace(go.Scatter(
        x=future_dates,
        y=upper,
        line=dict(width=0),
        showlegend=False
    ))

    fig.add_trace(go.Scatter(
        x=future_dates,
        y=lower,
        fill='tonexty',
        name="Confidence Interval"
    ))

    fig.update_layout(
        template="plotly_dark",
        title="Revenue Forecast with Confidence Interval"
    )

    st.plotly_chart(fig, use_container_width=True)

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

    break_even = adjusted_expense.sum()
    st.warning(f"Break-even Revenue Required: ₹{break_even:,.0f}")

st.divider()
st.download_button(
    "⬇ Download Full Dataset",
    df.to_csv(index=False),
    file_name="restaurant_financial_report.csv"
)
