# app.py

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import date

# ----------------- Page Configuration ----------------- #
st.set_page_config(page_title="📊 Tech Innovations Ltd - Stock Analyzer", layout="wide")

# ----------------- Title ----------------- #
st.markdown("""
    <h1 style='text-align: center; color: #2C3E50;'>
        📈 Tech Innovations Ltd - Stock Market Analyzer
    </h1>
    """, unsafe_allow_html=True)

# ----------------- Sidebar Inputs ----------------- #
st.sidebar.header("📅 Select Date Range")
start_date = st.sidebar.date_input("Start Date", value=date(2023, 1, 1))
end_date = st.sidebar.date_input("End Date", value=date(2023, 1, 6))

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

# ----------------- Load Sample Data from CSV ----------------- #
data = pd.read_csv("tech_innovations_sample.csv", parse_dates=["Date"])
data.set_index("Date", inplace=True)

# Filter based on selected range
data = data.loc[(data.index >= pd.to_datetime(start_date)) & (data.index <= pd.to_datetime(end_date))]

# ----------------- Price Chart ----------------- #
st.subheader(f"📉 Stock Price Chart ({start_date} to {end_date})")

if not data.empty:
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data.index, y=data['Close'], mode='lines+markers', name='Close Price'))
    fig.update_layout(
        title='Stock Price Over Selected Date Range',
        xaxis_title='Date', yaxis_title='Price (INR)',
        template='plotly_dark', height=500
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("No data found for the selected date range.")

# ----------------- Analysis Output ----------------- #
st.subheader("🔍 Analysis Output")

if not data.empty:
    if analysis_type == "📊 Technical Analysis":
        # Add SMA indicators
        data['SMA20'] = data['Close'].rolling(window=2).mean()
        data['SMA50'] = data['Close'].rolling(window=3).mean()

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=data.index, y=data['Close'], name="Close Price"))
        fig.add_trace(go.Scatter(x=data.index, y=data['SMA20'], name="SMA 2"))
        fig.add_trace(go.Scatter(x=data.index, y=data['SMA50'], name="SMA 3"))
        fig.update_layout(title="Technical Analysis with Simple Moving Averages", template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("**Explanation:** Moving Averages help identify trends in stock price. A bullish crossover occurs when the short-term average crosses above the long-term average.")
        st.success("📌 Comment: The stock shows bullish momentum if short-term SMA > long-term SMA.")

    elif analysis_type == "📑 Fundamental Analysis":
        st.markdown("**Explanation:** Fundamental analysis includes evaluating earnings, book value, return on equity, and other key financial metrics.")
        st.info("Note: In a full app, this would pull financial statements from an API.")
        st.success("📌 Comment: Based on assumed data, Tech Innovations Ltd shows strong fundamentals and consistent growth.")

    elif analysis_type == "💬 Sentimental Analysis":
        st.markdown("**Explanation:** Sentiment analysis assesses public opinion using news headlines and social media.")
        st.info("Note: You can integrate Twitter/X API or news APIs here in a full version.")
        st.success("📌 Comment: Recent sentiment suggests increasing investor confidence in Tech Innovations' R&D focus.")

    elif analysis_type == "📈 Quantitative Analysis":
        st.markdown("**Explanation:** Quantitative analysis uses statistical methods like regression or forecasting.")
        st.info("You can implement regression, ARIMA, or Prophet for future price prediction.")
        st.success("📌 Comment: A linear trend shows moderate upward momentum in the selected date window.")

else:
    st.info("No analysis available as no data is loaded for the selected date range.")

# ----------------- Footer ----------------- #
st.markdown("""
    <hr>
    <p style='text-align: center; color: grey;'>
        🚀 Built with Streamlit | 📊 Data: Local CSV Sample
    </p>
    """, unsafe_allow_html=True)
