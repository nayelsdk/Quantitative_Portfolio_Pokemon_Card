import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import os
from tqdm import tqdm


from bs4 import BeautifulSoup
from datetime import datetime
import glob
from selenium import webdriver 
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager



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
    Attempts to click on a web element using JavaScript with enhanced reliability.
    
    Args:
        driver (selenium.webdriver.Chrome): Chrome WebDriver instance
        wait (selenium.webdriver.support.ui.WebDriverWait): WebDriverWait instance
        selector (str): Element selector (e.g., "button.submit")
        by (selenium.webdriver.common.by.By, optional): Selector strategy. 
            Defaults to CSS_SELECTOR.
    
    Returns:
        bool: True if click succeeds, False otherwise
    
    Notes:
        - Waits for element presence and clickability
        - Centers element in viewport before clicking
        - Uses JavaScript click for reliability
        - Provides detailed error feedback
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
    Extracts price history chart data and card state from webpage.
    
    Args:
        driver (selenium.webdriver.Chrome): Chrome WebDriver instance
        wait (selenium.webdriver.support.ui.WebDriverWait): WebDriverWait instance
    
    Returns:
        tuple: (html_content, card_state) containing:
            - html_content (str): Page HTML with price history data
            - card_state (str): Card state from chart title (e.g. "Holofoil")
            Returns (None, None) if extraction fails
    
    Raises:
        TimeoutException: When chart fails to load
        NoSuchElementException: When title element not found
        WebDriverException: For other WebDriver errors
    
    Notes:
        - Waits for chart element with "martech-charts-history" class
        - Gets state from "charts-title" class element
        - Returns "Unknown" if title missing
        - Captures full HTML for price extraction
    """
    try:
        # Attendre que le graphique soit chargé
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "martech-charts-history")))
        
        # Extraire l'état de la carte depuis le titre du graphique
        card_state_element = driver.find_element(By.CLASS_NAME, "charts-title")
        card_state = card_state_element.text if card_state_element else "Unknown"
        
        # Obtenir le contenu HTML
        html_content = driver.page_source
        
        return html_content, card_state
        
    except Exception as e:
        print(f"Error extracting chart data: {str(e)}")
        return None, None


def get_near_mint_prices(driver, wait):
    """
    Extracts prices and states from the Near Mint Comparison Prices table.
    
    This function scrapes the Near Mint price table to find available card states 
    (Normal, Holofoil, Reverse Holofoil) and their corresponding prices. It then 
    determines the highest priced variant.
    
    Args:
        driver (selenium.webdriver.Chrome): Instance of Chrome WebDriver
        wait (selenium.webdriver.support.ui.WebDriverWait): WebDriverWait instance for handling timeouts
    
    Returns:
        tuple: (selected_state, highest_price) where:
            - selected_state (str): Card state with highest price (e.g., "Holofoil", "Reverse Holofoil", "Normal")
            - highest_price (float): The corresponding price value
            Returns (None, None) if no valid prices are found
    
    Example:
        >>> state, price = get_near_mint_prices(driver, wait)
        >>> print(f"Selected {state} with price ${price}")
        Selected Holofoil with price $357.42
    
    Notes:
        - Ignores "N/A" prices
        - Compares all available variants to find highest price
        - Uses specific HTML classes from the price table structure
        - Handles both single and multiple variant cases
    """
    wait.until(EC.presence_of_element_located((By.CLASS_NAME, "near-mint-table")))
    
    states_prices = {}
    cells = driver.find_elements(By.CSS_SELECTOR, "td[data-v-762a0eeb]")
    
    i = 0
    while i < len(cells):
        try:
            state = cells[i].find_element(By.CLASS_NAME, "text").text.strip().replace(':', '')
            price_element = cells[i+1].find_element(By.CLASS_NAME, "near-mint-table__price")
            price_text = price_element.text.replace('$', '')
            
            if price_text != 'N/A':
                states_prices[state] = float(price_text)
            i += 2
                
        except Exception as e:
            print(f"Erreur d'extraction : {e}")
            i += 1
    
    if states_prices:
        selected_state = max(states_prices.items(), key=lambda x: x[1])[0]
        return selected_state, states_prices[selected_state]
        
    return None, None

def get_html_content(website):
    """
    Extracts price history data for a Pokemon card by selecting and filtering the highest priced variant.
    
    Args:
        website (str): URL of the Pokemon card price page
    
    Returns:
        tuple: (html_content, selected_state) containing:
            - html_content (str): Page HTML after filtering
            - selected_state (str): Selected card state (e.g. "Holofoil")
            Returns (None, None) if any step fails
    
    Notes:
        - Extracts prices from Near Mint table
        - Selects variant with highest price
        - Clicks sequence: 1Y > Filters > Near Mint > Selected State
        - Handles multiple card states (Normal/Holofoil/Reverse)
        - Returns full HTML for price history extraction
    """
    driver = setup_driver()
    wait = WebDriverWait(driver, 60)
    
    try:
        driver.get(website)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        
        selected_state, highest_price = get_near_mint_prices(driver, wait)
        if not selected_state:
            return None, None
            
        initial_clicks = [
            ('CSS_SELECTOR', 'button[data-v-0177b97d][class="charts-item"]:last-child'),
            ('CSS_SELECTOR', 'div.modal__activator[role="button"]'),
            ('CSS_SELECTOR', 'button.sales-history-snapshot__show-filters'),
            ('XPATH', '//label[span[text()="Near Mint"]]')
        ]
        
        for selector_type, selector in initial_clicks:
            by_type = By.CSS_SELECTOR if selector_type == 'CSS_SELECTOR' else By.XPATH
            if not test_button_click(driver, wait, selector, by=by_type):
                print(f"Click failed for selector: {selector}")
                return None, None
        
        state_selector = f'//span[@class="checkbox__option-value checkbox__option-value-mobile" and text()="{selected_state}"]'
        if not test_button_click(driver, wait, state_selector, By.XPATH):
            print(f"Click failed for state: {selected_state}")
            return None, None
            
        html_content = driver.page_source
        return html_content, selected_state
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return None, None
    
    finally:
        driver.quit()


def extract_price_history(html_content, card_state):
    """
    Extracts and processes price history data from Pokemon card sales table.
    
    Args:
        html_content (str): Raw HTML containing price history table
        card_state (str): Card state (e.g. "Holofoil", "Reverse Holofoil")
    
    Returns:
        pandas.DataFrame: Price history with columns:
            - MultiIndex: (start_date, end_date) as datetime objects
            - price: Card price for the period
            - quantity_sold: Number of cards sold
    
    Notes:
        - Removes "Near Mint" prefix from card state
        - Handles date ranges across year boundaries
        - Converts prices and quantities to numeric values
        - Returns sorted DataFrame by date range
    """
    soup = BeautifulSoup(html_content, "html.parser")
    price_history = {}
    card_state = card_state.replace("Near Mint ", "")

    
    def convert_date(date_str):
        try:
            start_date, end_date = date_str.split(" to ")
            start_month, start_day = map(int, start_date.split("/"))
            end_month, end_day = map(int, end_date.split("/"))
            
            current_year = 2024
            previous_year = current_year - 1
            
            start_year = previous_year if start_month == 12 else current_year
            end_year = current_year if end_month == 1 else start_year
            
            return datetime(start_year, start_month, start_day), datetime(end_year, end_month, end_day)
            
        except Exception as e:
            print(f"Date conversion error: {date_str} - {str(e)}")
            return None, None

    rows = soup.find_all("tr")
    
    for row in rows[1:]:
        cells = row.find_all("td")
        if len(cells) >= 3:
            try:
                date = cells[0].get_text(strip=True)
                price = float(cells[1].get_text(strip=True).replace('$', ''))
                quantity = float(cells[2].get_text(strip=True).replace('$', ''))
                
                start_date_obj, end_date_obj = convert_date(date)
                if start_date_obj and end_date_obj:
                    price_history[(start_date_obj, end_date_obj)] = {
                        'price': price,
                        'quantity_sold': int(quantity)
                    }
            except (ValueError, AttributeError) as e:
                continue

    df = pd.DataFrame.from_dict(price_history, orient='index')
    df.index = pd.MultiIndex.from_tuples(df.index, names=['start_date', 'end_date'])
        
    return df.sort_index()



def save_historic_prices(cards_df, output_dir='price_history'):
    """
    Extracts and saves price history data for multiple Pokemon cards with progress tracking.
    
    Args:
        cards_df (pandas.DataFrame): DataFrame containing card information with 'id' column
        output_dir (str, optional): Base directory for saving price history files.
            Defaults to 'price_history'
    
    Notes:
        - Creates subdirectories for different sales volumes:
            - low_sales: < 5 sales
            - medium_sales: 5-20 sales
            - high_sales: > 20 sales
        - Skips existing files to avoid duplicate processing
        - Shows progress with tqdm bar including current card status
        - Saves price history as CSV with format: {card_id}_{state}.csv
        - Handles errors gracefully with status updates
    """
    subdirs = {
        'low_sales': os.path.join(output_dir, 'low_sales'),
        'medium_sales': os.path.join(output_dir, 'medium_sales'),
        'high_sales': os.path.join(output_dir, 'high_sales')
    }
    
    failed_ids = load_failed_ids()
    
    for subdir in subdirs.values():
        os.makedirs(subdir, exist_ok=True)
    
    with tqdm(total=len(cards_df), desc="Price Extraction", position=0, leave=True) as pbar:
        for index, card_row in cards_df.iterrows():
            card_id = card_row['id']
            
            if card_id in failed_ids:
                pbar.update(1)
                continue
                
            pbar.set_postfix_str(f"Processing {card_id}", refresh=True)
            
            file_exists = False
            for subdir in subdirs.values():
                if glob.glob(os.path.join(subdir, f'{card_id}_*.csv')):
                    pbar.set_postfix_str(f"Skipped {card_id} (exists)", refresh=True)
                    file_exists = True
                    break
                    
            if file_exists:
                pbar.update(1)
                continue
                
            try:
                html_content, card_state = get_html_content(
                    f"https://prices.pokemontcg.io/tcgplayer/{card_id}")
                
                if html_content and card_state:
                    price_history = extract_price_history(html_content, card_state)
                    
                    if price_history is not None:
                        total_sales = price_history['quantity_sold'].sum()
                        
                        if total_sales < 5:
                            subdir = subdirs['low_sales']
                        elif total_sales <= 20:
                            subdir = subdirs['medium_sales']
                        else:
                            subdir = subdirs['high_sales']
                        
                        sanitized_state = card_state.replace(" ", "_")
                        file_path = os.path.join(subdir, f'{card_id}_{sanitized_state}.csv')
                        
                        price_df = price_history.reset_index()
                        price_df.columns = ['start_date', 'end_date', 'price', 'quantity_sold']
                        price_df.to_csv(file_path, index=False)
                        
                        pbar.set_postfix_str(f"Saved {card_id}", refresh=True)
                    else:
                        pbar.set_postfix_str(f"No data for {card_id}", refresh=True)
                
            except Exception as e:
                pbar.set_postfix_str(f"Failed {card_id}: {str(e)}", refresh=True)
                save_failed_id(card_id)
                failed_ids.add(card_id)
            
            pbar.update(1)
            time.sleep(1)


def load_failed_ids(file_path='failed_ids.txt'):
    """Load the IDs that failed from a txt file"""
    try:
        with open(file_path, 'r') as f:
            return set(line.strip() for line in f)
    except FileNotFoundError:
        return set()

def save_failed_id(card_id, file_path='failed_ids.txt'):
    """Add a new ID that that faild to the txt file"""
    with open(file_path, 'a') as f:
        f.write(f"{card_id}\n")