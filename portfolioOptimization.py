# Using Sharpe Ratio to get max return for lowest risk

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import numpy as np
from scipy.optimize import minimize
import tkinter as tk
from fredapi import Fred
import streamlit as st
import time
'''
BACKEND
'''

def run_analysis():
    # Set the risk-free rate ---> Simplified
    #risk_free_rate = 2.5
    # Replace 'your_api_key' with your actual FRED API key
    fred = Fred(api_key = 'b87221305af25a6edfeca4d69d6e6f72')
    ten_year_treasury_rate = fred.get_series_latest_release('GS10') / 100
    
    # Set the risk-free rate
    risk_free_rate = ten_year_treasury_rate.iloc[-1]
    print(risk_free_rate)
    

    # Define the tickers we need
    # List of them all
    tickers = ["SPY", "BND", "GLD", "QQQ", "VTI"]
    # Set end date to today
    end_date = datetime.today()
    # Set start date to 5 years ago
    start_date = end_date - timedelta(days = 5*365)

    # Download adjusted close prices. More accurate than just closed price
    adj_close_df = pd.DataFrame()

    # Download the close prices for each ticker. Loop through all in list
    for ticker in tickers:
        data = yf.download(ticker, start = start_date, end = end_date)
        adj_close_df[ticker] = data['Close'] # We didn't download adjsuted clost unfortunately. Find out how to do that
        # Display the DataFrame
        print (adj_close_df)

        '''
        import yfinance as yf
        from datetime import datetime, timedelta

        tickers = ["SPY", "BND", "GLD", "QQQ", "VTI"]
        end_date = datetime.today()
        start_date = end_date - timedelta(days=5*365)

        for t in tickers:
        data = yf.download(t, start=start_date, end=end_date)
        print(t, "empty?" , data.empty, "shape:", data.shape)
        print("columns:", list(data.columns))
        print(data.head(1))
        print("---")
        '''

    # Calculating Lognormal daily returns
    log_return = np.log(adj_close_df / adj_close_df.shift(1))

    # Drop any missing values
    log_return = log_return.dropna()

    print (log_return)

    # Calculate the covariance matrix. STD and risk in optimal way
    cov_matrix = log_return.cov()*252
    print (cov_matrix)

    # Calculate the portfolio performance metrics
    # Portfolio SD
    print ("standard deviation")
    def standard_deviation (weights, cov_matrix):
        variance = weights.t @ cov_matrix @ weights
        return np.sqrt(variance)

    # Expected returns based on historical returns (average of the past returns... not the best assumption but best we have right now)
    print ("expected return")
    def expected_return (weights, log_returns):
        return np.sum(log_returns.mean()*weights) * 252 # number of trading days in a year

    # Calculate the Sharpe Ratio
    print ("sharpe ratio")
    def sharpe_ratio (weights, log_returns, cov_matrix, risk_free_rate):
        return(expected_return (weights, log_returns) - risk_free_rate) / standard_deviation(weights, cov_matrix)
   




'''
Testing
print (start_date)
print (end_date)
print (tickers)
'''



'''
FRONTEND UserInterface
'''
root = tk.Tk()
root.title("Portfolio Analyzer")

# Variable to hold results
result_text = tk.StringVar()
result_text.set("Click 'Run Analysis' to begin.")

# Add a label to show results
label = tk.Label(root, textvariable=result_text, justify="left")
label.pack(pady=10)

# Add a button to trigger analysis
button = tk.Button(root, text="Run Analysis", command=run_analysis)
button.pack(pady=5)

root.mainloop()

st.title("Portfolio Analyzer")

tickers = ["SPY", "BND", "GLD", "QQQ", "VTI"]
end_date = datetime.today()
start_date = end_date - timedelta(days=5*365)

# Download prices
adj_close_df = yf.download(tickers, start=start_date, end=end_date)["Adj Close"]

# Returns
log_return = np.log(adj_close_df / adj_close_df.shift(1)).dropna()

# Show table + chart
st.line_chart(adj_close_df)
st.write("Log Returns:", log_return.head())


# Live updating dynamic graphs
st.title("Live Stock Price")

ticker = "SPY"
chart = st.line_chart([])

while True:
    data = yf.download(ticker, period="1d", interval="1m")["Adj Close"]
    chart.line_chart(data)
    time.sleep(60)  # update every 60 seconds