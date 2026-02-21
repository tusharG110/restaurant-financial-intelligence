import streamlit as st

st.set_page_config(
    page_title="Restaurant Financial Intelligence",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("📊 Restaurant Financial Intelligence Platform")

st.markdown("""
Welcome to the Financial Intelligence System.

Use the sidebar to navigate between modules:

- KPI Dashboard
- Product Analytics
- Forecasting
- Scenario Simulator

Dataset Version: v2.0
""")
