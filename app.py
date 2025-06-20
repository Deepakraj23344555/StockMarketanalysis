import yfinance as yf
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import ta
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import requests
from bs4 import BeautifulSoup

st.set_page_config(page_title="Reliance Stock Analysis", layout="wide")

# Title
st.title("📊 Reliance Industries Stock Market Dashboard")

# Sidebar
st.sidebar.header("Settings")
start_date = st.sidebar.date_input("Start Date", pd.to_datetime("2021-01-01"))
end_date = st.sidebar.date_input("End Date", pd.to_datetime("2024-12-31"))

# Download data
@st.cache_data
def load_data():
    data = yf.download("RELIANCE.NS", start=start_date, end=end_date)
    data.reset_index(inplace=True)
    data.to_csv("reliance_data.csv", index=False)
    return data

df = load_data()

# Show dataframe
st.subheader("📈 Historical Data")
st.dataframe(df.tail())

# Technical Analysis
df["SMA_20"] = ta.trend.sma_indicator(df["Close"], window=20)
df["RSI"] = ta.momentum.rsi(df["Close"], window=14)
df["MACD"] = ta.trend.macd_diff(df["Close"])

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
col1.metric("Market Cap", f'{info["marketCap"]:,}')
col2.metric("PE Ratio", info.get("trailingPE", "N/A"))
col3.metric("Return on Equity", round(info.get("returnOnEquity", 0)*100, 2) if info.get("returnOnEquity") else "N/A")

st.write("📌 Sector:", info.get("sector"))
st.write("📌 Website:", info.get("website"))
st.write("📌 Business Summary:")
st.markdown(f'> {info.get("longBusinessSummary")}')

# Sentiment Analysis - News Headlines
st.subheader("📰 News Sentiment Analysis")

def fetch_news_sentiment():
    url = "https://news.google.com/search?q=Reliance+Industries+Limited"
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    analyzer = SentimentIntensityAnalyzer()
    headlines = []
    for title in soup.find_all('a'):
        text = title.text
        if "Reliance" in text:
            sentiment = analyzer.polarity_scores(text)
            headlines.append((text, sentiment["compound"]))
    return headlines[:10]

news_sentiments = fetch_news_sentiment()

for headline, score in news_sentiments:
    st.write(f"**{headline}** — Sentiment Score: {score}")

st.success("✅ Analysis Complete")
