from dash import Dash, html, dcc, Input, Output, State
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import anthropic
from fpdf import FPDF
import os
import base64
import tempfile

# Define the ClaudeReportGenerator class first
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
        pdf.cell(0, 10, "AI-Generated Analysis", ln=True)
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

# Define color themes
THEMES = {
    'default': {
        'primary': '#2563eb',
        'success': '#16a34a',
        'danger': '#dc2626',
        'background': '#f8fafc',
        'card': '#ffffff',
        'text': '#1e293b',
        'muted': '#64748b',
        'chart': '#2563eb'
    },
    'dark': {
        'primary': '#3b82f6',
        'success': '#22c55e',
        'danger': '#ef4444',
        'background': '#1e293b',
        'card': '#2d3748',
        'text': '#f8fafc',
        'muted': '#94a3b8',
        'chart': '#60a5fa'
    },
    'professional': {
        'primary': '#0369a1',
        'success': '#15803d',
        'danger': '#b91c1c',
        'background': '#f1f5f9',
        'card': '#ffffff',
        'text': '#0f172a',
        'muted': '#475569',
        'chart': '#0284c7'
    }
}

class StockVisualizer:
    def __init__(self, df, market_overview, claude_api_key=None):
        self.df = df
        self.market_overview = market_overview
        self.current_theme = 'default'
        self.claude_generator = ClaudeReportGenerator(claude_api_key) if claude_api_key else None
        
        self.app = Dash(
            __name__,
            external_stylesheets=[
                dbc.themes.BOOTSTRAP,
                'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap'
            ],
            suppress_callback_exceptions=True
        )
        self.setup_layout()
        self.setup_callbacks()

    def create_metric_card(self, title, value, theme, status='primary'):
        return dbc.Card([
            dbc.CardBody([
                html.H6(title, style={'color': theme['muted']}),
                html.H4(value, style={'color': theme[status]})
            ])
        ], style={'backgroundColor': theme['card']})

    def setup_layout(self):
        theme = THEMES[self.current_theme]
        
        self.app.layout = html.Div(id='main-container', children=[
            dbc.Container([
                html.Div([
                    html.H1("Market Analysis Dashboard", 
                           style={'color': theme['text'], 'fontWeight': '700'}),
                    html.Div([
                        dbc.Select(
                            id='theme-selector',
                            options=[
                                {'label': 'Default Theme', 'value': 'default'},
                                {'label': 'Dark Theme', 'value': 'dark'},
                                {'label': 'Professional Theme', 'value': 'professional'}
                            ],
                            value='default',
                            style={'width': '200px', 'marginRight': '1rem'}
                        ),
                        dbc.Button(
                            "Download Report",
                            id="download-button",
                            color="primary",
                            className="mr-2"
                        ),
                        dcc.Download(id="download-report")
                    ], style={'display': 'flex', 'alignItems': 'center'})
                ], style={
                    'display': 'flex',
                    'justifyContent': 'space-between',
                    'alignItems': 'center',
                    'marginBottom': '2rem',
                    'padding': '1rem'
                }),
                
                dbc.Row([
                    dbc.Col([
                        self.create_metric_card(
                            "Market Cap",
                            f"₹{self.market_overview['Total Market Cap']/1000:.2f}T",
                            theme
                        )
                    ], width=12, lg=4),
                    dbc.Col([
                        self.create_metric_card(
                            "Market Breadth",
                            f"{self.market_overview['Market Breadth']*100:.1f}%",
                            theme,
                            'success' if self.market_overview['Market Breadth'] > 0.5 else 'danger'
                        )
                    ], width=12, lg=4),
                    dbc.Col([
                        self.create_metric_card(
                            "Average P/E",
                            f"{self.market_overview['Average P/E']:.2f}",
                            theme
                        )
                    ], width=12, lg=4),
                ], className="mb-4"),
                
                dbc.Card([
                    dbc.CardBody([
                        html.H5("Stock Analysis", style={'color': theme['text']}),
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
                            className="mb-4"
                        ),
                        html.Div(id='stock-info'),
                        html.Div([
                            dcc.Graph(id='price-chart'),
                            dcc.Graph(id='volume-chart')
                        ])
                    ])
                ], style={'backgroundColor': theme['card']})
            ], fluid=True)
        ], style={'backgroundColor': theme['background']})

    def setup_callbacks(self):
        @self.app.callback(
            Output("download-report", "data"),
            [Input("download-button", "n_clicks")],
            [State("stock-selector", "value")],
            prevent_initial_call=True
        )
        def generate_report(n_clicks, selected_stock):
            if n_clicks is None:
                return None
                
            if self.claude_generator:
                try:
                    pdf_data = self.claude_generator.create_pdf_report(
                        self.df,
                        self.market_overview,
                        selected_stock
                    )
                    if pdf_data:
                        return dcc.send_bytes(
                            pdf_data,
                            f"claude_stock_report_{selected_stock}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                        )
                except Exception as e:
                    print(f"Error generating Claude report: {str(e)}")
            
            # If Claude report fails or is not available, generate basic HTML report
            html_content = self.generate_basic_report_html(selected_stock)
            return dict(
                content=html_content,
                filename=f"stock_report_{selected_stock}.html",
                type="text/html"
            )
        @self.app.callback(
            Output("main-container", "style"),
            Input("theme-selector", "value")
        )
        def update_theme(selected_theme):
            theme = THEMES[selected_theme]
            return {'backgroundColor': theme['background']}

        @self.app.callback(
            [Output('stock-info', 'children'),
             Output('price-chart', 'figure'),
             Output('volume-chart', 'figure')],
            [Input('stock-selector', 'value')]
        )
        def update_stock_display(symbol):
            stock_data = self.df[self.df['Symbol'] == symbol].iloc[0]
            hist_data = stock_data['Historical Data']
            theme = THEMES[self.current_theme]
            
            stock_info = dbc.Row([
                dbc.Col(
                    self.create_metric_card(
                        "Current Price",
                        f"₹{stock_data['Current Price']:.2f}",
                        theme
                    ),
                    width=3
                ),
                dbc.Col(
                    self.create_metric_card(
                        "Daily Change",
                        f"{stock_data['Daily Change %']:.2f}%",
                        theme,
                        'success' if stock_data['Daily Change %'] > 0 else 'danger'
                    ),
                    width=3
                ),
                dbc.Col(
                    self.create_metric_card(
                        "Stock P/E",
                        f"{stock_data['P/E Ratio']:.2f}",
                        theme
                    ),
                    width=3
                ),
                dbc.Col(
                    self.create_metric_card(
                        "Sector P/E",
                        f"{stock_data['Sector P/E']:.2f}",
                        theme
                    ),
                    width=3
                )
            ], className="mb-4")
            
            price_fig = go.Figure()
            price_fig.add_trace(go.Candlestick(
                x=hist_data.index,
                open=hist_data['Open'],
                high=hist_data['High'],
                low=hist_data['Low'],
                close=hist_data['Close'],
                name='Price'
            ))
            
            price_fig.update_layout(
                title='Price Movement',
                yaxis_title='Price (₹)',
                template='plotly_white',
                height=500,
                margin=dict(l=40, r=40, t=40, b=40),
                paper_bgcolor=theme['card'],
                plot_bgcolor=theme['card'],
                font={'color': theme['text']}
            )
            
            volume_fig = go.Figure()
            volume_fig.add_trace(go.Bar(
                x=hist_data.index,
                y=hist_data['Volume'],
                name='Volume',
                marker_color=theme['chart']
            ))
            
            volume_fig.update_layout(
                title='Trading Volume',
                yaxis_title='Volume',
                template='plotly_white',
                height=300,
                margin=dict(l=40, r=40, t=40, b=40),
                paper_bgcolor=theme['card'],
                plot_bgcolor=theme['card'],
                font={'color': theme['text']}
            )
            
            return stock_info, price_fig, volume_fig

    def generate_basic_report_html(self, selected_stock):
        """Generate basic HTML report for the selected stock"""
        stock_data = self.df[self.df['Symbol'] == selected_stock].iloc[0]
        hist_data = stock_data['Historical Data']
        
        # Calculate additional metrics
        recent_high = hist_data['High'].tail(30).max()
        recent_low = hist_data['Low'].tail(30).min()
        avg_volume = hist_data['Volume'].mean()
        volume_trend = (hist_data['Volume'].tail(5).mean() / hist_data['Volume'].tail(30).mean() - 1) * 100
        
        html_content = f"""
        <html>
        <head>
            <style>
                body {{
                    font-family: 'Inter', sans-serif;
                    padding: 2rem;
                    max-width: 1200px;
                    margin: 0 auto;
                    line-height: 1.6;
                }}
                .header {{
                    margin-bottom: 2rem;
                    border-bottom: 2px solid #eee;
                    padding-bottom: 1rem;
                }}
                .section {{
                    margin: 2rem 0;
                    padding: 1rem;
                    background-color: #f8fafc;
                    border-radius: 8px;
                }}
                .metric {{
                    margin: 1rem 0;
                    padding: 0.5rem;
                }}
                .metric strong {{
                    color: #2563eb;
                }}
                .chart {{
                    margin: 2rem 0;
                    padding: 1rem;
                    background-color: white;
                    border-radius: 8px;
                    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
                }}
                .trend-positive {{
                    color: #16a34a;
                }}
                .trend-negative {{
                    color: #dc2626;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>{stock_data['Company Name']} ({stock_data['Symbol']}) Analysis Report</h1>
                <p>Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
            
            <div class="section">
                <h2>Market Overview</h2>
                <div class="metric">
                    <strong>Total Market Cap:</strong> ₹{self.market_overview['Total Market Cap']/1000:.2f}T
                </div>
                <div class="metric">
                    <strong>Market Breadth:</strong> {self.market_overview['Market Breadth']*100:.1f}%
                </div>
                <div class="metric">
                    <strong>Average P/E:</strong> {self.market_overview['Average P/E']:.2f}
                </div>
            </div>
            
            <div class="section">
                <h2>Stock Details</h2>
                <div class="metric">
                    <strong>Current Price:</strong> ₹{stock_data['Current Price']:.2f}
                </div>
                <div class="metric">
                    <strong>Daily Change:</strong> 
                    <span class="{'trend-positive' if stock_data['Daily Change %'] > 0 else 'trend-negative'}">
                        {stock_data['Daily Change %']:.2f}%
                    </span>
                </div>
                <div class="metric">
                    <strong>P/E Ratio:</strong> {stock_data['P/E Ratio']:.2f}
                </div>
                <div class="metric">
                    <strong>Sector P/E:</strong> {stock_data['Sector P/E']:.2f}
                </div>
            </div>
            
            <div class="section">
                <h2>Technical Indicators</h2>
                <div class="metric">
                    <strong>30-Day High:</strong> ₹{recent_high:.2f}
                </div>
                <div class="metric">
                    <strong>30-Day Low:</strong> ₹{recent_low:.2f}
                </div>
                <div class="metric">
                    <strong>Average Volume:</strong> {avg_volume:,.0f}
                </div>
                <div class="metric">
                    <strong>Volume Trend:</strong>
                    <span class="{'trend-positive' if volume_trend > 0 else 'trend-negative'}">
                        {volume_trend:+.1f}%
                    </span>
                </div>
            </div>
        </body>
        </html>
        """
        return html_content

    def run_server(self, debug=False, port=8050):
        self.app.run_server(debug=debug, port=port)