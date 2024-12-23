# Afficher un graphique
from PokemonCardManager import *
# from GetHistoricCardPrices import save_historic_prices
from MarkowitzPortfolioOptimizer import MarkowitzOptimizer
from UsefulFunctionsForModels import *

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st
from IPython.display import display,HTML
import ast
import os
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import random

def wide_space_default():
    st.set_page_config(layout="wide")

wide_space_default()

st.title("Investment Portfolio Pokemon Card")

# Sidebar Title
st.sidebar.title("Parameters")

# Slider for amount
amount = st.sidebar.slider(
    "Choose the amount you want to invest",  # Name of the slider
    min_value=0,  
    max_value=1000, 
    value=500,  # Initial value
    step=10,  # Increment
)

# Slider for amount
k = st.sidebar.slider(
    "Choose the sales_volume_sensitivity",  # Name of the slider
    min_value=0.,  
    max_value=1., 
    value=0.1,  # Initial value
    step=0.01,  # Increment
)

# Slider for amount
x0 = st.sidebar.slider(
    "Choose the critical_sales_threshold",  # Name of the slider
    min_value=0.,  
    max_value=1., 
    value=0.4,  # Initial value
    step=0.01,  # Increment
)


#######################################################################################
#Markovitz
df=pd.read_csv("datas/pokemon_cards.csv")

markowitz=MarkowitzOptimizer(amount,x0,k)

amount_invested, mean_return, portfolio=markowitz.get_streamlit_database_markowitz()

# Print the real amount
# st.write(f"Amount you need to invest **{amount_invested} €**.")


# col1, col2 = st.columns(2)

# with col1:
#     st.markdown(f"""
#         <style>
#             body {{
#                 display: flex;
#                 justify-content: center;
#                 align-items: center;
#                 height: 100vh; /* Prend toute la hauteur de la fenêtre */
#                 margin: 0;
#                 background-color: #f7f7f7; /* Couleur de fond de la page */
#             }}
#             .rectangle {{
#                 width: 300px;
#                 height: 100px;
#                 background-color: #487617; /* Couleur du carré */
#                 color: white; /* Couleur du texte */
#                 display: flex;
#                 justify-content: center;
#                 align-items: center;
#                 font-size: 20px;
#                 font-weight: bold;
#                 border-radius: 10px; /* Coins arrondis */
#                 box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2); /* Ombre du carré */
#             }}
#         </style>
#         <div class="carre">
#             {amount_invested}€
#         </div>
#     """, unsafe_allow_html=True)

# with col2:
#     st.markdown(f"""
#         <style>
#             body {{
#                 display: flex;
#                 justify-content: center;
#                 align-items: center;
#                 height: 100vh; /* Prend toute la hauteur de la fenêtre */
#                 margin: 0;
#                 background-color: #f7f7f7; /* Couleur de fond de la page */
#             }}
#             .rectangle {{
#                 width: 300px;
#                 height: 100px;
#                 background-color: #487617; /* Couleur du carré */
#                 color: white; /* Couleur du texte */
#                 display: flex;
#                 justify-content: center;
#                 align-items: center;
#                 font-size: 20px;
#                 font-weight: bold;
#                 border-radius: 10px; /* Coins arrondis */
#                 box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2); /* Ombre du carré */
#             }}
#         </style>
#         <div class="carre">
#             {mean_return}
#         </div>
#     """, unsafe_allow_html=True)

title1 = "Amount you need to invest"
title2 = "The mean return of the portfolio"

col1, col2, col3, col4, col5 = st.columns([1, 2, 1, 2, 1])

st.markdown(
    """
    <style>
    .title-container {
        min-height: 50px; /* Set a minimum height for titles */
        max-width: 400px; /* Set a maximum width for titles */
        width: 100%; /* Allow title container to scale */
        display: flex;
        justify-content: center;
        align-items: center;
        text-align: center;
        word-wrap: break-word;
    }
    .rectangle {
        background-color: #3498db;
        color: white;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        width: 200px;
    }
    .rectangle.green {
        background-color: #2ecc71;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Premier rectangle dans la deuxième colonne
with col2:
    st.markdown(
        f"""
        <div style="text-align: center;">
            <div class="title-container">
                <h3>{title1}</h3>
            </div>
            <div class="rectangle">
                <h2>{amount_invested} €</h2>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

with col4:
    st.markdown(
        f"""
        <div style="text-align: center;">
            <div class="title-container">
                <h3>{title2}</h3>
            </div>
            <div class="rectangle green">
                <h2>{mean_return} €</h2>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

# # AJOUT COURBE MARKOVITZ
# def get_file_paths(directory):
#     """
#     Récupère tous les chemins des fichiers dans un dossier donné.

#     Args:
#         directory (str): Le chemin du dossier.

#     Returns:
#         list: Une liste contenant les chemins complets des fichiers dans le dossier.
#     """
#     file_paths = []
#     for root, _, files in os.walk(directory):
#         for file in files:
#             file_paths.append(os.path.join(root, file))
#     return file_paths


# def prepare_card_data(df):
#     """Prépare les données des cartes pour l'optimisation"""
#     processed_data = []
#     # Calcul des rendements logarithmiques
#     df['log_return'] = np.log(df['price'] / df['price'].shift(1)).fillna(0)
    
#     # Calcul des poids basés sur les transactions
#     total_transactions = df['quantity_sold'].sum()
#     df['weight'] = df['quantity_sold'] / total_transactions if total_transactions > 0 else 0
    
#     processed_data.append(df)

#     return processed_data



# import random

# def generate_random_color():
#     """Génère une couleur aléatoire au format hexadécimal."""
#     return f'#{random.randint(0, 0xFFFFFF):06x}'

# def generate_distinct_colors(num_colors):
#     """Génère une liste de couleurs distinctes."""
#     colors = []
#     for _ in range(num_colors):
#         while True:
#             new_color = generate_random_color()
#             # Vérifier si la couleur est suffisamment différente des autres
#             if not any(is_similar(new_color, color) for color in colors):
#                 colors.append(new_color)
#                 break
#     return colors

# def is_similar(color1, color2, threshold=50):
#     """Retourne True si deux couleurs sont trop similaires (sur une échelle de 0 à 255 pour chaque canal RGB)."""
#     # Convertir la couleur hexadécimale en RGB
#     color1_rgb = tuple(int(color1[i:i+2], 16) for i in (1, 3, 5))
#     color2_rgb = tuple(int(color2[i:i+2], 16) for i in (1, 3, 5))
    
#     # Calculer la différence euclidienne entre les deux couleurs dans l'espace RGB
#     diff = sum((c1 - c2) ** 2 for c1, c2 in zip(color1_rgb, color2_rgb)) ** 0.5
#     return diff < threshold


# #affichage
# def create_elegant_pokemon_chart(dataframes, labels):
#     # Créer la figure avec un subplot secondaire pour le volume
#     fig = make_subplots(
#         rows=2, cols=1,
#         row_heights=[0.7, 0.3],
#         vertical_spacing=0.05,
#         shared_xaxes=True
#     )
    
#     # Couleurs élégantes
#     colors = generate_distinct_colors(len(dataframes))  # Bleu nuit et Bordeaux
    
#     # Ajouter les rendements pour chaque carte
#     for i, (df, label) in enumerate(zip(dataframes, labels)):
#         fig.add_trace(
#             go.Scatter(
#                 x=df['start_date'],
#                 y=df['log_return'],
#                 name=label,
#                 line=dict(
#                     color=colors[i],
#                     width=1.5,
#                     shape='spline',
#                     smoothing=0.3
#                 ),
#                 mode='lines',
#             ),
#             row=1, col=1
#         )
        
#         # Ajouter le volume
#         fig.add_trace(
#             go.Bar(
#                 x=df['start_date'],
#                 y=df['quantity_sold'],
#                 name=f"Volume {label}",
#                 marker_color=colors[i],
#                 opacity=0.5,
#                 showlegend=False
#             ),
#             row=2, col=1
#         )

#     # Mise en page élégante
#     fig.update_layout(
#         title={
#             'text': 'Analyse des Rendements des Cartes Pokémon',
#             'y': 0.95,
#             'x': 0.5,
#             'xanchor': 'center',
#             'yanchor': 'top',
#             'font': dict(
#                 family='Playfair Display',
#                 size=24,
#                 color='#2F4F4F'
#             )
#         },
#         paper_bgcolor='white',
#         plot_bgcolor='rgba(248,248,255,0.95)',
#         font=dict(
#             family='Playfair Display',
#             size=12,
#             color='#2F4F4F'
#         ),
#         xaxis=dict(
#             showgrid=True,
#             gridwidth=1,
#             gridcolor='rgba(128,128,128,0.1)',
#             showline=True,
#             linewidth=1,
#             linecolor='rgba(128,128,128,0.3)'
#         ),
#         yaxis=dict(
#             title='Rendement Logarithmique',
#             tickformat='.1%',
#             showgrid=True,
#             gridwidth=1,
#             gridcolor='rgba(128,128,128,0.1)',
#             showline=True,
#             linewidth=1,
#             linecolor='rgba(128,128,128,0.3)'
#         ),
#         yaxis2=dict(
#             title='Volume de Transactions',
#             showgrid=True,
#             gridwidth=1,
#             gridcolor='rgba(128,128,128,0.1)',
#             showline=True,
#             linewidth=1,
#             linecolor='rgba(128,128,128,0.3)'
#         ),
#         legend=dict(
#             bgcolor='rgba(255,255,255,0.8)',
#             bordercolor='rgba(128,128,128,0.2)',
#             borderwidth=1,
#             orientation='h',
#             yanchor='bottom',
#             y=1.02,
#             xanchor='center',
#             x=0.5
#         ),
#         hovermode='x unified',
#         margin=dict(t=100, l=60, r=20, b=40)
#     )
    
#     # Ajouter des annotations pour les valeurs extrêmes
#     max_return = max(df['log_return'].max() for df in dataframes)
#     min_return = min(df['log_return'].min() for df in dataframes)
    
#     return fig

# # Calculer les rendements logarithmiques
# def calculate_log_returns(df):
#     df['log_return'] = np.log(df['price'] / df['price'].shift(1))
#     return df
# n=5
# L=get_file_paths('price_history')
# dataframes = []
# labels = [f"Carte {i+1}" for i in range(n)]

# selected_cards = random.sample(L, n)
# for file in selected_cards:
#     df = pd.read_csv(file)
#     df = calculate_log_returns(df)
#     dataframes.append(df)

# print(len(labels))
# print(len(dataframes))
# # Création et affichage du graphique
# # Tracer les rendements interactifs
# fig = create_elegant_pokemon_chart(dataframes, labels)

# #fonction compatible avec plotly
# st.plotly_chart(fig)


#############################################################################################
#dataframe

# #afficher une image
# # URL de l'image Pokémon et lien cible
# image_url = "https://images.pokemontcg.io/dp3/1.png"  # URL de l'image
# link_url = "https://www.pokemontcg.io/"  # URL cible

# # Afficher l'image avec un lien cliquable
# st.markdown(
#     f'''
#     <a href="{link_url}" target="_blank">
#         <img src="{image_url}" alt="Carte Pokémon" style="width:300px;">
#     </a>
#     ''',
#     unsafe_allow_html=True
# )

# # Ajouter une description
# st.write("Cliquez sur la carte Pokémon pour explorer plus de détails !")


# st.image("https://images.pokemontcg.io/dp3/1.png")

# Add a dataframe

# portfolio['images'] = portfolio['images'].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else x)
# portfolio['images'] = portfolio['images'].apply(lambda x: list(x.values())[0])

portfolio['images_url'] = portfolio['images_url'].apply(lambda x: f'<img src="{x}" width="60">')

# df1['Nom'] = df['name']
# df1['id'] = df['id']
# df1['date achat'] = None
# df1['date vente'] = None
# df1['prix achat'] = None
# df1['prix vente'] = None
# df1['benefice'] = None
# df1.drop(columns=["images", "images2"], inplace=True)

# new_order = ['id','Nom','images','date achat', 'date vente', 'prix achat', 'prix vente', 'benefice']
# df1 = df1[new_order]

portfolio_plot = portfolio.drop('Card Info', axis = 1)

pd.set_option('display.max_colwidth', None)

st.write(HTML(portfolio_plot.to_html(escape=False)), unsafe_allow_html=True)

# st.dataframe(HTML(df.to_html(escape=False ,formatters=format_dict)))









