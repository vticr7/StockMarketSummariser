
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from tqdm import tqdm
import time

class StockDataFetcher:
    def __init__(self):
        self.nifty50_symbols = [
    "ADANIENT.NS", "ADANIPORTS.NS", "APOLLOHOSP.NS", "ASIANPAINT.NS", "AXISBANK.NS",
    "BAJAJ-AUTO.NS", "BAJAJFINSV.NS", "BAJFINANCE.NS", "BPCL.NS", "BHARTIARTL.NS",
    "BRITANNIA.NS", "CIPLA.NS", "COALINDIA.NS", "DIVISLAB.NS", "DRREDDY.NS",
    "EICHERMOT.NS", "GRASIM.NS", "HCLTECH.NS", "HDFC.NS", "HDFCBANK.NS",
    "HDFCLIFE.NS", "HEROMOTOCO.NS", "HINDALCO.NS", "HINDUNILVR.NS", "ICICIBANK.NS",
    "INDUSINDBK.NS", "INFY.NS", "ITC.NS", "JSWSTEEL.NS", "KOTAKBANK.NS",
    "LT.NS", "M&M.NS", "MARUTI.NS", "NTPC.NS", "NESTLEIND.NS",
    "ONGC.NS", "POWERGRID.NS", "RELIANCE.NS", "SBILIFE.NS", "SBIN.NS",
    "SUNPHARMA.NS", "TCS.NS", "TATACONSUM.NS", "TATAMOTORS.NS", "TATASTEEL.NS",
    "TECHM.NS", "TITAN.NS", "ULTRACEMCO.NS", "UPL.NS", "WIPRO.NS"
]


    def fetch_stock_data(self, period="1y"):
        """Fetch stock data including prices and basic metrics."""
        all_stock_data = []
        
        for symbol in tqdm(self.nifty50_symbols, desc="Fetching stock data"):
            try:
                # Get stock data
                stock = yf.Ticker(symbol)
                info = stock.info
                hist = stock.history(period=period)
                
                if hist.empty:
                    continue
                
                # Calculate basic metrics using iloc for index access
                latest_price = hist['Close'].iloc[-1]
                prev_price = hist['Close'].iloc[-2]
                daily_return = (latest_price - prev_price) / prev_price * 100
                
                # Store relevant data
                stock_data = {
                    'Symbol': symbol.replace('.NS', ''),
                    'Company Name': info.get('longName', 'N/A'),
                    'Sector': info.get('sector', 'N/A'),
                    'Current Price': latest_price,
                    'Daily Change %': daily_return,
                    'Market Cap (Cr)': info.get('marketCap', 0) / 10000000,  # Convert to Crores
                    'P/E Ratio': info.get('trailingPE', 0),
                    '52W High': info.get('fiftyTwoWeekHigh', 0),
                    '52W Low': info.get('fiftyTwoWeekLow', 0),
                    'Volume': hist['Volume'].iloc[-1],
                    'Historical Data': hist
                }
                
                all_stock_data.append(stock_data)
                time.sleep(1)  # Prevent rate limiting
                
            except Exception as e:
                print(f"Error fetching {symbol}: {str(e)}")
                continue
                
        return pd.DataFrame(all_stock_data)