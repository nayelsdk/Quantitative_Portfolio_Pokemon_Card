import os
import pandas as pd
import numpy as np

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

def sigmoid_discrete(x, k, x0):
    """
    Computes a sigmoid function for a given input for a fiability rate for each card.

    Args:
        x (float): The input value.
        k (float): The steepness of the curve.
        x0 (float): The midpoint of the sigmoid curve.

    Returns:
        float: The sigmoid value for the input x.

    Formula:
        sigmoid(x) = 1 / (1 + exp(-k * (x - x0)))
    """
    return 1 / (1 + np.exp(-k * (x - x0)))



def get_fiability_card(df):
    """
    Calculates a "fiability" score for a card based on sales quantity using a sigmoid function.

    Args:
        df (pd.DataFrame): A DataFrame containing sales data with a column 'quantity_sold'.

    Returns:
        float: The fiability score.
    """
    try:
        sum_sales_card = np.sum(df["quantity_sold"])
        fiability=sigmoid_discrete(sum_sales_card,k=0.3, x0=15)
    except Exception as e:
        print(f"Error processing {df}: {e}")
    return fiability



def get_dataframe_cards_matrix(folder_path):
    """
    Generates a DataFrame summarizing all the information we need to compute the Markowitz model

    Args:
        folder_path (str): Path to the folder containing card CSV files.

    Returns:
        pd.DataFrame: A DataFrame with columns:
            - card_id: Card identifier derived from file names.
            - last_price: Last recorded price of each card.
            - mean_return: Mean logarithmic return of each card's prices.
            - fiability: Fiability score based on sales data and sigmoid function.
            - fiability_dot_return: Product of fiability and mean return.

    Example:
        >>> cards_df = get_dataframe_cards_matrix("path/to/folder")
        >>> print(cards_df.head())
    """
 
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

        


def calculate_covariance_matrix(cards_df,folder_path = 'pokemon_cards'):
    """
    Computes the covariance matrix of card prices across multiple cards.

    Args:
        cards_df (pd.DataFrame): A DataFrame containing card IDs and related statistics.
        folder_path (str, optional): Path to the folder containing CSV files for each card. Default is 'pokemon_cards'.

    Returns:
        pd.DataFrame: Covariance matrix of prices for all cards. Returns an empty DataFrame if no prices are available.

    Notes:
        - Each card's CSV file must include columns such as 'price', and optionally, date columns ('start_date', 'end_date') for proper parsing.
        - Handles missing files or errors gracefully by printing error messages without interrupting execution.
    """
    cards_prices = {}
    
    for _, row in cards_df.iterrows():
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


    