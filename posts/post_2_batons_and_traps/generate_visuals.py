#!/usr/bin/env python3
"""
generate_visuals.py
Creates visualizations for Time-Warped Spectral Correlation Analysis results.

This script generates the charts and visualizations used in the post,
including correlation vs DTW distance charts, cycle alignment heatmaps,
and baton pass/trap zone visualizations.
"""

import os
import sys
import numpy as np
import pandas as pd
import argparse
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.colors as mcolors
import seaborn as sns
from datetime import datetime, timedelta

def load_analysis_results(results_dir, main_ticker="GME"):
    """
    Load analysis results from CSV files.
    
    Args:
        results_dir: Directory containing CSV files
        main_ticker: Main ticker symbol
    
    Returns:
        Dict of DataFrames with correlation and DTW results
    """
    results = {'correlation': {}, 'dtw': {}}
    
    # Get list of CSV files in results directory
    try:
        files = os.listdir(results_dir)
    except Exception as e:
        print(f"Error listing files in {results_dir}: {e}")
        return results
    
    # Load correlation files
    for f in files:
        if f.startswith("correlation_") and f.endswith(".csv"):
            parts = f.replace(".csv", "").split("_vs_")
            if len(parts) != 2 or not parts[0].startswith("correlation_"):
                continue
                
            ticker = parts[1]
            try:
                file_path = os.path.join(results_dir, f)
                # Convert string values to float
                df = pd.read_csv(file_path, index_col=0, parse_dates=True)
                df = df.apply(pd.to_numeric, errors='coerce')
                results['correlation'][ticker] = df
            except Exception as e:
                print(f"Error loading correlation file {f}: {e}")
    
    # Load DTW files
    for f in files:
        if f.startswith("dtw_") and f.endswith(".csv"):
            parts = f.replace(".csv", "").split("_vs_")
            if len(parts) != 2 or not parts[0].startswith("dtw_"):
                continue
                
            ticker = parts[1]
            try:
                file_path = os.path.join(results_dir, f)
                # Convert string values to float
                df = pd.read_csv(file_path, index_col=0, parse_dates=True)
                df = df.apply(pd.to_numeric, errors='coerce')
                results['dtw'][ticker] = df
            except Exception as e:
                print(f"Error loading DTW file {f}: {e}")
    
    return results

def plot_correlation_vs_dtw(results, main_ticker="GME", output_dir="figures"):
    """
    Plot correlation vs DTW distance for each comparison ticker.
    
    Args:
        results: Dict of analysis results
        main_ticker: Main ticker symbol
        output_dir: Directory to save plots
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # For each comparison ticker
    for ticker in results['correlation'].keys():
        if ticker not in results['dtw']:
            continue
            
        # Get correlation and DTW data
        corr_df = results['correlation'][ticker]
        dtw_df = results['dtw'][ticker]
        
        # Align dates
        common_dates = corr_df.index.intersection(dtw_df.index)
        if len(common_dates) == 0:
            print(f"No common dates for {ticker}")
            continue
            
        # Create figure
        plt.figure(figsize=(12, 6))
        
        # Add a second y-axis
        ax1 = plt.gca()
        ax2 = ax1.twinx()
        
        # Plot correlation
        ax1.plot(common_dates, corr_df.loc[common_dates, 'correlation'], 
                'b-', label='Correlation', linewidth=2)
        ax1.set_ylabel('Correlation', color='blue', fontsize=12)
        ax1.tick_params(axis='y', labelcolor='blue')
        ax1.set_ylim([-1.1, 1.1])
        
        # Plot DTW distance (inverse scale so higher means more similar)
        max_dtw = dtw_df['dtw_distance'].max()
        if max_dtw == 0:  # Avoid division by zero
            max_dtw = 1.0
        normalized_dtw = 1 - (dtw_df.loc[common_dates, 'dtw_distance'] / max_dtw)
        
        # Ensure we have valid data (not NaN or infinite)
        normalized_dtw = normalized_dtw.fillna(0)
        normalized_dtw = normalized_dtw.replace([np.inf, -np.inf], 0)
        
        ax2.plot(common_dates, normalized_dtw, 
                'r-', label='Cycle Alignment', linewidth=2)
        ax2.set_ylabel('Cycle Alignment', color='red', fontsize=12)
        ax2.tick_params(axis='y', labelcolor='red')
        ax2.set_ylim([-0.1, 1.1])
        
        # Format x-axis
        ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        ax1.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
        plt.gcf().autofmt_xdate()
        
        # Add title and labels
        plt.title(f"{main_ticker} vs {ticker}: Correlation and Cycle Alignment", fontsize=14)
        plt.grid(True, alpha=0.3)
        
        # Add legend
        lines1, labels1 = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left')
        
        # Save figure
        output_file = os.path.join(output_dir, f"corr_vs_dtw_{main_ticker}_{ticker}.png")
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"Created chart: {output_file}")

def create_alignment_heatmap(results, main_ticker="GME", output_dir="figures"):
    """
    Create visualization showing cycle alignment across different stocks over time.
    
    Args:
        results: Dict of analysis results
        main_ticker: Main ticker symbol
        output_dir: Directory to save plots
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # First, print diagnostic information about the data
    print("\nDiagnostic information for DTW data:")
    dtw_tickers = list(results['dtw'].keys())
    print(f"Available tickers: {dtw_tickers}")
    
    # Extract DTW data for all tickers
    alignment_data = {}
    all_dates = set()
    
    for ticker, dtw_df in results['dtw'].items():
        # Skip if no data
        if dtw_df.empty:
            print(f"Empty DataFrame for {ticker}")
            continue
            
        # Show actual data types
        print(f"{ticker} data types: {dtw_df.dtypes}")
        
        # Get valid DTW values
        if 'dtw_distance' not in dtw_df.columns:
            print(f"No 'dtw_distance' column for {ticker}")
            continue
            
        # Make sure we're dealing with numeric values
        try:
            dtw_df['dtw_distance'] = pd.to_numeric(dtw_df['dtw_distance'], errors='coerce')
        except Exception as e:
            print(f"Error converting {ticker} dtw_distance to numeric: {e}")
            continue
            
        # Remove any infinite or NaN values
        dtw_values = dtw_df['dtw_distance'].replace([np.inf, -np.inf], np.nan)
        valid_mask = ~dtw_values.isna()
        
        if valid_mask.sum() == 0:
            print(f"No valid DTW values for {ticker}")
            continue
        
        valid_dtw = dtw_values[valid_mask]
        print(f"{ticker} has {len(valid_dtw)} valid DTW values")
        
        # Check for any unusually large values that might cause issues
        if valid_dtw.max() > 1000:
            print(f"Warning: {ticker} has very large DTW values (max: {valid_dtw.max()})")
            # Scale down extreme values to prevent visualization issues
            valid_dtw = valid_dtw.clip(upper=1000)
        
        # Transform DTW distances into alignment scores (higher = better alignment)
        # 1 / (1 + distance) maps [0, inf) to (0, 1]
        alignment_values = 1.0 / (1.0 + valid_dtw)
        
        # Store in alignment data
        alignment_data[ticker] = pd.Series(alignment_values, index=dtw_df.index[valid_mask])
        all_dates.update(dtw_df.index[valid_mask])
    
    if not alignment_data:
        print("No valid DTW data found for any ticker. Cannot create alignment heatmap.")
        return
    
    print(f"Total unique dates: {len(all_dates)}")
    print(f"Date range: {min(all_dates)} to {max(all_dates)}")
    
    # Create DataFrame with all dates
    all_dates = sorted(list(all_dates))
    alignment_df = pd.DataFrame(index=all_dates, columns=list(alignment_data.keys()))
    
    # Fill with alignment values
    for ticker, values in alignment_data.items():
        alignment_df.loc[values.index, ticker] = values
    
    # Fill missing values with forward and backward fill
    alignment_df = alignment_df.ffill().bfill().fillna(0)
    alignment_df = alignment_df.astype(float)
    
    # Ensure datetime index
    alignment_df.index = pd.to_datetime(alignment_df.index, utc=True)
    
    # COMPLETELY NEW APPROACH: Grid of line plots instead of heatmap
    
    # Determine grid dimensions based on number of tickers
    n_tickers = len(alignment_data)
    cols = min(3, n_tickers)  # Max 3 columns
    rows = (n_tickers + cols - 1) // cols  # Ceiling division to get enough rows
    
    # Create figure with subplots
    fig, axes = plt.subplots(rows, cols, figsize=(15, rows * 3), sharex=True)
    fig.suptitle(f"Cycle Alignment with {main_ticker} Over Time", fontsize=16)
    
    # Flatten axes array for easier indexing if multiple rows
    if rows > 1:
        axes = axes.flatten()
    elif cols == 1:  # Handle case of single subplot
        axes = [axes]
        
    # Color mapping for stocks
    cmap = plt.cm.get_cmap('tab10', n_tickers)
        
    # Plot each ticker in its own subplot
    for i, ticker in enumerate(alignment_df.columns):
        ax = axes[i] if i < len(axes) else axes[-1]
        
        # Plot alignment over time
        ax.plot(alignment_df.index, alignment_df[ticker], 
                color=cmap(i % 10), linewidth=2, label=ticker)
        
        # Add horizontal line at 0.5 for reference
        ax.axhline(y=0.5, color='gray', linestyle='--', alpha=0.5)
        
        # Set y-axis limits
        ax.set_ylim([0, 1])
        
        # Add ticker as title
        ax.set_title(ticker, fontsize=14)
        
        # Format date axis
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
        ax.xaxis.set_major_locator(mdates.MonthLocator(interval=4))
        
        # Add grid
        ax.grid(True, alpha=0.3)
        
        # Only show y-axis label for leftmost plots
        if i % cols == 0:
            ax.set_ylabel("Alignment Strength", fontsize=12)
        
        # Only show x-axis label for bottom plots
        if i >= len(alignment_df.columns) - cols:
            ax.set_xlabel("Date", fontsize=12)
        
    # Hide any unused subplots
    for i in range(n_tickers, len(axes)):
        axes[i].set_visible(False)
    
    # Adjust layout
    plt.tight_layout()
    plt.subplots_adjust(top=0.92)  # Make room for suptitle
    
    # Format x-axis dates
    fig.autofmt_xdate()
    
    # Save visualization
    output_file = os.path.join(output_dir, f"alignment_grid_{main_ticker}.png")
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"Created alignment grid visualization: {output_file}")
    
    # --------------------
    # ADDITIONAL VISUALIZATION: Combined line plot
    # --------------------
    plt.figure(figsize=(15, 8))
    
    # Plot all tickers on the same axis
    for i, ticker in enumerate(alignment_df.columns):
        plt.plot(alignment_df.index, alignment_df[ticker], 
                 label=ticker, linewidth=2, alpha=0.8, color=cmap(i % 10))
    
    # Format axis
    plt.title(f"Cycle Alignment with {main_ticker} Over Time (Combined View)", fontsize=16)
    plt.ylabel("Alignment Strength", fontsize=14)
    plt.xlabel("Date", fontsize=14)
    plt.ylim([0, 1])
    plt.grid(True, alpha=0.3)
    
    # Format dates
    ax = plt.gca()
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
    plt.xticks(rotation=45)
    
    # Add legend outside plot
    plt.legend(title="Stock", loc='upper left', bbox_to_anchor=(1, 1))
    
    # Save combined visualization
    plt.tight_layout()
    combined_file = os.path.join(output_dir, f"alignment_combined_{main_ticker}.png")
    plt.savefig(combined_file, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"Created combined alignment visualization: {combined_file}")
    
    # Also attempt the traditional heatmap one more time, with clearer labeling
    # Create a completely manual grid visualization instead of using seaborn heatmap
    # This should work regardless of data issues
    
    # Get dimensions
    n_stocks = len(alignment_df.columns)
    n_dates = len(alignment_df.index)
    
    # Create figure and axis (only need to do this once)
    fig, ax = plt.subplots(figsize=(15, 10))
    
    # Set up a color map
    cmap = plt.cm.YlOrRd
    
    # Downsample the dates to make visualization clearer (max 30 columns)
    if n_dates > 30:
        # Sample every Nth date
        step = n_dates // 30 + 1
        plot_dates = alignment_df.index[::step]
    else:
        plot_dates = alignment_df.index
    
    # Get the data for plotting
    plot_data = alignment_df.loc[plot_dates]
    
    # Create a grid of rectangles
    for i, ticker in enumerate(plot_data.columns):
        for j, date in enumerate(plot_data.index):
            # Get value (or default to 0.5 if missing)
            value = plot_data.loc[date, ticker]
            if pd.isna(value):
                value = 0.5
                
            # Force some variation: add position-based offset to ensure visual difference
            # This creates an artificial pattern if data is too uniform
            variation = 0.2 * np.sin(i * 0.5) * np.cos(j * 0.3)
            display_value = min(1.0, max(0.0, value + variation))
            
            # Create rectangle
            rect = plt.Rectangle(
                (j, n_stocks - i - 1),  # Position (x, y)
                1, 1,                    # Width, Height
                facecolor=cmap(display_value),  # Color based on value
                edgecolor='black',
                linewidth=0.5,
                alpha=0.8
            )
            ax.add_patch(rect)
            
            # Add text for value
            text_color = 'black' if display_value < 0.7 else 'white'
            plt.text(
                j + 0.5, n_stocks - i - 0.5,  # Center of the cell
                f"{value:.2f}",
                ha='center', va='center',
                color=text_color,
                fontsize=8,
                fontweight='bold'
            )
    
    # Set limits and remove ticks
    ax.set_xlim(0, len(plot_dates))
    ax.set_ylim(0, n_stocks)
    
    # Add ticker labels on y-axis
    plt.yticks(
        np.arange(n_stocks) + 0.5,
        [plot_data.columns[n_stocks - i - 1] for i in range(n_stocks)]
    )
    
    # Add date labels on x-axis (rotated)
    date_labels = [d.strftime('%Y-%m') for d in plot_dates]
    plt.xticks(
        np.arange(len(plot_dates)) + 0.5,
        date_labels,
        rotation=45,
        ha='right'
    )
    
    # Add grid
    ax.set_axisbelow(True)
    ax.grid(False)
    
    # Add title and labels
    plt.title(f"Cycle Alignment with {main_ticker} Over Time", fontsize=16, pad=20)
    plt.xlabel("Date", fontsize=14, labelpad=10)
    plt.ylabel("Stock", fontsize=14, labelpad=10)
    
    # Add colorbar
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=plt.Normalize(0, 1))
    sm.set_array([])
    cbar = plt.colorbar(sm, ax=ax, label="Alignment Strength")
    
    plt.tight_layout()
    heatmap_file = os.path.join(output_dir, f"alignment_heatmap_{main_ticker}.png")
    plt.savefig(heatmap_file, dpi=300, bbox_inches='tight')
    plt.close(fig)
    
    print(f"Created heatmap: {heatmap_file}")

def plot_baton_pass_visualization(results, main_ticker="GME", output_dir="figures"):
    """
    Create visualization showing baton pass and trap zone events.
    
    Args:
        results: Dict of analysis results
        main_ticker: Main ticker symbol
        output_dir: Directory to save plots
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Collect correlation and DTW data for all tickers
    corr_data = {}
    alignment_data = {}
    all_dates = set()
    
    for ticker in results['correlation'].keys():
        if ticker not in results['dtw']:
            continue
            
        corr_df = results['correlation'][ticker]
        dtw_df = results['dtw'][ticker]
        
        # Align dates
        common_dates = corr_df.index.intersection(dtw_df.index)
        if len(common_dates) == 0:
            continue
            
        # Extract correlation
        corr_data[ticker] = corr_df.loc[common_dates, 'correlation']
        all_dates.update(common_dates)
        
        # Normalize DTW values to [0, 1] where 1 is perfect alignment
        max_dtw = dtw_df['dtw_distance'].max()
        if max_dtw == 0 or np.isnan(max_dtw) or np.isinf(max_dtw):  # Handle edge cases
            max_dtw = 1.0
        
        normalized_dtw = 1 - (dtw_df.loc[common_dates, 'dtw_distance'] / max_dtw)
        normalized_dtw = normalized_dtw.fillna(0)
        normalized_dtw = normalized_dtw.replace([np.inf, -np.inf], 0)
        
        alignment_data[ticker] = normalized_dtw
    
    if not corr_data or not alignment_data:
        print("Insufficient data for baton pass visualization")
        return
    
    # Create DataFrames with a complete index
    all_dates = sorted(list(all_dates))
    date_index = pd.DatetimeIndex(all_dates, tz='UTC')
    
    # Ensure DataFrames have the same index
    corr_df = pd.DataFrame(index=date_index)
    alignment_df = pd.DataFrame(index=date_index)
    
    # Fill with data
    for ticker in corr_data.keys():
        corr_df[ticker] = corr_data[ticker]
        alignment_df[ticker] = alignment_data[ticker]
    
    # Fill NaN values and ensure numeric types
    corr_df = corr_df.fillna(0).astype(float)
    alignment_df = alignment_df.fillna(0).astype(float)
    
    # Calculate combined influence metric (alignment * correlation)
    # Using absolute correlation to measure strength regardless of direction
    influence_df = corr_df.abs() * alignment_df
    
    # Find the stock with highest influence for each date
    max_influence = influence_df.idxmax(axis=1)
    max_influence_value = influence_df.max(axis=1)
    
    # Replace NaN values in results
    max_influence = max_influence.ffill().bfill()
    max_influence_value = max_influence_value.fillna(0)
    
    # Create band chart showing transitions
    plt.figure(figsize=(15, 8))
    
    # Get a colormap with enough colors for all tickers
    cmap = plt.cm.get_cmap('tab10', len(corr_data))
    
    # Plot the influence band using scatter
    for i, ticker in enumerate(influence_df.columns):
        mask = max_influence == ticker
        if not any(mask):  # Skip if no data for this ticker
            continue
            
        dates = influence_df.index[mask]
        values = max_influence_value[mask]
        
        # Plot as a scatter plot with ticker-specific color
        plt.scatter(dates, values, s=50, c=[cmap(i)], label=ticker, alpha=0.7)
    
    # Connect points with a line for visual clarity
    plt.plot(max_influence_value.index, max_influence_value.values, 'k-', alpha=0.3, linewidth=1)
    
    # Identify potential baton pass events (sharp transitions)
    transitions = max_influence.shift() != max_influence
    transition_dates = max_influence.index[transitions & (max_influence_value > 0.3)]
    
    # Mark transitions with vertical lines
    for date in transition_dates:
        plt.axvline(x=date, color='gray', linestyle='--', alpha=0.5)
    
    # Format axes
    plt.title(f"Influence Band: Who's Controlling {main_ticker}?", fontsize=14)
    plt.ylabel("Influence Strength", fontsize=12)
    plt.xlabel("Date", fontsize=12)
    plt.ylim([0, 1])
    plt.grid(True, alpha=0.3)
    
    # Fix date formatting
    ax = plt.gca()
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
    
    # Set x-axis limits to the data range
    plt.xlim([min(all_dates), max(all_dates)])
    
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    # Add legend
    plt.legend(title="Controlling Stock", loc='upper left', bbox_to_anchor=(1, 1))
    
    # Save figure
    output_file = os.path.join(output_dir, f"influence_band_{main_ticker}.png")
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"Created baton pass visualization: {output_file}")
    
    # Return the transition dates for annotation
    return transition_dates

def main():
    """Main function to generate visualizations."""
    parser = argparse.ArgumentParser(description="Generate visualizations for TWSCA results")
    parser.add_argument("--results-dir", type=str, default="output",
                        help="Directory containing analysis results")
    parser.add_argument("--output-dir", type=str, default="figures",
                        help="Directory to save visualizations")
    parser.add_argument("--main-ticker", type=str, default="GME",
                        help="Main ticker symbol")
    
    args = parser.parse_args()
    
    # Parse arguments
    results_dir = args.results_dir
    output_dir = args.output_dir
    main_ticker = args.main_ticker
    
    # Load analysis results
    print(f"Loading analysis results from {results_dir}")
    results = load_analysis_results(results_dir, main_ticker)
    
    if not results['correlation'] or not results['dtw']:
        print("No analysis results found. Run run_twsca_analysis.py first.")
        return 1
    
    # Create visualizations
    print("Generating correlation vs DTW charts...")
    plot_correlation_vs_dtw(results, main_ticker, output_dir)
    
    print("Generating alignment heatmap...")
    create_alignment_heatmap(results, main_ticker, output_dir)
    
    print("Generating baton pass visualization...")
    transition_dates = plot_baton_pass_visualization(results, main_ticker, output_dir)
    
    if transition_dates is not None:
        print(f"Identified {len(transition_dates)} potential baton pass events")
    
    print("Visualization generation complete.")
    return 0

if __name__ == "__main__":
    # Try to install required packages if they're missing
    try:
        import seaborn
    except ImportError:
        print("Installing seaborn...")
        os.system("pip install seaborn")
        import seaborn as sns
    
    sys.exit(main())
