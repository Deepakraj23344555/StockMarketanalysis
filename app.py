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

# Title
st.title("📊 Reliance Industries Stock Market Dashboard")

# Sidebar date selection
st.sidebar.header("Settings")
start_date = st.sidebar.date_input("Start Date", pd.to_datetime("2021-01-01"))
end_date = st.sidebar.date_input("End Date", pd.to_datetime("2024-12-31"))

# Load data from Yahoo Finance
@st.cache_data
def load_data():
    df = yf.download("RELIANCE.NS", start=start_date, end=end_date)
    df.reset_index(inplace=True)
    return df

df = load_data()

# Debug preview
st.write("🔍 Preview of Data", df.head())
st.write("📌 Columns Found:", df.columns.tolist())

# Error handling
if df.empty or "Close" not in df.columns:
    st.error("No data retrieved or 'Close' column missing. Please check date or ticker.")
    st.stop()

# Ensure Close column is a 1D Series
close_series = df["Close"]
if isinstance(close_series, pd.DataFrame):
    close_series = close_series.iloc[:, 0]

# Convert Close to numeric safely
df["Close"] = pd.to_numeric(close_series.values.flatten(), errors="coerce")

# Drop rows with missing Close values
df.dropna(subset=["Close"], inplace=True)

# Display historical data
st.subheader("📈 Historical Stock Data")
st.dataframe(df.tail(), use_container_width=True)

# Technical Indicators
try:
    df["SMA_20"] = ta.trend.SMAIndicator(close=df["Close"], window=20).sma_indicator()
    df["RSI"] = ta.momentum.RSIIndicator(close=df["Close"], window=14).rsi()
    df["MACD"] = ta.trend.MACD(close=df["Close"]).macd_diff()
except Exception as e:
    st.error(f"Error computing indicators: {e}")
    st.stop()

# Tabs for visualizing indicators
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
col3.metric("Return on Equity", f"{round(roe*100, 2)}%" if roe else "N/A")

st.write("📌 Sector:", info.get("sector", "N/A"))
st.write("📌 Website:", info.get("website", "N/A"))
st.write("📌 Business Summary:")
st.markdown(f"> {info.get('longBusinessSummary', 'No summary available.')}")

# Sentiment Analysis
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
        return [("News fetch failed", 0.0)]

news_sentiments = fetch_news_sentiment()

for headline, score in news_sentiments:
    st.write(f"**{headline}** — Sentiment Score: {score:.2f}")

st.success("✅ Analysis Complete")
