#!/usr/bin/env python3
"""
run_twsca_analysis.py
Performs Time-Warped Spectral Correlation Analysis (TWSCA) on stock data.

This script implements the Time-Warped Spectral Correlation Analysis
technique using the official twsca package.
"""

import os
import sys
import numpy as np
import pandas as pd
import argparse
from pathlib import Path
from datetime import datetime, timedelta
import matplotlib.pyplot as plt

def load_stock_data(data_dir, tickers):
    """
    Load stock data for specified tickers from CSV files.
    
    Args:
        data_dir: Directory containing CSV files
        tickers: List of stock tickers to load
    
    Returns:
        Dict of DataFrames with ticker as key
    """
    data_frames = {}
    for ticker in tickers:
        csv_path = os.path.join(data_dir, f"{ticker}.csv")
        if os.path.exists(csv_path):
            try:
                # Parse directly - yfinance already creates proper CSV format
                df = pd.read_csv(csv_path, index_col=0, parse_dates=True)
                data_frames[ticker] = df
                print(f"Loaded {len(df)} rows for {ticker}")
            except Exception as e:
                print(f"Error loading data for {ticker}: {e}")
        else:
            print(f"Data file not found: {csv_path}")
    
    return data_frames

def perform_twsca_analysis(data_frames, main_ticker, comparison_tickers, 
                          window=30, output_dir='output'):
    """
    Perform Time-Warped Spectral Correlation Analysis using the official twsca package.
    
    Args:
        data_frames: Dict of DataFrames with ticker as key
        main_ticker: Main ticker to analyze (e.g., 'GME')
        comparison_tickers: List of tickers to compare against
        window: Rolling window size (in trading days)
        output_dir: Directory to save results
    
    Returns:
        Dict containing analysis results
    """
    # Import the official twsca package
    try:
        import twsca
    except ImportError:
        print("Installing official twsca package...")
        os.system("pip install twsca")
        import twsca
    
    # Print package information
    try:
        version = getattr(twsca, '__version__', 'unknown')
        print(f"Using twsca package version: {version}")
    except Exception:
        print("Using twsca package (version unknown)")
    
    # Print available attributes and methods to understand the API
    print("Available functions in twsca module:", [attr for attr in dir(twsca) if not attr.startswith('_')])
    
    results = {'correlation': {}, 'dtw': {}}
    
    # Get main stock data
    if main_ticker not in data_frames:
        print(f"Main ticker {main_ticker} not found in data")
        return results
    
    main_stock = data_frames[main_ticker]
    results['main_stock'] = main_stock
    
    # Extract price series for analysis
    main_prices = main_stock['Close']
    
    # Run TWSCA for each comparison ticker
    for ticker in comparison_tickers:
        if ticker not in data_frames:
            print(f"Comparison ticker {ticker} not found in data")
            continue
        
        print(f"Running TWSCA analysis for {main_ticker} vs {ticker}")
        comparison_prices = data_frames[ticker]['Close']
        
        # Align both series to common dates
        common_dates = main_prices.index.intersection(comparison_prices.index)
        if len(common_dates) < window:
            print(f"Not enough common dates for {ticker}")
            continue
            
        aligned_main = main_prices.loc[common_dates]
        aligned_comp = comparison_prices.loc[common_dates]
        
        # Run the analysis using the compute_twsca function
        try:
            # First, smooth the series using LLT filter
            smoothed_main = twsca.llt_filter(aligned_main.values)
            smoothed_comp = twsca.llt_filter(aligned_comp.values)
            
            # Normalize the series
            normalized_main = twsca.normalize_series(smoothed_main)
            normalized_comp = twsca.normalize_series(smoothed_comp)
            
            # Compute TWSCA analysis - use the appropriate function
            results_dict = twsca.compute_twsca(
                normalized_main, normalized_comp, 
                window_size=window
            )
            
            # Extract results
            correlations = results_dict.get('correlations', [])
            distances = results_dict.get('distances', [])
            
            # If results are empty, try directly with spectral_correlation and dtw_distance
            if not correlations or not distances:
                print("  Using lower-level functions for analysis")
                
                # Manual computation using window-based approach
                corr_values = []
                dtw_values = []
                
                for i in range(window, len(normalized_main)):
                    # Get window segments
                    segment1 = normalized_main[i-window:i]
                    segment2 = normalized_comp[i-window:i]
                    
                    # Calculate spectral correlation
                    corr = twsca.spectral_correlation(segment1, segment2)
                    corr_values.append(corr)
                    
                    # Calculate DTW distance
                    dist = twsca.dtw_distance(segment1, segment2)
                    # Extract just the distance value, not the warping path
                    # The result may be a tuple with (distance, path)
                    if isinstance(dist, tuple) and len(dist) > 0:
                        dist_value = float(dist[0])  # Extract just the distance value
                    else:
                        dist_value = float(dist)  # If it's already a scalar
                    dtw_values.append(dist_value)
                
                correlations = corr_values
                distances = dtw_values
            
            # Create DataFrames with results
            result_dates = common_dates[window:]
            
            # Make sure we have the right number of dates
            if len(result_dates) != len(correlations):
                # Trim to match the shorter length
                min_len = min(len(result_dates), len(correlations))
                result_dates = result_dates[:min_len]
                correlations = correlations[:min_len]
                distances = distances[:min_len]
            
            corr_df = pd.DataFrame({'correlation': correlations}, index=result_dates)
            dtw_df = pd.DataFrame({'dtw_distance': distances}, index=result_dates)
            
            results['correlation'][ticker] = corr_df
            results['dtw'][ticker] = dtw_df
            
            print(f"  Completed analysis with {len(correlations)} points")
            
        except Exception as e:
            print(f"Error in TWSCA analysis for {ticker}: {e}")
            continue
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Save results
    for ticker, corr_df in results['correlation'].items():
        corr_df.to_csv(os.path.join(output_dir, f"correlation_{main_ticker}_vs_{ticker}.csv"))
    
    for ticker, dtw_df in results['dtw'].items():
        dtw_df.to_csv(os.path.join(output_dir, f"dtw_{main_ticker}_vs_{ticker}.csv"))
    
    print(f"Analysis results saved to {output_dir}")
    return results

def main():
    """Main function to run TWSCA analysis."""
    parser = argparse.ArgumentParser(description="Run Time-Warped Spectral Correlation Analysis")
    parser.add_argument("--data-dir", type=str, default="data",
                        help="Directory containing CSV files")
    parser.add_argument("--output-dir", type=str, default="output",
                        help="Directory to save results")
    parser.add_argument("--main-ticker", type=str, default="GME",
                        help="Main ticker to analyze")
    parser.add_argument("--comparison-tickers", type=str, default="CHWY,AMC,KOSS,BB,NOK,SPY",
                        help="Comma-separated list of tickers to compare against")
    parser.add_argument("--window", type=int, default=30,
                        help="Rolling window size (in trading days)")
    
    args = parser.parse_args()
    
    # Parse arguments
    data_dir = args.data_dir
    output_dir = args.output_dir
    main_ticker = args.main_ticker
    comparison_tickers = [ticker.strip() for ticker in args.comparison_tickers.split(",")]
    window = args.window
    
    # Load data
    print(f"Loading data from {data_dir}")
    all_tickers = [main_ticker] + comparison_tickers
    data_frames = load_stock_data(data_dir, all_tickers)
    
    if not data_frames:
        print("No data loaded. Exiting.")
        return 1
    
    # Perform analysis
    print(f"Running TWSCA analysis with window={window}")
    results = perform_twsca_analysis(
        data_frames, main_ticker, comparison_tickers,
        window=window, output_dir=output_dir
    )
    
    print("Analysis complete.")
    return 0

if __name__ == "__main__":
    # Try to install required packages if they're missing
    try:
        import twsca
    except ImportError:
        print("Installing twsca package...")
        os.system("pip install twsca")
    
    sys.exit(main())
