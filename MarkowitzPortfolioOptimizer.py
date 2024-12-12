import numpy as np
import pulp as pl
import pandas as pd
import os

def get_file_paths(directory):
    file_paths = []
    for root, _, files in os.walk(directory):
        for file in files:
            file_paths.append(os.path.join(root, file))
    return file_paths


class MarkowitzPortfolioOptimizer:
    def __init__(self, returns, prices, cov_matrix, budget, num_cards, risk_aversion=1):
        self.returns = returns
        self.prices = prices
        self.cov_matrix = cov_matrix
        self.budget = budget
        self.num_cards = num_cards
        self.risk_aversion = risk_aversion
        self.n_assets = len(returns)
    
    def optimize(self):
        prob = pl.LpProblem("Portfolio_Optimization", pl.LpMinimize)
        
        # Variables binaires (0-1)
        x = pl.LpVariable.dicts("asset",
                              range(self.n_assets),
                              cat='Binary')
        
        # Fonction objectif (rendement uniquement)
        portfolio_returns = pl.lpSum([self.returns[i] * x[i] 
                                    for i in range(self.n_assets)])
        prob += -portfolio_returns
        
        # Contraintes budgétaires
        prob += pl.lpSum([self.prices[i] * x[i] 
                         for i in range(self.n_assets)]) <= 1.15 * self.budget
        prob += pl.lpSum([self.prices[i] * x[i] 
                         for i in range(self.n_assets)]) >= 0.85 * self.budget
        
        # Contrainte nombre de cartes
        prob += pl.lpSum([x[i] for i in range(self.n_assets)]) == self.num_cards
        
        prob.solve()
        
        # Calcul du montant réel investi
        weights = np.array([x[i].value() for i in range(self.n_assets)])
        invested_amount = np.sum(weights * self.prices)
        
        return weights, invested_amount
