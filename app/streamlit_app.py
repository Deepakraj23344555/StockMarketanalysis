import streamlit as st
import pandas as pd
from textblob import TextBlob
import yfinance as yf
import ta
import requests
from bs4 import BeautifulSoup

# 1. Load Historical Stock Data
@st.cache_data
def load_data(ticker="TITAN.NS", start="2015-01-01"):
    df = yf.download(ticker, start=start)
    df.reset_index(inplace=True)
    return df

# 2. Technical Indicators
def add_technical_indicators(df):
    df["SMA_50"] = ta.trend.sma_indicator(df["Close"], window=50)
    df["RSI"] = ta.momentum.RSIIndicator(df["Close"]).rsi()
    df["MACD"] = ta.trend.macd_diff(df["Close"])
    return df

# 3. Fundamental Analysis
def get_fundamentals(ticker="TITAN.NS"):
    stock = yf.Ticker(ticker)
    info = stock.info
    return {
        "Market Cap": info.get("marketCap"),
        "PE Ratio": info.get("trailingPE"),
        "Dividend Yield": info.get("dividendYield"),
        "ROE": info.get("returnOnEquity"),
        "Book Value": info.get("bookValue"),
        "Debt to Equity": info.get("debtToEquity"),
        "EPS Growth": info.get("earningsQuarterlyGrowth"),
    }

# 4. Sentiment Analysis
def get_news_headlines(keyword="Titan Company"):
    headers = {"User-Agent": "Mozilla/5.0"}
    url = f"https://news.google.com/rss/search?q={keyword.replace(' ', '+')}"
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'xml')
    headlines = [item.title.text for item in soup.find_all('item')][:10]
    return headlines

def sentiment_score(texts):
    sentiments = [TextBlob(text).sentiment.polarity for text in texts]
    return round(sum(sentiments) / len(sentiments), 2) if sentiments else 0

# STREAMLIT APP
st.set_page_config(page_title="Titan Stock Analysis", layout="wide")
st.title("📊 Titan Company Stock Market Analysis")

# Load data
df = load_data()
df = add_technical_indicators(df)

# Sidebar Controls
st.sidebar.header("Display Options")
show_fundamentals = st.sidebar.checkbox("Show Fundamentals", value=True)
show_technical = st.sidebar.checkbox("Show Technical Analysis", value=True)
show_sentiment = st.sidebar.checkbox("Show Sentiment Analysis", value=True)

# Fundamentals
if show_fundamentals:
    st.subheader("🧾 Fundamental Analysis")
    fundamentals = get_fundamentals()
    st.dataframe(pd.DataFrame(fundamentals.items(), columns=["Metric", "Value"]))

# Technical Analysis
if show_technical:
    st.subheader("📈 Technical Analysis")
    st.line_chart(df.set_index("Date")[["Close", "SMA_50"]])
    st.line_chart(df.set_index("Date")[["RSI", "MACD"]])

# Sentiment Analysis
if show_sentiment:
    st.subheader("📰 Sentiment Analysis from News")
    headlines = get_news_headlines()
    st.write("### Latest Headlines:")
    for headline in headlines:
        st.markdown(f"- {headline}")
    sentiment = sentiment_score(headlines)
    st.metric("Average Sentiment Score", sentiment)

st.caption("Data Source: Yahoo Finance and Google News RSS")
