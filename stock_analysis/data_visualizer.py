from dash import Dash, html, dcc, Input, Output, State
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from datetime import datetime
import pandas as pd
import google.generativeai as genai
from fpdf import FPDF
import tempfile
import os

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
    def __init__(self, df, market_overview, gemini_api_key=None):
        self.df = df
        self.market_overview = market_overview
        self.current_theme = 'default'
        self.gemini_api_key = gemini_api_key
        
        if gemini_api_key:
            genai.configure(api_key=gemini_api_key)
        
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

    def generate_gemini_report(self, stock_data, market_overview, selected_stock):
        """Generate a PDF report using Gemini API"""
        try:
            # Initialize Gemini model
            model = genai.GenerativeModel('gemini-pro')
            
            # Prepare the prompt
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
            
            Please provide specific insights about:
            1. Price trends and momentum
            2. Valuation compared to sector peers
            3. Key risks and opportunities
            4. Market sentiment and positioning
            
            Format the response in clear sections with headers.
            """
            
            # Get Gemini's analysis
            response = model.generate_content(prompt)
            analysis = response.text
            
            # Generate PDF
            pdf = FPDF()
            pdf.add_page()
            
            # Use Arial font (built-in)
            pdf.set_font('Arial', '', 12)
            
            # Title
            pdf.set_font('Arial', 'B', 24)
            pdf.cell(0, 10, f"{stock_data['Company Name']} ({stock_data['Symbol']})", ln=True, align='C')
            pdf.ln(10)
            
            # Date
            pdf.set_font('Arial', '', 10)
            pdf.cell(0, 10, f"AI-Enhanced Analysis Report (Gemini)", ln=True)
            pdf.cell(0, 10, f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True)
            pdf.ln(10)
            
            # Key Metrics
            pdf.set_font('Arial', 'B', 14)
            pdf.cell(0, 10, "Key Metrics", ln=True)
            pdf.ln(5)
            
            pdf.set_font('Arial', '', 12)
            metrics = [
                f"Current Price: Rs.{stock_data['Current Price']:.2f}",
                f"Daily Change: {stock_data['Daily Change %']:.2f}%",
                f"P/E Ratio: {stock_data['P/E Ratio']:.2f}",
                f"Market Cap: Rs.{stock_data['Market Cap (Cr)']:.2f} Cr",
                f"52W High: Rs.{stock_data['52W High']:.2f}",
                f"52W Low: Rs.{stock_data['52W Low']:.2f}"
            ]
            
            for metric in metrics:
                pdf.cell(0, 8, metric, ln=True)
            pdf.ln(10)
            
            # Market Context
            pdf.set_font('Arial', 'B', 14)
            pdf.cell(0, 10, "Market Context", ln=True)
            pdf.ln(5)
            
            pdf.set_font('Arial', '', 12)
            market_metrics = [
                f"Total Market Cap: Rs.{self.market_overview['Total Market Cap']/1000:.2f}T",
                f"Market Breadth: {self.market_overview['Market Breadth']*100:.1f}%",
                f"Average Market P/E: {self.market_overview['Average P/E']:.2f}"
            ]
            
            for metric in market_metrics:
                pdf.cell(0, 8, metric, ln=True)
            pdf.ln(10)
            
            # Gemini Analysis
            pdf.set_font('Arial', 'B', 14)
            pdf.cell(0, 10, "AI-Generated Analysis", ln=True)
            pdf.ln(5)
            
            pdf.set_font('Arial', '', 12)
            paragraphs = analysis.split('\n\n')
            for para in paragraphs:
                # Handle any special characters
                clean_para = para.strip().encode('latin-1', 'replace').decode('latin-1')
                pdf.multi_cell(0, 6, clean_para)
                pdf.ln(5)
            
            # Create temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
                pdf.output(tmp.name)
                with open(tmp.name, 'rb') as f:
                    pdf_data = f.read()
                os.unlink(tmp.name)
                return pdf_data
                
        except Exception as e:
            print(f"Error generating Gemini report: {str(e)}")
            return None

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
                    font-family: Arial, sans-serif;
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
        return dict(
            content=html_content,
            filename=f"stock_report_{selected_stock}.html",
            type="text/html"
        )

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
            
            stock_data = self.df[self.df['Symbol'] == selected_stock].iloc[0]
            
            # Try Gemini report only if API key is available
            if self.gemini_api_key:
                try:
                    pdf_data = self.generate_gemini_report(stock_data, self.market_overview, selected_stock)
                    if pdf_data:
                        return dcc.send_bytes(
                            pdf_data,
                            f"gemini_stock_report_{selected_stock}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                        )
                except Exception as e:
                    print(f"Error with Gemini report generation: {str(e)}")
                    print("Falling back to basic report...")
            
            # Generate basic HTML report as fallback
            return self.generate_basic_report_html(selected_stock)

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

    def run_server(self, debug=False, port=8050):
        self.app.run_server(debug=debug, port=port)