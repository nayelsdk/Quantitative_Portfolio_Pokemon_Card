import os
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

def get_file_paths(directory):
    """
    Retrieves all file paths from a given directory.

    This function walks through the specified directory and collects the complete
    paths of all files found, including those in subdirectories.

    Parameters:
        directory (str): The path to the directory to scan.

    Returns:
        list: A list containing the complete paths of all files in the directory
             and its subdirectories.

    Example:
        >>> paths = get_file_paths("/home/user/documents")
        >>> print(paths)
        ['/home/user/documents/file1.txt', '/home/user/documents/subfolder/file2.pdf']
    """
    file_paths = []
    for root, _, files in os.walk(directory):
        for file in files:
            file_paths.append(os.path.join(root, file))
    return file_paths

def get_last_price(df):
    # Read the CSV file
    # Determine price column name ('Close' or 'price')
    price_column = 'Close' if 'Close' in df.columns else 'price'
    # Get the last price
    last_price = df[price_column].iloc[-1]
    return last_price

def get_mean_return_card (df):
    price_column = 'Close' if 'Close' in df.columns else 'price'
    log_returns = np.log(df[price_column] / df[price_column].shift(1)).dropna()
    mean_return=np.mean(log_returns)
    return round(mean_return,4)

def sigmoid_discrete(x, k, x0):
    return 1 / (1 + np.exp(-k * (x - x0)))



def get_fiability_card(df):
    try:
        sum_sales_card = np.sum(df["quantity_sold"])
        fiability=sigmoid_discrete(sum_sales_card,k=0.3, x0=15)
    except Exception as e:
        print(f"Error processing {df}: {e}")
    return fiability



def get_dataframe_cards_matrix(folder_path): 
    list_paths=get_file_paths(folder_path)
    dataframe_cards = {
        "card_id": [],
        "last_price": [],
        "mean_return": [],
        "fiability": [],
        "fiability_dot_return": []
    }   
    try:
        for path in list_paths:
            df=pd.read_csv(path)
            card_id = path.split('/')[-1].replace('.csv', '')
            last_price=get_last_price(df)
            mean_return=get_mean_return_card(df)*100
            fiability=get_fiability_card(df)
            
            dataframe_cards["card_id"].append(card_id)
            dataframe_cards["last_price"].append(last_price)
            dataframe_cards["mean_return"].append(mean_return)
            dataframe_cards["fiability"].append(fiability)
            dataframe_cards["fiability_dot_return"].append(fiability*mean_return)
            
    except Exception as e:
        print(f"Error reading card {card_id}: {e}")
    return pd.DataFrame(dataframe_cards)

        

import os
import pandas as pd

def calculate_covariance_matrix(cards_df,folder_path = 'pokemon_cards'):
    cards_prices = {}
    
    for _, row in cards_df.iterrows():
        # Le card_id dans le DataFrame contient déjà le suffixe (_Holofoil, etc.)
        file_path = os.path.join(folder_path, f'{row["card_id"]}.csv')
        
        try:
            df = pd.read_csv(file_path)
            
            df['start_date'] = pd.to_datetime(df['start_date'])
            df['end_date'] = pd.to_datetime(df['end_date'])
            
            prices = df['price'].tolist()
            
            cards_prices[row["card_id"]] = prices
            
        except FileNotFoundError:
            print(f"Fichier non trouvé pour {row['card_id']}")
        except Exception as e:
            print(f"Erreur lors du traitement de {row['card_id']}: {e}")
    
    if cards_prices:
        price_df = pd.DataFrame(cards_prices)
        covariance_matrix = price_df.cov()
        return covariance_matrix
    else:
        return pd.DataFrame()
