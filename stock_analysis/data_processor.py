import pandas as pd
import json
import os

class DataProcessor:
    def __init__(self, data_dir="data/screener_data"):
        self.data_dir = data_dir

    def load_company_data(self, symbol):
        """Load company data from JSON file."""
        try:
            filename = os.path.join(self.data_dir, f"{symbol}_data.json")
            with open(filename, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading data for {symbol}: {str(e)}")
            return None

    def get_latest_concall_highlights(self, symbol):
        """Get the latest earnings call highlights."""
        data = self.load_company_data(symbol)
        if not data or 'concalls' not in data or not data['concalls']:
            return None
        
        return data['concalls'][0]  # Return most recent concall

    def get_quarterly_trends(self, symbol):
        """Get quarterly performance trends."""
        data = self.load_company_data(symbol)
        if not data or 'quarterly_results' not in data:
            return None
        
        df = pd.DataFrame(data['quarterly_results'])
        return df

    def get_financial_summary(self, symbol):
        """Get key financial metrics summary."""
        data = self.load_company_data(symbol)
        if not data:
            return None
        
        return {
            'general_info': data.get('general_info', {}),
            'latest_quarter': data.get('quarterly_results', [{}])[0],
            'key_ratios': data.get('ratios', [{}])[0]
        }