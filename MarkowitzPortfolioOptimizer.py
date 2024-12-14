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


def normalize_data(returns, covariance, reliability, prices):
    returns_norm = (returns - np.min(returns)) / (np.max(returns) - np.min(returns))
    
    cov_mean = np.mean(covariance)
    cov_std = np.std(covariance)
    cov_norm=(covariance - cov_mean) / cov_std
    
    return returns_norm, cov_norm, reliability, prices


