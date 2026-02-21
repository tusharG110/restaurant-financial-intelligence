import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from sklearn.linear_model import LinearRegression

st.set_page_config(page_title="Restaurant Financial Intelligence", layout="wide")

# ================= LOAD DATA =================
df = pd.read_csv("final_complete_restaurant_dataset.csv")
df["Date"] = pd.to_datetime(df["Date"])

# ================= STYLING =================
st.markdown("""
<style>
.stApp {background-color:#0E1117;color:white;}
.block-container {border:1px solid #2A2F3A;border-radius:15px;padding:2rem;margin-top:1rem;}
.kpi-card {background:linear-gradient(135deg,#161A23,#1F2633);
padding:25px;border-radius:15px;border:1px solid #2A2F3A;}
.section-card {background-color:#161A23;padding:20px;border-radius:12px;
border:1px solid #2A2F3A;margin-top:20px;}
</style>
""", unsafe_allow_html=True)

# ================= HELPERS =================
def calculate_risk_index(data):
    revenue_vol = data["Revenue_Generated"].std()
    margin_vol = data["Net_Profit_Margin_%"].std()
    expense_growth = data["Expense_Allocated"].pct_change().mean()
    score = 100 - (revenue_vol*0.01 + margin_vol*2 + expense_growth*50)
    return round(max(0,min(100,score)),2)

def detect_anomalies(daily):
    mean = daily["Revenue_Generated"].mean()
    std = daily["Revenue_Generated"].std()
    daily["Z"] = (daily["Revenue_Generated"]-mean)/std
    return daily[abs(daily["Z"])>2]

# ================= HEADER =================
st.markdown("## 📊 Restaurant Financial Intelligence Platform")

page = st.radio("",["Executive Overview","KPI Dashboard",
                    "Product Analytics","Forecasting",
                    "Scenario Simulator"],horizontal=True)

st.divider()

# ================= EXECUTIVE OVERVIEW =================
if page=="Executive Overview":

    st.markdown("### 🏢 Overall Financial Summary")
    st.markdown("High-level performance metrics representing total financial health of the restaurant business.")

    total_revenue=df["Revenue_Generated"].sum()
    total_expense=df["Expense_Allocated"].sum()
    net_profit=df["Net_Profit_After_Expense"].sum()
    avg_margin=df["Net_Profit_Margin_%"].mean()

    monthly=df.groupby(df["Date"].dt.to_period("M"))[
        ["Revenue_Generated","Net_Profit_After_Expense"]].sum()

    if len(monthly)>1:
        rev_growth=((monthly.iloc[-1,0]-monthly.iloc[-2,0])/monthly.iloc[-2,0])*100
        prof_growth=((monthly.iloc[-1,1]-monthly.iloc[-2,1])/monthly.iloc[-2,1])*100
    else:
        rev_growth=prof_growth=0

    col1,col2,col3,col4=st.columns(4)
    col1.markdown(f'<div class="kpi-card"><h4>Total Revenue</h4><h2>₹{total_revenue:,.0f}</h2><p>{rev_growth:.2f}% MoM Growth</p></div>',unsafe_allow_html=True)
    col2.markdown(f'<div class="kpi-card"><h4>Total Expense</h4><h2>₹{total_expense:,.0f}</h2></div>',unsafe_allow_html=True)
    col3.markdown(f'<div class="kpi-card"><h4>Net Profit</h4><h2>₹{net_profit:,.0f}</h2><p>{prof_growth:.2f}% MoM Growth</p></div>',unsafe_allow_html=True)
    col4.markdown(f'<div class="kpi-card"><h4>Average Margin</h4><h2>{avg_margin:.2f}%</h2></div>',unsafe_allow_html=True)

    st.markdown("---")

    st.markdown("### 📊 Profitability Gauge")
    st.markdown("Visual representation of overall profitability margin score (0–100%).")

    fig=go.Figure(go.Indicator(mode="gauge+number",
        value=avg_margin,
        title={'text':"Profitability Score (%)"},
        gauge={'axis':{'range':[0,100]}}))
    fig.update_layout(template="plotly_dark")
    st.plotly_chart(fig,use_container_width=True)

    st.markdown("---")

    st.markdown("### 💰 Financial Breakdown (Waterfall Analysis)")
    st.markdown("Shows how revenue converts into net profit after deducting expenses.")

    fig2=go.Figure(go.Waterfall(
        measure=["relative","relative","total"],
        x=["Revenue","Expense","Net Profit"],
        y=[total_revenue,-total_expense,net_profit]))
    fig2.update_layout(template="plotly_dark")
    st.plotly_chart(fig2,use_container_width=True)

    st.markdown("---")

    st.markdown("### ⚠ Business Risk Index")
    st.markdown("Composite risk score based on revenue volatility, margin variability, and expense growth.")

    risk=calculate_risk_index(df)
    risk_label="🟢 Low" if risk>70 else ("🟡 Moderate" if risk>40 else "🔴 High")

    st.markdown(f'<div class="section-card">Risk Index: {risk}/100 ({risk_label})</div>',unsafe_allow_html=True)

# ================= KPI DASHBOARD =================
elif page=="KPI Dashboard":

    daily=df.groupby("Date")["Revenue_Generated"].sum().reset_index()
    daily["MA_7"]=daily["Revenue_Generated"].rolling(7).mean()
    daily["Cumulative"]=daily["Revenue_Generated"].cumsum()

    st.markdown("### 📈 Daily Revenue Trend")
    st.markdown("Displays daily revenue alongside 7-day moving average to identify short-term performance trends.")
    fig=px.line(daily,x="Date",y=["Revenue_Generated","MA_7"],template="plotly_dark")
    st.plotly_chart(fig,use_container_width=True)

    st.markdown("---")

    st.markdown("### 📊 Cumulative Revenue Growth")
    st.markdown("Tracks cumulative revenue accumulation over time.")
    fig2=px.line(daily,x="Date",y="Cumulative",template="plotly_dark")
    st.plotly_chart(fig2,use_container_width=True)

    st.markdown("---")

    st.markdown("### 💰 Revenue vs Expense Comparison")
    st.markdown("Compares daily revenue performance against operational expenses.")
    daily_full=df.groupby("Date")[["Revenue_Generated","Expense_Allocated"]].sum().reset_index()
    fig3=px.line(daily_full,x="Date",y=["Revenue_Generated","Expense_Allocated"],template="plotly_dark")
    st.plotly_chart(fig3,use_container_width=True)

    st.markdown("---")

    best=daily.loc[daily["Revenue_Generated"].idxmax()]
    worst=daily.loc[daily["Revenue_Generated"].idxmin()]
    col1,col2=st.columns(2)
    col1.success(f"🏆 Peak Revenue Day: {best['Date'].date()} (₹{best['Revenue_Generated']:,.0f})")
    col2.error(f"⚠ Worst Revenue Day: {worst['Date'].date()} (₹{worst['Revenue_Generated']:,.0f})")

    anomalies=detect_anomalies(daily)
    if not anomalies.empty:
        st.markdown("### 🚨 Revenue Anomaly Detection")
        st.markdown("Highlights days where revenue significantly deviates from normal patterns.")
        st.dataframe(anomalies[["Date","Revenue_Generated"]])

    st.markdown("---")

    st.markdown("### 🗓 Revenue Seasonal Heatmap")
    st.markdown("Monthly and daily revenue intensity visualization to identify seasonal trends.")
    daily["Day"]=daily["Date"].dt.day
    daily["Month"]=daily["Date"].dt.month
    pivot=daily.pivot_table(values="Revenue_Generated",index="Month",columns="Day",aggfunc="sum")
    fig4=px.imshow(pivot,template="plotly_dark",aspect="auto")
    st.plotly_chart(fig4,use_container_width=True)

# ================= PRODUCT ANALYTICS =================
elif page=="Product Analytics":

    product=df.groupby("Product_Name")[["Revenue_Generated","Net_Profit_After_Expense"]].sum().reset_index()
    product["Margin_%"]=product["Net_Profit_After_Expense"]/product["Revenue_Generated"]*100

    st.markdown("### 📦 Revenue by Product")
    st.markdown("Total revenue generated by each product category.")
    fig=px.bar(product,x="Product_Name",y="Revenue_Generated",template="plotly_dark")
    st.plotly_chart(fig,use_container_width=True)

    st.markdown("---")

    st.markdown("### 🥧 Revenue Contribution Distribution")
    st.markdown("Percentage share of each product in total revenue.")
    fig2=px.pie(product,names="Product_Name",values="Revenue_Generated",template="plotly_dark")
    st.plotly_chart(fig2,use_container_width=True)

    st.markdown("---")

    st.markdown("### 📈 Profit Margin by Product")
    st.markdown("Comparison of profit margins across products.")
    fig3=px.bar(product,x="Product_Name",y="Margin_%",template="plotly_dark")
    st.plotly_chart(fig3,use_container_width=True)

    st.markdown("---")

    st.markdown("### 🏆 Top & Bottom Performing Products")
    st.markdown("Ranking products based on total net profit.")
    top3=product.sort_values("Net_Profit_After_Expense",ascending=False).head(3)
    bottom3=product.sort_values("Net_Profit_After_Expense").head(3)
    col1,col2=st.columns(2)
    col1.dataframe(top3)
    col2.dataframe(bottom3)

# ================= FORECASTING =================
elif page=="Forecasting":

    st.markdown("### 🔮 Revenue Forecasting")
    st.markdown("Predictive model estimating future revenue with 95% confidence interval.")

    daily=df.groupby("Date")["Revenue_Generated"].sum().reset_index()
    daily["Date_Ordinal"]=daily["Date"].map(pd.Timestamp.toordinal)

    model=LinearRegression()
    model.fit(daily[["Date_Ordinal"]],daily["Revenue_Generated"])

    future_dates=pd.date_range(daily["Date"].max(),periods=15)[1:]
    future_ord=future_dates.map(pd.Timestamp.toordinal)
    preds=model.predict(np.array(future_ord).reshape(-1,1))

    residuals=daily["Revenue_Generated"]-model.predict(daily[["Date_Ordinal"]])
    std=np.std(residuals)

    upper=preds+1.96*std
    lower=preds-1.96*std

    fig=go.Figure()
    fig.add_trace(go.Scatter(x=daily["Date"],y=daily["Revenue_Generated"],name="Actual Revenue"))
    fig.add_trace(go.Scatter(x=future_dates,y=preds,name="Forecast"))
    fig.add_trace(go.Scatter(x=future_dates,y=upper,line=dict(width=0),showlegend=False))
    fig.add_trace(go.Scatter(x=future_dates,y=lower,fill="tonexty",name="Confidence Interval"))

    fig.update_layout(template="plotly_dark")
    st.plotly_chart(fig,use_container_width=True)

# ================= SCENARIO =================
elif page=="Scenario Simulator":

    st.markdown("### 🧮 Scenario Simulation")
    st.markdown("Adjust revenue and expense growth assumptions to simulate financial outcomes.")

    rev=st.slider("Revenue Growth %",0,50,5)
    exp=st.slider("Expense Growth %",0,50,10)

    adj_rev=df["Revenue_Generated"]*(1+rev/100)
    adj_exp=df["Expense_Allocated"]*(1+exp/100)
    adj_profit=adj_rev-adj_exp

    margin=(adj_profit.sum()/adj_rev.sum())*100
    breakeven=adj_exp.sum()

    st.metric("Projected Net Profit",f"₹{adj_profit.sum():,.0f}")
    st.metric("Projected Margin",f"{margin:.2f}%")
    st.warning(f"Break-even Revenue Required: ₹{breakeven:,.0f}")
