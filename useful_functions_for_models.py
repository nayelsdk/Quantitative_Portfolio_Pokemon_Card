import os
import pandas as pd
import numpy as np
import glob
import matplotlib.pyplot as plt
from statsmodels.nonparametric.smoothers_lowess import lowess

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
        "Card Info": []
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
            dataframe_cards["Card Info"].append(df)
            
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


def plot_distributions(cards_df, log_scale=False):
    """
    Affiche la distribution des prix et des ventes totales de toutes les cartes.

    Args:
        cards_df (pd.DataFrame): Sortie de get_dataframe_cards_matrix(),
                                 avec colonnes 'last_price' et 'Quantity Sold'.
        log_scale (bool): Si True, applique une échelle log sur l'axe x (log-normale).
    """
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    for ax, col, label in [
        (axes[0], 'Quantity Sold', 'Quantité vendue'),
        (axes[1], 'last_price',    'Prix ($)')
    ]:
        data = cards_df[col].dropna()
        if log_scale:
            data = data[data > 0]
            ax.hist(np.log(data), bins=100, edgecolor='black')
            ax.set_xlabel(f'log({label})')
        else:
            ax.hist(data, bins=100, edgecolor='black')
            ax.set_xlabel(label)
        ax.set_ylabel('Nombre de cartes')

    axes[0].set_title('Distribution des ventes totales')
    axes[1].set_title('Distribution des prix')

    plt.tight_layout()
    plt.show()


def plot_liquidity_frontier(cards_df):
    """
    Scatter plot log(prix_médian) × fréquence de trading (nb semaines avec volume > 0 / 52).

    Les points sont colorés selon trois zones de liquidité :
        - Rouge  : fréquence < 0.25  → quasi-illiquide (< 1 vente/mois)
        - Orange : 0.25 ≤ fréquence ≤ 0.60 → liquidité intermédiaire
        - Vert   : fréquence > 0.60  → tradé régulièrement

    Args:
        cards_df (pd.DataFrame): Sortie de get_dataframe_cards_matrix(),
                                 avec colonnes 'card_id' et 'Card Info'.
    """
    LOW, HIGH = 0.25, 0.60

    rows = []
    for _, row in cards_df.iterrows():
        df = row['Card Info']
        median_price = df['price'].median()
        if median_price <= 0:
            continue
        freq = (df['quantity_sold'] > 0).sum() / len(df)
        rows.append({'log_price': np.log(median_price), 'freq': freq})

    plot_df = pd.DataFrame(rows)

    def zone_color(f):
        if f < LOW:
            return 'red'
        elif f <= HIGH:
            return 'orange'
        return 'green'

    plot_df['color'] = plot_df['freq'].apply(zone_color)

    fig, ax = plt.subplots(figsize=(12, 6))

    for color, label in [('red', f'Illiquide  (freq < {LOW})'),
                         ('orange', f'Intermédiaire ({LOW}–{HIGH})'),
                         ('green', f'Liquide  (freq > {HIGH})')]:
        mask = plot_df['color'] == color
        ax.scatter(plot_df.loc[mask, 'log_price'], plot_df.loc[mask, 'freq'],
                   c=color, label=f'{label}  (n={mask.sum()})',
                   alpha=0.5, s=20, edgecolors='none')

    ax.axhline(LOW, color='red',    linestyle='--', linewidth=1.2, alpha=0.8)
    ax.axhline(HIGH, color='green', linestyle='--', linewidth=1.2, alpha=0.8)

    ax.set_xlabel('log(Prix médian annuel $)')
    ax.set_ylabel('Fréquence de trading (semaines actives / 52)')
    ax.set_title('Frontière de liquidité — Univers investissable')
    ax.set_ylim(-0.02, 1.05)
    ax.legend(loc='upper left', fontsize=9)

    # Annotation des zones
    xmin = plot_df['log_price'].min()
    ax.text(xmin, LOW / 2,        'Quasi-illiquide',    color='red',    fontsize=8, va='center')
    ax.text(xmin, (LOW + HIGH) / 2, 'Liquidité partielle', color='orange', fontsize=8, va='center')
    ax.text(xmin, (HIGH + 1) / 2, 'Univers investissable', color='green', fontsize=8, va='center')

    plt.tight_layout()
    plt.show()

    n_total  = len(plot_df)
    n_invest = (plot_df['color'] == 'green').sum()
    print(f"Univers investissable (freq > {HIGH}) : {n_invest} / {n_total} cartes "
          f"({100 * n_invest / n_total:.1f}%)")


def plot_market_structure(cards_df, cards_db_path='datas/pokemon_cards.csv'):
    """
    Scatter plot log(prix_médian) × log(volume_médian) coloré par rareté,
    avec une régression LOWESS non-paramétrique.

    Args:
        cards_df (pd.DataFrame): Sortie de get_dataframe_cards_matrix(),
                                 avec colonnes 'card_id' et 'Card Info'.
        cards_db_path (str): Chemin vers le CSV principal des cartes (pour la rareté).
    """
    # Calcul des médianes par carte
    rows = []
    for _, row in cards_df.iterrows():
        df = row['Card Info']
        median_price = df['price'].median()
        non_zero_volumes = df['quantity_sold'][df['quantity_sold'] > 0]
        if median_price <= 0 or non_zero_volumes.empty:
            continue
        median_volume = non_zero_volumes.median()
        # Supprime le suffixe _Holofoil / _Reverse_Holofoil pour rejoindre la DB
        base_id = row['card_id'].rsplit('_', 1)[0]
        rows.append({
            'card_id': base_id,
            'log_price': np.log(median_price),
            'log_volume': np.log(median_volume)
        })

    plot_df = pd.DataFrame(rows)

    # Jointure avec la rareté
    db = pd.read_csv(cards_db_path, usecols=['id', 'rarity'])
    plot_df = plot_df.merge(db, left_on='card_id', right_on='id', how='left')
    plot_df['rarity'] = plot_df['rarity'].fillna('Unknown')

    # Couleur par rareté
    rarities = plot_df['rarity'].unique()
    colors = plt.cm.tab20.colors
    color_map = {r: colors[i % len(colors)] for i, r in enumerate(rarities)}

    fig, ax = plt.subplots(figsize=(12, 7))

    for rarity, group in plot_df.groupby('rarity'):
        ax.scatter(group['log_price'], group['log_volume'],
                   color=color_map[rarity], label=rarity, alpha=0.6, s=25)

    # LOWESS sur l'ensemble des points
    sorted_df = plot_df.sort_values('log_price')
    smoothed = lowess(sorted_df['log_volume'], sorted_df['log_price'], frac=0.4)
    ax.plot(smoothed[:, 0], smoothed[:, 1], color='red', linewidth=2, label='LOWESS')

    ax.set_xlabel('log(Prix médian annuel)')
    ax.set_ylabel('log(Volume médian hebdomadaire)')
    ax.set_title('Structure du marché : Prix vs Liquidité par rareté')
    ax.legend(bbox_to_anchor=(1.01, 1), loc='upper left', fontsize=8)

    plt.tight_layout()
    plt.show()


def get_csv_by_card_id(card_id, folder_path='datas/price_history'):
    """
    Renvoie le DataFrame associé à un identifiant de carte.

    Cherche dans les sous-dossiers low_sales, medium_sales et high_sales
    un fichier CSV dont le nom correspond à card_id.

    Args:
        card_id (str): Identifiant de la carte (ex: 'swsh6-207_Holofoil').
        folder_path (str): Chemin vers le dossier contenant les historiques de prix.

    Returns:
        pd.DataFrame: Données de prix de la carte.

    Raises:
        FileNotFoundError: Si aucun fichier CSV ne correspond à l'identifiant donné.
    """
    for subdir in ['low_sales', 'medium_sales', 'high_sales']:
        matching_files = glob.glob(os.path.join(folder_path, subdir, f'{card_id}_*.csv'))
        if matching_files:
            return pd.read_csv(matching_files[0])

    raise FileNotFoundError(f"Aucun fichier CSV trouvé pour la carte '{card_id}' dans {folder_path}")


def plot_card_history(card_id, folder_path='datas/price_history'):
    """
    Affiche l'évolution du prix et le nombre de ventes d'une carte.

    Args:
        card_id (str): Identifiant de la carte (ex: 'hgss3-26').
        folder_path (str): Chemin vers le dossier contenant les historiques de prix.

    Returns:
        matplotlib.figure.Figure: Figure avec deux panneaux :
            - Haut : évolution du prix dans le temps (ligne)
            - Bas  : nombre de ventes par semaine (barres)
    """
    df = get_csv_by_card_id(card_id, folder_path)
    df['start_date'] = pd.to_datetime(df['start_date'])

    _, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 6), sharex=True)

    ax1.plot(df['start_date'], df['price'])
    ax1.set_ylabel('Prix ($)')
    ax1.set_title(f'Historique — {card_id}')

    ax2.bar(df['start_date'], df['quantity_sold'], width=5)
    ax2.set_ylabel('Ventes')

    plt.tight_layout()
    plt.show()


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


    