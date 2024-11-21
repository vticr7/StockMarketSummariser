from stock_analysis.data_fetcher import StockDataFetcher
from stock_analysis.data_analyzer import StockAnalyzer
from stock_analysis.data_visualizer import StockVisualizer
import pandas as pd
import os

def main():
    # Create data directory if it doesn't exist
    os.makedirs('data', exist_ok=True)
    
    print("Starting Stock Market Analysis...")
    
    # Initialize components
    fetcher = StockDataFetcher()
    
    # Fetch data
    print("\nFetching stock data...")
    stock_data = fetcher.fetch_stock_data()
    
    # Save raw data
    stock_data.to_csv('data/raw_stock_data.csv', index=False)
    print("Raw data saved to data/raw_stock_data.csv")
    
    # Analyze data
    print("\nAnalyzing stock data...")
    analyzer = StockAnalyzer(stock_data)
    market_overview = analyzer.get_market_overview()
    trading_signals = analyzer.get_stock_signals()
    
    # Save analysis results
    print("\nSaving analysis results...")
    with pd.ExcelWriter('data/stock_analysis.xlsx') as writer:
        trading_signals.to_excel(writer, sheet_name='Trading Signals', index=False)
        pd.DataFrame([market_overview]).to_excel(writer, sheet_name='Market Overview')
    
    print("\nAnalysis saved to data/stock_analysis.xlsx")
    
    # Start visualization dashboard
    print("\nStarting visualization dashboard...")
    print("Access the dashboard at http://localhost:8050")
    visualizer = StockVisualizer(stock_data, market_overview)
    visualizer.run_server(debug=True)

if __name__ == '__main__':
    main()