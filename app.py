import yfinance as yf
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import ta
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import requests
from bs4 import BeautifulSoup

# Page setup
st.set_page_config(page_title="Reliance Stock Analysis", layout="wide")
st.title("📊 Reliance Industries Stock Market Dashboard")

# Sidebar date inputs
st.sidebar.header("Settings")
start_date = st.sidebar.date_input("Start Date", pd.to_datetime("2021-01-01"))
end_date = st.sidebar.date_input("End Date", pd.to_datetime("2024-12-31"))

# Load data
@st.cache_data
def load_data():
    df = yf.download("RELIANCE.NS", start=start_date, end=end_date)
    df.reset_index(inplace=True)
    return df

df = load_data()

# Debug info
st.write("✅ Raw Data Preview")
st.write(df.head())
st.write("📌 Columns Available:", df.columns.tolist())

# Check if data is empty or invalid
if df is None or df.empty:
    st.error("❌ No data retrieved. Check date range or internet connection.")
    st.stop()

if "Close" not in df.columns:
    st.error("❌ 'Close' column missing. Please verify data source.")
    st.stop()

# Convert 'Close' column safely
try:
    close_data = df["Close"]

    # If Close is accidentally a DataFrame (multi-indexed), fix it
    if isinstance(close_data, pd.DataFrame):
        close_data = close_data.iloc[:, 0]

    df["Close"] = pd.to_numeric(close_data, errors="coerce")
    df.dropna(subset=["Close"], inplace=True)

except Exception as e:
    st.error(f"❌ Error converting 'Close' to numeric: {e}")
    st.stop()

# Show latest cleaned data
st.subheader("📈 Cleaned Stock Data")
st.dataframe(df.tail(), use_container_width=True)

# Technical Indicators
try:
    df["SMA_20"] = ta.trend.SMAIndicator(close=df["Close"], window=20).sma_indicator()
    df["RSI"] = ta.momentum.RSIIndicator(close=df["Close"], window=14).rsi()
    df["MACD"] = ta.trend.MACD(close=df["Close"]).macd_diff()
except Exception as e:
    st.error(f"❌ Technical Indicator Error: {e}")
    st.stop()

# Technical Analysis Tabs
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
st.markdown(f'> {info.get("longBusinessSummary", "No summary available.")}')

# Sentiment Analysis from Google News
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
    except Exception as e:
        return [(f"❌ Failed to fetch news: {e}", 0.0)]

# Display news sentiment
news_sentiments = fetch_news_sentiment()
for headline, score in news_sentiments:
    st.write(f"**{headline}** — Sentiment Score: {score:.2f}")

st.success("✅ All analysis complete.")
