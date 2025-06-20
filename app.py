import yfinance as yf
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import ta
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import requests
from bs4 import BeautifulSoup

# Streamlit configuration
st.set_page_config(page_title="Reliance Stock Analysis", layout="wide")

# App title
st.title("📊 Reliance Industries Stock Market Dashboard")

# Sidebar date selection
st.sidebar.header("Settings")
start_date = st.sidebar.date_input("Start Date", pd.to_datetime("2021-01-01"))
end_date = st.sidebar.date_input("End Date", pd.to_datetime("2024-12-31"))

# Download historical data
@st.cache_data
def load_data():
    df = yf.download("RELIANCE.NS", start=start_date, end=end_date)
    df.reset_index(inplace=True)
    return df

df = load_data()

# Preview and safety check
st.write("✅ Downloaded Data Preview")
st.write(df.head())
st.write("📌 Columns in Data:", df.columns.tolist())

# Handle missing or incorrect data
if df.empty:
    st.error("❌ No data retrieved. Please check the date range or internet connection.")
    st.stop()

if "Close" not in df.columns:
    st.error("❌ 'Close' column not found. Data may be corrupted.")
    st.stop()

# Convert 'Close' column to numeric safely
try:
    df["Close"] = pd.to_numeric(df["Close"], errors="coerce")
    df.dropna(subset=["Close"], inplace=True)
except Exception as e:
    st.error(f"❌ Error converting 'Close' to numeric: {e}")
    st.stop()

# Display latest data
st.subheader("📈 Historical Stock Data")
st.dataframe(df.tail(), use_container_width=True)

# Technical indicators
try:
    df["SMA_20"] = ta.trend.SMAIndicator(close=df["Close"], window=20).sma_indicator()
    df["RSI"] = ta.momentum.RSIIndicator(close=df["Close"], window=14).rsi()
    df["MACD"] = ta.trend.MACD(close=df["Close"]).macd_diff()
except Exception as e:
    st.error(f"❌ Failed to calculate technical indicators: {e}")
    st.stop()

# Plotting indicators
st.subheader("📉 Technical Analysis")
tab1, tab2, tab3 = st.tabs(["SMA 20", "RSI", "MACD"])

with tab1:
    st.line_chart(df[["Close", "SMA_20"]])
with tab2:
    st.line_chart(df["RSI"])
with tab3:
    st.line_chart(df["MACD"])

# Fundamental Analysis
st.subheader("📊 Fundamental Analysis")
stock = yf.Ticker("RELIANCE.NS")
info = stock.info

col1, col2, col3 = st.columns(3)
col1.metric("Market Cap", f'{info.get("marketCap", 0):,}')
col2.metric("PE Ratio", info.get("trailingPE", "N/A"))
roe = info.get("returnOnEquity")
col3.metric("Return on Equity", f"{round(roe * 100, 2)}%" if roe else "N/A")

st.write("📌 Sector:", info.get("sector", "N/A"))
st.write("📌 Website:", info.get("website", "N/A"))
st.write("📌 Business Summary:")
st.markdown(f'> {info.get("longBusinessSummary", "Summary not available.")}')

# Sentiment Analysis (News headlines)
st.subheader("📰 News Sentiment Analysis")

def fetch_news_sentiment():
    url = "https://news.google.com/search?q=Reliance+Industries+Limited"
    try:
        r = requests.get(url)
        soup = BeautifulSoup(r.text, 'html.parser')
        analyzer = SentimentIntensityAnalyzer()
        headlines = []
        for title in soup.find_all('a'):
            text = title.text.strip()
            if "Reliance" in text and len(text) > 30:
                sentiment = analyzer.polarity_scores(text)
                headlines.append((text, sentiment["compound"]))
        return headlines[:10]
    except:
        return [("❌ Failed to fetch news", 0.0)]

news_sentiments = fetch_news_sentiment()
for headline, score in news_sentiments:
    st.write(f"**{headline}** — Sentiment Score: {score:.2f}")

st.success("✅ All analysis completed successfully!")
