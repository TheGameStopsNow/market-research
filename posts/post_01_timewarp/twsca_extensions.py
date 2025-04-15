import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import sys

# Import from the updated TWSCA package
try:
    # Import from the updated TWSCA 0.3.0 package
    from twsca import (
        llt_filter, smoothing, compute_twsca, compute_spectrum, 
        spectral_correlation, dtw_distance
    )
    print("Successfully imported from TWSCA 0.3.0 package.")
    use_built_in_llt = True
except ImportError as e:
    print(f"Warning: Could not import from TWSCA package: {e}")
    use_built_in_llt = False
    from scipy import signal

# Define custom smoothing implementation as fallback if TWSCA package is not available
class Smoothing:
    @staticmethod
    def llt_filter(data, sigma=1.5, alpha=0.5, iterations=3):
        """Local Laplacian Transform (LLT) smoothing implementation.
        This is a wrapper around the TWSCA implementation or a fallback using Savitzky-Golay.
        
        Parameters:
        -----------
        data : array-like
            The input time series to smooth
        sigma : float, default=1.5
            Controls the smoothing intensity (higher = more smoothing)
        alpha : float, default=0.5
            In new TWSCA (0.3.0), alpha must be between 0 and 1
        iterations : int, default=3
            Number of iterations to apply the filter
        """
        if use_built_in_llt:
            # Use the built-in LLT filter from the TWSCA package
            # Make sure alpha is between 0 and 1 as required by the new version
            clamped_alpha = min(max(alpha, 0.01), 0.99)
            return llt_filter(data, sigma=sigma, alpha=clamped_alpha, iterations=iterations)
        else:
            # Fallback to Savitzky-Golay filter
            window = int(len(data) * 0.1)  # 10% of data length
            if window % 2 == 0:
                window += 1  # Make window odd
            return signal.savgol_filter(data, window, 3)

class Plotting:
    @staticmethod
    def setup_plotting_style():
        """Set up matplotlib plotting style for consistency."""
        plt.style.use('default')  # Reset to default style
        plt.rcParams['figure.figsize'] = [12, 6]
        plt.rcParams['lines.linewidth'] = 2
        plt.rcParams['axes.grid'] = True
        plt.rcParams['grid.alpha'] = 0.3
        
    @staticmethod
    def plot_baton_map(rolling_correlations):
        """Plot correlation heatmap visualization showing GME vs other stocks over time."""
        # Create a figure with appropriate dimensions
        fig, ax = plt.subplots(figsize=(16, 8))
        
        # Get all tickers and sort them
        tickers = sorted(list(rolling_correlations.keys()))
        
        # Create a combined DataFrame with all correlations
        # First, make sure we have a common date range
        all_dates = set()
        for ticker, df in rolling_correlations.items():
            all_dates.update(df.index)
        all_dates = sorted(list(all_dates))
        
        # Create empty correlation matrix 
        correlation_matrix = np.empty((len(tickers), len(all_dates)))
        correlation_matrix[:] = np.nan  # Fill with NaN for missing values
        
        # Fill in correlation matrix
        for i, ticker in enumerate(tickers):
            if ticker in rolling_correlations:
                df = rolling_correlations[ticker]
                for j, date in enumerate(all_dates):
                    if date in df.index:
                        correlation_matrix[i, j] = df.loc[date, 'Correlation']
        
        # Plot heatmap
        im = ax.imshow(correlation_matrix, cmap='coolwarm', aspect='auto', 
                      interpolation='none', vmin=-1, vmax=1)
        
        # Add colorbar
        cbar = plt.colorbar(im, ax=ax)
        cbar.set_label('Correlation with GME')
        
        # Format x-axis (dates)
        # Choose subset of dates to display to avoid overcrowding
        date_indices = np.linspace(0, len(all_dates)-1, min(25, len(all_dates))).astype(int)
        date_labels = [all_dates[i].strftime('%Y-%m-%d') for i in date_indices]
        ax.set_xticks(date_indices)
        ax.set_xticklabels(date_labels, rotation=45, ha='right')
        ax.set_xlabel('Week Ending')
        
        # Format y-axis (tickers)
        ax.set_yticks(range(len(tickers)))
        ax.set_yticklabels(tickers)
        ax.set_ylabel('Stock')
        
        # Add title
        ax.set_title('Weekly Rolling Influence Heatmap: GME vs Stocks (6-week Corr)')
        
        # Adjust layout
        plt.tight_layout()
        
        return fig

class AnalysisExtensions:
    @staticmethod
    def run_twsca(target, comparison, max_warp=5, freq_band=[0.02, 0.5]):
        """Run TWSCA analysis between target and comparison series."""
        try:
            if not use_built_in_llt:
                raise ImportError("TWSCA package not available")
                
            # Use the updated compute_twsca function with its new parameters
            # The updated function accepts direct time series input
            result = compute_twsca(
                target, comparison,
                # Set the DTW radius parameter (equivalent to max_warp)
                dtw_radius=max_warp,
                # Use LLT filtering for the input series
                use_llt=True,
                llt_sigma=1.5,
                llt_alpha=0.5,  # Updated to be compatible with TWSCA 0.3.0
                # Normalize and detrend the series
                normalize=True,
                detrend=True
            )
            
            # Extract alignment cost and correlation from the result
            # Updated to use the correct key names from TWSCA 0.3.0 result dictionary
            alignment_cost = result.get('dtw_distance', np.nan)  # Changed from 'alignment_cost'
            correlation = result.get('spectral_correlation', 0.0)  # Changed from 'correlation'
            
            return alignment_cost, correlation
        except Exception as e:
            print(f"Error in TWSCA calculation: {e}")
            return np.nan, 0.0
    
    @staticmethod
    def rolling_correlation(target, comparison, window_days=30):
        """Calculate rolling correlation between two series."""
        # Ensure indexes match
        combined = pd.DataFrame({'target': target, 'comparison': comparison})
        combined = combined.dropna()
        
        # Calculate rolling correlation
        rolling_corr = combined['target'].rolling(window=window_days).corr(combined['comparison'])
        
        # Return as DataFrame
        return pd.DataFrame({'Correlation': rolling_corr}, index=rolling_corr.index)

# Create instances for easy import
twsca_smoothing = Smoothing()
twsca_plotting = Plotting()
twsca_analysis = AnalysisExtensions() 