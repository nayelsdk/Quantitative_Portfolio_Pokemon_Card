import pandas as pd
import numpy as np
from typing import Dict
from dataclasses import dataclass
from UsefulFunctionsForModels import select_mixed_cards, calculate_covariance_matrix, get_dataframe_cards_matrix
from scipy.optimize import minimize
@dataclass
class SigmoidParameters:
    MAX_K: float = 1
    MIN_K: float = 0.1
    
    MAX_X0: float = 300
    MIN_X0: float = 10

class MarkowitzOptimizer:
    def __init__(self, 
                 amount_to_invest: float, 
                 critical_sales_threshold: float, 
                 sales_volume_sensitivity: float,
                dataframe_cards_info: pd.DataFrame = get_dataframe_cards_matrix()):
        """
        Initialize the Markowitz Optimizer
        
        Args:
            amount_to_invest: Total investment amount
            dataframe_cards_info: DataFrame containing card information
            critical_sales_threshold: Threshold for sales (x0)
            sales_volume_sensitivity: Sensitivity parameter (k)
        """
        self.amount_to_invest = amount_to_invest
        self.df = dataframe_cards_info[['card_id', 'last_price', 'mean_return', 'Quantity Sold', 'Card Info']].copy()        
        self.critical_sales_threshold = critical_sales_threshold
        self.sales_volume_sensitivity = sales_volume_sensitivity
        self.params = SigmoidParameters()
    
    @staticmethod
    def sigmoid(x: np.ndarray, x0: float, k: float) -> np.ndarray:
        """Calculate sigmoid function values"""
        return 1 / (1 + np.exp(-k * (x - x0)))
    
    def calculate_parameters(self) -> Dict[str, float]:
        """Calculate k and x0 parameters based on sensitivity"""
        k = (self.params.MAX_K - self.params.MIN_K) * self.sales_volume_sensitivity + self.params.MIN_K
        x0 = (self.params.MAX_X0 - self.params.MIN_X0) * self.critical_sales_threshold + self.params.MIN_X0
        return {"k": k, "x0": x0}
    
    def add_fiability_metrics(self) -> pd.DataFrame:
        """Add fiability metrics to the dataframe"""
        params = self.calculate_parameters()
        
        self.df['Fiability'] = self.sigmoid(self.df['Quantity Sold'].values, params['x0'], params['k'])
        self.df['Fiability']=round(self.df['Fiability'],3)
        self.df['Return x Fiability'] = round(self.df['Fiability'] * self.df['mean_return'],3)
        return self.df


    def get_optimized_return_mean_matrix_fiability(self, threshold=0.01, ratio=0.5, N=30):
        """
        Filter the DataFrame according to the given criterias and limits the dataframe with N to reduce time complexity of the Markowitz model
        """
        self.df=self.add_fiability_metrics()
        filtered_df = self.df[
            (self.df['Return x Fiability'] > threshold) & 
            (self.df['last_price'] < ratio * self.amount_to_invest)
        ]
        
        if len(filtered_df) > N:
            filtered_df = select_mixed_cards(filtered_df, N)
        return filtered_df


    def objective_weights(self, weights):
        filtered_df = self.get_optimized_return_mean_matrix_fiability()
        covariance_filtered_cards = calculate_covariance_matrix(filtered_df)
        return np.dot(weights.T, np.dot(covariance_filtered_cards, weights))
    
    def set_constraints(self):
        filtered_df = self.get_optimized_return_mean_matrix_fiability()
        mean_matrix = filtered_df["Return x Fiability"].values
        n_cards = len(mean_matrix)
                
        constraints = [
            {'type': 'eq', 'fun': lambda x: np.sum(x) - 1}
        ]
        
        bounds = tuple((0, 1) for _ in range(n_cards))
        return constraints, bounds
    
    def optimize_portfolio(self):
        filtered_df = self.get_optimized_return_mean_matrix_fiability()
        n_cards = len(filtered_df)
        
        if n_cards == 0:
            raise ValueError("No cards correspond to the filter criterias")
        
        constraints, bounds = self.set_constraints()
        initial_weights = np.array([1/n_cards] * n_cards)
        
        result = minimize(
            self.objective_weights, 
            initial_weights, 
            method='SLSQP', 
            bounds=bounds, 
            constraints=constraints
        )
        
        
        return result.x, filtered_df

    def optimize_cards_sell(self):
        df = self.get_optimized_return_mean_matrix_fiability()
        prices = df["last_price"].values
        weights, _ = self.optimize_portfolio()
        
        sorted_indices = np.argsort(weights)[::-1]
        
        total_investment = 0
        selected_indices = []
        
        for idx in sorted_indices:
            if total_investment + prices[idx] <= self.amount_to_invest:
                total_investment += prices[idx]
                selected_indices.append(idx)
            else:
                if abs(self.amount_to_invest - (total_investment + prices[idx])) < abs(self.amount_to_invest - total_investment):
                    total_investment += prices[idx]
                    selected_indices.append(idx)
                break
        
        binary_selection = np.zeros(len(weights))
        binary_selection[selected_indices] = 1
        mean_return= np.mean(df.iloc[selected_indices]["Return x Fiability"])
        
        return round(total_investment,2),  round(mean_return,3), df.iloc[selected_indices]
    
    def get_streamlit_database_markowitz(self, path_database="datas/pokemon_cards.csv"):
        pokemon_cards_df=pd.read_csv(path_database)
        total_investment, mean_return, df = self.optimize_cards_sell()
        df['base_id'] = df['card_id'].str.split('_').str[0]
        
        pokemon_info = pokemon_cards_df[['id', 'name', 'rarity', 'collection', 'release_date', 'images_url']]
        
        result_df = pd.merge(
            df[['base_id', 'last_price',"Fiability", "Return x Fiability", "Card Info"]],
            pokemon_info,
            left_on='base_id',
            right_on='id',
            how='left'
        )
        
        return total_investment, mean_return, result_df[['id', 'name', 'rarity', 'last_price',"Fiability", "Return x Fiability", 'collection', 'release_date', 'images_url', "Card Info"]]

            