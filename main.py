from datetime import datetime
import openai
from fpdf import FPDF
import tempfile
import os
import pandas as pd
from stock_analysis.data_fetcher import StockDataFetcher
from stock_analysis.data_analyzer import StockAnalyzer
from stock_analysis.data_visualizer import StockVisualizer
import anthropic
from fpdf import FPDF
import tempfile
import os
from datetime import datetime

class ClaudeReportGenerator:
    def __init__(self, api_key):
        self.client = anthropic.Anthropic(api_key=api_key)

    def get_claude_analysis(self, stock_data, market_overview):
        """Get Claude analysis of the stock data."""
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
        
        Provide specific insights about:
        1. Price trends and momentum
        2. Valuation compared to sector peers
        3. Key risks and opportunities
        4. Market sentiment and positioning
        """
        
        response = self.client.messages.create(
            model="claude-3-opus-20240229",
            max_tokens=4000,
            messages=[{
                "role": "user",
                "content": prompt
            }]
        )
        
        return response.content[0].text

    def create_pdf_report(self, stock_data, market_overview, selected_stock):
        """Generate a complete PDF report for the given stock."""
        stock_info = stock_data[stock_data['Symbol'] == selected_stock].iloc[0]
        
        try:
            claude_analysis = self.get_claude_analysis(stock_info, market_overview)
        except Exception as e:
            print(f"Error getting Claude analysis: {str(e)}")
            return None
            
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
        pdf.cell(0, 10, f"AI-Enhanced Analysis Report (Claude)", ln=True)
        pdf.cell(0, 10, f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True)
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
        
        # Claude Analysis
        pdf.set_font('DejaVu', '', 14)
        
        pdf.ln(5)
        
        pdf.set_font('DejaVu', '', 12)
        paragraphs = claude_analysis.split('\n\n')
        for para in paragraphs:
            pdf.multi_cell(0, 6, para.strip())
            pdf.ln(5)
        
        try:
            # Create temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
                pdf.output(tmp.name)
                with open(tmp.name, 'rb') as f:
                    pdf_data = f.read()
                os.unlink(tmp.name)
                return pdf_data
        except Exception as e:
            print(f"Error creating PDF: {str(e)}")
            return None
from stock_analysis.data_fetcher import StockDataFetcher
from stock_analysis.data_analyzer import StockAnalyzer
from stock_analysis.data_visualizer import StockVisualizer
import os
import pandas as pd

def main():
    # Gemini API key
    GEMINI_API_KEY = "AIzaSyAtTFQCMaqQglEkSobKHCCUERbyXK5zjCs"
    
    # Create data directory if it doesn't exist
    os.makedirs('data', exist_ok=True)
    
    print("Starting Stock Market Analysis...")

    # Initialize the data fetcher and get stock data
    print("\nFetching stock data...")
    fetcher = StockDataFetcher()
    stock_data = fetcher.fetch_stock_data()

    # Save raw data to CSV
    stock_data_save = stock_data.copy()
    stock_data_save.drop('Historical Data', axis=1, inplace=True)
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
        market_overview['Top Gainers'].to_excel(writer, sheet_name='Top Gainers', index=False)
        market_overview['Most Active'].to_excel(writer, sheet_name='Most Active', index=False)
        sector_dist = pd.DataFrame(market_overview['Sector Distribution'])
        sector_dist.to_excel(writer, sheet_name='Sector Distribution')

    print("Analysis saved to data/stock_analysis.xlsx")

    # Start the visualization dashboard
    print("\nStarting visualization dashboard...")
    print("Access the dashboard at http://localhost:8050")
    
    try:
        visualizer = StockVisualizer(stock_data, market_overview, gemini_api_key=GEMINI_API_KEY)
        print("Gemini API integration enabled successfully.")
    except Exception as e:
        print(f"\nWarning: Gemini API integration failed: {str(e)}")
        print("Falling back to basic visualization without AI analysis.")
        visualizer = StockVisualizer(stock_data, market_overview)
    
    visualizer.run_server(debug=True)

if __name__ == '__main__':
    main()