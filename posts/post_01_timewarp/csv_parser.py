import pandas as pd
import numpy as np

def load_stock_data(file_path):
    """Load stock data from CSV with the custom 3-row header format."""
    try:
        # Skip headers and use pandas directly with column positions
        df = pd.read_csv(file_path, skiprows=3, header=None)
        
        # Convert first column to datetime and set as index
        df.index = pd.to_datetime(df[0])
        df.index.name = 'Date'
        
        # Create properly named columns, ensuring all values are numeric
        df = pd.DataFrame({
            'Price': pd.to_numeric(df[0], errors='coerce'),
            'Close': pd.to_numeric(df[1], errors='coerce'),
            'High': pd.to_numeric(df[2], errors='coerce'),
            'Low': pd.to_numeric(df[3], errors='coerce'),
            'Open': pd.to_numeric(df[4], errors='coerce'),
            'Volume': pd.to_numeric(df[5], errors='coerce')
        }, index=df.index)
        
        # Add Adj Close using the Close column
        df['Adj Close'] = df['Close']
        
        return df
    except Exception as e:
        print(f"Error loading data: {e}")
        return None 