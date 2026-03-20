import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.express as px
from stocknews import StockNews as sn

name = st.sidebar.text_input("Enter name....")
date_start = st.sidebar.date_input("Start date")
date_end = st.sidebar.date_input("End date")
st.title(f"Stock Data of {name}")

if name == '':
    st.warning("Please enter a stock name in the sidebar.")
    st.stop()
if name == 'SPY':
    name = '^GSPC'
elif name == 'IHSG':
    name = '^JKSE'
elif name == 'NASDAQ':
    name = '^IXIC'
elif name == 'DOW JONES':
    name = '^DJI'

data = yf.download(name, start=date_start, end=date_end)
data.columns = data.columns.droplevel(1)
chart = px.line(data, x=data.index, y= data['Close'], title=f"{name} Closing Price")
st.plotly_chart(chart)
st.metric(label="Start Price", value=f"${data['Close'][0]:.2f}", delta=f"{((data['Close'][-1] - data['Close'][0]) / data['Close'][0]) * 100:.2f}%")
st.metric(label="End Price", value=f"${data['Close'][-1]:.2f}", delta=f"{((data['Close'][-1] - data['Close'][0]) / data['Close'][0]) * 100:.2f}%")
bar = px.bar(data, x=data.index, y= data['Volume'], title=f"{name} Volume")
st.plotly_chart(bar) 

price_data, fundamental_data, news_data = st.tabs(["Price", "Fundamental", "News"])
with price_data:
    st.subheader("Price Data")
    move = data
    move['% Change'] = move['Close'] / move['Close'].shift(1) - 1
    st.write(move)
    returns = move['% Change'].mean() * 252 * 100
    stdev = np.std(data['% Change'])*np.sqrt(252)
    risk = returns/(stdev*100)
    confusion_matrix = pd.DataFrame(
    {
        "returns": [f"{returns:.2%}"],
        "standard deviation": [f"{stdev:.2%}"],
        "risk": [f"{risk:.2%}"]
    },
    index=["Metrics"]
    )
    st.table(confusion_matrix)

with fundamental_data:
    st.subheader("Fundamental Data")
    ticker = yf.Ticker(name)
    col1, col2 = st.columns(2)
    with col1:
        date_start = st.date_input("start date")
    with col2:
        date_end = st.date_input("End date")
    if ticker :
            try:
                saham = yf.Ticker(name)
                report = st.radio("Select Report Type", ("Quarterly", "yearly"), horizontal=True)
                if report == "yearly":
                    financials = saham.financials
                else:
                    financials = saham.quarterly_financials
                if financials is not None and not financials.empty:
                    financials_ts = financials.T
                    financials_ts.index = pd.to_datetime(financials_ts.index)
                    mask = (financials_ts.index >= pd.Timestamp(date_start)) & (financials_ts.index <= pd.Timestamp(date_end))
                    df_filtered = financials_ts.loc[mask]

                    if not df_filtered.empty:
                        st.subheader(f"{report} Financials of {name}")
                        st.data_editor(df_filtered)
                        if 'Total Revenue' in df_filtered.columns and 'Net Income' in df_filtered.columns:
                            df_filtered['Profit Margin'] = (df_filtered['Net Income'] / df_filtered['Total Revenue']) * 100
                            st.subheader(f"{report} Profit Margin of {name}")
                            st.data_editor(df_filtered[['Profit Margin']])
                    else:
                        st.warning("No financial data available for the selected date range.")
                else:
                    st.error("Financial data is not available for this stock.")
            except Exception as e:
                st.error(f"An error occurred while fetching financial data: {e}")
    else:
        st.error("Failed to fetch stock data. Please check the stock name and try again.")

with news_data:
    st.subheader(f"News Data of {name}")
    news = sn(name)    
    news_df = news.read_rss()

    if news_df is not None and not news_df.empty:
        for i in range(len(news_df)):
                st.write(f"**{news_df['published'][i]}**")
                st.write(f"### {news_df['title'][i]}")
                st.write(news_df['summary'][i])
                if 'link' in news_df.columns:
                    st.link_button(label="Read more", url=news_df['link'][i])
                
    if 'sentiment' in news_df.columns:
        val = news_df['sentiment'][i]
        # Memberi warna berdasarkan nilai sentimen
        if val > 0:
            st.success(f"Sentimen Positif: {val}")
        elif val < 0:
            st.error(f"Sentimen Negatif: {val}")
        else:
            st.info(f"Sentimen Netral: {val}")
    
    else:
        st.caption("Tidak ada data sentimen tersedia.")