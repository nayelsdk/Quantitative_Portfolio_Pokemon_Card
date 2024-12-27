from MarkowitzPortfolioOptimizer import MarkowitzOptimizer
from UsefulFunctionsForModels import *
from PlotsStreamlit import *
import pandas as pd
import streamlit as st

def wide_space_default():
    st.set_page_config(
        layout="wide",
        page_title="Pokemon Portfolio Builder",
        page_icon="⚡"
    )

wide_space_default()

st.markdown(
    """
    <style>
    .sidebar-content {
        text-align: center;
    }
    .sidebar-text {
        text-align: center;
        padding: 5px;
        font-size: 14px;
    }
    </style>
    """, 
    unsafe_allow_html=True
)


col1, col2, col3 = st.sidebar.columns([1,2,1])
with col2:
    st.image("images/LOGO-ENSAE.png", width=130)
st.title("Build your own Portfolio Pokemon Card !")


st.sidebar.markdown("---")  

st.sidebar.title("Parameters ⚙️")
amount = st.sidebar.slider(
    "Amount to invest 💰",  
    min_value=10,  
    max_value=1000, 
    value=500,  
    step=10,  
)

# Slider for amount
x0 = st.sidebar.slider(
    "Sales volume sensitivity 🎲", 
    min_value=0.,  
    max_value=1., 
    value=0.5,  
    step=0.01, 
)

# Slider for amount
k = st.sidebar.slider(
    "Reliability sensitivity 🎯",  
    min_value=0.,  
    max_value=1., 
    value=0.5,  
    step=0.01, 
)

if st.sidebar.button("Run 🏃"):
    #Markovitz
    df=pd.read_csv("datas/pokemon_cards.csv")

    markowitz=MarkowitzOptimizer(amount,x0,k)

    amount_invested, mean_return, portfolio=markowitz.get_streamlit_database_markowitz()

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="Amount to Invest ($)", value=f"{amount_invested}")
    with col2:
        st.metric(label="Mean Return (%)", value=f"{mean_return * 100:.2f}")
    with col3:
        st.metric(label="Number of cards", value=f"{len(portfolio)}")
    ##############################################################################################
    
    #Plot
    price, returns = plot_analysis(portfolio)
    repartition = plot_pie(portfolio)

    st.plotly_chart(price)
    st.plotly_chart(returns)
    st.plotly_chart(repartition)

    #############################################################################################
    
    #Dataframe
    portfolio['images_url'] = portfolio.apply(
        lambda row: f'<a href="https://prices.pokemontcg.io/tcgplayer/{row["id"]}" target="_blank">'
                f'<img src="{row["images_url"]}" style="width:100px;"/></a>', axis=1)

    portfolio_plot = portfolio.drop(columns = ['Card Info','id'])

    #Rename and reorder
    portfolio_plot = portfolio_plot.rename(columns={
    'name': 'Card Name',
    'rarity': 'Rarity',
    'last_price': 'Price',
    'Fiability': 'Reliability',
    'Return x Fiability': 'Mean Return',
    'collection': 'Set Name',
    'release_date': 'Release Date',
    'images_url': 'Card Layout + URL'
})
    column_order=['Card Layout + URL', 'Card Name', 'Price', 'Rarity', 'Mean Return', 'Reliability', 'Set Name', 'Release Date']
    portfolio_plot=portfolio_plot[column_order]

    
    portfolio_plot = portfolio_plot.style.format({
        'Price': "{:.2f}$",
        'Reliability': "{:.2%}",
        'Mean Return' : "{:.2%}"
    })

    portfolio_plot = portfolio_plot.set_table_styles(
        [{
            'selector': 'table',
            'props': [('width', '100%'), ('border-collapse', 'collapse')],
        },
        {
            'selector': 'td, th',  
            'props': [('text-align', 'center')
        ],
    }
    ]).set_table_attributes('style="width: 100%; border-collapse: collapse;"').to_html(escape=False, index=False)

    # Streamlit title
    st.title("Portfolio 🃏")

    st.markdown(
        f"""
        <div style="overflow-x: auto; width: 100%;">
            {portfolio_plot}
        </div>
        """,
        unsafe_allow_html=True,
    )

else:
    st.write("Adjust the settings in the sidebar and click 'Run' to see the results.")
