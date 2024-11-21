
# stock_analysis/data_visualizer.py
from dash import Dash, dcc, html, Input, Output, State
import plotly.express as px
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate
import pdfkit
from datetime import datetime
import yfinance as yf
import pandas as pd
import base64
import io

class StockVisualizer:
    def __init__(self, df, market_overview):
        self.df = df
        self.market_overview = market_overview
        self.app = Dash(
            __name__,
            external_stylesheets=[
                dbc.themes.DARKLY,  # Dark theme for better aesthetics
                'https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap',
                'https://fonts.googleapis.com/icon?family=Material+Icons'
            ]
        )
        self.setup_custom_styles()
        self._setup_layout()
        self._setup_callbacks()

    def setup_custom_styles(self):
        """Add custom styles to the dashboard."""
        self.app.index_string = '''
        <!DOCTYPE html>
        <html>
            <head>
                {%metas%}
                <title>Stock Market Analysis Dashboard</title>
                {%favicon%}
                {%css%}
                <style>
                    /* Custom CSS */
                    :root {
                        --primary-color: #2c3e50;
                        --secondary-color: #3498db;
                        --accent-color: #e74c3c;
                        --background-color: #1a1a1a;
                        --card-background: #2d2d2d;
                        --text-color: #ecf0f1;
                    }
                    
                    body {
                        background-color: var(--background-color);
                        color: var(--text-color);
                        font-family: 'Poppins', sans-serif;
                    }
                    
                    .dashboard-container {
                        max-width: 1800px;
                        margin: 0 auto;
                        padding: 20px;
                    }
                    
                    .header {
                        background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
                        padding: 20px;
                        border-radius: 15px;
                        margin-bottom: 30px;
                        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
                    }
                    
                    .dashboard-title {
                        font-size: 2.5em;
                        font-weight: 700;
                        margin: 0;
                        color: white;
                        text-align: center;
                    }
                    
                    .metrics-container {
                        display: grid;
                        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                        gap: 20px;
                        margin-bottom: 30px;
                    }
                    
                    .metric-card {
                        background: var(--card-background);
                        padding: 25px;
                        border-radius: 15px;
                        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
                        transition: transform 0.3s ease;
                        display: flex;
                        align-items: center;
                    }
                    
                    .metric-card:hover {
                        transform: translateY(-5px);
                    }
                    
                    .metric-icon {
                        font-size: 2.5em;
                        margin-right: 20px;
                        color: var(--secondary-color);
                    }
                    
                    .metric-content {
                        flex-grow: 1;
                    }
                    
                    .metric-title {
                        font-size: 1em;
                        color: #95a5a6;
                        margin: 0;
                    }
                    
                    .metric-value {
                        font-size: 1.8em;
                        font-weight: 600;
                        margin: 5px 0 0;
                        color: white;
                    }
                    
                    .chart-container {
                        background: var(--card-background);
                        padding: 20px;
                        border-radius: 15px;
                        margin-bottom: 20px;
                        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
                    }
                    
                    .data-table {
                        width: 100%;
                        border-collapse: separate;
                        border-spacing: 0;
                        margin: 10px 0;
                        background: var(--card-background);
                        border-radius: 10px;
                        overflow: hidden;
                    }
                    
                    .data-table th {
                        background: var(--primary-color);
                        padding: 15px;
                        color: white;
                        font-weight: 600;
                    }
                    
                    .data-table td {
                        padding: 12px 15px;
                        border-bottom: 1px solid rgba(255,255,255,0.1);
                    }
                    
                    .data-table tbody tr:hover {
                        background: rgba(52, 152, 219, 0.1);
                    }
                    
                    .tab-container {
                        margin: 20px 0;
                    }
                    
                    .custom-tab {
                        background-color: var(--card-background);
                        border-radius: 10px;
                        padding: 20px;
                        margin-top: 10px;
                    }
                    
                    /* Export button styles */
                    .export-button {
                        background: var(--secondary-color);
                        color: white;
                        border: none;
                        padding: 10px 20px;
                        border-radius: 5px;
                        cursor: pointer;
                        transition: background-color 0.3s ease;
                    }
                    
                    .export-button:hover {
                        background: #2980b9;
                    }
                </style>
            </head>
            <body>
                {%app_entry%}
                <footer>
                    {%config%}
                    {%scripts%}
                    {%renderer%}
                </footer>
            </body>
        </html>
        '''

    def _setup_layout(self):
        """Create the enhanced dashboard layout."""
        self.app.layout = html.Div([
            # Header with Export Button
            html.Div([
                html.Div([
                    html.H1('Stock Market Analysis Dashboard', className='dashboard-title'),
                    html.P(f"Last Updated: {self.market_overview['Analysis Date']}", 
                          className='update-time'),
                    html.Button(
                        'Export Report (PDF)',
                        id='export-button',
                        className='export-button'
                    ),
                    dcc.Download(id="download-pdf")
                ], className='header-content')
            ], className='header'),
            
            # Market Overview Cards
            html.Div([
                self._create_metric_card(
                    "Total Market Cap",
                    f"₹{self.market_overview['Total Market Cap']:,.0f} Cr",
                    "trending_up"
                ),
                self._create_metric_card(
                    "Average P/E",
                    f"{self.market_overview['Average P/E']:.2f}",
                    "analytics"
                ),
                self._create_metric_card(
                    "Market Breadth",
                    f"{self.market_overview['Market Breadth']:.1%}",
                    "show_chart"
                )
            ], className='metrics-container'),
            
            # Main Content Tabs
            dcc.Tabs([
                # Stock Analysis Tab
                dcc.Tab(label='Stock Analysis', children=[
                    html.Div([
                        # Stock Selector and Charts
                        html.Div([
                            html.Div([
                                html.Label('Select Stock:', className='select-label'),
                                dcc.Dropdown(
                                    id='stock-selector',
                                    options=[{
                                        'label': f"{name} ({symbol})", 
                                        'value': symbol
                                    } for symbol, name in zip(
                                        self.df['Symbol'], 
                                        self.df['Company Name']
                                    )],
                                    value=self.df['Symbol'].iloc[0],
                                    className='stock-dropdown'
                                )
                            ], className='selector-container'),
                            
                            dcc.Graph(id='price-chart', className='chart-container'),
                            dcc.Graph(id='volume-chart', className='chart-container')
                        ], className='charts-panel'),
                        
                        # Stock Info Panel
                        html.Div([
                            html.Div(id='stock-info-panel', className='info-panel')
                        ], className='info-container')
                    ], className='tab-content')
                ], className='custom-tab'),
                
                # Sector Analysis Tab
                dcc.Tab(label='Sector Analysis', children=[
                    html.Div([
                        dcc.Graph(id='sector-chart'),
                        html.Div(id='sector-metrics', className='metrics-grid')
                    ], className='tab-content')
                ], className='custom-tab'),
                
                # Earnings Call Analysis Tab
                dcc.Tab(label='Earnings Analysis', children=[
                    html.Div([
                        html.H3('Latest Earnings Call Highlights'),
                        html.Div(id='earnings-highlights', className='highlights-container'),
                        dcc.Graph(id='earnings-trends')
                    ], className='tab-content')
                ], className='custom-tab')
            ], className='tabs-container')
        ], className='dashboard-container')

    def _create_metric_card(self, title, value, icon):
        """Create an enhanced metric card."""
        return html.Div([
            html.Div([
                html.I(className="material-icons metric-icon", children=icon)
            ], className='metric-icon-container'),
            html.Div([
                html.H3(title, className='metric-title'),
                html.H2(value, className='metric-value')
            ], className='metric-content')
        ], className='metric-card')

    def _setup_callbacks(self):
        """Setup enhanced interactive callbacks."""
        @self.app.callback(
            [Output('price-chart', 'figure'),
             Output('volume-chart', 'figure'),
             Output('stock-info-panel', 'children'),
             Output('earnings-highlights', 'children')],
            [Input('stock-selector', 'value')]
        )
        def update_stock_charts(symbol):
            if not symbol:
                raise PreventUpdate
            
            # Get stock data
            stock_data = self.df[self.df['Symbol'] == symbol]['Historical Data'].iloc[0]
            stock_info = yf.Ticker(f"{symbol}.NS").info
            
            # Create price chart
            price_fig = go.Figure()
            price_fig.add_trace(go.Candlestick(
                x=stock_data.index,
                open=stock_data['Open'],
                high=stock_data['High'],
                low=stock_data['Low'],
                close=stock_data['Close'],
                name='Price'
            ))
            
            if 'SMA_20' in stock_data.columns:
                price_fig.add_trace(go.Scatter(
                    x=stock_data.index,
                    y=stock_data['SMA_20'],
                    name='20-day MA',
                    line=dict(color='orange', width=2)
                ))
            
            price_fig.update_layout(
                template='plotly_dark',
                title=f'{symbol} Price Movement',
                yaxis_title='Price (₹)',
                xaxis_title='Date',
                height=400
            )
            
            # Create volume chart
            volume_fig = go.Figure()
            volume_fig.add_trace(go.Bar(
                x=stock_data.index,
                y=stock_data['Volume'],
                name='Volume'
            ))
            
            volume_fig.update_layout(
                template='plotly_dark',
                title=f'{symbol} Trading Volume',
                yaxis_title='Volume',
                xaxis_title='Date',
                height=300
            )
            
            # Create stock info panel
            stock_info_panel = html.Div([
                html.H3('Company Overview'),
                html.P(stock_info.get('longBusinessSummary', 'No description available')),
                html.Div([
                    self._create_info_card('Market Cap', f"₹{stock_info.get('marketCap', 0)/10000000:,.0f}Cr"),
                    self._create_info_card('52 Week High', f"₹{stock_info.get('fiftyTwoWeekHigh', 0):,.2f}"),
                    self._create_info_card('52 Week Low', f"₹{stock_info.get('fiftyTwoWeekLow', 0):,.2f}"),
                    self._create_info_card('P/E Ratio', f"{stock_info.get('trailingPE', 0):,.2f}")
                ], className='info-grid')
            ])
            
            # Get earnings call highlights
            earnings_highlights = self._get_earnings_highlights(symbol)
            
            return price_fig, volume_fig, stock_info_panel, earnings_highlights

        @self.app.callback(
            Output("download-pdf", "data"),
            Input("export-button", "n_clicks"),
            prevent_initial_call=True
        )
        def export_report(n_clicks):
            if not n_clicks:
                raise PreventUpdate
            
            # Generate report content
            report_html = self._generate_report_html()
            
            # Convert to PDF using pdfkit
            pdf_buffer = io.BytesIO()
            pdfkit.from_string(report_html, pdf_buffer)
            
            # Return the PDF file
            return dcc.send_bytes(
                pdf_buffer.getvalue(),
                f"stock_analysis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            )

    def _create_info_card(self, title, value):
        """Create an info card for stock details."""
        return html.Div([
            html.H4(title, className='info-title'),
            html.P(value, className='info-value')
        ], className='info-card')

    def _get_earnings_highlights(self, symbol):
        """Get and analyze earnings call transcripts."""
        try:
            # This is a placeholder - you would need to implement actual earnings call data fetching
            # For now, we'll return some sample data
            return html.Div([
                html.H4('Latest Earnings Call Highlights'),
                html.Ul([
                    html.Li('Revenue grew by XX% year-over-year'),
                    html.Li('Expanded market share in key segments'),
                    html.Li('Launched new product initiatives'),
                    html.Li('Positive outlook for next quarter')
                ], className='highlights-list')
            ])
        except Exception as e:
            return html.P('Earnings call data not available')

    def _generate_report_html(self):
        """Generate HTML content for PDF report."""
        report_date = datetime.now().strftime("%d %B, %Y")
        
        html_content = f'''
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 1200px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                
                .header {{
                    text-align: center;
                    padding: 20px;
                    background: #2c3e50;
                    color: white;
                    margin-bottom: 30px;
                }}
                
                .section {{
                    margin-bottom: 30px;
                    padding: 20px;
                    background: #f9f9f9;
                    border-radius: 5px;
                }}
                
                table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin: 15px 0;
                }}
                
                th, td {{
                    border: 1px solid #ddd;
                    padding: 12px;
                    text-align: left;
                }}
                
                th {{
                    background-color: #2c3e50;
                    color: white;
                }}
                
                tr:nth-child(even) {{
                    background-color: #f2f2f2;
                }}
                
                .metric-card {{
                    background: white;
                    padding: 15px;
                    border-radius: 5px;
                    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                    margin-bottom: 15px;
                }}
                
                .chart-container {{
                    margin: 20px 0;
                    text-align: center;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Stock Market Analysis Report</h1>
                <p>Generated on {report_date}</p>
            </div>
            
            {self._generate_market_overview_html()}
            
            {self._generate_top_stocks_html()}
            
            {self._generate_sector_analysis_html()}
            
            {self._generate_technical_analysis_html()}
            
            {self._generate_earnings_analysis_html()}
        </body>
        </html>
        '''
        
        return html_content
    
    def _generate_market_overview_html(self):
        """Generate HTML for market overview section."""
        return f'''
        <div class="section">
            <h2>Market Overview</h2>
            <div class="metric-card">
                <h3>Total Market Cap</h3>
                <p>₹{self.market_overview['Total Market Cap']:,.0f} Cr</p>
            </div>
            <div class="metric-card">
                <h3>Average P/E</h3>
                <p>{self.market_overview['Average P/E']:.2f}</p>
            </div>
            <div class="metric-card">
                <h3>Market Breadth</h3>
                <p>{self.market_overview['Market Breadth']:.1%}</p>
            </div>
        </div>
        '''
    
    def _generate_top_stocks_html(self):
        """Generate HTML for top stocks section."""
        top_gainers = self.market_overview['Top Gainers']
        
        gainers_table = '''
        <table>
            <thead>
                <tr>
                    <th>Symbol</th>
                    <th>Company Name</th>
                    <th>Price</th>
                    <th>Daily Change %</th>
                </tr>
            </thead>
            <tbody>
        '''
        
        for _, row in top_gainers.iterrows():
            gainers_table += f'''
                <tr>
                    <td>{row['Symbol']}</td>
                    <td>{row['Company Name']}</td>
                    <td>₹{row['Current Price']:,.2f}</td>
                    <td>{row['Daily Change %']:.2f}%</td>
                </tr>
            '''
        
        gainers_table += '''
            </tbody>
        </table>
        '''
        
        return f'''
        <div class="section">
            <h2>Top Performing Stocks</h2>
            {gainers_table}
        </div>
        '''
    
    def _generate_sector_analysis_html(self):
        """Generate HTML for sector analysis section."""
        sector_data = self.df.groupby('Sector').agg({
            'Market Cap (Cr)': 'sum',
            'P/E Ratio': 'mean',
            'Daily Change %': 'mean'
        }).round(2)
        
        sector_table = '''
        <table>
            <thead>
                <tr>
                    <th>Sector</th>
                    <th>Market Cap (Cr)</th>
                    <th>Average P/E</th>
                    <th>Daily Change %</th>
                </tr>
            </thead>
            <tbody>
        '''
        
        for sector, row in sector_data.iterrows():
            sector_table += f'''
                <tr>
                    <td>{sector}</td>
                    <td>₹{row['Market Cap (Cr)']:,.0f}</td>
                    <td>{row['P/E Ratio']:.2f}</td>
                    <td>{row['Daily Change %']:.2f}%</td>
                </tr>
            '''
        
        sector_table += '''
            </tbody>
        </table>
        '''
        
        return f'''
        <div class="section">
            <h2>Sector Analysis</h2>
            {sector_table}
        </div>
        '''
    
    def _generate_technical_analysis_html(self):
        """Generate HTML for technical analysis section."""
        signals = []
        for _, row in self.df.iterrows():
            if hasattr(row, 'Signal'):
                signals.append({
                    'Symbol': row['Symbol'],
                    'Company Name': row['Company Name'],
                    'Signal': row['Signal'],
                    'Current Price': row['Current Price'],
                    'SMA_20': row.get('SMA_20', 0),
                    'SMA_50': row.get('SMA_50', 0)
                })
        
        if not signals:
            return ''
        
        signals_table = '''
        <table>
            <thead>
                <tr>
                    <th>Symbol</th>
                    <th>Company Name</th>
                    <th>Signal</th>
                    <th>Price</th>
                    <th>SMA 20</th>
                    <th>SMA 50</th>
                </tr>
            </thead>
            <tbody>
        '''
        
        for signal in signals:
            signals_table += f'''
                <tr>
                    <td>{signal['Symbol']}</td>
                    <td>{signal['Company Name']}</td>
                    <td>{signal['Signal']}</td>
                    <td>₹{signal['Current Price']:,.2f}</td>
                    <td>₹{signal['SMA_20']:,.2f}</td>
                    <td>₹{signal['SMA_50']:,.2f}</td>
                </tr>
            '''
        
        signals_table += '''
            </tbody>
        </table>
        '''
        
        return f'''
        <div class="section">
            <h2>Technical Analysis Signals</h2>
            {signals_table}
        </div>
        '''
    
    def _generate_earnings_analysis_html(self):
        """Generate HTML for earnings analysis section."""
        return f'''
        <div class="section">
            <h2>Earnings Analysis Summary</h2>
            <p>Note: This section provides analysis of recent earnings calls and financial performance highlights.</p>
            <div class="metric-card">
                <h3>Key Findings</h3>
                <ul>
                    <li>Overall sector performance trends</li>
                    <li>Notable company developments</li>
                    <li>Future outlook and guidance</li>
                </ul>
            </div>
        </div>
        '''

    def run_server(self, debug=False, port=8050):
        """Run the dashboard server."""
        self.app.run_server(debug=debug, port=port)