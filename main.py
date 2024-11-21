from stock_analysis.data_fetcher import StockDataFetcher
from stock_analysis.data_analyzer import StockAnalyzer
from stock_analysis.data_visualizer import StockVisualizer
import os
import pandas as pd

def main():
    # Create data directory if it doesn't exist
    os.makedirs('data', exist_ok=True)
    
    print("Starting Stock Market Analysis...")

    # Initialize the data fetcher and get stock data
    print("\nFetching stock data...")
    fetcher = StockDataFetcher()
    stock_data = fetcher.fetch_stock_data()

    # Save raw data to CSV
    stock_data_save = stock_data.copy()
    stock_data_save.drop('Historical Data', axis=1, inplace=True)  # Remove historical data for CSV saving
    stock_data_save.to_csv('data/raw_stock_data.csv', index=False)
    print("Raw data saved to data/raw_stock_data.csv")

    # Analyze the data
    print("\nAnalyzing stock data...")
    analyzer = StockAnalyzer(stock_data)
    market_overview = analyzer.get_market_overview()
    trading_signals = analyzer.get_stock_signals()

    # Save analysis results
    print("\nSaving analysis results...")
    with pd.ExcelWriter('data/stock_analysis.xlsx') as writer:
        trading_signals.to_excel(writer, sheet_name='Trading Signals', index=False)
        
        # Convert market overview to DataFrame for Excel
        market_overview_df = pd.DataFrame({
            'Metric': ['Analysis Date', 'Total Market Cap', 'Average P/E', 'Market Breadth'],
            'Value': [
                market_overview['Analysis Date'],
                market_overview['Total Market Cap'],
                market_overview['Average P/E'],
                market_overview['Market Breadth']
            ]
        })
        market_overview_df.to_excel(writer, sheet_name='Market Overview', index=False)
        
        # Save top gainers
        market_overview['Top Gainers'].to_excel(writer, sheet_name='Top Gainers', index=False)
        
        # Save most active stocks
        market_overview['Most Active'].to_excel(writer, sheet_name='Most Active', index=False)
        
        # Save sector distribution
        sector_dist = pd.DataFrame(market_overview['Sector Distribution'])
        sector_dist.to_excel(writer, sheet_name='Sector Distribution')

    print("Analysis saved to data/stock_analysis.xlsx")

    # Start the visualization dashboard
    print("\nStarting visualization dashboard...")
    print("Access the dashboard at http://localhost:8050")
    visualizer = StockVisualizer(stock_data, market_overview)
    visualizer.run_server(debug=True)

if __name__ == '__main__':
    main()