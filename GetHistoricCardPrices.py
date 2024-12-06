import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import os
from tqdm import tqdm


from bs4 import BeautifulSoup
from datetime import datetime

from selenium import webdriver 
from selenium.webdriver.common.action_chains import ActionChains
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
    Attempts to click on a web element using JavaScript after ensuring it's present and centered.
    """
    try:
        # Wait for element to be present in DOM with longer timeout
        wait = WebDriverWait(driver, 20)
        element = wait.until(EC.presence_of_element_located((by, selector)))
        
        # Center element in viewport
        driver.execute_script("""
            arguments[0].scrollIntoView({
                behavior: 'instant',
                block: 'center',
                inline: 'center'
            });
        """, element)
        
        # Pause court pour laisser le temps au scroll de se terminer
        time.sleep(0.5)
        
        # Essayer plusieurs méthodes de clic
        try:
            # Méthode 1: Clic JavaScript direct
            driver.execute_script("arguments[0].click();", element)
        except:
            try:
                # Méthode 2: Actions chains
                actions = ActionChains(driver)
                actions.move_to_element(element).click().perform()
            except:
                # Méthode 3: Clic Selenium standard
                element.click()
                
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

def get_html_content(website, holofoil_price, reverse_holofoil_price):
    """
    Extracts price history data for Pokemon cards from TCGPlayer, handling both Holofoil and Reverse Holofoil variants.
    
    The function navigates through the TCGPlayer website interface to extract historical price data for a specific Pokemon card.
    It automatically selects between Holofoil and Reverse Holofoil based on provided prices, handling NaN values appropriately.
    
    Args:
        website (str): TCGPlayer URL for the specific Pokemon card
                      Format: "https://prices.pokemontcg.io/tcgplayer/{card_id}"
        holofoil_price (float): Current market price for Holofoil variant
                               Can be NaN if variant doesn't exist
        reverse_holofoil_price (float): Current market price for Reverse Holofoil variant
                                       Can be NaN if variant doesn't exist
    
    Returns:
        str or None: HTML content containing price history data if successful,
                    None if extraction fails or no valid prices found
    
    Example:
        >>> url = "https://prices.pokemontcg.io/tcgplayer/ex12-1"
        >>> holofoil = 21.21
        >>> reverse = 32.65
        >>> html_data = get_html_content(url, holofoil, reverse)
    
    Technical Process:
        1. Initializes WebDriver
        2. Navigates to card page
        3. Executes sequence of clicks:
           - Selects 1Y timeframe
           - Opens filters modal
           - Selects Near Mint condition
           - Chooses appropriate foil type
        4. Extracts price history data
    """
    driver = setup_driver()
    wait = WebDriverWait(driver, 40)
    
    try:
        # Load the webpage
        driver.get(website)
        #print("Page loaded successfully")
        
        # Wait for page to be fully loaded
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        
        # Define click sequence for data filtering
        initial_clicks = [
            ('CSS_SELECTOR', 'button[data-v-0177b97d][class="charts-item"]:last-child'),   # 1Y timeframe button
            ('CSS_SELECTOR', 'div.modal__activator[role="button"]'),                        # View More Data button
            ('CSS_SELECTOR', 'button.sales-history-snapshot__show-filters'),                # Sales Filter button
            ('XPATH', '//label[span[text()="Near Mint"]]')                                  # Near Mint condition filter
        ]
        
        # Execute click sequence
        for selector_type, selector in initial_clicks:
            by_type = By.CSS_SELECTOR if selector_type == 'CSS_SELECTOR' else By.XPATH
            if not test_button_click(driver, wait, selector, by=by_type):
                print(f"Click failed for selector: {selector}")
                return None
        
        # If the price is a Nan value
        holofoil_valid = not pd.isna(holofoil_price)
        reverse_valid = not pd.isna(reverse_holofoil_price)
        
        holo_selector = '//span[@class="checkbox__option-value checkbox__option-value-mobile" and text()="Holofoil"]'
        reverse_holo_selector = '//span[@class="checkbox__option-value checkbox__option-value-mobile" and text()="Reverse Holofoil"]'
            
        if holofoil_valid and reverse_valid:
            # we take the highest price ! 

            if holofoil_price > reverse_holofoil_price:
                print('Selecting Holofoil')
                test_button_click(driver, wait, holo_selector, By.XPATH)
            else:
                print('Selecting Reverse Holofoil')
                test_button_click(driver, wait, reverse_holo_selector, By.XPATH)
                
        elif holofoil_valid:
            # If the holofoil price is valid
            test_button_click(driver, wait, holo_selector, By.XPATH)
        elif reverse_valid:
            # If the reverse holofoil price is valid
            test_button_click(driver, wait, reverse_holo_selector, By.XPATH)
        else:
            # No valid prices
            print("No valid prices found")
            return None
            
        # Extract chart data
        html_content = get_chart_data(driver, wait)
        if html_content:
            #print("HTML content successfully retrieved")
            return html_content
            
        print("Failed to retrieve HTML content")
        return None
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return None
        
    finally:
        driver.quit()
        print("Browser session terminated")


def extract_price_history(html_content):
    """
    Extracts and processes price history data from a Pokemon card website.
    
    This function parses HTML content containing price history data for Pokemon cards,
    processes date ranges, prices, and quantities, and returns a structured DataFrame.
    
    Args:
        html_content (str): Raw HTML content containing price history table data
        
    Returns:
        pandas.DataFrame: A sorted DataFrame containing:
            - MultiIndex: (start_date, end_date) as datetime objects
            - Columns: 
                - price (float): Card price for the period
                - quantity_sold (int): Number of cards sold
                
    Example:
        >>> html_data = get_html_content()
        >>> price_df = extract_price_history_(html_data)
    """
    soup = BeautifulSoup(html_content, "html.parser")
    price_history = {}
    
    def convert_date(date_str):
        """
        Converts date range strings to datetime objects with proper year assignment.
        
        Handles date ranges that span across years (Dec-Jan) by automatically
        assigning the correct year to each date.
        
        Args:
            date_str (str): Date range string in format "MM/DD to MM/DD"
            
        Returns:
            tuple: (start_date, end_date) as datetime objects
                  Returns (None, None) if conversion fails
        """
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



def sequential_price_extraction(cards_df, output_dir='price_history'):
    """
    Extracts and saves price history data for multiple Pokemon cards.

    This function processes a DataFrame of Pokemon cards, extracting historical price data
    for each card based on its highest value variant (Holofoil or Reverse Holofoil),
    and saves the data as individual CSV files.

    Args:
        cards_df (pandas.DataFrame): DataFrame containing card information with columns:
            - id: Card identifier
            - holofoil_price: Price of holofoil variant
            - reverse_holofoil_price: Price of reverse holofoil variant
        output_dir (str, optional): Directory path for saving CSV files. Defaults to 'price_history'

    Creates:
        CSV files for each card with columns:
            - start_date: Start date of price period
            - end_date: End date of price period
            - price: Card price during the period
            - quantity_sold: Number of cards sold

    Example:
        >>> cards_data = pd.read_csv('pokemon_cards.csv')
        >>> sequential_price_extraction(cards_data)
    """
    # Create output directory
    subdirs = {
        'low_sales': os.path.join(output_dir, 'low_sales'),
        'medium_sales': os.path.join(output_dir, 'medium_sales'),
        'high_sales': os.path.join(output_dir, 'high_sales')
    }
    
    for subdir in subdirs.values():
        os.makedirs(subdir, exist_ok=True)
    
    progress_bar = tqdm(total=len(cards_df), desc="Price Extraction")
    
    for index, card_row in cards_df.iterrows():
        card_id = card_row['id']
        price_holofoil = card_row["holofoil_price"]
        price_reverse_holofoil = card_row["reverse_holofoil_price"]
        
        
        file_exists = False
        for subdir in subdirs.values():
            if os.path.exists(os.path.join(subdir, f'{card_id}.csv')):
                progress_bar.set_description(f"File exists for {card_id}")
                file_exists = True
                break
        
        if file_exists:
            progress_bar.update(1)
            continue
            
        
        try:
            html_content = get_html_content(
                f"https://prices.pokemontcg.io/tcgplayer/{card_id}",
                price_holofoil,
                price_reverse_holofoil
            )
            price_history = extract_price_history(html_content)
            
            if price_history is not None:
                # Calculate total sales
                total_sales = price_history['quantity_sold'].sum()
                
                # Determine appropriate subdirectory
                if total_sales < 5:
                    subdir = subdirs['low_sales']
                elif total_sales <= 20:
                    subdir = subdirs['medium_sales']
                else:
                    subdir = subdirs['high_sales']
                
                # Create file path in appropriate subdirectory
                file_path = os.path.join(subdir, f'{card_id}.csv')
                
                
                # Reset index and save to CSV
                price_df = price_history.reset_index()
                price_df.columns = ['start_date', 'end_date', 'price', 'quantity_sold']
                price_df.to_csv(file_path, index=False)
                
                progress_bar.set_description(f"Extraction successful for {card_id}")
            
        except Exception as e:
            progress_bar.set_description(f"Failed for {card_id}: {str(e)}")
        
        progress_bar.update(1)
        time.sleep(1)
    
    progress_bar.close()