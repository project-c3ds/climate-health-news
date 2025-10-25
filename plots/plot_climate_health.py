"""
Generate combined visualization with maps and time series.

This script creates a single figure containing:
- Top: Two maps showing climate and health coverage by country
- Bottom: Two time series plots showing trends over time
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from visualize_article_map import load_shapefile, df_country
from analysis.plot_time_series import plot_combined_maps_and_timeseries, df_grouped
import matplotlib.pyplot as plt

if __name__ == "__main__":
    print("=" * 70)
    print("Creating Combined Maps and Time Series Visualization")
    print("=" * 70)
    
    # Load shapefile
    gdf = load_shapefile()
    
    # Create combined visualization
    fig = plot_combined_maps_and_timeseries(df_grouped, df_country, gdf)
    
    print("\n" + "=" * 70)
    print("Visualization complete!")
    print("=" * 70)
    
    # Display the plot
    plt.show()

