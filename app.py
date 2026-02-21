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

# ================= THEME STATE =================
if "theme" not in st.session_state:
    st.session_state.theme = "Dark"

def toggle_theme():
    st.session_state.theme = (
        "Light" if st.session_state.theme == "Dark" else "Dark"
    )

# ================= TOP BAR =================
col_left, col_right = st.columns([10, 1])
with col_right:
    st.button("🌗", on_click=toggle_theme)

# ================= THEME SETTINGS =================
if st.session_state.theme == "Dark":
    bg_color = "#0E1117"
    card_bg = "#161A23"
    border_color = "#2A2F3A"
    text_color = "#FFFFFF"
    plotly_template = "plotly_dark"
else:
    bg_color = "#F8F9FA"
    card_bg = "#FFFFFF"
    border_color = "#E0E0E0"
    text_color = "#000000"
    plotly_template = "plotly"

# ================= PREMIUM UI CSS =================
st.markdown(
    f"""
    <style>
    .stApp {{
        background-color: {bg_color};
        transition: all 0.4s ease-in-out;
    }}

    .block-container {{
        animation: fadeIn 0.6s ease-in-out;
    }}

    @keyframes fadeIn {{
        from {{ opacity: 0; transform: translateY(10px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}

    h1, h2, h3, h4, h5, h6 {{
        color: {text_color};
    }}

    div[role="radiogroup"] label {{
        color: {text_color};
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
        box-shadow: 0 10px 22px rgba(0,0,0,0.12);
    }}

    .kpi-title {{
        font-size: 15px;
        opacity: 0.7;
    }}

    .kpi-value {{
        font-size: 28px;
        font-weight: bold;
        margin-top: 5px;
    }}

    .section-card {{
        background-color: {card_bg};
        padding: 20px;
        border-radius: 15px;
        border: 1px solid {border_color};
        margin-top: 20px;
    }}

    </style>
    """,
    unsafe_allow_html=True
)

# ================= HEADER =================
st.markdown("## 📊 Restaurant Financial Intelligence Platform")

page = st.radio(
    "",
    [
        "Executive Overview",
        "KPI Dashboard",
        "Product Analytics",
        "Forecasting",
        "Scenario Simulator"
    ],
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
            <div class="kpi-title">Total Revenue</div>
            <div class="kpi-value">₹{total_revenue:,.0f}</div>
        </div>
    """, unsafe_allow_html=True)

    col2.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Total Expense</div>
            <div class="kpi-value">₹{total_expense:,.0f}</div>
        </div>
    """, unsafe_allow_html=True)

    col3.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Net Profit</div>
            <div class="kpi-value">₹{net_profit:,.0f}</div>
        </div>
    """, unsafe_allow_html=True)

    col4.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Avg Net Margin</div>
            <div class="kpi-value">{avg_margin:.2f}%</div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("### 📌 Strategic Insight")

    if avg_margin > 45:
        insight = "Business is highly profitable and financially strong."
    elif avg_margin > 30:
        insight = "Margins are stable. Cost optimization recommended."
    else:
        insight = "Profitability risk detected. Immediate action required."

    st.markdown(f"""
        <div class="section-card">
            {insight}
        </div>
    """, unsafe_allow_html=True)

# ================= KPI DASHBOARD =================
elif page == "KPI Dashboard":

    monthly = df.groupby(df["Date"].dt.to_period("M"))[
        ["Revenue_Generated",
         "Expense_Allocated",
         "Net_Profit_After_Expense"]
    ].sum().reset_index()

    monthly["Date"] = monthly["Date"].astype(str)

    fig = px.line(
        monthly,
        x="Date",
        y=[
            "Revenue_Generated",
            "Expense_Allocated",
            "Net_Profit_After_Expense"
        ],
        title="Monthly Financial Trend"
    )

    fig.update_layout(template=plotly_template)
    st.plotly_chart(fig, use_container_width=True)

# ================= PRODUCT ANALYTICS =================
elif page == "Product Analytics":

    product_summary = df.groupby("Product_Name")[
        ["Revenue_Generated", "Net_Profit_After_Expense"]
    ].sum().reset_index()

    fig = px.bar(
        product_summary,
        x="Product_Name",
        y="Net_Profit_After_Expense",
        title="Net Profit by Product",
        text_auto=True
    )

    fig.update_layout(template=plotly_template)
    st.plotly_chart(fig, use_container_width=True)

    top3 = product_summary.sort_values(
        by="Net_Profit_After_Expense",
        ascending=False
    ).head(3)

    bottom3 = product_summary.sort_values(
        by="Net_Profit_After_Expense"
    ).head(3)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="section-card"><h4>🏆 Top 3 Performing Products</h4></div>', unsafe_allow_html=True)
        st.dataframe(top3, use_container_width=True)

    with col2:
        st.markdown('<div class="section-card"><h4>⚠ Bottom 3 Performing Products</h4></div>', unsafe_allow_html=True)
        st.dataframe(bottom3, use_container_width=True)

# ================= FORECASTING =================
elif page == "Forecasting":

    daily = df.groupby("Date")["Revenue_Generated"].sum().reset_index()
    daily["Date_Ordinal"] = daily["Date"].map(pd.Timestamp.toordinal)

    model = LinearRegression()
    model.fit(daily[["Date_Ordinal"]], daily["Revenue_Generated"])

    future_dates = pd.date_range(daily["Date"].max(), periods=8)[1:]
    future_df = pd.DataFrame({
        "Date_Ordinal": future_dates.map(pd.Timestamp.toordinal)
    })

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

    fig.update_layout(template=plotly_template)
    st.plotly_chart(fig, use_container_width=True)

# ================= SCENARIO SIMULATOR =================
elif page == "Scenario Simulator":

    cost_increase = st.slider("Increase Expenses (%)", 0, 50, 10)

    adjusted_expense = df["Expense_Allocated"] * (
        1 + cost_increase / 100
    )
    adjusted_profit = df["Revenue_Generated"] - adjusted_expense

    st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Projected Net Profit</div>
            <div class="kpi-value">₹{adjusted_profit.sum():,.0f}</div>
        </div>
    """, unsafe_allow_html=True)

st.divider()
st.download_button(
    "⬇ Download Full Dataset",
    df.to_csv(index=False),
    file_name="restaurant_financial_report.csv"
)
