# Titan Stock Analysis with Streamlit

import streamlit as st
import yfinance as yf
import pandas as pd
from ta.trend import SMAIndicator, MACD
from ta.momentum import RSIIndicator
from textblob import TextBlob
from bs4 import BeautifulSoup
import requests

# ----------------------- Data Loader -----------------------
@st.cache_data
def load_stock_data(ticker="TITAN.NS", start="2015-01-01"):
    df = yf.download(ticker, start=start)
    df.reset_index(inplace=True)
    return df

# ------------------ Technical Analysis ---------------------
def apply_technical_indicators(df):
    df['SMA_50'] = SMAIndicator(close=df['Close'], window=50).sma_indicator()
    df['RSI'] = RSIIndicator(close=df['Close']).rsi()
    df['MACD'] = MACD(close=df['Close']).macd_diff()
    return df

# ------------------ Fundamental Analysis -------------------
def get_fundamentals(ticker="TITAN.NS"):
    stock = yf.Ticker(ticker)
    info = stock.info
    return {
        "Market Cap": info.get("marketCap"),
        "Trailing P/E": info.get("trailingPE"),
        "Dividend Yield": info.get("dividendYield"),
        "ROE": info.get("returnOnEquity"),
        "Book Value": info.get("bookValue"),
        "Debt to Equity": info.get("debtToEquity"),
        "Earnings Growth": info.get("earningsQuarterlyGrowth"),
    }

# ------------------ Sentiment Analysis ---------------------
def get_news_headlines(keyword="Titan Company"):
    url = f"https://news.google.com/rss/search?q={keyword.replace(' ', '+')}"
    r = requests.get(url)
    soup = BeautifulSoup(r.content, features="xml")
    headlines = [item.title.text for item in soup.findAll("item")]
    return headlines[:10]

def analyze_sentiment(texts):
    sentiments = [TextBlob(text).sentiment.polarity for text in texts]
    return sum(sentiments)/len(sentiments) if sentiments else 0

# -------------------- Streamlit App ------------------------
st.set_page_config(page_title="Titan Stock Analysis", layout="wide")
st.title("Titan Company Ltd (TITAN.NS) - Stock Analysis")

# Load Data
df = load_stock_data()
df = apply_technical_indicators(df)

# Show Price Chart
st.subheader("📈 Stock Price with SMA")
st.line_chart(df.set_index("Date")[['Close', 'SMA_50']])

# Technical Indicators
st.subheader("📊 Technical Indicators")
st.line_chart(df.set_index("Date")[['RSI', 'MACD']])

# Fundamental Analysis
st.subheader("🧾 Fundamental Analysis")
fundamentals = get_fundamentals()
for k, v in fundamentals.items():
    st.metric(label=k, value=v)

# Sentiment Analysis
st.subheader("📰 Sentiment Analysis from News")
news = get_news_headlines()
sentiment_score = analyze_sentiment(news)
st.metric("Average Sentiment Score", f"{sentiment_score:.2f}")
