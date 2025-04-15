import yfinance as yf
import pandas as pd
import os

# === SETTINGS FOR STREAMLIT APP DATA ===
# Tickers for weekly download (Streamlit app)
weekly_tickers = ["GME", "XRT", "SPY", "AMC", "KOSS", "BB", "NOK"]

# Date ranges
start_date = "2024-01-01"
end_date = "2025-01-01"  # Use start of next year to include full 2024

# Get the directory where this script is located
script_dir = os.path.dirname(os.path.abspath(__file__))
# Output directory relative to this script
data_dir = os.path.join(script_dir, "data_streamlit")

print(f"Ensuring data directory exists: {data_dir}")
os.makedirs(data_dir, exist_ok=True)

# === Process Weekly Data for Streamlit App ===
print("\n--- Processing Weekly Data for Streamlit App ---")
weekly_combined = pd.DataFrame()

for ticker in weekly_tickers:
    print(f"Processing weekly data for {ticker} ({start_date} to {end_date})...")
    try:
        # Download weekly data
        df_weekly = yf.download(ticker, start=start_date, end=end_date, interval="1wk")
        
        if df_weekly.empty:
            print(f"  -> No weekly data returned for {ticker}.")
            continue

        # Select and rename columns
        df_processed = pd.DataFrame(index=df_weekly.index)
        if 'Close' in df_weekly.columns:
            df_processed[f"{ticker}_Close"] = df_weekly['Close']
            df_processed[f"{ticker}_Return"] = df_processed[f"{ticker}_Close"].pct_change()
        else:
            print(f"  -> Warning: 'Close' column missing for {ticker}. Cannot calculate return.")
            df_processed[f"{ticker}_Close"] = pd.NA
            df_processed[f"{ticker}_Return"] = pd.NA
            
        if 'Volume' in df_weekly.columns:
            df_processed[f"{ticker}_Volume"] = df_weekly['Volume']
        else:
             df_processed[f"{ticker}_Volume"] = pd.NA

        # Keep only relevant columns
        df_processed = df_processed[[col for col in [f"{ticker}_Close", f"{ticker}_Volume", f"{ticker}_Return"] if col in df_processed.columns]]

        # Merge into the combined dataframe
        if weekly_combined.empty:
            weekly_combined = df_processed
            weekly_combined.index.name = 'date'  # Set index name for clarity
        else:
            weekly_combined = weekly_combined.merge(df_processed, left_index=True, right_index=True, how="outer")
            
    except Exception as e:
        print(f"  -> ERROR processing weekly data for {ticker}: {e}")

# Reset index to make 'date' a column
if not weekly_combined.empty:
    weekly_combined = weekly_combined.reset_index()
    # Ensure date column is called 'date'
    if 'index' in weekly_combined.columns:
        weekly_combined = weekly_combined.rename(columns={'index': 'date'})
        
    # Reorder columns for Streamlit app compatibility, ensuring date is first
    final_columns = ['date']
    # Define expected tickers for final ordering
    ordered_tickers = ["GME", "XRT", "SPY", "AMC", "KOSS", "BB", "NOK"]
    for ticker in ordered_tickers:
        for suffix in ['_Close', '_Volume', '_Return']:
            col_name = f"{ticker}{suffix}"
            if col_name in weekly_combined.columns:
                final_columns.append(col_name)
    
    # Add any remaining columns not in the preferred order (shouldn't happen ideally)
    remaining_cols = [col for col in weekly_combined.columns if col not in final_columns]
    final_columns.extend(remaining_cols)

    weekly_combined = weekly_combined[final_columns]
    
    # Save the combined weekly file
    output_file = os.path.join(data_dir, "combined_weekly_2024_2025.csv")
    print(f"\nSaving combined weekly data -> {output_file}")
    weekly_combined.to_csv(output_file, index=False)
else:
    print("\nNo weekly data was processed. Cannot save combined weekly file.")

print(f"\n✅ Streamlit app data download complete. Files saved to: {data_dir}") 