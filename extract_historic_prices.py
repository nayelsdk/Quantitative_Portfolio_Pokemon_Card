import requests
from bs4 import BeautifulSoup
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime

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
    service = Service(ChromeDriverManager().install())
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--window-size=1920,1080")  # Définir une taille d'écran standard
    #chrome_options.add_argument("--disable-gpu")
    return webdriver.Chrome(service=service, options=chrome_options)

def wait_and_click_button(driver, wait):
    try:
        one_year_button = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[data-v-0177b97d][class*="charts-item"]:last-child'))
        )
        
        driver.execute_script("arguments[0].scrollIntoView(true);", one_year_button)
        time.sleep(1) 
        
        try:
            one_year_button.click()
        except ElementClickInterceptedException:
            # Si le clic direct échoue, essayer avec JavaScript
            driver.execute_script("arguments[0].click();", one_year_button)
        
        print("Clic sur le bouton 1Y effectué avec succès!")
        return True
        
    except TimeoutException:
        print("Le bouton 1Y n'a pas été trouvé avec le premier sélecteur, essai avec alternative...")
        try:
            # Essayer avec un sélecteur alternatif
            one_year_button = wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'charts-item') and contains(text(), '1Y')]"))
            )
            driver.execute_script("arguments[0].click();", one_year_button)
            print("Clic sur le bouton 1Y effectué avec succès (méthode alternative)!")
            return True
        except TimeoutException:
            print("Impossible de trouver le bouton 1Y même avec le sélecteur alternatif.")
            return False

def get_chart_data(driver, wait):
    try:
        # Attendre que le graphique soit mis à jour
        chart = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.martech-charts-history[data-testid='History']"))
        )
        
        time.sleep(2)
        
        return chart.get_attribute('outerHTML')
    except TimeoutException:
        print("Impossible de trouver le graphique après le clic.")
        return None

def extract_html_code_1Y(website):
    driver = setup_driver()
    wait = WebDriverWait(driver, 20)
    
    try:
        driver.get(website)
        print("Page chargée avec succès")
        
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        
        # Cliquer sur le bouton 1Y
        if wait_and_click_button(driver, wait):
            html_content = get_chart_data(driver, wait)
            if html_content:
                print("Contenu HTML récupéré avec succès:")
                print(html_content)
            else:
                print("Échec de la récupération du contenu HTML")
        else:
            print("Échec du clic sur le bouton 1Y")
            
    except Exception as e:
        print(f"Une erreur est survenue : {str(e)}")
        
    finally:
        driver.quit()
        print("Navigation terminée - Driver fermé")
    return html_content
