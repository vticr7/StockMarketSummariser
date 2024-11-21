from dash import Dash, html, dcc, Input, Output, State
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import pdfkit
import io
import base64

# Color themes
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
    def __init__(self, df, market_overview):
        self.df = df
        self.market_overview = market_overview
        self.current_theme = 'default'
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

    def generate_report_html(self, selected_stock):
        """Generate HTML report for the selected stock"""
        stock_data = self.df[self.df['Symbol'] == selected_stock].iloc[0]
        
        html_content = f"""
        <html>
        <head>
            <style>
                body {{ font-family: 'Inter', sans-serif; padding: 2rem; }}
                .header {{ margin-bottom: 2rem; }}
                .metric {{ margin: 1rem 0; }}
                .chart {{ margin: 2rem 0; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Stock Analysis Report</h1>
                <p>Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
            
            <div class="market-overview">
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
            
            <div class="stock-details">
                <h2>Stock Details: {stock_data['Company Name']} ({stock_data['Symbol']})</h2>
                <div class="metric">
                    <strong>Current Price:</strong> ₹{stock_data['Current Price']:.2f}
                </div>
                <div class="metric">
                    <strong>Daily Change:</strong> {stock_data['Daily Change %']:.2f}%
                </div>
                <div class="metric">
                    <strong>P/E Ratio:</strong> {stock_data['P/E Ratio']:.2f}
                </div>
                <div class="metric">
                    <strong>Sector P/E:</strong> {stock_data['Sector P/E']:.2f}
                </div>
            </div>
        </body>
        </html>
        """
        return html_content

    def setup_layout(self):
        theme = THEMES[self.current_theme]
        
        self.app.layout = html.Div(id='main-container', children=[
            dbc.Container([
                # Theme Selector and Download Button
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
                
                # Market Overview Cards
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
                
                # Stock Selector
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

    def create_metric_card(self, title, value, theme, status='primary'):
        return dbc.Card([
            dbc.CardBody([
                html.H6(title, style={'color': theme['muted']}),
                html.H4(value, style={'color': theme[status]})
            ])
        ], style={'backgroundColor': theme['card']})

    def setup_callbacks(self):
        @self.app.callback(
            Output("download-report", "data"),
            Input("download-button", "n_clicks"),
            State("stock-selector", "value"),
            prevent_initial_call=True
        )
        def generate_report(n_clicks, selected_stock):
            if n_clicks is None:
                return None
                
            html_content = self.generate_report_html(selected_stock)
            
            try:
                pdf = pdfkit.from_string(html_content, False)
                return dcc.send_bytes(pdf, f"stock_report_{selected_stock}.pdf")
            except Exception as e:
                print(f"Error generating PDF: {str(e)}")
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

    def run_server(self, debug=False, port=8050):
        self.app.run_server(debug=debug, port=port)