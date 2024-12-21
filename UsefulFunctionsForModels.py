import os
import pandas as pd
import numpy as np
import glob

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
    """
    Extracts the last price from a DataFrame based on the column name ('Close' or 'price').

    Args:
        df (pd.DataFrame): A DataFrame containing price data.

    Returns:
        float: The last price in the specified column
    """
    price_column = 'Close' if 'Close' in df.columns else 'price'
    last_price = df[price_column].iloc[-1]
    return last_price

def get_mean_return_card (df):
    """
    Calculates the mean logarithmic return of prices in a DataFrame.

    Args:
        df (pd.DataFrame): A DataFrame containing price data.

    Returns:
        float: The mean logarithmic return, rounded to 4 decimal places.

    Notes:
        - Missing values are dropped during computation.
    """
    price_column = 'Close' if 'Close' in df.columns else 'price'
    log_returns = np.log(df[price_column] / df[price_column].shift(1)).dropna()
    mean_return=np.mean(log_returns)
    return round(mean_return,4)


def get_dataframe_cards_matrix(folder_path="datas/price_history"):
    """
    Generates a DataFrame summarizing all the information we need to compute the Markowitz model

    Args:
        folder_path (str): Path to the folder containing card CSV files.

    Returns:
        pd.DataFrame: A DataFrame with columns:
            - card_id: Card identifier derived from file names.
            - last_price: Last recorded price of each card.
            - mean_return: Mean logarithmic return of each card's prices.
            - Quantity Sold : Sum of the quantity sold over the past year.

    Example:
        >>> cards_df = get_dataframe_cards_matrix("path/to/folder")
        >>> print(cards_df.head())
    """
    
    # Use os.walk to get all file paths including subdirectories
    list_paths = []
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith('.csv'):
                list_paths.append(os.path.join(root, file))

    dataframe_cards = {
        "card_id": [],
        "last_price": [],
        "mean_return": [],
        "Quantity Sold": [],
    }   
    try:
        for path in list_paths:
            df = pd.read_csv(path)
            card_id = os.path.basename(path).replace('.csv', '')
            last_price = get_last_price(df)
            mean_return = get_mean_return_card(df) * 100
            sum_sales = np.sum(df["quantity_sold"])
            
            dataframe_cards["card_id"].append(card_id)
            dataframe_cards["last_price"].append(last_price)
            dataframe_cards["mean_return"].append(mean_return)
            dataframe_cards["Quantity Sold"].append(sum_sales)
            
    except Exception as e:
        print(f"Error reading card {card_id}: {e}")
    return pd.DataFrame(dataframe_cards)

        


def calculate_covariance_matrix(cards_df,folder_path = 'datas/price_history'):
    """
    Computes the covariance matrix of card prices across multiple cards.

    Args:
        cards_df (pd.DataFrame): A DataFrame containing card IDs and related statistics.
        folder_path (str): Path to the folder containing CSV files for each card.

    Returns:
        pd.DataFrame: Covariance matrix of prices for all cards.
    """
    cards_prices = {}
    
    for _, row in cards_df.iterrows():
        card_id = row["card_id"]
        found = False
        
        for subdir in ['low_sales', 'medium_sales', 'high_sales']:
            file_path = os.path.join(folder_path, subdir, f'{card_id}.csv')
            matching_files = glob.glob(file_path)
            
            if matching_files:
                try:
                    df = pd.read_csv(matching_files[0])
                    df['start_date'] = pd.to_datetime(df['start_date'])
                    df['end_date'] = pd.to_datetime(df['end_date'])
                    prices = df['price'].tolist()
                    cards_prices[card_id] = prices
                    found = True
                    break
                except Exception as e:
                    print(f"Erreur lors du traitement de {card_id}: {e}")
        
        if not found:
            print(f"Fichier non trouvé pour {card_id}")
    
    if cards_prices:
        price_df = pd.DataFrame(cards_prices)
        covariance_matrix = price_df.cov()
        return covariance_matrix
    else:
        return pd.DataFrame()


def select_mixed_cards(filtered_df, N):
    """
    Selects N cards: half by descending price, half randomly
    
    Args:
        filtered_df: DataFrame containing card information
        N: Total number of cards to select
        
    Returns:
        DataFrame with selected cards
    """
    n_price_select = N // 2
    
    price_sorted_df = filtered_df.nlargest(n_price_select, 'last_price')
    
    remaining_df = filtered_df[~filtered_df.index.isin(price_sorted_df.index)]
    n_random_select = min(N - n_price_select, len(remaining_df))
    
    if n_random_select > 0:
        random_df = remaining_df.sample(n=n_random_select, random_state=42)
        result_df = pd.concat([price_sorted_df, random_df])
    else:
        result_df = price_sorted_df
        
    return result_df


    