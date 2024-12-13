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

def calculate_return_matrix_avg(foldr_path):
    """
    Calculates the average returns matrix for a list of CSV files with their identifiers.

    This function processes multiple CSV files containing price data, calculates
    logarithmic returns, and computes the average return for each file. The results
    are stored in a dictionary where the keys are the file identifiers (derived from
    filenames) and the values are the corresponding average returns.

    Parameters:
        directory (str): The path to the directory to scan.

    Returns:
        dict: A dictionary where:
              - Keys are the card IDs (extracted from filenames)
              - Values are the average logarithmic returns

    Example:
        >>> paths = ['data/card1.csv', 'data/card2.csv']
        >>> returns = calculate_matrice_rendement_avg(paths)
        >>> print(returns)
        {'card1': 0.0023, 'card2': 0.0045}

    Notes:
        - The function expects CSV files with either a 'Close' or 'price' column
        - Returns are calculated using natural logarithm of price ratios
        - Any errors during file processing are caught and printed
        - Files with processing errors are skipped
        - NaN values are automatically dropped from calculations
    """
    csv_paths=get_file_paths(foldr_path)
    returns_dict = {}
    
    for path in csv_paths:
        try:
            df = pd.read_csv(path)
            
            # Determine price column name ('Close' or 'price')
            price_column = 'Close' if 'Close' in df.columns else 'price'
            
            # Calculate logarithmic returns
            returns = np.log(df[price_column] / df[price_column].shift(1)).dropna()
            
            # Calculate average return
            mean_return = returns.mean()
            
            card_id = path.split('/')[-1].replace('.csv', '')
            
            returns_dict[card_id] = mean_return
            
        except Exception as e:
            print(f"Error processing {path}: {str(e)}")
    
    return returns_dict


def get_last_prices(folder_path):
    """
    Retrieves the last price from each CSV file in the provided list.

    This function reads multiple CSV files containing price data and extracts
    the most recent price from each file. The results are stored in a dictionary
    where the keys are the filenames (without extension) and the values are
    the corresponding last prices.

    Parameters:
        directory (str): The path to the directory to scan.

    Returns:
        dict: A dictionary where:
              - Keys are the filenames (without .csv extension)
              - Values are the last recorded prices from each file

    Example:
        >>> paths = ['data/card1.csv', 'data/card2.csv']
        >>> prices = get_last_prices(paths)
        >>> print(prices)
        {'card1': 125.50, 'card2': 67.25}

    Notes:
        - The function expects CSV files with either a 'Close' or 'price' column
        - If a file cannot be processed, an error message is printed and the file is skipped
        - The last price is extracted using pandas' iloc[-1] indexing
    """
    csv_paths=get_file_paths(folder_path)    
    last_prices = {}
    
    for path in csv_paths:
        try:
            # Read the CSV file
            df = pd.read_csv(path)
            
            # Determine price column name ('Close' or 'price')
            price_column = 'Close' if 'Close' in df.columns else 'price'
            
            # Get the last price
            last_price = df[price_column].iloc[-1]
            
            # Extract filename without extension
            file_name = path.split('/')[-1].replace('.csv', '')
            
            last_prices[file_name] = last_price
            
        except Exception as e:
            print(f"Error reading {path}: {str(e)}")
            
    return last_prices

def calculate_covariance_matrix(folder_path):
    """
    Transforms CSV files containing price data into a dictionary and calculates 
    their covariance matrix.

    This function reads all CSV files from a specified folder, extracts weekly
    prices for each asset, creates a dictionary structure, and computes the
    covariance matrix between all cards.

    Parameters:
        folder_path (str): Path to the directory containing CSV files with price data.
                          Each CSV file should have columns: 'start_date', 'end_date', 
                          and 'price'.

    Returns:
        tuple: A tuple containing:
               - pandas.DataFrame: The covariance matrix between all assets

    Example:
        >>> prices, cov_matrix = calculate_weekly_prices_dict("data/prices/")
        >>> print(prices)
        {'card1': [10.5, 11.0, 10.8], 'card2': [20.1, 20.5, 20.3]}
        >>> print(cov_matrix)
                card1    card2
        card1   0.063   0.045
        card2   0.045   0.040
    """
    cards_prices = {}
    
    for file in os.listdir(folder_path):
        if file.endswith('.csv'):
            try:
                # Read CSV file
                df = pd.read_csv(os.path.join(folder_path, file))
                
                # Convert date columns
                df['start_date'] = pd.to_datetime(df['start_date'])
                df['end_date'] = pd.to_datetime(df['end_date'])
                
                # Extract weekly prices
                prices = df['price'].tolist()
                
                # Extract card ID from filename
                card_id = file.replace('.csv', '')
                
                # Store prices in dictionary
                cards_prices[card_id] = prices
                
            except Exception as e:
                print(f"Error processing {file}: {e}")
    
    # Create DataFrame from dictionary and calculate covariance matrix
    price_df = pd.DataFrame(cards_prices)
    covariance_matrix = price_df.cov()
    
    return covariance_matrix


def attribute_fiability_score(folder_path):
    """
    Calculates a more conservative reliability score for each card based on sales volume data.

    This function processes CSV files containing sales data and computes a reliability
    score using a rational formula: total_sales) / (total_sales + c). Here c=10.

    Parameters:
        folder_path (str): Path to the directory containing CSV files.
                          Each CSV file should have a 'quantity_sold' column.

    Returns:
        dict: A dictionary where:
              - Keys are card IDs (derived from filenames)
              - Values are reliability scores between 0 and 1

    Example:
        >>> scores = attribute_fiability_score_soft("data/sales/")
        >>> print(scores)
        {'card1': 0.75, 'card2': 0.62}

    Notes:
        - Score formula: log(1 + x) / (1 + log(1 + x)) where x is total_sales
        - Score range: [0,1) where:
          * 0 indicates no sales
          * Values increase more gradually than exponential
        - Files with processing errors are skipped
    """
    cards_fiability = {}
    
    for file in os.listdir(folder_path):
        if file.endswith('.csv'):
            try:
                # Read CSV file
                df = pd.read_csv(os.path.join(folder_path, file))
                
                # Calculate total sales
                sum_sales_card = np.sum(df["quantity_sold"])
                
                # Calculate reliability score using logarithmic formula
                score = sum_sales_card / (10 + sum_sales_card)
                
                # Extract card ID from filename
                card_id = os.path.basename(file).replace('.csv', '')
                cards_fiability[card_id] = score
                
            except Exception as e:
                print(f"Error processing {file}: {e}")
                
    return cards_fiability
