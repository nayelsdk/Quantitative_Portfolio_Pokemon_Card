import numpy as np
import pandas as pd
import os
from UsefulFunctionsForModels import calculate_covariance_matrix

class MarkowitzOptimizer:
    def __init__(self, amount_to_invest, hope_return, dataframe_cards_info):
        self.amount_to_invest=amount_to_invest
        self.hope_return=hope_return
        self.dataframe_cards_info=dataframe_cards_info
    
            
    def get_optimized_return_mean_matrix_fiability(self, threshold=-0.05, ratio=0.4):
        filtered_df=self.dataframe_cards_info[(self.dataframe_cards_info["fiability_dot_return"] > threshold) & (self.dataframe_cards_info['last_price'] < ratio*self.amount_to_invest)]
        return filtered_df

    def get_covariance_matrix_filtered_cards(self):
        filtered_df=calculate_covariance_matrix(self)
        
        
    