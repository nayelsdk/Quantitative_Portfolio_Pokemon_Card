import os
import pandas as pd
import numpy as np
from UsefulFunctionsForModels import calculate_covariance_matrix
from scipy.optimize import minimize

path='price_history/high_sales'
class MarkowitzOptimizer:
    def __init__(self, amount_to_invest, dataframe_cards_info):
        self.amount_to_invest = amount_to_invest
        self.dataframe_cards_info = dataframe_cards_info
    
    def get_optimized_return_mean_matrix_fiability(self, threshold=0.01, ratio=0.40):
        filtered_df = self.dataframe_cards_info[
            (self.dataframe_cards_info["fiability_dot_return"] > threshold) & 
            (self.dataframe_cards_info['last_price'] < ratio * self.amount_to_invest)
        ]
        return filtered_df

    def objective_weights(self, weights):
        filtered_df = self.get_optimized_return_mean_matrix_fiability()
        covariance_filtered_cards = calculate_covariance_matrix(filtered_df,path)
        return np.dot(weights.T, np.dot(covariance_filtered_cards, weights))
    
    def set_constraints(self):
        filtered_df = self.get_optimized_return_mean_matrix_fiability()
        mean_matrix = filtered_df["fiability_dot_return"].values  # Convertir en array numpy
        n_cards = len(mean_matrix)
                
        constraints = [
            {'type': 'eq', 'fun': lambda x: np.sum(x) - 1}
            #{'type': 'ineq', 'fun': lambda x: np.dot(x, mean_matrix) - 0.9 * self.hope_return},  
            #{'type': 'ineq', 'fun': lambda x: 1.1 * self.hope_return - np.dot(x, mean_matrix)}  
        ]
        
        bounds = tuple((0, 1) for _ in range(n_cards))
        return constraints, bounds
    
    def optimize_portfolio(self):
        filtered_df = self.get_optimized_return_mean_matrix_fiability()
        n_cards = len(filtered_df)
        
        if n_cards == 0:
            raise ValueError("Aucune carte ne correspond aux critères de filtrage")
        
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
        mean_return= np.mean(df.iloc[selected_indices]["fiability_dot_return"])
        
        return total_investment,  mean_return, df.iloc[selected_indices]