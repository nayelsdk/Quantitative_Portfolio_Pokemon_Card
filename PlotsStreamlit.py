import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

def plot_analysis(portfolio):
    """Creates two interactive visualizations for Pokemon card portfolio analysis.

    Args:
        portfolio (DataFrame): DataFrame containing Pokemon card information


    Returns:
        tuple(plotly.graph_objects.Figure, plotly.graph_objects.Figure): Two interactive figures:
            
        Figure 1 - Portfolio Price Analysis:
            - Main panel: Portfolio value over time with Bollinger Bands
            - Sub panel: RSI (Relative Strength Index) with overbought/oversold levels
            
        Figure 2 - Returns and Volume Analysis:
            - Main panel: Logarithmic returns over time
            - Sub panel: Monthly average sales volume
            
        Both figures feature:
            - Time range selector (1M, 3M, 6M, ALL)
            - Interactive hover information
    """
    total_prices = pd.DataFrame()
    total_sales = pd.DataFrame()
    
    for _, card in portfolio.iterrows():
        price_data = card['Card Info']
        if total_prices.empty:
            total_prices['date'] = pd.to_datetime(price_data['start_date'])
            total_prices['total_price'] = price_data['price']
            total_sales['date'] = pd.to_datetime(price_data['start_date'])
            total_sales['quantity_sold'] = price_data['quantity_sold']
        else:
            total_prices['total_price'] += price_data['price']
            total_sales['quantity_sold'] += price_data['quantity_sold']
    
    # RSI
    delta = total_prices['total_price'].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(window=14).mean()
    avg_loss = loss.rolling(window=14).mean()
    rs = avg_gain / avg_loss
    total_prices['RSI'] = 100 - (100 / (1 + rs))
    
    window = 20
    rolling_mean = total_prices['total_price'].rolling(window=window).mean()
    rolling_std = total_prices['total_price'].rolling(window=window).std()
    total_prices['BB_upper'] = rolling_mean + (2 * rolling_std)
    total_prices['BB_lower'] = rolling_mean - (2 * rolling_std)
    
    total_prices['log_return'] = np.log(total_prices['total_price'] / total_prices['total_price'].shift(1))
    
    total_sales['month'] = total_sales['date'].dt.to_period('M')
    monthly_avg_sales = total_sales.groupby('month')['quantity_sold'].mean().reset_index()
    monthly_avg_sales['month'] = monthly_avg_sales['month'].dt.to_timestamp()

    common_layout = dict(
        paper_bgcolor='rgb(13, 13, 13)',
        plot_bgcolor='rgb(13, 13, 13)',
        font=dict(family='Courier New', size=10, color='white'),
        height=700,
        showlegend=True,
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=0.98,
            xanchor='center',
            x=0.5,
            bgcolor='rgba(13, 13, 13, 0.8)',
            borderwidth=1,
            bordercolor='rgba(255, 255, 255, 0.3)'
        ),
        hovermode='x unified',
        margin=dict(t=80, l=60, r=60, b=50),
        title=dict(
            y=0.95,
            x=0.5,
            xanchor='center',
            yanchor='top',
            font=dict(family='Courier New', size=18, color='white')
        )
    )
    common_xaxis = dict(
        showgrid=True,
        gridwidth=0.3,
        gridcolor='rgba(255, 255, 255, 0.03)',
        zeroline=False,
        dtick="M1",
        tickformat="%b\n%Y",
        rangeselector=dict(
            buttons=list([
                dict(count=1, label="1M", step="month", stepmode="backward"),
                dict(count=3, label="3M", step="month", stepmode="backward"),
                dict(count=6, label="6M", step="month", stepmode="backward"),
                dict(step="all", label="ALL")
            ]),
            font=dict(color='white'),
            bgcolor='rgba(13, 13, 13, 0.8)'
        )
    )

    fig1 = make_subplots(rows=2, cols=1, shared_xaxes=True,
                        vertical_spacing=0.05,
                        row_heights=[0.7, 0.3])
    
    # Fig: Prix and RSI
    fig1.add_trace(
        go.Scatter(x=total_prices['date'], y=total_prices['total_price'],
                  name='Portfolio Value', line=dict(color='rgb(0, 183, 255)', width=2)),
        row=1, col=1
    )
    
    fig1.add_trace(
        go.Scatter(x=total_prices['date'], y=total_prices['BB_upper'],
                  name='BB Upper', line=dict(color='rgba(255, 255, 255, 0.2)', 
                  width=1, dash='dot')),
        row=1, col=1
    )
    
    fig1.add_trace(
        go.Scatter(x=total_prices['date'], y=total_prices['BB_lower'],
                  name='BB Lower', line=dict(color='rgba(255, 255, 255, 0.2)',
                  width=1, dash='dot'), fill='tonexty',
                  fillcolor='rgba(255, 255, 255, 0.05)'),
        row=1, col=1
    )
    
    fig1.add_trace(
        go.Scatter(x=total_prices['date'], y=total_prices['RSI'],
                  name='RSI', line=dict(color='rgb(255, 99, 71)', width=1.5)),
        row=2, col=1
    )
    
    # Fig 2: 
    fig2 = make_subplots(rows=2, cols=1, shared_xaxes=True,
                        vertical_spacing=0.05,
                        row_heights=[0.7, 0.3])
    
    fig2.add_trace(
        go.Scatter(x=total_prices['date'], y=total_prices['log_return'],
                  name='Log Return', line=dict(color='rgb(0, 183, 255)', width=2)),
        row=1, col=1
    )
    
    fig2.add_trace(
        go.Bar(x=monthly_avg_sales['month'], y=monthly_avg_sales['quantity_sold'],
               name='Volume', marker_color='rgba(255, 99, 71, 0.6)'),
        row=2, col=1
    )

    for fig in [fig1, fig2]:
        fig.update_layout(**common_layout)
        fig.update_xaxes(**common_xaxis)
        fig.update_yaxes(showgrid=True, gridwidth=0.3,
                        gridcolor='rgba(255, 255, 255, 0.03)',
                        zeroline=False)

    fig1.add_hline(y=70, line_dash="dash", line_color="red", opacity=0.5, row=2, col=1)
    fig1.add_hline(y=30, line_dash="dash", line_color="green", opacity=0.5, row=2, col=1)
    fig1.update_layout(
        title=dict(
            text='Portfolio Price Analysis 💵',
            **common_layout['title']
        )
    )
    fig2.update_layout(
        title=dict(
            text='Returns and Volume Analysis 📈',
            **common_layout['title']
        )
    )
    return fig1, fig2


def plot_pie(portfolio):
    """
    Args:
    portfolio (DataFrame): DataFrame containing Pokemon card information

Returns:
    plotly.graph_objects.Figure: Interactive donut chart showing:
        - Portfolio distribution by card value
        - Percentage allocation for each card
    """
    fig = go.Figure(data=[go.Pie(
        labels=portfolio['name'],
        values=portfolio['last_price'],
        hole=0.2,
        marker=dict(
            colors=['rgba(0, 183, 255, 0.8)', 
                   'rgba(255, 99, 71, 0.8)',
                   'rgba(50, 205, 50, 0.8)', 
                   'rgba(255, 215, 0, 0.8)',
                   'rgba(147, 112, 219, 0.8)',
                   'rgba(255, 165, 0, 0.8)',
                   'rgba(128, 0, 128, 0.8)',
                   'rgba(0, 128, 128, 0.8)']
        ),
        textinfo='label+percent',
        hovertemplate="<b>%{label}</b><br>" +
                     "Current Price : %{value:.2f}$<br>" +
                     "Mean Return : %{customdata:.1f}%<br>" +
                     "Rarity : %{text}<extra></extra>",
        customdata=round(portfolio['Return x Fiability']*100,3),
        text=portfolio['rarity']
    )])


    fig.update_layout(
        title={
            'text': 'Portfolio Distribution 📊',
            'y': 0.95,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': dict(family='Courier New', size=24, color='white'),
            'pad': dict(b=20) 
        },
        paper_bgcolor='rgb(13, 13, 13)',
        plot_bgcolor='rgb(13, 13, 13)',
        font=dict(family='Courier New', size=12, color='white'),
        height=600, 
        width=950, 
        showlegend=True,
        legend=dict(
            orientation='v',  
            yanchor='middle',
            y=0.5,
            xanchor='left',
            x=1.25,  
            bgcolor='rgba(13, 13, 13, 0.8)',
            borderwidth=1,
            bordercolor='rgba(255, 255, 255, 0.3)',
            font=dict(size=14) 
        ),
        margin=dict(t=100, l=10, r=300, b=20)  
    )

    return fig
