from MarkowitzPortfolioOptimizer import MarkowitzOptimizer
from UsefulFunctionsForModels import *
from PlotsStreamlit import *

import numpy as np
import pandas as pd
import streamlit as st
from IPython.display import display,HTML
import ast
import os
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def wide_space_default():
    st.set_page_config(layout="wide")

wide_space_default()

st.title("Investment Portfolio Pokemon Card")

# Sidebar Title
st.sidebar.title("Parameters")

# Slider for amount
amount = st.sidebar.slider(
    "Amount to invest",  # Name of the slider
    min_value=0,  
    max_value=1000, 
    value=500,  # Initial value
    step=10,  # Increment
)

# Slider for amount
k = st.sidebar.slider(
    "Sales volume sensitivity",  # Name of the slider
    min_value=0.,  
    max_value=1., 
    value=0.1,  # Initial value
    step=0.01,  # Increment
)

# Slider for amount
x0 = st.sidebar.slider(
    "Critical sales threshold",  # Name of the slider
    min_value=0.,  
    max_value=1., 
    value=0.4,  # Initial value
    step=0.01,  # Increment
)


if st.sidebar.button("Run"):
    #######################################################################################
    #Markovitz
    df=pd.read_csv("datas/pokemon_cards.csv")

    markowitz=MarkowitzOptimizer(amount,x0,k)

    amount_invested, mean_return, portfolio=markowitz.get_streamlit_database_markowitz()

    n = len(portfolio)

    st.subheader("Quick Metrics")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="Amount to Invest (€)", value=f"{amount_invested}")
    with col2:
        st.metric(label="Mean Return (%)", value=f"{mean_return * 100:.2f}")
    with col3:
        st.metric(label="Number of Cards to buy", value = f"{n}")

    ##############################################################################################
    #Plot

    price, returns = plot_analysis(portfolio)
    repartition = plot_pie(portfolio)

    st.plotly_chart(price)
    st.plotly_chart(returns)
    st.plotly_chart(repartition)



    #############################################################################################
    #dataframe

    portfolio['images_url'] = portfolio.apply(
        lambda row: f'<a href="https://prices.pokemontcg.io/tcgplayer/{row["id"]}" target="_blank">'
                f'<img src="{row["images_url"]}" style="width:100px;"/></a>', axis=1)

    portfolio_plot = portfolio.drop(columns = ['Card Info','id'])

    #Renaming and reorder
    portfolio_plot = portfolio_plot.rename(columns = {
        'name': 'Card Name',
        'rarity': 'Rarity',
        'last_price': 'Price',
        'Fiability': 'Reliability Score',
        'Return x Fiability': 'Return',
        'collection': 'Set Name',
        'release_date': 'Release Date',
        'images_url':'Image + URL'
    })
    portfolio_plot = portfolio_plot[['Image + URL', 'Card Name', 'Rarity', 'Price', 'Reliability Score', 'Return', 'Set Name', 'Release Date']]

    portfolio_plot.reset_index(drop = True, inplace = True)

    ##Styling the dataframe
    #Truncate and adding symbol
    portfolio_plot = portfolio_plot.style.format({
        'Price': "{:.2f}€",
        'Reliability Score': "{:.2%}",
        'Return' : "{:.2%}"
    })
    
    #Center the text + convert to html
    portfolio_plot = portfolio_plot.set_table_styles(
        [{
            'selector': 'table',
            'props': [('width', '100%'), ('border-collapse', 'collapse')],
        },
        {
            'selector': 'td, th',  # Center align both table cells and headers
            'props': [('text-align', 'center')
        ],
    }
    ]).set_table_attributes('style="width: 100%; border-collapse: collapse;"').to_html(escape=False, index=False)

    # Portfolio dataframe title
    st.title("Portfolio")

    # Render HTML in Streamlit
    st.markdown(
        f"""
        <div style="overflow-x: auto; width: 100%;">
            {portfolio_plot}
        </div>
        """,
        unsafe_allow_html=True,
    )



else:
    # Inform the user they need to click the button
    st.write("Adjust the settings in the sidebar and click 'Run' to see the results.")





