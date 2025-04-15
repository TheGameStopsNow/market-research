# GME Timewarp Analysis

This directory contains a fixed and improved version of the GameStop (GME) Timewarp Analysis using TWSCA (Time-Warped Spectral Correlation Analysis).

## Contents

- `run_analysis.py` - Main script to run the GME Timewarp Analysis
- `twsca_extensions.py` - Extensions to the TWSCA package for this specific analysis
- `fixed_csv_parser.py` - Fixed CSV parser for loading stock data

## Features

This analysis includes:

- LLT (Linear Line Transformation) smoothing for stock price data
- Rolling correlation analysis between GME and other stocks
- Time-warped correlation analysis to identify similar patterns
- Visualization of correlation "baton handoffs" between stocks
- Heatmap grid visualization of GME correlations over time

## Usage

To run the analysis:

```bash
python run_analysis.py
```

Output visualizations will be saved to the `figures/` directory.

## Improvements

This fixed version includes:

1. Proper CSV parsing to handle the specific format of the stock data files
2. Improved error handling for missing files or columns
3. Updated visualization code for better readability and interpretation
4. Compatibility with TWSCA 0.3.0, including the updated LLT filter parameters
5. Heatmap grid visualization showing GME's correlation with other stocks over time

## Requirements

- Python 3.7+
- TWSCA 0.3.0+
- pandas, numpy, matplotlib
- Stock data files in the `data/` directory 