#!/usr/bin/env python3
"""
download_data.py
Downloads required stock data for Time-Warped Spectral Correlation Analysis.
"""

import os
import sys
import argparse
import pandas as pd
from datetime import datetime, timedelta

def download_stock_data(tickers, start_date, end_date, output_dir="data"):
    """
    Download historical data for specified tickers.
    
    Args:
        tickers: List of stock tickers to download
        start_date: Start date for data download
        end_date: End date for data download
        output_dir: Directory to save CSV files
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Try to import yfinance, install if needed
    try:
        import yfinance as yf
    except ImportError:
        print("Installing yfinance...")
        os.system("pip install yfinance")
        import yfinance as yf
    
    # Download data for each ticker
    for ticker in tickers:
        try:
            print(f"Downloading data for {ticker}...")
            stock = yf.Ticker(ticker)
            data = stock.history(start=start_date, end=end_date)
            
            if data.empty:
                print(f"No data found for {ticker}")
                continue
                
            # Save to CSV
            csv_path = os.path.join(output_dir, f"{ticker}.csv")
            data.to_csv(csv_path)
            print(f"Saved {len(data)} rows to {csv_path}")
            
        except Exception as e:
            print(f"Error downloading data for {ticker}: {e}")
    
    print(f"Download complete. Data saved to {output_dir}")

def main():
    """Main function to download stock data."""
    parser = argparse.ArgumentParser(description="Download stock data for TWSCA analysis")
    parser.add_argument("--output-dir", type=str, default="data",
                        help="Directory to save CSV files")
    parser.add_argument("--tickers", type=str, default="GME,CHWY,AMC,KOSS,BB,NOK,SPY",
                        help="Comma-separated list of tickers to download")
    parser.add_argument("--start-date", type=str, default="2020-01-01",
                        help="Start date for data download (YYYY-MM-DD)")
    parser.add_argument("--end-date", type=str, default="2023-12-31",
                        help="End date for data download (YYYY-MM-DD)")
    
    args = parser.parse_args()
    
    # Parse arguments
    output_dir = args.output_dir
    tickers = [ticker.strip() for ticker in args.tickers.split(",")]
    start_date = args.start_date
    end_date = args.end_date
    
    # Download data
    download_stock_data(tickers, start_date, end_date, output_dir)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
