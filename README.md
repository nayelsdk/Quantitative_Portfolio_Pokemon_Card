# Pokémon Card Investment Portfolio 🃏

This project aims to create a robust investment portfolio for Pokémon cards by leveraging historical price trends and advanced financial modeling. The ultimate goal is to help investors make informed decisions about buying and selling Pokémon cards, maximizing returns while managing risk.

# 1. Data Extraction

- Scrape Pokémon card prices and historical sales data from TCGPlayer.

- Focus on the "Near Mint Comparison Prices" table to identify the most valuable card variants (e.g., Holofoil, Reverse Holofoil).
- Extract and organize price history data into structured CSV files.

Portfolio_Pokemon_Card/
│
├── data/
│   ├── raw/                 # Scraped raw data
│   └── processed/           # Cleaned datasets
│
├── src/
│   ├── scraping/           # Scraping scripts
│   ├── analysis/           # Financial models
│   └── visualization/      # Streamlit components
│
├── notebooks/              # Jupyter notebooks
├── requirements.txt        # Dependencies
└── README.md