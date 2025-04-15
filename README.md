# Market Research Repository

This repository contains market research analysis, data, and interactive visualizations focusing on stock market dynamics and manipulation patterns.

## Repository Structure

The repository is organized into the following sections:

1. `posts/` - Contains scripts and data for specific analysis posts:
   - `post_00_gme_manipulation_evidence/` - Analysis of GME stock manipulation evidence
      - Contains detailed analysis of trading patterns, dark pool activity, and market structure implications
      - [Read the full analysis](./posts/post_00_gme_manipulation_evidence/GME-Manipulation-and-Key-Evidence.md)
   - `post_01_timewarp/` - GME TWSCA (Time-Warped Spectral Correlation Analysis) analysis - [Read the full analysis](./posts/post_01_timewarp/post_01-GME_Timewarp-Decoding_RoaringKittys_Clues.md)

2. `extras/` - Contains the Streamlit dashboard and weekly data:
   - `streamlit-twsca.py` - Main Streamlit app for interactive visualization
   - `plot_visuals_streamlit.py` - Plotting utilities for the Streamlit app
   - `data_streamlit/` - Weekly aggregated data for the dashboard

## Setup Instructions

### Prerequisites

- Python 3.7+
- pip
- git
- Internet connection (for data download)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/market-research.git
   cd market-research
   ```

2. Create a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Download the data (REQUIRED):
   ```bash
   python download_all_data.py
   ```

### Running the Streamlit Dashboard

To run the interactive dashboard:

```bash
streamlit run extras/streamlit-twsca.py
```

## Research Posts

### Post 00: GME Manipulation Evidence
- Location: `post_00_gme_manipulation_evidence/`
- Content: Comprehensive analysis of GME stock manipulation patterns
- Key findings on dark pool activity, short interest, and market structure implications

### Post 01: Time-Warped Analysis
- Location: `posts/post_01_timewarp/`
- Content: TWSCA analysis of GME stock dynamics
- Interactive visualizations and correlation studies

## Data Notes

- The `download_all_data.py` script fetches necessary data from Yahoo Finance
- Data is organized by post in respective directories
- Streamlit dashboard uses weekly aggregated data in `extras/data_streamlit/`

## License

[MIT License](LICENSE)

## Acknowledgments

- Thanks to the open-source community for libraries like pandas, numpy, matplotlib, and streamlit
- Special thanks to contributors and researchers in the GME community 