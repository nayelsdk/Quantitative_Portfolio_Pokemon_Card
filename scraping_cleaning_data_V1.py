import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime


url = "https://api.pokemontcg.io/v2/cards"

def import_data():
    """
    Retrieves all available cards from the Pokemon TCG API.
    
    Returns:
        pandas.DataFrame: DataFrame containing all cards with their raw information
        
    Example:
        df = import_data()
        # Returns a DataFrame with columns like id, name, rarity, etc.
    """
    page = 1
    all_cards = []
    
    while True:
        params = {"page": page, "pageSize": 250}
        response = requests.get(url, params=params)

        if response.status_code == 200:
            data = response.json()["data"]
            if not data:
                break
            all_cards.extend(data)
            page += 1
        else:
            print(f"Erreur: {response.status_code}")
            break
            
    return pd.DataFrame(all_cards)


variables_to_drop=['attacks',
                   'supertype',
                   'hp',
                   'abilities',
                   'types',
                   'level',
                   'evolvesFrom',
                   'evolvesTo',
                   'weaknesses',
                   'resistances',
                   'retreatCost',
                   'convertedRetreatCost',
                   'flavorText',
                   'legalities',
                    'images',
                    'rules',
                    'regulationMark',
                    'ancientTrait',
                    'number',
                    'set',
                    'subtypes',
                    'tcgplayer',
                    'cardmarket',
                    'url'
                    
]
new_order=["id",
            "name",
            "rarity",
            "collection",
            "series",
            "holofoil_price",
            "reverse_holofoil_price",
            "release_date",
            "nationalPokedexNumbers",
            "artist"]

def get_prices(x):
    """
    Extracts holofoil and reverse holofoil prices for a card.
    
    Args:
        x (dict): Dictionary containing card information
        
    Returns:
        tuple: (url, holofoil_price, reverse_holofoil_price)
        
    Note:
        Returns None values if the card is common or prices are below threshold
    """
    if pd.isna(x["tcgplayer"]) or x["rarity"] == "Common" or pd.isna(x["rarity"]):
        return None, None, None
    
    prices = x["tcgplayer"].get("prices", {})
    holofoil_data = prices.get("holofoil", {})
    reverse_holofoil_data = prices.get("reverseHolofoil", {})

    holofoil_price = holofoil_data.get("market", None)
    reverse_holofoil_price = reverse_holofoil_data.get("market", None)

    if (holofoil_price is not None and holofoil_price > 10) or (reverse_holofoil_price is not None and reverse_holofoil_price > 10):
        return x["tcgplayer"].get("url", None), holofoil_price, reverse_holofoil_price
    else:
        return None, None, None    



def filter_holofoil_data(df, threshold_price=5):
    """
    Cleans and filters card data based on rarity and price.
    
    Args:
        df (pandas.DataFrame): DataFrame containing raw data
        threshold_price (float, optional): Minimum price to keep a card. Defaults to 5.
        
    Returns:
        pandas.DataFrame: Cleaned DataFrame containing only valuable cards
        
    Note:
        - Removes common cards
        - Keeps only cards above threshold price
        - Extracts collection and series information
        - Removes unnecessary columns
    """
    df[["url", "holofoil_price", "reverse_holofoil_price"]] = df.apply(get_prices, axis=1, result_type="expand")
    df_cleaned = df.dropna(subset=["url"])
    df_cleaned = df_cleaned[(df_cleaned["rarity"] != "Common") & ((df_cleaned["holofoil_price"] > threshold_price) | (df_cleaned["reverse_holofoil_price"] > threshold_price))]
    df_cleaned["collection"]=df_cleaned["set"].apply(lambda x:x["name"])
    df_cleaned["series"]=df_cleaned["set"].apply(lambda x:x["series"])
    df_cleaned["release_date"] = df_cleaned["set"].apply(lambda x: x.get("releaseDate", None))
    
    #drop all the variables we used or not
    df_cleaned = df_cleaned.drop(columns=variables_to_drop, errors='ignore')
    df_cleaned=df_cleaned[new_order]
    return df_cleaned