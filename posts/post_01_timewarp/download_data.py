import yfinance as yf
import pandas as pd
import os

# === SETTINGS FOR POST 1 DATA ===
# Tickers for daily download (Post 1)
daily_tickers = ["GME", "CHWY", "SPY", "AMC", "KOSS", "BB", "NOK"]

# Date ranges
start_date = "2020-01-01"
end_date = "2024-12-31"  # Inclusive end date for yfinance

# Get the directory where this script is located
script_dir = os.path.dirname(os.path.abspath(__file__))
# Output directory relative to this script
data_dir = os.path.join(script_dir, "data")

print(f"Ensuring data directory exists: {data_dir}")
os.makedirs(data_dir, exist_ok=True)

# === Download Daily Data for Post 1 ===
print("\n--- Downloading Daily Data for Post 1 Analysis ---")
for ticker in daily_tickers:
    output_file = os.path.join(data_dir, f"{ticker}.csv")
    print(f"Downloading daily data for {ticker} ({start_date} to {end_date}) -> {output_file}")
    try:
        df = yf.download(ticker, start=start_date, end=end_date, interval="1d")
        if not df.empty:
            df.to_csv(output_file)
            print(f"  -> Saved {ticker}.csv")
        else:
            print(f"  -> No data returned for {ticker}.")
    except Exception as e:
        print(f"  -> ERROR downloading {ticker}: {e}")

print(f"\n✅ Post 1 data download complete. Files saved to: {data_dir}") 