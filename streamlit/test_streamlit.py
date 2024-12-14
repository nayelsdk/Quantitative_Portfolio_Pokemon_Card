# Afficher un graphique
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st
from IPython.display import display,HTML
import ast
import os
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.title("Sélecteur de montant d'argent 💰")

# Ajouter une description
st.sidebar.title("Paramètres")

# Slider pour sélectionner un montant
montant = st.sidebar.slider(
    "Choisissez le montant (en euros)",  # Étiquette du slider
    min_value=0,  # Valeur minimale
    max_value=1000,  # Valeur maximale
    value=100,  # Valeur initiale
    step=10,  # Incrément
)
# Afficher le montant sélectionné
st.write(f"Vous avez choisi de mettre **{montant} €**.")

# Slider pour sélectionner un nombre de cartes
carte = st.sidebar.slider(
    "Choisissez le nombre de cartes",  # Étiquette du slider
    min_value=0,  # Valeur minimale
    max_value=249,  # Valeur maximale
    value=100,  # Valeur initiale
    step=1,  # Incrément
)

# Sélection du niveau de risque
aversion_risque = st.sidebar.radio(
    "Quelle est votre aversion au risque ?",  # Étiquette
    options=["Faible", "Moyenne", "Élevée"],  # Options disponibles
    index=1  # Option par défaut
)
nombre1 = st.sidebar.number_input("Entrez le premier nombre", value=0)
nombre2 = st.sidebar.number_input("Entrez le deuxième nombre", value=0)

# Description principale
st.write(f"Vous avez choisi une aversion au risque : **{aversion_risque}**.")










# AJOUT COURBE MARKOVITZ
def get_file_paths(directory):
    """
    Récupère tous les chemins des fichiers dans un dossier donné.

    Args:
        directory (str): Le chemin du dossier.

    Returns:
        list: Une liste contenant les chemins complets des fichiers dans le dossier.
    """
    file_paths = []
    for root, _, files in os.walk(directory):
        for file in files:
            file_paths.append(os.path.join(root, file))
    return file_paths

L=get_file_paths('price_history')
a=pd.read_csv(L[nombre1])
c=pd.read_csv(L[nombre2])


def prepare_card_data(df):
    """Prépare les données des cartes pour l'optimisation"""
    processed_data = []
    # Calcul des rendements logarithmiques
    df['log_return'] = np.log(df['price'] / df['price'].shift(1)).fillna(0)
    
    # Calcul des poids basés sur les transactions
    total_transactions = df['quantity_sold'].sum()
    df['weight'] = df['quantity_sold'] / total_transactions if total_transactions > 0 else 0
    
    processed_data.append(df)

    return processed_data


b=prepare_card_data(a)




#affichage
def create_elegant_pokemon_chart(dataframes, labels):
    # Créer la figure avec un subplot secondaire pour le volume
    fig = make_subplots(
        rows=2, cols=1,
        row_heights=[0.7, 0.3],
        vertical_spacing=0.05,
        shared_xaxes=True
    )
    
    # Couleurs élégantes
    colors = ['#2E3F6E', '#A63A50']  # Bleu nuit et Bordeaux
    
    # Ajouter les rendements pour chaque carte
    for i, (df, label) in enumerate(zip(dataframes, labels)):
        fig.add_trace(
            go.Scatter(
                x=df['start_date'],
                y=df['log_return'],
                name=label,
                line=dict(
                    color=colors[i],
                    width=1.5,
                    shape='spline',
                    smoothing=0.3
                ),
                mode='lines',
            ),
            row=1, col=1
        )
        
        # Ajouter le volume
        fig.add_trace(
            go.Bar(
                x=df['start_date'],
                y=df['quantity_sold'],
                name=f"Volume {label}",
                marker_color=colors[i],
                opacity=0.5,
                showlegend=False
            ),
            row=2, col=1
        )

    # Mise en page élégante
    fig.update_layout(
        title={
            'text': 'Analyse des Rendements des Cartes Pokémon',
            'y': 0.95,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': dict(
                family='Playfair Display',
                size=24,
                color='#2F4F4F'
            )
        },
        paper_bgcolor='white',
        plot_bgcolor='rgba(248,248,255,0.95)',
        font=dict(
            family='Playfair Display',
            size=12,
            color='#2F4F4F'
        ),
        xaxis=dict(
            showgrid=True,
            gridwidth=1,
            gridcolor='rgba(128,128,128,0.1)',
            showline=True,
            linewidth=1,
            linecolor='rgba(128,128,128,0.3)'
        ),
        yaxis=dict(
            title='Rendement Logarithmique',
            tickformat='.1%',
            showgrid=True,
            gridwidth=1,
            gridcolor='rgba(128,128,128,0.1)',
            showline=True,
            linewidth=1,
            linecolor='rgba(128,128,128,0.3)'
        ),
        yaxis2=dict(
            title='Volume de Transactions',
            showgrid=True,
            gridwidth=1,
            gridcolor='rgba(128,128,128,0.1)',
            showline=True,
            linewidth=1,
            linecolor='rgba(128,128,128,0.3)'
        ),
        legend=dict(
            bgcolor='rgba(255,255,255,0.8)',
            bordercolor='rgba(128,128,128,0.2)',
            borderwidth=1,
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='center',
            x=0.5
        ),
        hovermode='x unified',
        margin=dict(t=100, l=60, r=20, b=40)
    )
    
    # Ajouter des annotations pour les valeurs extrêmes
    max_return = max(df['log_return'].max() for df in dataframes)
    min_return = min(df['log_return'].min() for df in dataframes)
    
    return fig

# Calculer les rendements logarithmiques
def calculate_log_returns(df):
    df['log_return'] = np.log(df['price'] / df['price'].shift(1))
    return df

xy8_22 = calculate_log_returns(a)
ex1_4 = calculate_log_returns(c)

# # Tracer les rendements interactifs
fig = create_elegant_pokemon_chart([xy8_22, ex1_4], ['xy8-22', 'ex1-4'])

#fonction compatible avec plotly
st.plotly_chart(fig)






# Génération de données en fonction du risque
if aversion_risque == "Faible":
    # Courbe pour les preneurs de risques (faible aversion)
    x = np.linspace(0, 10, 100)
    y = np.sin(x) * np.exp(0.1 * x)  # Courbe croissante avec oscillations
elif aversion_risque == "Moyenne":
    # Courbe pour un équilibre entre risque et sécurité
    x = np.linspace(0, 10, 100)
    y = np.log(x + 1) * 5  # Croissance logarhythmique
else:
    # Courbe pour les aversions élevées (sécurité avant tout)
    x = np.linspace(0, 10, 100)
    y = 5 + np.cos(x)  # Ligne stable avec de petites oscillations

# Affichage du graphique
st.line_chart(pd.DataFrame({"x": x, "y": y}).set_index("x"))

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


st.image("https://images.pokemontcg.io/dp3/1.png")

# Add a dataframe

df = pd.read_csv("streamlit/dfstreamlit.csv")
df1 = pd.DataFrame(df['images'])
df1['images'] = df1['images'].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else x)
df1['images2'] = df1['images'].apply(lambda x: list(x.values())[0])
df1['images3'] =df1['images2'].apply(lambda x: f'<img src="{x}" width="60">')



pd.set_option('display.max_colwidth', None)

st.write(df1.head(carte).to_html(escape=False), unsafe_allow_html=True)

# st.dataframe(HTML(df.to_html(escape=False ,formatters=format_dict)))









