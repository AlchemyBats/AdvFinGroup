import pandas as pd
from wrds import Connection
from getpass import getpass
import os

user = None
passw = None

def get_login_info():
    global user
    global passw
    if user == None or passw == None:
        """
        Load WRDS login credentials from a file or prompt the user for input.
        The file 'credentials.txt' must contain the username on the first line and the password on the second line.
        If the file contains default values ('username' and 'password'), prompt the user to input credentials.
        """
        credentials_file = "credentials.txt"
        
        # Check if the credentials file exists
        if os.path.exists(credentials_file):
            with open(credentials_file, "r") as f:
                lines = f.readlines()
                if len(lines) >= 2:
                    username = lines[0].strip()
                    password = lines[1].strip()
                    
                    # Check if the default credentials are being used
                    if username.lower() == "username" and password.lower() == "password":
                        print("Default credentials detected. Please enter your WRDS credentials.")
                        username = input("Enter WRDS username: ")
                        password = getpass("Enter WRDS password: ")
                else:
                    print("Invalid credentials file format. Please enter your WRDS credentials.")
                    username = input("Enter WRDS username: ")
                    password = getpass("Enter WRDS password: ")
        else:
            # Prompt for credentials if the file doesn't exist
            print("Credentials file not found. Please enter your WRDS credentials.")
            username = input("Enter WRDS username: ")
            password = getpass("Enter WRDS password: ")
    else:
        return user, passw
    user = username
    passw = passw
    return username, password


def get_wrds_connection(username, password):
    """
    Establish and return a WRDS connection using user-provided credentials.
    """
    return Connection(wrds_username=username, password=password)

def get_permnos_for_tickers(tickers, conn):
    """
    Fetch the permno values corresponding to the given tickers from WRDS.
    """
    tickers_str = "', '".join(tickers)
    query = f"""
    SELECT permno, ticker
    FROM crsp.stocknames
    WHERE ticker IN ('{tickers_str}')
    """
    #print("Fetching permno mappings for tickers...")
    mapping = conn.raw_sql(query)
    if mapping.empty:
        raise ValueError("No matching permno values found for the provided tickers.")
    return mapping

def fetch_live_data_from_api(tickers, start_date="2010-01-01", benchmark_ticker=None, username=None, password=None):
    """
    Fetch live data from WRDS API and return it in the format of yfinance data.
    """
    if username is None or password is None:
        username, password = get_login_info()
    
    # Establish connection
    conn = get_wrds_connection(username, password)
    
    # Map tickers to permnos
    all_tickers = tickers + ([benchmark_ticker] if benchmark_ticker else [])
    mapping = get_permnos_for_tickers(all_tickers, conn)
    permnos = mapping['permno'].tolist()
    
    # Fetch historical returns for the permnos
    permnos_str = ", ".join(map(str, permnos))
    query = f"""
    SELECT date, permno, ret 
    FROM crsp.dsf 
    WHERE date >= '{start_date}' AND permno IN ({permnos_str})
    """
    #print("Fetching historical data from WRDS...")
    data = conn.raw_sql(query)
    conn.close()
    
    if data.empty:
        raise ValueError("No data returned from WRDS for the specified tickers and date range.")
    
    # Transform returns into cumulative prices
    data['date'] = pd.to_datetime(data['date'])
    data.sort_values(by=['permno', 'date'], inplace=True)
    
    # Calculate cumulative prices for each permno
    data['price'] = data.groupby('permno')['ret'].apply(lambda x: (1 + x).cumprod() * 100).reset_index(level=0, drop=True)
    
    # Pivot the data to match yfinance format
    pivot_data = data.pivot(index='date', columns='permno', values='price')
    
    # Map permno columns back to tickers
    permno_to_ticker = dict(zip(mapping['permno'], mapping['ticker']))
    pivot_data.columns = [permno_to_ticker.get(col, f"Unknown-{col}") for col in pivot_data.columns]
    
    # Ensure the column order matches the input tickers
    pivot_data = pivot_data[tickers]
    
    # Format index and columns to match yfinance
    pivot_data.index.name = 'Date'
    pivot_data.index = pivot_data.index.tz_localize('UTC')  # Add timezone information to match yfinance
    
    return pivot_data

if __name__ == "__main__":
    tickers = ['DBC', 'GSG', 'GLD', 'DIA', 'SPY', 'GOVT', 'FBND', 'SCHZ']
    benchmark_ticker = 'SPY'
    
    # Fetch data from WRDS
    data = fetch_live_data_from_api(tickers, start_date="2010-01-01", benchmark_ticker=benchmark_ticker)
    
    # Display the fetched data
    #print("Fetched Data:")
    #print(data.head())
