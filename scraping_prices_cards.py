import requests
from bs4 import BeautifulSoup
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime
from selenium.webdriver import ActionChains
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException
from webdriver_manager.chrome import ChromeDriverManager
import time

def setup_driver():
    """
    Configure and initialize a headless Chrome WebDriver for web scraping.
    
    Returns:
        webdriver.Chrome: Configured Chrome WebDriver instance
        
    Features:
        - Headless mode for background operation
        - Standard window size (1920x1080)
        - Automated chromedriver installation
    """
    service = Service(ChromeDriverManager().install())
    
    # Configure Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode
    chrome_options.add_argument("--window-size=1920,1080")  # Set standard screen size
    
    # Additional recommended options for stability
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-extensions")
    
    # Initialize and return the WebDriver
    return webdriver.Chrome(service=service, options=chrome_options)


def test_button_click(driver, wait, selector, by=By.CSS_SELECTOR):
    """
    Attempts to click on a web element using JavaScript after ensuring it's present and centered.
    
    Args:
        driver: Selenium WebDriver instance
        wait: WebDriverWait instance for explicit waits
        selector: String selector to locate the element
        by: Selenium By method to locate element (default: CSS_SELECTOR)
    
    Returns:
        bool: True if click successful, False otherwise
    
    Features:
        - Explicit wait for element presence
        - Centered scrolling for better visibility
        - JavaScript click for reliability
        - Error handling with detailed feedback
    """
    try:
        # Wait for element to be present in DOM
        element = wait.until(EC.presence_of_element_located((by, selector)))
        
        # Center element in viewport using smooth scrolling
        driver.execute_script("""
            arguments[0].scrollIntoView({
                behavior: 'instant',
                block: 'center',
                inline: 'center'
            });
        """, element)
        
        # Ensure element is clickable
        wait.until(EC.element_to_be_clickable((by, selector)))
        
        # Use JavaScript click for better reliability
        driver.execute_script("arguments[0].click();", element)
        return True
        
    except Exception as e:
        print(f"Click failed for {selector}: {str(e)}")
        return False

def get_chart_data(driver, wait):
    """
    Extracts HTML content of the price history chart from the Pokemon card webpage.
    
    Args:
        driver: Selenium WebDriver instance
        wait: WebDriverWait instance for explicit waits
    
    Returns:
        str or None: HTML content of the chart if found, None if timeout occurs
        
    Features:
        - Explicit wait for chart element
        - Robust selector targeting
        - HTML extraction with outerHTML
    """
    try:
        # Wait for chart element to be present in DOM
        chart_selector = "div.martech-charts-history[data-testid='History']"
        chart = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, chart_selector))
        )
        
        # Allow time for dynamic content to fully load
        wait.until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "table"))
        )
        
        # Extract complete HTML content
        return chart.get_attribute('outerHTML')
        
    except TimeoutException:
        print("Failed to locate chart element after specified timeout")
        return None

def extract_html_code_1Y_NM(website):
    """
    Extracts 1-year price history data for Near Mint Pokemon cards from a website using Selenium.
    
    This function:
    1. Sets up a Chrome WebDriver
    2. Navigates to the specified website
    3. Clicks through a sequence of buttons to access Near Mint card data
    4. Extracts the HTML content containing price history
    
    Args:
        website (str): URL of the Pokemon card price history page
        
    Returns:
        str or None: HTML content containing price data if successful, None if any step fails
        
    Note:
        Requires setup_driver() and test_button_click() helper functions to be defined
        Uses explicit waits to handle dynamic content loading
    """
    driver = setup_driver()
    wait = WebDriverWait(driver, 25)  # 25 second timeout for slow connections
    
    try:
        # Load the webpage
        driver.get(website)
        print("Page loaded successfully")
        
        # Wait for page to be fully loaded
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        
        # Define click sequence for data filtering
        click_sequence = [
            ('CSS_SELECTOR', 'button[data-v-0177b97d][class*="charts-item"]:last-child'),   # 1Y timeframe button
            ('CSS_SELECTOR', 'div.modal__activator[role="button"]'),        # View More Data button
            ('CSS_SELECTOR', 'button.sales-history-snapshot__show-filters'), # Sales Filter button
            ('XPATH', '//label[span[text()="Near Mint"]]')             # Near Mint condition filter
        ]
        
        # Execute click sequence
        for selector_type, selector in click_sequence:
            by_type = By.CSS_SELECTOR if selector_type == 'CSS_SELECTOR' else By.XPATH
            if not test_button_click(driver, wait, selector, by=by_type):
                print(f"Click failed for selector: {selector}")
                return None
                
        # Extract chart data
        html_content = get_chart_data(driver, wait)
        if html_content:
            print("HTML content successfully retrieved")
            return html_content
            
        print("Failed to retrieve HTML content")
        return None

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return None
        
    finally:
        driver.quit()
        print("Browser session terminated")

def extract_price_history(website):
    """
    Extracts and processes price history data from a Pokemon card website.
    
    Args:
        website (str): URL of the Pokemon card price history page
        
    Returns:
        pandas.DataFrame: Sorted DataFrame with price and quantity data indexed by date ranges
    """
    # Get HTML content from the website
    html_content = extract_html_code_1Y_NM(website)
    soup = BeautifulSoup(html_content, "html.parser")
    price_history = {}
    
    def convert_date(date_str):
        """
        Converts date strings to datetime objects with correct year assignment.
        
        Args:
            date_str (str): Date range string in format "MM/DD to MM/DD"
            
        Returns:
            tuple: (start_date, end_date) as datetime objects
        """
        try:
            start_date, end_date = date_str.split(" to ")
            start_month, start_day = map(int, start_date.split("/"))
            end_month, end_day = map(int, end_date.split("/"))
            
            # Year determination logic
            current_year = 2024
            previous_year = current_year - 1
            
            # Assign previous year if month is December
            start_year = previous_year if start_month == 12 else current_year
            # Assign current year if end month is January
            end_year = current_year if end_month == 1 else start_year
            
            return datetime(start_year, start_month, start_day), datetime(end_year, end_month, end_day)
            
        except Exception as e:
            print(f"Date conversion error: {date_str} - {str(e)}")
            return None, None

    # Process table rows from HTML
    rows = soup.find_all("tr")
    
    # Skip header row and process data rows
    for row in rows[1:]:
        cells = row.find_all("td")
        if len(cells) >= 3:
            try:
                # Extract and clean data from cells
                date = cells[0].get_text(strip=True)
                price = float(cells[1].get_text(strip=True).replace('$', ''))
                quantity = float(cells[2].get_text(strip=True).replace('$', ''))
                
                # Convert dates and store data
                start_date_obj, end_date_obj = convert_date(date)
                if start_date_obj and end_date_obj:
                    price_history[(start_date_obj, end_date_obj)] = {
                        'price': price,
                        'quantity_sold': int(quantity)
                    }
            except (ValueError, AttributeError) as e:
                continue

    # Create DataFrame with MultiIndex and sort by date
    df = pd.DataFrame.from_dict(price_history, orient='index')
    df.index = pd.MultiIndex.from_tuples(df.index, names=['start_date', 'end_date'])
    return df.sort_index()