import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import pandas as pd
import numpy as np



def plot_price_quantity_variation_matplotlib(df):
    """
    Creates a dual-axis plot showing price trends and sales quantity for a Pokemon card.
    
    Args:
        df: DataFrame with MultiIndex (start_date, end_date) containing price and quantity_sold
        
    Returns:
        tuple: (figure, (price_axis, quantity_axis))
    """
    fig, ax1 = plt.subplots(figsize=(15, 7))
    
    ax1.set_xlabel('Start Date')
    ax1.set_ylabel('Price ($)', color='blue')
    ax1.plot(df.index.get_level_values('start_date'), df['price'], 
             color='blue', marker='o', linewidth=1.5, label='Price', markersize=4)
    ax1.tick_params(axis='y', labelcolor='blue')
    
    mean_price = df['price'].mean()
    ax1.axhline(y=mean_price, color='blue', linestyle='--', alpha=0.3, 
                label=f'Average Price: ${mean_price:.2f}')
    
    ax2 = ax1.twinx()
    ax2.set_ylabel('Quantity Sold', color='orange')
    ax2.bar(df.index.get_level_values('start_date'), df['quantity_sold'], 
            color='orange', alpha=0.3, label='Quantity Sold')
    ax2.tick_params(axis='y', labelcolor='orange')
    
    plt.xticks(rotation=45, ha='right')
    
    plt.title('Pokemon Card Price and Sales Volume Evolution')
    
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax2.legend(lines1 + lines2, labels1 + labels2, loc='upper right')
    
    plt.tight_layout()
    
    return fig, (ax1, ax2)



def plot_price_quantity_variation_seaborn(df):
    """
    Creates an advanced visualization of Pokemon card price and sales data using seaborn.
    
    Args:
        df: DataFrame with MultiIndex (start_date, end_date) containing price and quantity_sold
        
    Returns:
        tuple: (figure, (price_axis, quantity_axis))
    """
    sns.set_style("darkgrid")
    sns.set_palette("husl")
    
    fig = plt.figure(figsize=(15, 10))
    
    gs = GridSpec(2, 1, height_ratios=[2, 1], hspace=0.3)
    
    ax1 = plt.subplot(gs[0])
    
    sns.lineplot(data=df, x=df.index.get_level_values('start_date'), 
                y='price', ax=ax1, color='#4C72B0', linewidth=2)
    ax1.fill_between(df.index.get_level_values('start_date'), 
                     df['price'].min(), df['price'], alpha=0.2)
    
    rolling_mean = df['price'].rolling(window=7).mean()
    ax1.plot(df.index.get_level_values('start_date'), rolling_mean, 
             '--', color='red', label='Moving Average (7 periods)')
    
    ax1.set_title('Pokemon Card Price Evolution', pad=20, fontsize=14)
    ax1.set_xlabel('')
    ax1.set_ylabel('Price ($)', fontsize=12)
    ax1.legend()
    
    ax2 = plt.subplot(gs[1])
    
    sns.barplot(x=df.index.get_level_values('start_date'), 
               y='quantity_sold', data=df, ax=ax2, 
               color='#FFA500', alpha=0.6)
    
    ax2.set_title('Sales Volume', fontsize=14)
    ax2.set_xlabel('Date', fontsize=12)
    ax2.set_ylabel('Quantity Sold', fontsize=12)
    
    for ax in [ax1, ax2]:
        ax.tick_params(axis='x', rotation=45)
        
    stats_text = f"""
    Average Price: ${df['price'].mean():.2f}
    Max Price: ${df['price'].max():.2f}
    Min Price: ${df['price'].min():.2f}
    Total Sold: {df['quantity_sold'].sum()} units
    """
    ax1.text(0.02, 0.98, stats_text, transform=ax1.transAxes, 
             bbox=dict(facecolor='white', alpha=0.8),
             verticalalignment='top', fontsize=10)
    
    plt.tight_layout()
    return fig, (ax1, ax2)


def plot_covariance_heatmap(covariance_matrix):
    correlation_matrix = covariance_matrix.corr()

    plt.figure(figsize=(20, 16))
    
    mask = np.triu(np.ones_like(correlation_matrix), k=1)  # Masque pour le triangle supérieur
    
    sns.heatmap(correlation_matrix,
                mask=mask,  # Afficher seulement le triangle inférieur
                annot=True,  # Afficher les valeurs
                fmt='.2f',  # Format à 2 décimales
                cmap='RdBu_r',  # Palette de couleurs
                center=0,  # Centrer la colormap sur 0
                square=True,  # Cellules carrées
                linewidths=0.5,  # Largeur des lignes de séparation
                cbar_kws={
                    'label': 'Corrélation',
                    'shrink': .8,
                    'aspect': 30,
                    'pad': 0.03
                },
                annot_kws={'size': 8})

    # Personnaliser les labels et le titre
    plt.title('Matrice de Corrélation des Prix des Cartes', 
              pad=20, 
              size=16, 
              weight='bold')
    
    # Rotation des labels pour une meilleure lisibilité
    plt.xticks(rotation=45, ha='right')
    plt.yticks(rotation=0)
    
    # Ajuster automatiquement la mise en page
    plt.tight_layout()
    
    return plt
