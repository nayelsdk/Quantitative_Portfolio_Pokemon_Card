import requests
from bs4 import BeautifulSoup
import pandas as pd


url = "https://api.pokemontcg.io/v2/cards"

def import_data(url):
    page = 1
    all_cards = []
    for i in range(5):
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
    return all_cards



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
                    'cardmarket'
                    
]


def get_prices(x):
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
    
    
def filter_holofoil_data(df):
    df[["url", "holofoil_price", "reverse_holofoil_price"]] = df.apply(get_prices, axis=1, result_type="expand")
    df_cleaned = df.dropna(subset=["url"])
    df_cleaned = df_cleaned[(df_cleaned["rarity"] != "Common") & ((df_cleaned["holofoil_price"] > 10) | (df_cleaned["reverse_holofoil_price"] > 10))]
    print(df_cleaned["set"])
    df_cleaned["collection"]=df_cleaned["set"].apply(lambda x:x["name"])
    df_cleaned["series"]=df_cleaned["set"].apply(lambda x:x["series"])
    
    #drop all the variables we used or not
    df_cleaned = df_cleaned.drop(columns=variables_to_drop, errors='ignore')


    return df_cleaned

