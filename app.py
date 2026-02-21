import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from sklearn.linear_model import LinearRegression
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import Table
from reportlab.platypus import TableStyle
from reportlab.platypus import SimpleDocTemplate
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph
from reportlab.platypus import Spacer
from reportlab.platypus import Table
from reportlab.platypus import TableStyle

# ================= PAGE CONFIG =================
st.set_page_config(
    page_title="Restaurant Financial Intelligence",
    page_icon="📊",
    layout="wide"
)

# ================= LOAD DATA =================
df = pd.read_csv("final_complete_restaurant_dataset.csv")
df["Date"] = pd.to_datetime(df["Date"])

# ================= MULTI-RESTAURANT FILTER =================
if "Restaurant" in df.columns:
    restaurant = st.selectbox(
        "Select Restaurant",
        df["Restaurant"].unique()
    )
    df = df[df["Restaurant"] == restaurant]

# ================= GLOBAL STYLING =================
st.markdown("""
<style>
.stApp {background-color:#0E1117;color:white;}
.block-container {
    border:1px solid #2A2F3A;
    border-radius:15px;
    padding:2rem;
    margin-top:1rem;
}
.section-card {
    background-color:#161A23;
    padding:20px;
    border-radius:12px;
    border:1px solid #2A2F3A;
    margin-top:20px;
}
.kpi-card {
    background-color:#161A23;
    padding:25px;
    border-radius:15px;
    border:1px solid #2A2F3A;
}
</style>
""", unsafe_allow_html=True)

# ================= HEADER =================
st.markdown("## 📊 Restaurant Financial Intelligence Platform")

page = st.radio(
    "",
    ["Executive Overview","KPI Dashboard",
     "Product Analytics","Forecasting",
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

    monthly = df.groupby(df["Date"].dt.to_period("M"))[
        ["Revenue_Generated","Net_Profit_After_Expense"]
    ].sum()

    if len(monthly) > 1:
        rev_growth = ((monthly.iloc[-1,0] - monthly.iloc[-2,0]) /
                      monthly.iloc[-2,0])*100
        prof_growth = ((monthly.iloc[-1,1] - monthly.iloc[-2,1]) /
                       monthly.iloc[-2,1])*100
    else:
        rev_growth = prof_growth = 0

    col1,col2,col3,col4 = st.columns(4)

    col1.markdown(f'<div class="kpi-card"><h4>Total Revenue</h4><h2>₹{total_revenue:,.0f}</h2><p>{rev_growth:.2f}% MoM</p></div>',unsafe_allow_html=True)
    col2.markdown(f'<div class="kpi-card"><h4>Total Expense</h4><h2>₹{total_expense:,.0f}</h2></div>',unsafe_allow_html=True)
    col3.markdown(f'<div class="kpi-card"><h4>Net Profit</h4><h2>₹{net_profit:,.0f}</h2><p>{prof_growth:.2f}% MoM</p></div>',unsafe_allow_html=True)
    col4.markdown(f'<div class="kpi-card"><h4>Avg Margin</h4><h2>{avg_margin:.2f}%</h2></div>',unsafe_allow_html=True)

    # Profitability Gauge
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=avg_margin,
        title={'text':"Profitability Score"},
        gauge={'axis':{'range':[0,100]}}
    ))
    fig.update_layout(template="plotly_dark")
    st.plotly_chart(fig,use_container_width=True)

    # Automated Monthly Summary
    summary_text = f"""
    📈 Revenue grew {rev_growth:.2f}% month-over-month.
    💰 Net profit change: {prof_growth:.2f}%.
    📊 Current margin stands at {avg_margin:.2f}%.
    """
    st.markdown(f'<div class="section-card">{summary_text}</div>',unsafe_allow_html=True)

# ================= KPI DASHBOARD =================
elif page == "KPI Dashboard":

    daily = df.groupby("Date")["Revenue_Generated"].sum().reset_index()
    daily["MA_7"] = daily["Revenue_Generated"].rolling(7).mean()
    daily["Cumulative"] = daily["Revenue_Generated"].cumsum()

    fig = px.line(daily,x="Date",
                  y=["Revenue_Generated","MA_7"],
                  template="plotly_dark",
                  title="Revenue Trend & 7-Day Moving Avg")
    st.plotly_chart(fig,use_container_width=True)

    fig2 = px.line(daily,x="Date",
                   y="Cumulative",
                   template="plotly_dark",
                   title="Cumulative Revenue")
    st.plotly_chart(fig2,use_container_width=True)

# ================= PRODUCT ANALYTICS =================
elif page == "Product Analytics":

    product_summary = df.groupby("Product_Name")[
        "Revenue_Generated"].sum().reset_index()

    product_summary = product_summary.sort_values(
        by="Revenue_Generated",ascending=False)

    product_summary["Cum%"] = (
        product_summary["Revenue_Generated"].cumsum() /
        product_summary["Revenue_Generated"].sum())*100

    product_summary["Class"] = product_summary["Cum%"].apply(
        lambda x: "A" if x<=70 else ("B" if x<=90 else "C")
    )

    fig = px.bar(product_summary,
                 x="Product_Name",
                 y="Revenue_Generated",
                 color="Class",
                 template="plotly_dark",
                 title="Revenue with ABC Classification")
    st.plotly_chart(fig,use_container_width=True)

# ================= FORECASTING =================
elif page == "Forecasting":

    daily = df.groupby("Date")["Revenue_Generated"].sum().reset_index()
    daily["Date_Ordinal"] = daily["Date"].map(pd.Timestamp.toordinal)

    model = LinearRegression()
    model.fit(daily[["Date_Ordinal"]],
              daily["Revenue_Generated"])

    future_dates = pd.date_range(
        daily["Date"].max(),periods=15)[1:]
    future_ord = future_dates.map(pd.Timestamp.toordinal)
    preds = model.predict(np.array(future_ord).reshape(-1,1))

    residuals = daily["Revenue_Generated"] - \
                model.predict(daily[["Date_Ordinal"]])
    std = np.std(residuals)

    upper = preds + 1.96*std
    lower = preds - 1.96*std

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=daily["Date"],
        y=daily["Revenue_Generated"],
        name="Actual"
    ))
    fig.add_trace(go.Scatter(
        x=future_dates,y=preds,name="Forecast"
    ))
    fig.add_trace(go.Scatter(
        x=future_dates,y=upper,line=dict(width=0),
        showlegend=False))
    fig.add_trace(go.Scatter(
        x=future_dates,y=lower,
        fill="tonexty",
        name="Confidence Interval"
    ))
    fig.update_layout(template="plotly_dark",
                      title="Revenue Forecast with Confidence Interval")
    st.plotly_chart(fig,use_container_width=True)

# ================= SCENARIO SIMULATOR =================
elif page == "Scenario Simulator":

    rev = st.slider("Revenue Growth %",0,50,5)
    exp = st.slider("Expense Growth %",0,50,10)

    adj_rev = df["Revenue_Generated"]*(1+rev/100)
    adj_exp = df["Expense_Allocated"]*(1+exp/100)
    adj_profit = adj_rev-adj_exp

    new_margin = (adj_profit.sum()/adj_rev.sum())*100

    st.metric("Projected Net Profit",
              f"₹{adj_profit.sum():,.0f}")
    st.metric("Projected Margin",
              f"{new_margin:.2f}%")

# ================= EXECUTIVE PDF REPORT =================
st.divider()

def generate_pdf():
    file_path = "/mnt/data/executive_report.pdf"
    doc = SimpleDocTemplate(file_path)
    elements = []
    styles = getSampleStyleSheet()

    elements.append(Paragraph("Executive Financial Summary", styles['Title']))
    elements.append(Spacer(1, 0.5*inch))

    elements.append(Paragraph(
        f"Total Revenue: ₹{total_revenue:,.0f}", styles['Normal']))
    elements.append(Paragraph(
        f"Total Expense: ₹{total_expense:,.0f}", styles['Normal']))
    elements.append(Paragraph(
        f"Net Profit: ₹{net_profit:,.0f}", styles['Normal']))
    elements.append(Paragraph(
        f"Average Margin: {avg_margin:.2f}%", styles['Normal']))

    doc.build(elements)
    return file_path

pdf_file = generate_pdf()
st.download_button(
    "⬇ Download Executive PDF Report",
    open(pdf_file,"rb"),
    file_name="executive_report.pdf"
)
