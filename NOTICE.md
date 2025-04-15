# IMPORTANT NOTICE ABOUT DATA FILES

## Data Requirements

This repository **does not** include data files. These must be downloaded using the provided scripts.

## Why aren't data files included?

1. **Licensing considerations**: The stock data from Yahoo Finance and other providers has specific terms of use that may restrict redistribution.

2. **Repository size**: Including years of stock data would make the repository unnecessarily large.

3. **Data freshness**: By downloading data at setup time, users get the most recent data available.

## How to download the required data

Run the following command from the project root before attempting to use any analysis scripts or the Streamlit app:

```bash
python download_all_data.py
```

This script will:

1. Download daily stock data (GME, CHWY, SPY, etc.) for post_01_timewarp analysis
2. Download and process weekly data for the Streamlit dashboard
3. Create all necessary directories and CSV files

## Troubleshooting

If you encounter errors:

- Ensure you have an internet connection
- Check that you've installed all requirements: `pip install -r requirements.txt`
- Yahoo Finance API occasionally has rate limits - try running the script again after a few minutes

## License Notice

The data downloaded through this project comes from Yahoo Finance and is subject to their terms of service. This repository only provides the tools to access this data, not the data itself. 