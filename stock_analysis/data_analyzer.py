import pandas as pd
import numpy as np
from datetime import datetime

class StockAnalyzer:
    def __init__(self, df):
        self.df = df
        self.analysis_date = datetime.now().strftime("%d-%m-%Y %H:%M")
        self._calculate_metrics()
    
    def _calculate_metrics(self):
        """Calculate additional analysis metrics."""
        # Ensure necessary columns are numeric
        numeric_columns = ['P/E Ratio', 'Market Cap (Cr)', 'Volume', 'Daily Change %']
        for col in numeric_columns:
            self.df[col] = pd.to_numeric(self.df[col], errors='coerce')
        
        # Calculate sector metrics
        sector_metrics = self.df.groupby('Sector').agg({
            'P/E Ratio': 'mean',
            'Market Cap (Cr)': 'sum',
            'Volume': 'sum',
            'Daily Change %': 'mean'
        }).round(2)
        
        # Add sector averages back to main dataframe
        self.df['Sector P/E'] = self.df['Sector'].map(sector_metrics['P/E Ratio'])
        self.df['P/E vs Sector'] = self.df['P/E Ratio'] / self.df['Sector P/E']
        
        # Calculate technical indicators for each stock
        for _, row in self.df.iterrows():
            hist_data = row['Historical Data']
            
            # Ensure 'Historical Data' exists and is in expected format
            if isinstance(hist_data, pd.DataFrame) and 'Close' in hist_data.columns:
                try:
                    # Calculate moving averages
                    hist_data['SMA_20'] = hist_data['Close'].rolling(window=20).mean()
                    hist_data['SMA_50'] = hist_data['Close'].rolling(window=50).mean()

                    # Store latest values in main dataframe
                    self.df.loc[self.df['Symbol'] == row['Symbol'], 'SMA_20'] = hist_data['SMA_20'].iloc[-1]
                    self.df.loc[self.df['Symbol'] == row['Symbol'], 'SMA_50'] = hist_data['SMA_50'].iloc[-1]
                    
                    # Calculate and store trading signals
                    self.df.loc[self.df['Symbol'] == row['Symbol'], 'Signal'] = \
                        'Buy' if hist_data['SMA_20'].iloc[-1] > hist_data['SMA_50'].iloc[-1] else 'Sell'
                except Exception as e:
                    print(f"Error processing historical data for {row['Symbol']}: {e}")
            else:
                print(f"Invalid historical data for {row['Symbol']}")
    
    def get_market_overview(self):
        """Get overall market summary."""
        gainers_count = len(self.df[self.df['Daily Change %'] > 0])
        total_stocks = len(self.df)
        market_breadth = gainers_count / total_stocks if total_stocks > 0 else 0
        
        return {
            'Analysis Date': self.analysis_date,
            'Total Market Cap': self.df['Market Cap (Cr)'].sum(),
            'Average P/E': self.df['P/E Ratio'].mean(),
            'Market Breadth': market_breadth,  # Added this metric
            'Top Gainers': self.df.nlargest(5, 'Daily Change %')[
                ['Symbol', 'Company Name', 'Current Price', 'Daily Change %', 'Volume']
            ],
            'Most Active': self.df.nlargest(5, 'Volume')[
                ['Symbol', 'Company Name', 'Current Price', 'Daily Change %', 'Volume']
            ],
            'Sector Distribution': self.df.groupby('Sector')['Market Cap (Cr)'].sum()
        }
    
    def get_sector_analysis(self):
        """Get detailed sector analysis."""
        return self.df.groupby('Sector').agg({
            'Company Name': 'count',
            'Market Cap (Cr)': ['sum', 'mean'],
            'P/E Ratio': ['mean', 'min', 'max'],
            'Daily Change %': ['mean', 'min', 'max'],
            'Volume': 'sum'
        }).round(2)
    
    def get_stock_signals(self):
        """Get trading signals for all stocks."""
        return self.df[['Symbol', 'Company Name', 'Current Price', 'Signal', 
                       'Daily Change %', 'P/E Ratio', 'Sector']].copy()
