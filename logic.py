import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.io as pio
import database_loader

pio.renderers.default = 'browser'


# Define ETF tickers
tickers = ['DBC', 'GSG', 'GLD', 'DIA', 'SPY', 'GOVT', 'FBND', 'SCHZ']
benchmark_ticker = 'SPY'

def fetch_data(tickers, benchmark_ticker, start_date="2010-01-01", api = True, u= None, p=None):
    if api == False:
        """Fetch historical price data for ETFs and benchmark."""
        data = yf.download(tickers + [benchmark_ticker], start=start_date, progress=False)['Adj Close']
        #print(data.head())
        return data
    else:
        data = database_loader.fetch_live_data_from_api(tickers, start_date, benchmark_ticker, u, p)
        #print(data.head())
        return data


def calculate_trailing_returns(data):
    """Calculate trailing returns for 1 month, 3 months, 1 year, and 3 years."""
    trailing_returns = {
        '1 Month': data.pct_change(periods=21).iloc[-1],
        '3 Month': data.pct_change(periods=63).iloc[-1],
        '1 Year': data.pct_change(periods=252).iloc[-1],
        '3 Year': data.pct_change(periods=252 * 3).iloc[-1]
    }
    return pd.DataFrame(trailing_returns).T

def calculate_risk_statistics(data):
    """Calculate risk statistics like volatility, Sharpe ratio, and max drawdown."""
    daily_returns = data.pct_change()
    risk_stats = {
        'Annualized Volatility': daily_returns.std() * np.sqrt(252),
        'Sharpe Ratio': (daily_returns.mean() * 252) / (daily_returns.std() * np.sqrt(252)),
        'Max Drawdown': data.div(data.cummax()).min() - 1
    }
    return pd.DataFrame(risk_stats)

def calculate_dividend_info(tickers, data):
    """Fetch dividend yield and annual payout for each ETF."""
    dividends = {}
    for ticker in tickers:
        etf = yf.Ticker(ticker)
        div = etf.dividends
        dividends[ticker] = {
            'Dividend Yield (%)': (div.sum() / data[ticker].iloc[-1]) * 100 if not div.empty else 0,
            'Annual Payout ($)': div.sum() if not div.empty else 0
        }
    return pd.DataFrame(dividends).T

def generate_visualization(trailing_returns_df):
    """Create a bar chart visualization for trailing returns."""
    fig = go.Figure()
    for col in trailing_returns_df.columns:
        fig.add_trace(go.Bar(
            x=trailing_returns_df.index,
            y=trailing_returns_df[col],
            name=col
        ))
    fig.update_layout(
        title="Trailing Returns Comparison",
        xaxis_title="Time Period",
        yaxis_title="Returns",
        barmode="group"
    )
    return fig

if __name__ == "__main__":
    # Step 1: Fetch data
    data = fetch_data(tickers, benchmark_ticker)
    
    # Step 2: Calculate metrics
    trailing_returns_df = calculate_trailing_returns(data)
    risk_stats_df = calculate_risk_statistics(data)
    dividends_df = calculate_dividend_info(tickers, data)
    
    # Step 3: Generate visualizations
    trailing_returns_fig = generate_visualization(trailing_returns_df)
    
    # Display results
    print("Trailing Returns:")
    print(trailing_returns_df)
    
    print("\nRisk Statistics:")
    print(risk_stats_df)
    
    print("\nDividend Information:")
    print(dividends_df)
    
    # Optional: Show the visualization
    trailing_returns_fig
