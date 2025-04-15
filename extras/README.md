# Extras - Streamlit Dashboard Components

This directory contains the components for the Streamlit dashboard application that visualizes GameStop (GME) and related stocks using TWSCA (Time-Warped Spectral Correlation Analysis).

## Contents

- `streamlit-twsca.py` - The main Streamlit application that provides an interactive dashboard for analyzing GME stock data
- `plot_visuals_streamlit.py` - Helper script containing visualization functions for the dashboard
- `download_data.py` - Script to download fresh stock data for the dashboard
- `data_streamlit/` - Directory containing the dataset used by the dashboard

## Features

The Streamlit dashboard provides:

- Interactive price charts for GME and related stocks
- Rolling correlation analysis between GME and other stocks
- Time-series analysis with various smoothing options
- Correlation matrices and heatmaps
- Distribution analysis of stock returns

## Usage

To run the Streamlit dashboard:

```bash
cd /path/to/streamlit-twsca
streamlit run extras/streamlit-twsca.py
```

To download fresh data:

```bash
python extras/download_data.py
```

## Data

The dashboard uses weekly stock data for:
- GameStop (GME)
- SPDR S&P Retail ETF (XRT)
- S&P 500 ETF (SPY)
- AMC Entertainment (AMC)
- Koss Corporation (KOSS)
- BlackBerry (BB)
- Nokia (NOK)

Data is stored in CSV format with columns for Close prices, Volume, and Returns for each stock. 