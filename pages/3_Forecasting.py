import streamlit as st
import pandas as pd
from sklearn.linear_model import LinearRegression
import plotly.graph_objects as go

st.title("📅 Revenue Forecasting")

df = pd.read_csv("final_complete_restaurant_dataset.csv")
df["Date"] = pd.to_datetime(df["Date"])

daily = df.groupby("Date")["Revenue_Generated"].sum().reset_index()
daily["Date_Ordinal"] = daily["Date"].map(pd.Timestamp.toordinal)

model = LinearRegression()
model.fit(daily[["Date_Ordinal"]], daily["Revenue_Generated"])

future_dates = pd.date_range(daily["Date"].max(), periods=8)[1:]
future_df = pd.DataFrame({"Date_Ordinal": future_dates.map(pd.Timestamp.toordinal)})

predictions = model.predict(future_df)

fig = go.Figure()
fig.add_trace(go.Scatter(x=daily["Date"], y=daily["Revenue_Generated"], name="Actual"))
fig.add_trace(go.Scatter(x=future_dates, y=predictions, name="Forecast"))

st.plotly_chart(fig, use_container_width=True)
