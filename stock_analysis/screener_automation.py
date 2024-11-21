from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time
import json
from datetime import datetime
import os

class ScreenerAutomation:
    def __init__(self, headless=True):
        self.setup_driver(headless)
        self.base_url = "https://www.screener.in"
        self.data_dir = "data/screener_data"
        os.makedirs(self.data_dir, exist_ok=True)

    def setup_driver(self, headless):
        """Setup Chrome driver with options."""
        chrome_options = Options()
        if headless:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1920,1080")
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.wait = WebDriverWait(self.driver, 10)

    def login(self, username, password):
        """Login to Screener.in"""
        try:
            self.driver.get(f"{self.base_url}/login/")
            
            # Wait for login form and input fields
            username_field = self.wait.until(
                EC.presence_of_element_located((By.NAME, "username"))
            )
            password_field = self.driver.find_element(By.NAME, "password")
            
            # Enter credentials
            username_field.send_keys(username)
            password_field.send_keys(password)
            
            # Submit form
            password_field.submit()
            
            # Wait for login to complete
            self.wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, "dropdown-toggle"))
            )
            
            return True
        except Exception as e:
            print(f"Login failed: {str(e)}")
            return False

    def get_company_data(self, symbol):
        """Get comprehensive company data from Screener.in"""
        try:
            url = f"{self.base_url}/company/{symbol}/consolidated/"
            self.driver.get(url)
            time.sleep(2)  # Allow page to load completely
            
            company_data = {
                'symbol': symbol,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'general_info': self._get_general_info(),
                'quarterly_results': self._get_quarterly_results(),
                'profit_loss': self._get_profit_loss(),
                'balance_sheet': self._get_balance_sheet(),
                'cash_flow': self._get_cash_flow(),
                'ratios': self._get_ratios(),
                'shareholding': self._get_shareholding(),
                'concalls': self._get_concalls()
            }
            
            # Save data to file
            self._save_company_data(symbol, company_data)
            
            return company_data
        
        except Exception as e:
            print(f"Error fetching data for {symbol}: {str(e)}")
            return None

    def _get_general_info(self):
        """Extract general company information."""
        try:
            info = {}
            
            # Get company name and market price
            company_header = self.wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, "company-name"))
            )
            info['company_name'] = company_header.text.strip()
            
            # Get market price and other metrics
            metrics = self.driver.find_elements(By.CLASS_NAME, "flex-row")
            for metric in metrics:
                try:
                    label = metric.find_element(By.CLASS_NAME, "name").text.strip()
                    value = metric.find_element(By.CLASS_NAME, "number").text.strip()
                    info[label.lower().replace(" ", "_")] = value
                except:
                    continue
            
            return info
        except Exception as e:
            print(f"Error getting general info: {str(e)}")
            return {}

    def _get_quarterly_results(self):
        """Extract quarterly results."""
        try:
            quarters_table = self.driver.find_element(By.ID, "quarters")
            df = pd.read_html(quarters_table.get_attribute('outerHTML'))[0]
            return df.to_dict('records')
        except:
            return []

    def _get_concalls(self):
        """Extract earnings call transcripts."""
        try:
            concalls = []
            concall_sections = self.driver.find_elements(By.CLASS_NAME, "concall")
            
            for section in concall_sections:
                try:
                    date = section.find_element(By.CLASS_NAME, "date").text.strip()
                    points = [point.text.strip() 
                            for point in section.find_elements(By.TAG_NAME, "li")]
                    
                    concalls.append({
                        'date': date,
                        'points': points
                    })
                except:
                    continue
            
            return concalls
        except:
            return []

    def _get_profit_loss(self):
        """Extract profit and loss statements."""
        try:
            pl_section = self.driver.find_element(By.ID, "profit-loss")
            df = pd.read_html(pl_section.get_attribute('outerHTML'))[0]
            return df.to_dict('records')
        except:
            return []

    def _get_balance_sheet(self):
        """Extract balance sheet data."""
        try:
            balance_section = self.driver.find_element(By.ID, "balance-sheet")
            df = pd.read_html(balance_section.get_attribute('outerHTML'))[0]
            return df.to_dict('records')
        except:
            return []

    def _get_cash_flow(self):
        """Extract cash flow statements."""
        try:
            cash_flow_section = self.driver.find_element(By.ID, "cash-flow")
            df = pd.read_html(cash_flow_section.get_attribute('outerHTML'))[0]
            return df.to_dict('records')
        except:
            return []

    def _get_ratios(self):
        """Extract financial ratios."""
        try:
            ratios_section = self.driver.find_element(By.ID, "ratios")
            df = pd.read_html(ratios_section.get_attribute('outerHTML'))[0]
            return df.to_dict('records')
        except:
            return []

    def _get_shareholding(self):
        """Extract shareholding patterns."""
        try:
            shareholding_section = self.driver.find_element(By.ID, "shareholding")
            df = pd.read_html(shareholding_section.get_attribute('outerHTML'))[0]
            return df.to_dict('records')
        except:
            return []

    def _save_company_data(self, symbol, data):
        """Save company data to JSON file."""
        filename = os.path.join(self.data_dir, f"{symbol}_data.json")
        with open(filename, 'w') as f:
            json.dump(data, f, indent=4)

    def batch_process_companies(self, symbols):
        """Process multiple companies."""
        results = {}
        for symbol in symbols:
            print(f"Processing {symbol}...")
            results[symbol] = self.get_company_data(symbol)
            time.sleep(2)  # Prevent rate limiting
        return results

    def close(self):
        """Close the browser."""
        if self.driver:
            self.driver.quit()