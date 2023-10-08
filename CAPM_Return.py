# importing libraries
import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import date, datetime
import capm_functions
import pandas_datareader.data as web


st.set_page_config(page_title="CAPM",
                   page_icon="chart_with_upwards_trends",
                   layout='wide'
                   )


st.title("Capital Asset Pricing Model ")

# GETTING INPUT FROM USER
try:

    col1, col2 = st.columns([1, 1])
    with col1:
        stocks_list = st.multiselect("Choose stocks by ticker ", ['TSLA', 'AAPL', 'NFLX', 'MSFT', 'MGM', 'AMZN', 'NVDA', 'GOOGL'], default=[
                                    'TSLA', 'AAPL', 'NFLX', 'MSFT', 'MGM', 'AMZN', 'NVDA', 'GOOGL'])
    with col2:
        year = st.number_input("Number of years", 1, 10)

    # downloading data for SP500

    end = date.today()
    start = date.today() - pd.DateOffset(years=year)
    SP500 = web.DataReader(['sp500'], 'fred', start, end)

    stocks_df = pd.DataFrame()

    for stock in stocks_list:
        data = yf.download(stock, period=f'{year}y')
        stocks_df[f'{stock}'] = data['Close']

    stocks_df.reset_index(inplace=True)
    SP500.reset_index(inplace=True)
    SP500.columns = ['Date', 'sp500']
    stocks_df['Date'] = stocks_df['Date'].astype('datetime64[ns]')
    stocks_df['Date'] = stocks_df['Date'].apply(lambda x: str(x)[:10])
    stocks_df['Date'] = pd.to_datetime(stocks_df['Date'])
    stocks_df = pd.merge(stocks_df, SP500, on='Date', how='inner')

    col1, col2 = st.columns([1, 1])
    with col1:
        st.markdown("### Dataframe Head")
        st.dataframe(stocks_df.head(), use_container_width=True)

    with col2:
        st.markdown("### Dataframe tail")
        st.dataframe(stocks_df.tail(), use_container_width=True)

    col1, col2 = st.columns([1, 1])
    with col1:
        st.markdown("### Price Of All Stocks")
        st.plotly_chart(capm_functions.interactive_plot(stocks_df))

    with col2:
        print(capm_functions.normalize(stocks_df))
        st.markdown("### Price of All Stocks (After Normalizing)")
        st.plotly_chart(capm_functions.interactive_plot(
            capm_functions.normalize(stocks_df)))

    stocks_daily_return = capm_functions.daily_return(stocks_df)
    print(stocks_daily_return.head())

    beta = {}
    alpha = {}

    for i in stocks_daily_return.columns:
        if i != 'Date' and i != 'SP500'and i != 'sp500' :
            b, a = capm_functions.calculate_beta(stocks_daily_return, i)

            beta[i] = b
            alpha[i] = a

    print(beta, alpha)

    beta_df = pd.DataFrame(columns=['Stock', 'Beta Value'])
    beta_df['Stock'] = beta.keys()
    beta_df['Beta Value'] = [str(round(i, 2)) for i in beta.values()]

    with col1:
        st.markdown('### Calculated Beta Value')
        st.dataframe(beta_df, use_container_width=True)

    rf = 0
    rm = stocks_daily_return['sp500'].mean() * 252

    market_return_premium = rm - rf  # Market return premium

    expected_return_df = pd.DataFrame()

    return_value = []
    for stock, beta_value in beta.items():
        if  stock != 'SP500' and stock != 'sp500':  # Exclude both 'SP500' and 'sp500'
            expected_return = rf + (beta_value * market_return_premium)
            return_value.append(str(round(expected_return, 2)))

    print("Length of stocks_list:", len(stocks_list))
    print("Length of return_value:", len(return_value))

    expected_return_df['Stock'] = stocks_list
    expected_return_df['Expected Return'] = return_value

    print("Length of expected_return_df:", len(expected_return_df))
    with col2:
        st.markdown("### Calculated Return Using CAPM")

        # Ensure that return_value has the same length as stocks_list
        if len(return_value) == len(stocks_list):
            st.dataframe(expected_return_df, use_container_width=True)
        else:
            st.error("Error calculating return values. Please ensure the lengths match.")

except:
    st.write("Please select valid inputs")

