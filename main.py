from stock_analysis.data_fetcher import StockDataFetcher
from stock_analysis.data_analyzer import StockAnalyzer
from stock_analysis.data_visualizer import StockVisualizer
import os
import pandas as pd
import openai
from fpdf import FPDF
from datetime import datetime

class GPTStockReportGenerator:
    def __init__(self, api_key):
        """Initialize the report generator with OpenAI API key."""
        openai.api_key = api_key
        
    def get_gpt_analysis(self, stock_data, market_overview):
        """Get GPT analysis of the stock data."""
        prompt = f"""
        Please analyze this stock data and provide a detailed report with the following sections:
        1. Executive Summary
        2. Technical Analysis
        3. Fundamental Analysis
        4. Market Context
        5. Risk Assessment
        
        Stock Data:
        - Symbol: {stock_data['Symbol']}
        - Company: {stock_data['Company Name']}
        - Current Price: ₹{stock_data['Current Price']:.2f}
        - Daily Change: {stock_data['Daily Change %']:.2f}%
        - P/E Ratio: {stock_data['P/E Ratio']:.2f}
        - Sector P/E: {stock_data['Sector P/E']:.2f}
        - Market Cap: ₹{stock_data['Market Cap (Cr)']:.2f} Cr
        
        Market Context:
        - Total Market Cap: ₹{market_overview['Total Market Cap']/1000:.2f}T
        - Market Breadth: {market_overview['Market Breadth']*100:.1f}%
        - Average Market P/E: {market_overview['Average P/E']:.2f}
        """
        
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a professional stock market analyst. Provide detailed, data-driven analysis using the provided metrics."},
                {"role": "user", "content": prompt}
            ]
        )
        
        return response.choices[0].message.content

    def create_pdf_report(self, stock_data, market_overview, stock_symbol, output_path=None):
        """Generate a complete PDF report for the given stock."""
        # Get stock-specific data
        stock_info = stock_data[stock_data['Symbol'] == stock_symbol].iloc[0]
        
        # Get GPT analysis
        gpt_analysis = self.get_gpt_analysis(stock_info, market_overview)
        
        # Create PDF
        pdf = FPDF()
        pdf.add_page()
        
        # Set up fonts
        pdf.add_font('DejaVu', '', 'DejaVuSansCondensed.ttf', uni=True)
        pdf.set_font('DejaVu', '', 12)
        
        # Title
        pdf.set_font('DejaVu', '', 24)
        pdf.cell(0, 10, f"{stock_info['Company Name']} ({stock_info['Symbol']})", ln=True, align='C')
        pdf.ln(10)
        
        # Date
        pdf.set_font('DejaVu', '', 10)
        pdf.cell(0, 10, f"Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True)
        pdf.ln(10)
        
        # Key Metrics
        pdf.set_font('DejaVu', '', 14)
        pdf.cell(0, 10, "Key Metrics", ln=True)
        pdf.ln(5)
        
        pdf.set_font('DejaVu', '', 12)
        metrics = [
            f"Current Price: ₹{stock_info['Current Price']:.2f}",
            f"Daily Change: {stock_info['Daily Change %']:.2f}%",
            f"P/E Ratio: {stock_info['P/E Ratio']:.2f}",
            f"Market Cap: ₹{stock_info['Market Cap (Cr)']:.2f} Cr",
            f"52W High: ₹{stock_info['52W High']:.2f}",
            f"52W Low: ₹{stock_info['52W Low']:.2f}"
        ]
        
        for metric in metrics:
            pdf.cell(0, 8, metric, ln=True)
        pdf.ln(10)
        
        # GPT Analysis
        pdf.set_font('DejaVu', '', 14)
        pdf.cell(0, 10, "Analysis", ln=True)
        pdf.ln(5)
        
        pdf.set_font('DejaVu', '', 12)
        # Split GPT analysis into paragraphs and add to PDF
        paragraphs = gpt_analysis.split('\n\n')
        for para in paragraphs:
            pdf.multi_cell(0, 6, para.strip())
            pdf.ln(5)
        
        # Save PDF
        if output_path is None:
            output_path = f"data/stock_report_{stock_symbol}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            
        pdf.output(output_path)
        return output_path

def main():
    # Replace with your OpenAI API key
    OPENAI_API_KEY = "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"
    
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

    # Generate GPT-enhanced PDF reports for each stock
    print("\nGenerating GPT-enhanced PDF reports...")
    report_gen = GPTStockReportGenerator(OPENAI_API_KEY)
    
    # Generate reports for all stocks
    for symbol in stock_data['Symbol'].unique():
        try:
            output_path = report_gen.create_pdf_report(
                stock_data=stock_data,
                market_overview=market_overview,
                stock_symbol=symbol
            )
            print(f"Generated report for {symbol}: {output_path}")
        except Exception as e:
            print(f"Error generating report for {symbol}: {str(e)}")

    # Start the visualization dashboard
    print("\nStarting visualization dashboard...")
    print("Access the dashboard at http://localhost:8050")
    visualizer = StockVisualizer(stock_data, market_overview)
    visualizer.run_server(debug=True)

if __name__ == '__main__':
    main()