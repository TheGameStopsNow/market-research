import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
from scipy import signal

# First ensure required packages are installed
import sys
import subprocess

def install_package(package):
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])

# Install required packages
required_packages = ['twsca>=0.3.0', 'seaborn', 'tqdm']
for package in required_packages:
    try:
        __import__(package.split('>=')[0])
        print(f"{package} already installed")
    except ImportError:
        print(f"Installing {package}...")
        install_package(package)
        print(f"{package} installed successfully")

# Import TWSCA after ensuring it's installed
try:
    from twsca import (
        llt_filter, analysis, spectral, spectral_correlation, 
        compute_twsca, compute_twsca_matrix
    )
    use_built_in_llt = True
except ImportError as e:
    print(f"Warning: Could not import from TWSCA package: {e}")
    use_built_in_llt = False

# Define the smoothing and plotting extensions
class Smoothing:
    @staticmethod
    def llt_filter(data, sigma=1.5, alpha=0.5):
        """
        Local Laplacian Transform (LLT) smoothing.
        If TWSCA package is available, uses its implementation,
        otherwise falls back to Savitzky-Golay filter.
        
        Parameters:
        -----------
        data : array-like
            Input time series
        sigma : float, default=1.5
            Smoothing factor
        alpha : float, default=0.5
            In TWSCA 0.3.0, alpha must be between 0 and 1
        """
        if use_built_in_llt:
            # Ensure alpha is in the valid range (0-1)
            clamped_alpha = min(max(alpha, 0.01), 0.99)
            return llt_filter(data, sigma=sigma, alpha=clamped_alpha)
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

# Create global instances
twsca_smoothing = Smoothing()
twsca_plotting = Plotting()

# Setup plotting style
twsca_plotting.setup_plotting_style()

# Set random seed for reproducibility
np.random.seed(42)
print("Setup complete. Random seed set to 42.") 