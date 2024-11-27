# Indian Stock Market Analysis System

A comprehensive stock analysis tool that processes data from over 2000 Indian stocks, providing technical analysis and interactive visualizations through a modern dashboard interface.

## ⚠️ Important Note
**Initial data fetching takes approximately 2 hours** due to:
- Processing 2000+ stocks from EQUITY_L.csv
- API rate limiting
- Historical data collection
- Technical indicator calculations

## Features
- Comprehensive data fetching from multiple sources
- Technical analysis with multiple indicators
- Interactive visualization dashboard
- Dynamic stock screening
- PDF report generation
- Sector-wise analysis

## Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager
- Internet connection

### Setup
1. Clone the repository
```bash
git clone https://github.com/vticr7/StockMarketSummariser.git
cd StockMarketSummariser
```

2. Create and activate virtual environment
```bash
python -m venv env
source env/bin/activate  # For Unix/macOS
env\Scripts\activate     # For Windows
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Place EQUITY_L.csv in the data directory
```bash
mkdir -p data
# Copy your EQUITY_L.csv to the data directory
```

## Usage

### Initial Setup
```bash
python main.py
```
Note: First run will take ~2 hours to fetch all stock data

### Accessing the Dashboard
1. After data fetching completes, access the dashboard at:
```
http://localhost:8050
```

2. Available Features:
- Interactive stock selection
- Technical charts and indicators
- Volume analysis
- Market breadth indicators
- Sector performance
- Export functionality

## Project Structure
```
project/
├── stock_analysis/
│   ├── __init__.py
│   ├── data_fetcher.py
│   ├── data_analyzer.py
│   └── data_visualizer.py
├── data/
│   └── EQUITY_L.csv
├── requirements.txt
├── README.md
└── main.py
```

## Dependencies
```
dash==2.6.0
pandas==1.4.0
yfinance==0.1.70
plotly==5.5.0
numpy==1.21.0
fpdf==2.5.0
```

## Data Sources
- EQUITY_L.csv from NSE
- Yahoo Finance API
- Market data through yfinance

## Technical Features
1. Stock Analysis
   - Moving averages (20, 50, 200 days)
   - RSI and MACD indicators
   - Volume analysis
   - Price momentum

2. Market Analysis
   - Sector-wise performance
   - Market breadth indicators
   - Top gainers and losers
   - Volume trends

3. Visualization
   - Candlestick charts
   - Technical overlays
   - Volume charts
   - Sector distribution

## Common Issues
1. Data Fetching Time
   - Initial fetch takes ~2 hours
   - Subsequent runs use cached data
   - Progress bar shows status

2. API Rate Limits
   - Built-in delays prevent blocking
   - Automatic retries on failure
   - Error handling for API issues

## Performance Requirements
- CPU: Process heavy during initial fetch
- RAM: ~4GB required for full dataset
- Storage: ~500MB for cached data
- Network: Stable connection needed

## Contributing
1. Fork the repository
2. Create feature branch
3. Commit changes
4. Push to branch
5. Create Pull Request

## License
MIT License

## Author
Vaibhav Tiwary

## Acknowledgments
- NSE India for stock data
- Yahoo Finance for API access
- Open source community

## Contact
- Email: vti9227@gmail.com
- GitHub: vticr7
