import pandas as pd

pokemon_popularity = pd.read_csv('pokemon_data_popularity.csv')
pokemon_cards = pd.read_csv('pokemon_cards.csv')

pokemon_popularity['en'] = pokemon_popularity['en'].astype(str)

popularity_dict = dict(zip(pokemon_popularity['en'], pokemon_popularity['Classement']))

def get_popularity_rank(card_name):
    """
    Determines the popularity rank of a Pokémon based on its card name.
    
    Args:
        card_name (str): Name of the Pokémon card
        
    Returns:
        str: Popularity rank or 'Not Referenced' if not found
    """
    # Check if card_name is a string
    if not isinstance(card_name, str):
        return 'Not Referenced'
    
    # Check if any Pokémon name is present in the card name
    for pokemon_name, rank in popularity_dict.items():
        # Skip nan values
        if pokemon_name == 'nan':
            continue
        # Check if pokemon name is in card name
        if pokemon_name in card_name:
            return rank
    return 'Not Referenced'


pokemon_cards['popularity_rank'] = pokemon_cards['name'].apply(get_popularity_rank)

pokemon_cards.to_csv('pokemon_cards_with_popularity.csv', index=False)
