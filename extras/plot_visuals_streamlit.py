# %% [markdown]
# # TWSCA GME Analysis - Visualizations
# 
# This notebook contains various visualizations for analyzing the GME data. We'll use the visualization functions defined in our `visualization.py` module to create insightful plots.

# %%
import sys
import os
# Remove sys.path manipulation as we import from installed package
# script_dir = os.path.dirname(os.path.abspath(__file__))
# project_root = os.path.dirname(script_dir) # This should be the main project root
# src_path = os.path.join(project_root, 'src')
# if src_path not in sys.path:
#     sys.path.insert(0, src_path) # Insert at the beginning for precedence

import pandas as pd
import numpy as np
import plotly.graph_objects as go
# Update import path for plotting module
from twsca.plotting import (
    setup_plotting_style,
    plot_time_series,
    plot_distribution,
    plot_correlation_matrix,
    plot_scatter_matrix,
    plot_volume_price
)

# Set up plotting style
setup_plotting_style()

# %% [markdown]
# ## Load and Prepare Data
# 
# First, let's load our processed data for visualization.

# %%
# Get the absolute path to the CSV file in the new extras/data_streamlit directory
extras_dir = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.join(extras_dir, 'data_streamlit', 'combined_weekly_2024_2025.csv')

# Load the weekly data
try:
    df = pd.read_csv(csv_path)
    # Convert date column to datetime
    df['date'] = pd.to_datetime(df['date']) # Assuming column name is 'date'
    print(f"Data loaded successfully from {csv_path}")
    # Display basic information about the dataset
    print(df.info())
    print('\nSummary Statistics:')
    print(df.describe())
except FileNotFoundError:
    print(f"Error: Data file not found at {csv_path}. Expected in extras/data_streamlit/")
    df = None # Ensure df is None if loading fails
except Exception as e:
    print(f"An error occurred loading data: {e}")
    df = None

# %% [markdown]
# ## Time Series Analysis
# 
# Let's analyze how GME price changes over time.

# %%
# Plot GME price over time
if df is not None:
    try:
        # Assuming price column is 'GME_Close' based on previous context
        fig_ts = plot_time_series(
            data=df,
            x_col='date', # Assuming date column name
            y_col='GME_Close', # Adjust if column name differs
            title='GME Price Over Time'
        )
        fig_ts.show()
    except KeyError as e:
        print(f"Error plotting time series: Missing column {e}")
else:
    print("Dataframe not loaded, skipping time series plot.")

# %% [markdown]
# ## Price Comparison Analysis
# 
# Compare GME price with other related stocks.

# %%
# Create a comparison plot
if df is not None:
    try:
        fig_comp = go.Figure()

        # Add GME price
        if 'GME_Close' in df.columns:
            fig_comp.add_trace(
                go.Scatter(
                    x=df['date'],
                    y=df['GME_Close'], # Adjust if column name differs
                    name='GME',
                    line=dict(color='red', width=2)
                )
            )
        else:
            print("Column 'GME_Close' not found for comparison plot.")

        # Add XRT (Retail ETF) for comparison
        if 'XRT_Close' in df.columns: # Adjust if column name differs
            fig_comp.add_trace(
                go.Scatter(
                    x=df['date'],
                    y=df['XRT_Close'], # Adjust if column name differs
                    name='XRT (Retail ETF)',
                    line=dict(color='blue', width=1)
                )
            )
        else:
            print("Column 'XRT_Close' not found for comparison plot.")

        # Add SPY (S&P 500) for market comparison
        if 'SPY_Close' in df.columns: # Adjust if column name differs
            fig_comp.add_trace(
                go.Scatter(
                    x=df['date'],
                    y=df['SPY_Close'], # Adjust if column name differs
                    name='SPY (S&P 500)',
                    line=dict(color='green', width=1)
                )
            )
        else:
            print("Column 'SPY_Close' not found for comparison plot.")

        # Update layout
        fig_comp.update_layout(
            title='GME vs XRT vs SPY Prices',
            xaxis_title='Date',
            yaxis_title='Price',
            hovermode='x unified'
        )
        fig_comp.show()

    except Exception as e:
        print(f"Error creating comparison plot: {e}")
else:
    print("Dataframe not loaded, skipping comparison plot.")

# %% [markdown]
# ## Distribution Analysis
# 
# Examine the distribution of GME returns.

# %%
# Plot GME return distribution
if df is not None:
    try:
        # Assuming return column is 'GME_Return'
        fig_dist = plot_distribution(
            data=df,
            column='GME_Return', # Adjust if column name differs
            title='GME Return Distribution'
        )
        fig_dist.show()
    except KeyError as e:
        print(f"Error plotting distribution: Missing column {e}")
else:
    print("Dataframe not loaded, skipping distribution plot.")

# %% [markdown]
# ## Correlation Analysis
# 
# Analyze relationships between returns of GME and other stocks.

# %%
# Create correlation matrix for returns
if df is not None:
    try:
        # Define columns for return correlation
        correlation_return_cols = ['GME_Return', 'XRT_Return', 'SPY_Return', 'KOSS_Return', 'AMC_Return', 'BB_Return', 'NOK_Return']
        # Filter to only include columns that exist in the dataframe
        available_cols = [col for col in correlation_return_cols if col in df.columns]

        if len(available_cols) > 1:
            fig_corr = plot_correlation_matrix(
                data=df,
                columns=available_cols
            )
            fig_corr.update_layout(title='Stock Return Correlation Matrix')
            fig_corr.show()
        else:
            print(f"Not enough available return columns for correlation: Found {available_cols}")

    except Exception as e:
        print(f"Error creating correlation plot: {e}")
else:
    print("Dataframe not loaded, skipping correlation plot.")

# %% [markdown]
# ## Scatter Plot Matrix
# 
# Visualize relationships between returns of GME and other key stocks.

# %%
# Create scatter plot matrix for returns
if df is not None:
    try:
        scatter_return_cols = ['GME_Return', 'XRT_Return', 'SPY_Return']
        available_cols = [col for col in scatter_return_cols if col in df.columns]

        if len(available_cols) > 1:
            fig_scatter = plot_scatter_matrix(
                data=df,
                columns=available_cols
            )
            fig_scatter.update_layout(title='Stock Return Scatter Matrix')
            fig_scatter.show()
        else:
            print(f"Not enough available return columns for scatter matrix: Found {available_cols}")
    except Exception as e:
        print(f"Error creating scatter matrix: {e}")
else:
    print("Dataframe not loaded, skipping scatter matrix plot.")

# %% [markdown]
# ## Custom Analysis: GME vs Retail Peers (Prices)
# 
# Compare GME price with other retail stocks.

# %%
# Create a comparison plot of GME and retail peers' prices
if df is not None:
    try:
        fig_peers = go.Figure()

        # Add GME price
        if 'GME_Close' in df.columns:
            fig_peers.add_trace(
                go.Scatter(
                    x=df['date'],
                    y=df['GME_Close'],
                    name='GME',
                    line=dict(color='red', width=2)
                )
            )
        else:
            print("Column 'GME_Close' not found for retail peers plot.")

        # Add other retail stocks if available (using Close prices)
        retail_peer_cols = ['BB_Close', 'KOSS_Close', 'AMC_Close', 'NOK_Close']
        for stock_col in retail_peer_cols:
            if stock_col in df.columns:
                stock_name = stock_col.replace('_Close', '') # Get ticker symbol
                fig_peers.add_trace(
                    go.Scatter(
                        x=df['date'],
                        y=df[stock_col],
                        name=stock_name,
                        line=dict(width=1)
                    )
                )
            else:
                print(f"Column '{stock_col}' not found for retail peers plot.")

        # Update layout
        fig_peers.update_layout(
            title='GME vs Retail Peers (Prices)',
            xaxis_title='Date',
            yaxis_title='Price',
            hovermode='x unified'
        )
        fig_peers.show()

    except Exception as e:
        print(f"Error creating retail peers plot: {e}")
else:
    print("Dataframe not loaded, skipping retail peers plot.")

# %% [markdown]
# ## Volume and Price Analysis

# %%
# Plot GME Volume and Price
if df is not None:
    try:
        fig_vol_price = plot_volume_price(df, 'date', 'GME_Close', 'GME_Volume')
        fig_vol_price.show()
    except KeyError as e:
        print(f"Error plotting volume/price: Missing column {e}")
else:
    print("Dataframe not loaded, skipping volume/price plot.") 