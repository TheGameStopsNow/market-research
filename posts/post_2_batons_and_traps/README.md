# Time-Warped Spectral Correlation Analysis (TWSCA)

This directory contains scripts and data for performing Time-Warped Spectral Correlation Analysis on stock market data.

## Scripts

- `download_data.py`: Downloads historical stock data using yfinance
- `run_twsca_analysis.py`: Performs TWSCA analysis using the official `twsca` package
- `generate_visuals.py`: Creates visualizations from the analysis results

## Directories

- `data/`: Contains CSV files with historical stock prices
- `output/`: Contains CSV files with correlation and DTW distance results
- `figures/`: Contains visualization images

## Usage

### 1. Download Data

```bash
python download_data.py
```

This will download historical data for GME, CHWY, AMC, KOSS, BB, NOK, and SPY from 2020-01-01 to 2023-12-31.

### 2. Run Analysis

```bash
python run_twsca_analysis.py
```

This will perform TWSCA analysis on the downloaded data and save the results to the `output` directory.

### 3. Generate Visualizations

```bash
python generate_visuals.py
```

This will create visualizations from the analysis results and save them to the `figures` directory.

## Visualizations

The scripts generate several types of visualizations:

1. **Correlation vs. DTW Charts**: Shows the correlation and cycle alignment between GME and each comparison stock over time
2. **Alignment Heatmap**: Displays the cycle alignment of all stocks with GME over time
3. **Alignment Grid**: Shows individual alignment charts for each stock
4. **Combined Alignment**: Shows all stocks' alignment on a single chart
5. **Influence Band**: Shows which stock has the strongest influence on GME at different times

## Requirements

The scripts require the following Python packages:
- twsca
- pandas
- numpy
- matplotlib
- seaborn
- yfinance

To install all requirements:

```bash
pip install twsca pandas numpy matplotlib seaborn yfinance
``` 