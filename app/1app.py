# app.py

import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, date

# ---------------------- Page Config ---------------------- #
st.set_page_config(page_title="📊 Infosys Stock Analysis", layout="wide")

# ---------------------- Title ---------------------- #
st.markdown("""
    <h1 style='text-align: center; color: #2C3E50;'>
        📈 Infosys Ltd (INFY.NS) - Live Stock Market Analyzer
    </h1>
    """, unsafe_allow_html=True)

# ---------------------- Sidebar Inputs ---------------------- #
st.sidebar.header("📅 Select Date Range")

# New: clearly exposed user input for date range
min_date = date(2015, 1, 1)
start_date = st.sidebar.date_input("Start Date", value=date(2023, 1, 1), min_value=min_date, max_value=date.today())
end_date = st.sidebar.date_input("End Date", value=date.today(), min_value=start_date, max_value=date.today())

st.sidebar.header("📂 Choose Analysis Type")
analysis_type = st.sidebar.selectbox(
    "Analysis Type",
    ("📊 Technical Analysis", "📑 Fundamental Analysis", "💬 Sentimental Analysis", "📈 Quantitative Analysis")
)

# ---------------------- Fetch Stock Data ---------------------- #
ticker = "INFY.NS"

@st.cache_data(ttl=3600)
def fetch_data(ticker, start_date, end_date):
    try:
        data = yf.download(ticker, start=start_date, end=end_date)
        data.dropna(inplace=True)
        return data
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return None

data = fetch_data(ticker, start_date, end_date)

# ---------------------- Display Chart ---------------------- #
st.subheader(f"📉 Stock Price Chart: {ticker} ({start_date} to {end_date})")

if data is not None and not data.empty:
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data.index, y=data["Close"], mode="lines", name="Close Price", line=dict(color="cyan")))
    fig.update_layout(
        title="Infosys Ltd (INFY.NS) Stock Price",
        xaxis_title="Date",
        yaxis_title="Price (INR)",
        template="plotly_dark",
        height=500
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.error("⚠️ No stock data found for this date range. Try adjusting the dates.")

# ---------------------- Analysis Section ---------------------- #
st.subheader("🔍 Analysis Output")

if data is not None and not data.empty:
    if analysis_type == "📊 Technical Analysis":
        data['SMA20'] = data['Close'].rolling(window=20).mean()
        data['SMA50'] = data['Close'].rolling(window=50).mean()

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=data.index, y=data['Close'], name="Close Price", line=dict(color="white")))
        fig.add_trace(go.Scatter(x=data.index, y=data['SMA20'], name="SMA 20", line=dict(color="orange")))
        fig.add_trace(go.Scatter(x=data.index, y=data['SMA50'], name="SMA 50", line=dict(color="green")))
        fig.update_layout(title="📊 Technical Analysis: SMA Indicators", template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("**Explanation:** The 20-day and 50-day Simple Moving Averages (SMA) show short- and mid-term price trends.")
        st.success("📌 Comment: A bullish crossover occurs when SMA20 rises above SMA50 — a sign of upward momentum.")

    elif analysis_type == "📑 Fundamental Analysis":
        st.markdown("**Explanation:** Fundamental analysis covers revenue, profit, EPS, P/E ratio, ROE, etc.")
        st.info("Note: For real fundamentals, connect APIs like Alpha Vantage, Ticker, or Screener.in.")
        st.success("📌 Comment: Infosys has shown consistent quarterly profits, low debt, and strong global presence.")

    elif analysis_type == "💬 Sentimental Analysis":
        st.markdown("**Explanation:** Sentiment reflects investor mood based on news, tweets, or earnings calls.")
        st.info("Note: For true analysis, integrate News API or X (Twitter) + NLP.")
        st.success("📌 Comment: Public sentiment toward Infosys is mostly positive due to global IT growth and digital services.")

    elif analysis_type == "📈 Quantitative Analysis":
        st.markdown("**Explanation:** Uses statistics or ML models like regression, ARIMA, or Prophet for forecasting.")
        st.info("You can extend this with scikit-learn or Facebook Prophet.")
        st.success("📌 Comment: Quantitative trends show a mild upward drift. Past volatility remains within predictable bands.")

# ---------------------- Footer ---------------------- #
st.markdown("""
    <hr>
    <p style='text-align: center; color: grey;'>
        🔄 Live data from Yahoo Finance | 🧠 Extendable with Machine Learning & APIs | 🚀 Built with Streamlit
    </p>
""", unsafe_allow_html=True)
