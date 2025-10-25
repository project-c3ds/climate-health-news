import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

df = pd.read_parquet('data/articles/lancet_europe_dataset_monthly.parquet')

df_grouped = df.groupby('month_year').agg({
    'article_count': 'sum',
    'climate': 'sum',
    'health': 'sum',
    'climate_health': 'sum',
    'urban': 'sum',
    'rural': 'sum'
}).reset_index()

# Remove 2025-09 data point
df_grouped = df_grouped[df_grouped['month_year'] != '2025-09']


def plot_percentage_timeseries(df_grouped, variables, figsize=(12, 6), colors=None, title=None):
    """
    Plot variables as a percentage of article_count over time.
    
    Parameters:
    -----------
    df_grouped : pd.DataFrame
        DataFrame with 'month_year', 'article_count', and variable columns
    variables : list
        List of column names to plot as percentages
    figsize : tuple, optional
        Figure size (width, height)
    colors : list, optional
        List of colors for each variable. If None, uses default color cycle
    title : str, optional
        Plot title. If None, generates a default title
    
    Returns:
    --------
    fig, ax : matplotlib figure and axis objects
    """
    # Calculate percentages
    df_plot = df_grouped.copy()
    for var in variables:
        df_plot[f'{var}_pct'] = (df_plot[var] / df_plot['article_count']) * 100
    
    # Create figure
    fig, ax = plt.subplots(figsize=figsize)
    
    # Plot each variable
    if colors is None:
        colors = plt.cm.Set2.colors  # Use a nice color palette
    
    for i, var in enumerate(variables):
        color = colors[i % len(colors)]
        ax.plot(df_plot['month_year'], df_plot[f'{var}_pct'], 
                marker='o', linewidth=2, markersize=4, 
                label=var.replace('_', ' ').title(), color=color)
    
    # Styling
    ax.set_xlabel('Month', fontsize=11, fontweight='bold')
    ax.set_ylabel('Percentage of Articles (%)', fontsize=11, fontweight='bold')
    
    if title is None:
        title = 'Article Distribution Over Time'
    ax.set_title(title, fontsize=13, fontweight='bold', pad=20)
    
    # Remove gridlines
    ax.grid(False)
    
    # Only show spines on left and bottom
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_linewidth(1.5)
    ax.spines['bottom'].set_linewidth(1.5)
    
    # Format x-axis to prevent label overlap
    n_labels = len(df_plot)
    if n_labels > 20:
        # Show every nth label
        step = n_labels // 15  # Show approximately 15 labels
        tick_positions = range(0, n_labels, step)
        ax.set_xticks(tick_positions)
        ax.set_xticklabels([df_plot['month_year'].iloc[i] for i in tick_positions])
    
    # Rotate labels for better readability
    plt.xticks(rotation=45, ha='right')
    
    # Add legend
    ax.legend(frameon=False, loc='best', fontsize=10)
    
    # Tight layout to prevent label cutoff
    plt.tight_layout()
    
    return fig, ax


def plot_climate_health_subplots(df_grouped, figsize=(12, 10), title=None):
    """
    Plot two stacked subplots:
    - Top: Climate as % of all articles (line)
    - Bottom: Health and climate_health as % of climate articles (area plots)
    
    Parameters:
    -----------
    df_grouped : pd.DataFrame
        DataFrame with 'month_year', 'article_count', 'climate', 'health', and 'climate_health' columns
    figsize : tuple, optional
        Figure size (width, height)
    title : str, optional
        Overall title. If None, generates a default title
    
    Returns:
    --------
    fig, (ax1, ax2) : matplotlib figure and axis objects
    """
    # Calculate percentages
    df_plot = df_grouped.copy()
    df_plot['climate_pct'] = (df_plot['climate'] / df_plot['article_count']) * 100
    df_plot['health_pct'] = (df_plot['health'] / df_plot['climate']) * 100
    df_plot['climate_health_pct'] = (df_plot['climate_health'] / df_plot['climate']) * 100
    
    # Create figure with two subplots
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=figsize, sharex=True)
    
    # Create x-axis positions (numeric for area plot)
    x = range(len(df_plot))
    
    # TOP PLOT: Climate as % of all articles
    color_climate = '#414a4c'
    ax1.plot(x, df_plot['climate_pct'], 
             color=color_climate, linewidth=2.5, marker='o', markersize=5,
             label='Climate Articles')
    
    ax1.set_ylabel('% of All Articles', fontsize=11, fontweight='bold')
    ax1.set_title('Climate Coverage', fontsize=12, fontweight='bold', pad=10)
    
    # Styling for top plot
    ax1.grid(False)
    ax1.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False)
    ax1.spines['left'].set_linewidth(1.5)
    ax1.spines['bottom'].set_linewidth(1.5)
    
    # BOTTOM PLOT: Health topics as % of climate articles (area plots)
    ax2.fill_between(x, 0, df_plot['health_pct'], 
                     color='#66c2a5', alpha=0.6,
                     label='Health (any mention)')
    ax2.fill_between(x, 0, df_plot['climate_health_pct'], 
                     color='#fc8d62', alpha=0.6,
                     label='Health (climate connection)')
    
    # Add line borders for area plots
    ax2.plot(x, df_plot['health_pct'], color='#66c2a5', linewidth=2)
    ax2.plot(x, df_plot['climate_health_pct'], color='#fc8d62', linewidth=2)
    
    ax2.set_xlabel('Month', fontsize=11, fontweight='bold')
    ax2.set_ylabel('% of Climate Articles', fontsize=11, fontweight='bold')
    ax2.set_title('Health Topics Within Climate Coverage', fontsize=12, fontweight='bold', pad=10)
    
    # Styling for bottom plot
    ax2.grid(False)
    ax2.spines['top'].set_visible(False)
    ax2.spines['right'].set_visible(False)
    ax2.spines['left'].set_linewidth(1.5)
    ax2.spines['bottom'].set_linewidth(1.5)
    ax2.legend(frameon=False, loc='best', fontsize=10)
    
    # Format x-axis to prevent label overlap
    n_labels = len(df_plot)
    if n_labels > 20:
        step = n_labels // 15
        tick_positions = range(0, n_labels, step)
        ax2.set_xticks(tick_positions)
        ax2.set_xticklabels([df_plot['month_year'].iloc[i] for i in tick_positions])
    else:
        ax2.set_xticks(x)
        ax2.set_xticklabels(df_plot['month_year'])
    
    plt.xticks(rotation=45, ha='right')
    
    # Overall title if provided
    if title:
        fig.suptitle(title, fontsize=14, fontweight='bold', y=0.995)
    
    plt.tight_layout()
    
    return fig, (ax1, ax2)


def plot_urban_rural(df_grouped, figsize=(12, 6), title=None):
    """
    Plot urban and rural as % of climate articles (line plot).
    
    Parameters:
    -----------
    df_grouped : pd.DataFrame
        DataFrame with 'month_year', 'climate', 'urban', and 'rural' columns
    figsize : tuple, optional
        Figure size (width, height)
    title : str, optional
        Plot title. If None, generates a default title
    
    Returns:
    --------
    fig, ax : matplotlib figure and axis objects
    """
    # Calculate percentages
    df_plot = df_grouped.copy()
    df_plot['urban_pct'] = (df_plot['urban'] / df_plot['climate']) * 100
    df_plot['rural_pct'] = (df_plot['rural'] / df_plot['climate']) * 100
    
    # Create figure
    fig, ax = plt.subplots(figsize=figsize)
    
    # Create x-axis positions
    x = range(len(df_plot))
    
    # Plot urban and rural lines
    ax.plot(x, df_plot['urban_pct'], 
            color='#8da0cb', linewidth=2.5, marker='o', markersize=5,
            label='Urban')
    ax.plot(x, df_plot['rural_pct'], 
            color='#e78ac3', linewidth=2.5, marker='o', markersize=5,
            label='Rural')
    
    # Styling
    ax.set_xlabel('Month', fontsize=11, fontweight='bold')
    ax.set_ylabel('% of Climate Articles', fontsize=11, fontweight='bold')
    
    if title is None:
        title = 'Urban and Rural Topics Within Climate Coverage'
    ax.set_title(title, fontsize=13, fontweight='bold', pad=20)
    
    # Remove gridlines
    ax.grid(False)
    
    # Only show spines on left and bottom
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_linewidth(1.5)
    ax.spines['bottom'].set_linewidth(1.5)
    
    # Format x-axis to prevent label overlap
    n_labels = len(df_plot)
    if n_labels > 20:
        step = n_labels // 15
        tick_positions = range(0, n_labels, step)
        ax.set_xticks(tick_positions)
        ax.set_xticklabels([df_plot['month_year'].iloc[i] for i in tick_positions])
    else:
        ax.set_xticks(x)
        ax.set_xticklabels(df_plot['month_year'])
    
    # Rotate labels for better readability
    plt.xticks(rotation=45, ha='right')
    
    # Add legend
    ax.legend(frameon=False, loc='best', fontsize=10)
    
    # Tight layout to prevent label cutoff
    plt.tight_layout()
    
    return fig, ax


def plot_combined_maps_and_timeseries(df_grouped, df_country, gdf, figsize=(24, 14)):
    """
    Create a combined figure with maps on left and time series plots on right.
    
    Layout:
    - Left side: Two maps stacked vertically (climate/article_count and health/climate)
    - Right side: Two time series plots stacked vertically (climate % and health topics %)
    
    Parameters:
    -----------
    df_grouped : pd.DataFrame
        DataFrame with monthly time series data
    df_country : pd.DataFrame
        DataFrame with country-level aggregated data
    gdf : gpd.GeoDataFrame
        GeoDataFrame with country geometries for mapping
    figsize : tuple, optional
        Figure size (width, height)
    
    Returns:
    --------
    fig : matplotlib figure object
    """
    # Import necessary functions from visualize_article_map
    import sys
    import os
    sys.path.insert(0, os.path.abspath('.'))
    from visualize_article_map import create_map
    import numpy as np
    from matplotlib.colors import LinearSegmentedColormap
    
    print("\nCreating combined maps and time series visualization...")
    
    # Create custom colormap using blue
    colors_blue = ['#ffffff', '#0072B2']
    cmap_blue = LinearSegmentedColormap.from_list('custom_blue', colors_blue)
    
    # Create figure with custom grid
    fig = plt.figure(figsize=figsize)
    gs = gridspec.GridSpec(2, 2, figure=fig, width_ratios=[1, 1], height_ratios=[1, 1], hspace=0.15, wspace=0.15)
    
    # Left column: Two maps stacked vertically
    ax_map1 = fig.add_subplot(gs[0, 0])
    ax_map2 = fig.add_subplot(gs[1, 0])
    
    # Right column: Two time series plots stacked vertically
    ax_ts1 = fig.add_subplot(gs[0, 1])
    ax_ts2 = fig.add_subplot(gs[1, 1], sharex=ax_ts1)
    
    # === CREATE MAPS ===
    print("\n--- MAP 1: Climate / Article Count ---")
    gdf_merged1, country_col = create_map(
        gdf, df_country, 
        numerator_col='climate', 
        denominator_col='article_count',
        ax=ax_map1,
        title='Climate Coverage\n(% of All Articles)',
        cmap=cmap_blue,
        show_percentage=True
    )
    
    print("\n--- MAP 2: Health / Climate ---")
    gdf_merged2, _ = create_map(
        gdf, df_country, 
        numerator_col='health', 
        denominator_col='climate',
        ax=ax_map2,
        title='Health Topics Within Climate Coverage\n(% of Climate Articles)',
        cmap=cmap_blue,
        show_percentage=True
    )
    
    # === CREATE TIME SERIES PLOTS ===
    print("\n--- TIME SERIES PLOTS ---")
    
    # Calculate percentages
    df_plot = df_grouped.copy()
    df_plot['climate_pct'] = (df_plot['climate'] / df_plot['article_count']) * 100
    df_plot['health_pct'] = (df_plot['health'] / df_plot['climate']) * 100
    df_plot['climate_health_pct'] = (df_plot['climate_health'] / df_plot['climate']) * 100
    
    # Create x-axis positions
    x = range(len(df_plot))
    
    # TIME SERIES 1: Climate as % of all articles
    ax_ts1.plot(x, df_plot['climate_pct'], 
                marker='o', linewidth=3.5, markersize=8, color='#999999',
                markerfacecolor='#0072B2', markeredgecolor='white', markeredgewidth=1.5,
                label='Climate Articles')
    
    ax_ts1.set_ylabel('% of All Articles', fontsize=11, fontweight='bold')
    ax_ts1.set_title('Climate Coverage Over Time', fontsize=12, fontweight='bold', pad=10)
    
    # Styling for first time series
    ax_ts1.grid(False)
    ax_ts1.spines['top'].set_visible(False)
    ax_ts1.spines['right'].set_visible(False)
    ax_ts1.spines['left'].set_linewidth(1.5)
    ax_ts1.spines['bottom'].set_linewidth(1.5)
    
    # Hide x-axis labels on top plot (since bottom plot shares x-axis)
    plt.setp(ax_ts1.xaxis.get_majorticklabels(), visible=False)
    
    # TIME SERIES 2: Health topics as % of climate articles (area plots)
    ax_ts2.fill_between(x, 0, df_plot['health_pct'], 
                        color='#0072B2', alpha=0.6,
                        label='Health (any mention)')
    ax_ts2.fill_between(x, 0, df_plot['climate_health_pct'], 
                        color='#E69F00', alpha=0.85,
                        label='Health (climate connection)')
    
    # Add line borders for area plots
    ax_ts2.plot(x, df_plot['health_pct'], color='#0072B2', linewidth=2)
    ax_ts2.plot(x, df_plot['climate_health_pct'], color='#E69F00', linewidth=2)
    
    ax_ts2.set_xlabel('Month', fontsize=11, fontweight='bold')
    ax_ts2.set_ylabel('% of Climate Articles', fontsize=11, fontweight='bold')
    ax_ts2.set_title('Health Topics Within Climate Coverage Over Time', fontsize=12, fontweight='bold', pad=10)
    
    # Styling for second time series
    ax_ts2.grid(False)
    ax_ts2.spines['top'].set_visible(False)
    ax_ts2.spines['right'].set_visible(False)
    ax_ts2.spines['left'].set_linewidth(1.5)
    ax_ts2.spines['bottom'].set_linewidth(1.5)
    ax_ts2.legend(frameon=False, loc='best', fontsize=10)
    
    # Format x-axis to prevent label overlap
    n_labels = len(df_plot)
    if n_labels > 20:
        step = n_labels // 15
        tick_positions = range(0, n_labels, step)
        ax_ts2.set_xticks(tick_positions)
        ax_ts2.set_xticklabels([df_plot['month_year'].iloc[i] for i in tick_positions])
    else:
        ax_ts2.set_xticks(x)
        ax_ts2.set_xticklabels(df_plot['month_year'])
    
    plt.setp(ax_ts2.xaxis.get_majorticklabels(), rotation=45, ha='right')
    
    # Save the combined figure
    import os
    os.makedirs('plots/images', exist_ok=True)
    output_file = 'plots/images/figure1.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"\nCombined visualization saved to: {output_file}")
    
    return fig


def plot_urban_rural_maps_and_timeseries(df_grouped, df_country, gdf, figsize=(12, 14)):
    """
    Create a combined figure with time series on top and difference map on bottom.
    
    Layout:
    - Top: Time series plot (urban and rural as % of climate)
    - Bottom: Single difference map showing (urban % - rural %) of climate articles
    
    Parameters:
    -----------
    df_grouped : pd.DataFrame
        DataFrame with monthly time series data
    df_country : pd.DataFrame
        DataFrame with country-level aggregated data
    gdf : gpd.GeoDataFrame
        GeoDataFrame with country geometries for mapping
    figsize : tuple, optional
        Figure size (width, height)
    
    Returns:
    --------
    fig : matplotlib figure object
    """
    # Import necessary functions
    import sys
    import os
    sys.path.insert(0, os.path.abspath('.'))
    from visualize_article_map import create_difference_map
    import numpy as np
    from matplotlib.colors import LinearSegmentedColormap
    
    print("\nCreating urban/rural maps and time series visualization...")
    
    # Create custom diverging colormap for difference map
    # Purple for rural (negative), white for neutral, teal for urban (positive)
    colors_diverging = ['#8e44ad', '#ffffff', '#16a085']
    cmap_diverging = LinearSegmentedColormap.from_list('urban_rural_diff', colors_diverging)
    
    # Create figure with custom grid
    fig = plt.figure(figsize=figsize)
    gs = gridspec.GridSpec(2, 1, figure=fig, height_ratios=[1, 1.2], hspace=0.35)
    
    # Top row: Time series
    ax_ts = fig.add_subplot(gs[0])
    
    # Bottom row: Difference map
    ax_map = fig.add_subplot(gs[1])
    
    # === CREATE TIME SERIES PLOT ===
    print("\n--- TIME SERIES: Urban and Rural in Climate Coverage ---")
    
    # Calculate percentages
    df_plot = df_grouped.copy()
    df_plot['urban_climate_pct'] = (df_plot['urban'] / df_plot['climate']) * 100
    df_plot['rural_climate_pct'] = (df_plot['rural'] / df_plot['climate']) * 100
    
    # Create x-axis positions
    x = range(len(df_plot))
    
    # Plot urban and rural lines
    ax_ts.plot(x, df_plot['urban_climate_pct'], 
               color='#16a085', linewidth=2.5, marker='o', markersize=5,
               label='Urban')
    ax_ts.plot(x, df_plot['rural_climate_pct'], 
               color='#8e44ad', linewidth=2.5, marker='o', markersize=5,
               label='Rural')
    
    ax_ts.set_xlabel('Month', fontsize=11, fontweight='bold')
    ax_ts.set_ylabel('% of Climate Articles', fontsize=11, fontweight='bold')
    ax_ts.set_title('Urban and Rural in Climate Coverage Over Time', fontsize=12, fontweight='bold', pad=10)
    
    # Styling for time series
    ax_ts.grid(False)
    ax_ts.spines['top'].set_visible(False)
    ax_ts.spines['right'].set_visible(False)
    ax_ts.spines['left'].set_linewidth(1.5)
    ax_ts.spines['bottom'].set_linewidth(1.5)
    ax_ts.legend(frameon=False, loc='best', fontsize=10)
    
    # Format x-axis to prevent label overlap
    n_labels = len(df_plot)
    if n_labels > 20:
        step = n_labels // 15
        tick_positions = range(0, n_labels, step)
        ax_ts.set_xticks(tick_positions)
        ax_ts.set_xticklabels([df_plot['month_year'].iloc[i] for i in tick_positions])
    else:
        ax_ts.set_xticks(x)
        ax_ts.set_xticklabels(df_plot['month_year'])
    
    plt.setp(ax_ts.xaxis.get_majorticklabels(), rotation=45, ha='right')
    
    # === CREATE DIFFERENCE MAP ===
    print("\n--- MAP: Urban - Rural (% of Climate) ---")
    gdf_merged, country_col = create_difference_map(
        gdf, df_country, 
        numerator_col1='urban',
        numerator_col2='rural',
        denominator_col='climate',
        ax=ax_map,
        title='Urban - Rural in Climate Coverage\n(% of Climate Articles)',
        cmap=cmap_diverging
    )
    
    # Save the combined figure
    import os
    os.makedirs('plots/images', exist_ok=True)
    output_file = 'plots/images/urban_rural_maps_timeseries.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"\nUrban/Rural visualization saved to: {output_file}")
    
    return fig


def plot_urban_rural_climate_health_maps_and_timeseries(df_grouped, df_country, gdf, figsize=(12, 14)):
    """
    Create a combined figure with time series on top and difference map on bottom.
    Focuses on urban/rural in health articles (which mention both climate and health).
    
    Layout:
    - Top: Time series plot (urban and rural as % of health articles)
    - Bottom: Single difference map showing (urban % - rural %) of health articles
    
    Parameters:
    -----------
    df_grouped : pd.DataFrame
        DataFrame with monthly time series data
    df_country : pd.DataFrame
        DataFrame with country-level aggregated data
    gdf : gpd.GeoDataFrame
        GeoDataFrame with country geometries for mapping
    figsize : tuple, optional
        Figure size (width, height)
    
    Returns:
    --------
    fig : matplotlib figure object
    """
    # Import necessary functions
    import sys
    import os
    sys.path.insert(0, os.path.abspath('.'))
    from visualize_article_map import create_difference_map
    import numpy as np
    from matplotlib.colors import LinearSegmentedColormap
    
    print("\nCreating urban/rural maps and time series visualization for climate-health stories...")
    
    # Create custom diverging colormap for difference map
    # Purple for rural (negative), white for neutral, teal for urban (positive)
    colors_diverging = ['#8e44ad', '#ffffff', '#16a085']
    cmap_diverging = LinearSegmentedColormap.from_list('urban_rural_diff', colors_diverging)
    
    # Create figure with custom grid
    fig = plt.figure(figsize=figsize)
    gs = gridspec.GridSpec(2, 1, figure=fig, height_ratios=[1, 1.2], hspace=0.35)
    
    # Top row: Time series
    ax_ts = fig.add_subplot(gs[0])
    
    # Bottom row: Difference map
    ax_map = fig.add_subplot(gs[1])
    
    # === CREATE TIME SERIES PLOT ===
    print("\n--- TIME SERIES: Urban and Rural in Health Articles ---")
    
    # Calculate percentages
    df_plot = df_grouped.copy()
    df_plot['urban_health_pct'] = (df_plot['urban'] / df_plot['health']) * 100
    df_plot['rural_health_pct'] = (df_plot['rural'] / df_plot['health']) * 100
    
    # Create x-axis positions
    x = range(len(df_plot))
    
    # Plot urban and rural lines
    ax_ts.plot(x, df_plot['urban_health_pct'], 
               color='#16a085', linewidth=2.5, marker='o', markersize=5,
               label='Urban')
    ax_ts.plot(x, df_plot['rural_health_pct'], 
               color='#8e44ad', linewidth=2.5, marker='o', markersize=5,
               label='Rural')
    
    ax_ts.set_xlabel('Month', fontsize=11, fontweight='bold')
    ax_ts.set_ylabel('% of Health Articles', fontsize=11, fontweight='bold')
    ax_ts.set_title('Urban and Rural in Health Articles Over Time', fontsize=12, fontweight='bold', pad=10)
    
    # Styling for time series
    ax_ts.grid(False)
    ax_ts.spines['top'].set_visible(False)
    ax_ts.spines['right'].set_visible(False)
    ax_ts.spines['left'].set_linewidth(1.5)
    ax_ts.spines['bottom'].set_linewidth(1.5)
    ax_ts.legend(frameon=False, loc='best', fontsize=10)
    
    # Format x-axis to prevent label overlap
    n_labels = len(df_plot)
    if n_labels > 20:
        step = n_labels // 15
        tick_positions = range(0, n_labels, step)
        ax_ts.set_xticks(tick_positions)
        ax_ts.set_xticklabels([df_plot['month_year'].iloc[i] for i in tick_positions])
    else:
        ax_ts.set_xticks(x)
        ax_ts.set_xticklabels(df_plot['month_year'])
    
    plt.setp(ax_ts.xaxis.get_majorticklabels(), rotation=45, ha='right')
    
    # === CREATE DIFFERENCE MAP ===
    print("\n--- MAP: Urban - Rural (% of Health Articles) ---")
    gdf_merged, country_col = create_difference_map(
        gdf, df_country, 
        numerator_col1='urban',
        numerator_col2='rural',
        denominator_col='health',
        ax=ax_map,
        title='Urban - Rural in Health Articles\n(% of Health Articles)',
        cmap=cmap_diverging
    )
    
    # Save the combined figure
    import os
    os.makedirs('plots/images', exist_ok=True)
    output_file = 'plots/images/urban_rural_climate_health_maps_timeseries.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"\nUrban/Rural visualization saved to: {output_file}")
    
    return fig


# Example usage:
# Single plots:
# fig, (ax1, ax2) = plot_climate_health_subplots(df_grouped)
# plt.show()

# For urban/rural plot:
# fig_ur, ax_ur = plot_urban_rural(df_grouped)
# plt.show()

# For combined maps and time series (maps on left, time series on right):
# from visualize_article_map import load_shapefile, df_country
# gdf = load_shapefile()
# fig = plot_combined_maps_and_timeseries(df_grouped, df_country, gdf)
# plt.show()

# For urban/rural analysis (difference maps on left, time series on right):
# from visualize_article_map import load_shapefile, df_country
# gdf = load_shapefile()
# fig = plot_urban_rural_maps_and_timeseries(df_grouped, df_country, gdf)
# plt.show()