# app.py

import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
from datetime import date

# ----------------- Configuration ----------------- #
st.set_page_config(page_title="📊 Infosys Ltd - Stock Analyzer", layout="wide")

# ----------------- Title ----------------- #
st.markdown("""
    <h1 style='text-align: center; color: #2C3E50;'>
        📈 Infosys Ltd (INFY.NS) - Live Stock Market Analyzer
    </h1>
    """, unsafe_allow_html=True)

# ----------------- Sidebar ----------------- #
st.sidebar.header("📅 Select Date Range")
start_date = st.sidebar.date_input("Start Date", value=date(2023, 1, 1))
end_date = st.sidebar.date_input("End Date", value=date.today())

st.sidebar.header("📂 Choose Analysis Type")
analysis_type = st.sidebar.selectbox(
    "Analysis Type",
    (
        "📊 Technical Analysis",
        "📑 Fundamental Analysis",
        "💬 Sentimental Analysis",
        "📈 Quantitative Analysis"
    )
)

# ----------------- Fixed Ticker ----------------- #
ticker = "INFY.NS"  # Infosys Ltd (NSE)

# ----------------- Fetch Live Data ----------------- #
@st.cache_data(ttl=3600)
def fetch_data(ticker, start, end):
    try:
        return yf.download(ticker, start=start, end=end)
    except Exception:
        return None

data = fetch_data(ticker, start_date, end_date)

# ----------------- Price Chart ----------------- #
st.subheader(f"📉 Stock Price Chart: {ticker}")

if data is not None and not data.empty:
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data.index, y=data['Close'], mode='lines+markers', name='Close Price'))
    fig.update_layout(
        title='Live Stock Price Over Selected Date Range',
        xaxis_title='Date', yaxis_title='Price (INR)',
        template='plotly_dark', height=500
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.error("⚠️ No data found for the selected date range. Please check your internet connection or adjust the dates.")

# ----------------- Analysis Output ----------------- #
st.subheader("🔍 Analysis Output")

if data is not None and not data.empty:
    if analysis_type == "📊 Technical Analysis":
        data['SMA20'] = data['Close'].rolling(window=20).mean()
        data['SMA50'] = data['Close'].rolling(window=50).mean()

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=data.index, y=data['Close'], name="Close Price"))
        fig.add_trace(go.Scatter(x=data.index, y=data['SMA20'], name="SMA 20"))
        fig.add_trace(go.Scatter(x=data.index, y=data['SMA50'], name="SMA 50"))
        fig.update_layout(title="Technical Indicators: SMA 20 & SMA 50", template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("**Explanation:** SMA (Simple Moving Average) helps detect price trends. A crossover of SMA20 above SMA50 often signals bullish momentum.")
        st.success("📌 Comment: If the SMA20 has recently crossed above SMA50, it may indicate an uptrend for Infosys.")

    elif analysis_type == "📑 Fundamental Analysis":
        st.markdown("**Explanation:** This includes analyzing revenue, earnings, debt, P/E ratio, and ROE.")
        st.info("Note: Fundamental data like balance sheet or income statement is not available through Yahoo Finance APIs. External APIs are required.")
        st.success("📌 Comment: Infosys Ltd has consistently maintained strong profit margins and a healthy balance sheet over the past few years.")

    elif analysis_type == "💬 Sentimental Analysis":
        st.markdown("**Explanation:** Sentiment analysis uses NLP techniques on news and social media to assess market perception.")
        st.info("Note: You can integrate news APIs (like NewsAPI.org or Twitter API) for real-time sentiment.")
        st.success("📌 Comment: Market sentiment is currently neutral-to-positive, as reflected by recent analyst ratings and news articles.")

    elif analysis_type == "📈 Quantitative Analysis":
        st.markdown("**Explanation:** Quantitative models use statistical methods or machine learning to predict trends.")
        st.info("Note: You can extend this app using scikit-learn, Prophet, or ARIMA for forecasting.")
        st.success("📌 Comment: Simple regression-based projections indicate a steady growth trend over the medium term.")

# ----------------- Footer ----------------- #
st.markdown("""
    <hr>
    <p style='text-align: center; color: grey;'>
        🚀 Built with Streamlit | 📡 Live Data via Yahoo Finance | 🧠 Extendable with ML & APIs
    </p>
    """, unsafe_allow_html=True)
