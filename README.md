import yfinance as yf
import pandas as pd
import numpy as np

# Define ETF tickers
tickers = ['DBC', 'GSG', 'GLD', 'DIA', 'SPY', 'GOVT', 'FBND', 'SCHZ']

# Define benchmark for comparison
benchmark_ticker = 'SPY'

# Download historical data for ETFs and benchmark
data = yf.download(tickers + [benchmark_ticker], start="2010-01-01", progress=False)['Adj Close']

# Calculate daily returns
daily_returns = data.pct_change()

# Calculate trailing returns
trailing_returns = {
    '1 Month': data.pct_change(periods=21).iloc[-1],
    '3 Month': data.pct_change(periods=63).iloc[-1],
    '1 Year': data.pct_change(periods=252).iloc[-1],
    '3 Year': data.pct_change(periods=252 * 3).iloc[-1]
}

# Convert trailing returns to DataFrame
trailing_returns_df = pd.DataFrame(trailing_returns).T

# Calculate risk statistics
risk_stats = {
    'Annualized Volatility': daily_returns.std() * np.sqrt(252),
    'Sharpe Ratio': (daily_returns.mean() * 252) / (daily_returns.std() * np.sqrt(252)),
    'Max Drawdown': data.div(data.cummax()).min() - 1
}
risk_stats_df = pd.DataFrame(risk_stats)

# Fetch dividend information
dividends = {}
for ticker in tickers:
    etf = yf.Ticker(ticker)
    div = etf.dividends
    dividends[ticker] = {
        'Dividend Yield (%)': (div.sum() / data[ticker].iloc[-1]) * 100 if not div.empty else 0,
        'Annual Payout ($)': div.sum() if not div.empty else 0
    }
dividends_df = pd.DataFrame(dividends).T

# Show results to user
print("Trailing Returns:")
print(trailing_returns_df)

print("\nRisk Statistics:")
print(risk_stats_df)

print("\nDividend Information:")
print(dividends_df)
