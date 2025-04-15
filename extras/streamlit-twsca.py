"""
TWSCA GME Analysis Dashboard
===========================

Purpose:
--------
This Streamlit application provides an interactive dashboard for analyzing GME stock data
using the TWSCA (Time-Windowed Stock Correlation Analysis) methodology. It visualizes
price movements, correlations, and market dynamics.

Features:
---------
- Interactive price charts
- Rolling correlation analysis
- Baton handoff analysis (identifying influential stocks)
- Entropy calculations
- Multiple visualization options

How to Use:
----------
1. Installation:
   - Run `./install.sh` (macOS/Linux) or `install.bat` (Windows)
   - This will set up all dependencies and start the app

2. Using the Dashboard:
   - Adjust the correlation window using the sidebar slider
   - View different visualizations in the tabs
   - Interact with plots (zoom, pan, hover for details)
   - Download data using the export buttons

FAQ:
----
Q: Why is the data not loading?
A: Make sure you've run the data download script first:
   python twsca_gme_analysis/src/data/data_download.py --source yahoo

Q: How do I interpret the correlation matrix?
A: Values closer to 1 indicate strong positive correlation,
   closer to -1 indicate strong negative correlation,
   and closer to 0 indicate weak correlation.

Q: What is the baton handoff analysis?
A: It identifies which stock has the strongest correlation
   with GME in each time window, showing how influence
   shifts between different stocks over time.

Q: How do I export the data?
A: Use the download buttons below each visualization
   to export the data in CSV format.

Troubleshooting:
---------------
1. If the app doesn't start:
   - Make sure all dependencies are installed
   - Check if the data files exist in the correct location
   - Verify Python version (3.7+ required)

2. If visualizations are slow:
   - Install the watchdog module: pip install watchdog
   - Reduce the correlation window size
   - Use fewer stocks in the analysis

3. If data is missing:
   - Run the data download script
   - Check file permissions
   - Verify the data directory structure

For more information, see the README.md file.
"""

# Script: Export TWSCA Influence Series (Baton, Entropy, Correlation)

import streamlit as st
# IMPORTANT: Set page config must be the first Streamlit command
st.set_page_config(page_title="TWSCA GME Analysis", layout="wide")

import pandas as pd
import numpy as np
from scipy.stats import entropy
from scipy.signal import savgol_filter
import plotly.express as px
import os
# Import functions from the src directory
import sys
# Get the project root directory (assuming extras is one level down)
# project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# src_path = os.path.join(project_root, 'src')
# if src_path not in sys.path:
#     sys.path.append(src_path)

# Import from the installed twsca package
try:
    # Update import path to reflect the installed package name
    from twsca.plotting import (
        setup_plotting_style,
        plot_time_series,
        plot_distribution,
        plot_correlation_matrix,
        plot_scatter_matrix,
        plot_volume_price
    )
except ImportError:
    st.error("Could not import functions from the 'twsca' package. Make sure it is installed (`pip install twsca`).")
    # Define dummy functions if import fails to prevent crashing
    # Need to import go for dummy functions
    import plotly.graph_objects as go
    def plot_time_series(*args, **kwargs):
        return go.Figure()
    def plot_distribution(*args, **kwargs):
        return go.Figure()
    def plot_correlation_matrix(*args, **kwargs):
        return go.Figure()
    def plot_scatter_matrix(*args, **kwargs):
        return go.Figure()
    def plot_volume_price(*args, **kwargs):
        return go.Figure()
    def setup_plotting_style():
        pass

setup_plotting_style() # Apply plotting style
st.title("TWSCA GME Analysis Dashboard")

# Define smoothing functions
def simple_llt(series, window=5):
    s = pd.Series(series)
    med = s.rolling(window=window, center=True).median()
    smoothed = med.rolling(window=window, center=True).mean()
    return smoothed.bfill().ffill().values

def smooth_ema(series, span=5):
    return pd.Series(series).ewm(span=span, adjust=False).mean().values

def smooth_savgol(series, window=7, order=2):
    return savgol_filter(series, window_length=window, polyorder=order)

# Load data
@st.cache_data
def load_data():
    # Update path to the data directory inside extras/
    # Go up one level from this script's dir to get to extras/
    extras_dir = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(extras_dir, "data_streamlit", "combined_weekly_2024_2025.csv")
    if not os.path.exists(data_path):
        st.error(f"""
        Data file not found: {data_path}
        
        Please run the data download script first:
        ```
        python download_all_data.py
        ```
        
        This will download the required data files from Yahoo Finance.
        """)
        return None
    
    try:
        df = pd.read_csv(data_path)
        df["date"] = pd.to_datetime(df["date"])
        return df
    except Exception as e:
        st.error(f"""
        Error loading data from {data_path}: {str(e)}
        
        Please try running the data download script again:
        ```
        python download_all_data.py
        ```
        """)
        return None

df_multi = load_data()

if df_multi is None:
    st.error("Data loading failed. Please check the instructions above.")
    st.stop()

# Get stock columns and apply smoothing
stock_cols = [col for col in df_multi.columns if col != "date"]
smoothed = {}

# Apply smoothing to each stock column (using SavGol filter by default)
for col in stock_cols:
    series = df_multi[col].values
    if len(series) >= 7:
        smoothed[col] = smooth_savgol(series)
    else:
        smoothed[col] = series  # fallback to raw

# Sidebar controls
st.sidebar.header("Analysis Parameters")
window = st.sidebar.slider("Correlation Window (weeks)", min_value=2, max_value=12, value=6, key="corr_window")

# Data Validation and Setup
if df_multi is None:
    st.warning("Data could not be loaded. Cannot proceed with analysis.")
    st.stop()

required_cols = ['date', 'GME_Close', 'GME_Return', 'GME_Volume', 'XRT_Return', 'SPY_Return']
missing_cols = [col for col in required_cols if col not in df_multi.columns]

if missing_cols:
    st.error(f"Missing required columns in the data file: {missing_cols}. Please check extras/data_streamlit/combined_weekly_2024_2025.csv")
    st.stop()

# Separate columns for TWSCA analysis (returns) and basic plotting (prices, volume)
price_vol_cols = [col for col in df_multi.columns if col == 'date' or col.endswith('_Close') or col.endswith('_Volume')]
df_prices_vol = df_multi[price_vol_cols]

return_cols = [col for col in df_multi.columns if col == 'date' or col.endswith('_Return')]
df_returns = df_multi[return_cols]

# Get stock tickers from return columns
stock_tickers_return = [col.replace('_Return', '') for col in return_cols if col != 'date']

# Apply smoothing (optional, can be added later if needed for TWSCA)
# smoothed = {}
# for col in stock_tickers_return:
#     series = df_returns[f"{col}_Return"].dropna().values
#     if len(series) >= 7:
#         smoothed[col] = smooth_savgol(series)
#     else:
#         smoothed[col] = series

# --- TWSCA Calculation --- (Based on original logic but using return columns)
st.sidebar.header("TWSCA Calculations")

if "GME_Return" not in df_returns.columns:
    st.error("GME_Return column not found. Cannot perform TWSCA analysis.")
    st.stop()

other_return_cols = [col for col in df_returns.columns if col != "date" and col != "GME_Return"]
dates = df_returns["date"]

correlations = []
for i in range(len(df_returns) - window + 1):
    window_df_returns = df_returns.iloc[i:i+window].drop(columns=["date"])
    date = dates.iloc[i + window - 1]

    # Ensure GME_Return exists in the window
    if 'GME_Return' not in window_df_returns.columns:
        continue

    corr_row = {}
    gme_return_window = window_df_returns["GME_Return"].dropna()

    for ticker_col in other_return_cols:
        if ticker_col in window_df_returns.columns:
            other_return_window = window_df_returns[ticker_col].dropna()
            # Ensure enough overlapping data points for correlation
            common_index = gme_return_window.index.intersection(other_return_window.index)
            if len(common_index) >= 2: # Need at least 2 points for correlation
                corr = np.corrcoef(gme_return_window[common_index], other_return_window[common_index])[0, 1]
                # Use ticker name (without _Return) as key
                corr_row[ticker_col.replace('_Return', '')] = corr
            else:
                corr_row[ticker_col.replace('_Return', '')] = np.nan # Not enough data
        else:
            corr_row[ticker_col.replace('_Return', '')] = np.nan # Column not present in window (shouldn't happen with iloc)

    corr_row["Week Ending"] = date
    if len(corr_row) > 1: # Only add if correlations were calculated
        correlations.append(corr_row)

rolling_corr_df = pd.DataFrame(correlations)
if not rolling_corr_df.empty:
    rolling_corr_df = rolling_corr_df.set_index("Week Ending")
else:
    st.warning("Could not calculate rolling correlations. Check data and window size.")
    rolling_corr_df = pd.DataFrame() # Ensure it's a DataFrame

# Baton Handoff Analysis
baton_df = pd.DataFrame()
if not rolling_corr_df.empty and len(rolling_corr_df.columns) > 0:
    baton_df["Week Ending"] = rolling_corr_df.index
    abs_corr_df = rolling_corr_df.abs()
    top_influencers = []
    actual_correlations = []

    for idx, row in abs_corr_df.iterrows():
        # Drop NaN before finding max
        valid_row = row.dropna()
        if not valid_row.empty:
            max_corr_ticker = valid_row.idxmax()
            top_influencers.append(max_corr_ticker)
            actual_corr = rolling_corr_df.loc[idx, max_corr_ticker]
            actual_correlations.append(actual_corr)
        else:
            top_influencers.append("N/A")
            actual_correlations.append(np.nan)

    baton_df["Top Influencer"] = top_influencers
    baton_df["Correlation"] = actual_correlations
    baton_df = baton_df.set_index("Week Ending")
else:
     st.warning("Rolling correlation data is empty, skipping Baton Handoff.")
     baton_df = pd.DataFrame(columns=["Top Influencer", "Correlation"])

# Entropy Calculation
entropy_df = pd.DataFrame(index=rolling_corr_df.index)
if not rolling_corr_df.empty and len(rolling_corr_df.columns) > 0:
    abs_corr = rolling_corr_df.abs().fillna(0) # Fill NaNs with 0 for entropy calculation
    valid_rows = abs_corr.sum(axis=1) > 1e-9 # Check for rows with non-negligible correlations
    abs_corr_valid = abs_corr[valid_rows]

    if not abs_corr_valid.empty:
        norm_corr = abs_corr_valid.div(abs_corr_valid.sum(axis=1), axis=0).fillna(0)
        # Ensure probabilities sum to 1 (or very close)
        norm_corr = norm_corr.apply(lambda row: row / row.sum() if row.sum() > 1e-9 else row, axis=1)
        entropy_series = norm_corr.apply(lambda row: entropy(row[row > 1e-9].values, base=2), axis=1) # Use only non-zero probabilities
        entropy_df["Entropy"] = entropy_series
else:
    st.warning("Rolling correlation data is empty, skipping Entropy calculation.")
    entropy_df = pd.DataFrame(columns=["Entropy"])


# --- Visualizations --- Use imported functions
st.header("GME Analysis")

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["Time Series", "Distribution", "Price/Volume", "Correlation Matrix", "Scatter Matrix", "TWSCA Analysis"])

with tab1:
    st.subheader("GME Price Over Time")
    fig_ts = plot_time_series(df_prices_vol, 'date', 'GME_Close', title="GME Price")
    st.plotly_chart(fig_ts, use_container_width=True, key="gme_price_timeseries")

with tab2:
    st.subheader("GME Return Distribution")
    fig_dist = plot_distribution(df_returns, 'GME_Return', title="Distribution of GME Weekly Returns")
    st.plotly_chart(fig_dist, use_container_width=True, key="gme_return_distribution")

with tab3:
    st.subheader("GME Price and Volume")
    fig_pv = plot_volume_price(df_prices_vol, 'date', 'GME_Close', 'GME_Volume')
    st.plotly_chart(fig_pv, use_container_width=True, key="gme_price_volume")

with tab4:
    st.subheader("Stock Return Correlation Matrix")
    # Select return columns for correlation plot
    corr_plot_cols = [col for col in df_returns.columns if col != 'date']
    if len(corr_plot_cols) > 1:
        fig_corr = plot_correlation_matrix(df_returns, corr_plot_cols)
        st.plotly_chart(fig_corr, use_container_width=True, key="correlation_matrix")
    else:
        st.warning("Not enough return columns available for correlation matrix plot.")

with tab5:
    st.subheader("Stock Return Scatter Matrix")
    # Select return columns for scatter plot
    scatter_plot_cols = ['GME_Return', 'XRT_Return', 'SPY_Return']
    available_scatter_cols = [col for col in scatter_plot_cols if col in df_returns.columns]
    if len(available_scatter_cols) > 1:
        fig_scatter = plot_scatter_matrix(df_returns, available_scatter_cols)
        st.plotly_chart(fig_scatter, use_container_width=True, key="scatter_matrix")
    else:
        st.warning("Not enough return columns (GME, XRT, SPY) available for scatter matrix plot.")

with tab6:
    st.header("TWSCA: Time-Windowed Stock Correlation Analysis")
    st.subheader("Top Influencer Analysis")
    if not baton_df.empty:
        # Ensure 'Top Influencer' column exists before plotting
        if "Top Influencer" in baton_df.columns:
             # Map influencers to colors consistently
            influencers = baton_df["Top Influencer"].unique()
            color_map = {inf: px.colors.qualitative.Plotly[i % len(px.colors.qualitative.Plotly)] for i, inf in enumerate(influencers)}

            fig_baton = px.scatter(baton_df.reset_index(), x="Week Ending", y="Correlation", 
                                   color="Top Influencer", 
                                   color_discrete_map=color_map,
                                   title="Top Influencer Correlation Over Time (Based on Returns)",
                                   hover_data=["Top Influencer", "Correlation"])
            fig_baton.update_layout(legend_title_text='Top Influencer')
            st.plotly_chart(fig_baton, use_container_width=True, key="top_influencer_scatter")
        else:
            st.warning("'Top Influencer' column not found in baton_df. Cannot plot.")
    else:
        st.info("No Baton Handoff data to display.")

    st.subheader("Correlation Entropy")
    if not entropy_df.empty:
        fig_entropy = px.line(entropy_df.reset_index(), x="Week Ending", y="Entropy", 
                               title="Correlation Distribution Entropy Over Time (Based on Returns)")
        st.plotly_chart(fig_entropy, use_container_width=True, key="correlation_entropy")
    else:
        st.info("No Entropy data to display.")

# Data tables for TWSCA results
st.header("TWSCA Data Tables")
twsca_tabs = st.tabs(["Rolling Correlations", "Top Influencers", "Entropy"])

with twsca_tabs[0]:
    st.dataframe(rolling_corr_df)
with twsca_tabs[1]:
    st.dataframe(baton_df)
with twsca_tabs[2]:
    st.dataframe(entropy_df)

# Add download buttons for TWSCA data
st.sidebar.header("Download TWSCA Data")

if not rolling_corr_df.empty:
    csv_corr = rolling_corr_df.to_csv().encode('utf-8')
    st.sidebar.download_button(
        label="Download Rolling Correlations (CSV)",
        data=csv_corr,
        file_name='rolling_correlations.csv',
        mime='text/csv',
    )

if not baton_df.empty:
    csv_baton = baton_df.to_csv().encode('utf-8')
    st.sidebar.download_button(
        label="Download Top Influencers (CSV)",
        data=csv_baton,
        file_name='top_influencers.csv',
        mime='text/csv',
    )

if not entropy_df.empty:
    csv_entropy = entropy_df.to_csv().encode('utf-8')
    st.sidebar.download_button(
        label="Download Entropy (CSV)",
        data=csv_entropy,
        file_name='entropy.csv',
        mime='text/csv',
    )

# Display original raw data (optional)
st.header("Original Input Data")
st.dataframe(df_multi)

csv_original = df_multi.to_csv(index=False).encode('utf-8')
st.download_button(
    label="Download Original Data (CSV)",
    data=csv_original,
    file_name='combined_weekly_input.csv',
    mime='text/csv',
)
