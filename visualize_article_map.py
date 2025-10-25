"""
Visualize article proportions by European country using shapefile data.

This script:
1. Loads a European countries shapefile
2. Loads article data by country from the monthly aggregated dataset
3. Calculates proportions based on numerator and denominator columns
4. Joins the proportions with the shapefile
5. Creates a choropleth map showing article proportions by country
"""

import json
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from collections import Counter
from utils import load_sources

# Configuration
SHAPEFILE_PATH = 'data/europe_shapefile/CNTR_RG_20M_2024_3035.shp'
ARTICLES_PATH = 'data/climate_articles.jsonl'
SOURCES_PATH = 'data/sources/sources.csv'

# Load and aggregate monthly data
df_monthly = pd.read_parquet('data/database/lancet_europe_dataset_monthly.parquet')

# Group by country and sum metrics
df_country = df_monthly.groupby('country_name').agg({
    'article_count': 'sum',
    'climate': 'sum', 
    'health': 'sum',
    'climate_health': 'sum',
    'urban': 'sum',
    'rural': 'sum'
}).reset_index()


def load_articles_by_country():
    """
    Load articles and count them by country using the sources mapping.
    
    Returns:
        pd.DataFrame: DataFrame with country names and article counts
    """
    print("Loading sources mapping...")
    sources_df = load_sources()
    
    # Create a mapping from source_uri to country_name
    source_to_country = dict(zip(sources_df['source_uri'], sources_df['country_name']))
    
    print(f"Loaded {len(source_to_country)} sources")
    
    print("Counting articles by country...")
    country_counts = Counter()
    
    # Read articles and count by country
    with open(ARTICLES_PATH, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f):
            if i % 50000 == 0:
                print(f"  Processed {i} articles...")
            
            try:
                article = json.loads(line)
                source_uri = article.get('source', {}).get('uri')
                
                if source_uri in source_to_country:
                    country = source_to_country[source_uri]
                    country_counts[country] += 1
            except json.JSONDecodeError:
                continue
    
    print(f"Total articles processed: {i+1}")
    
    # Convert to DataFrame
    country_df = pd.DataFrame([
        {'country_name': country, 'article_count': count}
        for country, count in country_counts.items()
    ])
    
    print(f"\nArticle counts by country:")
    print(country_df.sort_values('article_count', ascending=False).to_string(index=False))
    
    return country_df

def load_shapefile():
    """
    Load the European countries shapefile and filter to European countries only.
    
    Returns:
        gpd.GeoDataFrame: GeoDataFrame with European country geometries
    """
    print("\nLoading shapefile...")
    gdf = gpd.read_file(SHAPEFILE_PATH)
    
    print(f"Shapefile loaded: {gdf.shape[0]} total regions")
    
    # Define European country ISO3 codes
    # Only including countries present in the data sources + immediate neighbors for geographic context
    european_iso_codes = {
        # EU countries
        'AUT', 'BEL', 'BGR', 'HRV', 'CYP', 'CZE', 'DNK', 'EST', 'FIN', 'FRA',
        'DEU', 'GRC', 'HUN', 'IRL', 'ITA', 'LVA', 'LTU', 'LUX', 'MLT', 'NLD',
        'POL', 'PRT', 'ROU', 'SVK', 'SVN', 'ESP', 'SWE',
        # Non-EU European countries in data sources
        'GBR', 'NOR', 'CHE', 'ISL', 'ALB', 'BIH', 'MKD', 'MNE', 'SRB', 
        'TUR', 'UKR', 'MDA', 'LIE'
    }
    
    # Filter to only European countries
    gdf_europe = gdf[gdf['ISO3_CODE'].isin(european_iso_codes)].copy()
    
    print(f"Filtered to {gdf_europe.shape[0]} European countries")
    print(f"Columns: {gdf_europe.columns.tolist()}")
    print(f"\nEuropean countries included:")
    print(sorted(gdf_europe['NAME_ENGL'].tolist()))
    
    return gdf_europe

def create_map(gdf, country_df, numerator_col, denominator_col, ax=None, title=None, cmap='YlOrRd', show_percentage=False):
    """
    Create a choropleth map showing article proportions by country.
    
    Args:
        gdf (gpd.GeoDataFrame): GeoDataFrame with country geometries
        country_df (pd.DataFrame): DataFrame with article data by country
        numerator_col (str): Column name to use as numerator
        denominator_col (str): Column name to use as denominator
        ax (matplotlib.axes.Axes, optional): Axes to plot on. If None, creates new figure
        title (str, optional): Custom title for the map. If None, generates default title
        cmap (str, optional): Colormap for the choropleth. Default is 'YlOrRd'
        show_percentage (bool, optional): If True, multiply proportion by 100 for display. Default is False
    """
    # Determine the country name column in the shapefile
    # Common possibilities: NAME_ENGL, CNTR_NAME, NAME, etc.
    country_col = None
    for col in ['NAME_ENGL', 'CNTR_NAME', 'NAME', 'COUNTRY']:
        if col in gdf.columns:
            country_col = col
            break
    
    if country_col is None:
        print("\nAvailable columns in shapefile:")
        print(gdf.columns.tolist())
        raise ValueError("Could not find country name column in shapefile")
    
    print(f"\nUsing '{country_col}' column for country names")
    
    # Create country name mapping to handle differences between sources and shapefile
    country_name_mapping = {
        'Macedonia': 'North Macedonia',
        'Bosnia and Herzegovina': 'Bosnia and Herzegovina',
        'Czech Republic': 'Czechia',
        'United Kingdom': 'United Kingdom',
        'Turkey': 'Türkiye',
    }
    
    # Apply mapping
    country_df['country_name_mapped'] = country_df['country_name'].replace(country_name_mapping)
    
    # Merge the data
    print("\nMerging article data with shapefile...")
    gdf_merged = gdf.merge(
        country_df,
        left_on=country_col,
        right_on='country_name_mapped',
        how='left'
    )
    
    # Calculate proportion (handling division by zero)
    print(f"\nCalculating proportion: {numerator_col} / {denominator_col}")
    
    # Use numpy's divide to handle division by zero safely
    import numpy as np
    gdf_merged['proportion'] = np.where(
        gdf_merged[denominator_col] > 0,
        gdf_merged[numerator_col] / gdf_merged[denominator_col],
        0
    )
    
    # Replace any remaining NaN or inf values with 0
    gdf_merged['proportion'] = gdf_merged['proportion'].replace([np.inf, -np.inf], 0).fillna(0)
    
    # Create display column for plotting (multiply by 100 if showing percentage)
    if show_percentage:
        gdf_merged['display_value'] = gdf_merged['proportion'] * 100
    else:
        gdf_merged['display_value'] = gdf_merged['proportion']
    
    print(f"Countries with data: {(gdf_merged['proportion'] > 0).sum()}")
    print(f"Countries without data: {(gdf_merged['proportion'] == 0).sum()}")
    print(f"Proportion range: {gdf_merged['proportion'].min():.4f} to {gdf_merged['proportion'].max():.4f}")
    
    # Create the map
    print("\nCreating map...")
    # Create figure only if ax is not provided
    created_fig = False
    if ax is None:
        fig, ax_main = plt.subplots(figsize=(14, 10))
        created_fig = True
    else:
        ax_main = ax
    
    # Define outlying islands to exclude from continental Europe view
    outliers = ['Iceland', 'Malta']
    
    # Focus on continental Europe + UK and Ireland
    gdf_main = gdf_merged[~gdf_merged[country_col].isin(outliers)].copy()
    
    # Filter out small island territories by keeping only the largest geometries per country
    # This removes overseas territories like Canary Islands, Azores, etc.
    # We'll dissolve multipolygons and filter by area
    import warnings
    warnings.filterwarnings('ignore', category=UserWarning)
    
    # Explode multipolygons into individual polygons
    gdf_exploded = gdf_main.explode(index_parts=True).reset_index(drop=False)
    
    # Calculate area for each polygon
    gdf_exploded['area'] = gdf_exploded.geometry.area
    
    # Get centroid of each polygon to filter by geographic location
    gdf_exploded['centroid'] = gdf_exploded.geometry.centroid
    gdf_exploded['lon'] = gdf_exploded['centroid'].x
    gdf_exploded['lat'] = gdf_exploded['centroid'].y
    
    # Define bounding box for mainland Europe + UK/Ireland
    # This excludes Atlantic islands (Azores, Canary Islands, etc.)
    min_lon = 2000000  # Western limit (excludes far Atlantic islands)
    max_lon = 7500000  # Eastern limit
    min_lat = 1000000  # Southern limit
    max_lat = 7500000  # Northern limit (but we already excluded Iceland)
    
    # Filter by bounding box
    gdf_exploded = gdf_exploded[
        (gdf_exploded['lon'] >= min_lon) &
        (gdf_exploded['lon'] <= max_lon) &
        (gdf_exploded['lat'] >= min_lat) &
        (gdf_exploded['lat'] <= max_lat)
    ]
    
    # For each country, keep only polygons with area > 10% of the largest polygon
    # This keeps mainland + nearby islands but removes distant territories
    filtered_geoms = []
    for country in gdf_exploded[country_col].unique():
        country_data = gdf_exploded[gdf_exploded[country_col] == country]
        max_area = country_data['area'].max()
        # Keep polygons that are at least 10% of the largest polygon area
        large_polys = country_data[country_data['area'] > max_area * 0.1]
        filtered_geoms.append(large_polys)
    
    gdf_filtered = pd.concat(filtered_geoms, ignore_index=True)
    
    # Dissolve back to one geometry per country
    gdf_main = gdf_filtered.dissolve(by=country_col, aggfunc='first').reset_index()
    
    # Plot map (continental Europe + UK/Ireland only, no distant islands)
    gdf_main.plot(
        column='display_value',
        ax=ax_main,
        legend=True,
        cmap=cmap,
        edgecolor='black',
        linewidth=0.5,
        legend_kwds={
            'orientation': 'vertical',
            'shrink': 0.3,
            'aspect': 15,
            'pad': 0.02
        }
    )
    
    # Set title with formatting (bold main title, regular subtitle)
    if title is None:
        title = f'Proportion of {numerator_col} to {denominator_col} by European Country'
    
    # Check if title has newline (for two-part titles with different formatting)
    if '\n' in title:
        parts = title.split('\n')
        # Add bold first line as title
        ax_main.set_title(parts[0], fontsize=12, fontweight='bold', pad=18)
        # Add regular second line as text annotation below the title
        ax_main.text(0.5, 1.005, parts[1], transform=ax_main.transAxes, 
                     fontsize=12, ha='center', va='top', fontweight='normal')
    else:
        ax_main.set_title(title, fontsize=12, fontweight='bold', pad=10)
    
    ax_main.axis('off')
    
    # Save the map only if we created the figure
    if created_fig:
        import os
        os.makedirs('data/images', exist_ok=True)
        output_file = 'data/images/article_frequency_map.png'
        plt.savefig(output_file, dpi=300, bbox_inches='tight', facecolor='white')
        print(f"\nMap saved to: {output_file}")
        plt.close()
    
    return gdf_merged, country_col

def create_two_maps(gdf, country_df):
    """
    Create two maps in a grid:
    - Left: climate / article_count
    - Right: health / climate
    
    Args:
        gdf (gpd.GeoDataFrame): GeoDataFrame with country geometries
        country_df (pd.DataFrame): DataFrame with article data by country
    
    Returns:
        tuple: (fig, (ax1, ax2), gdf_merged1, gdf_merged2, country_col)
    """
    print("\nCreating two-map grid visualization...")
    
    # Create figure with two subplots
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(24, 10))
    
    # Map 1: climate / article_count
    print("\n--- MAP 1: Climate / Article Count ---")
    gdf_merged1, country_col = create_map(
        gdf, country_df, 
        numerator_col='climate', 
        denominator_col='article_count',
        ax=ax1,
        title='Climate Coverage\n(% of All Articles)'
    )
    
    # Map 2: health / climate
    print("\n--- MAP 2: Health / Climate ---")
    gdf_merged2, _ = create_map(
        gdf, country_df, 
        numerator_col='health', 
        denominator_col='climate',
        ax=ax2,
        title='Health Topics in Climate Coverage\n(% of Climate Articles)'
    )
    
    # Save the combined figure
    import os
    os.makedirs('data/images', exist_ok=True)
    output_file = 'data/images/article_frequency_maps_grid.png'
    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"\nCombined map saved to: {output_file}")
    
    plt.show()
    
    return fig, (ax1, ax2), gdf_merged1, gdf_merged2, country_col

def create_difference_map(gdf, country_df, numerator_col1, numerator_col2, denominator_col, ax=None, title=None, cmap='RdBu_r'):
    """
    Create a choropleth map showing the difference between two proportions by country.
    Calculates: (numerator_col1/denominator_col - numerator_col2/denominator_col) * 100
    
    Args:
        gdf (gpd.GeoDataFrame): GeoDataFrame with country geometries
        country_df (pd.DataFrame): DataFrame with article data by country
        numerator_col1 (str): First column name to use as numerator (e.g., 'urban')
        numerator_col2 (str): Second column name to use as numerator (e.g., 'rural')
        denominator_col (str): Column name to use as denominator
        ax (matplotlib.axes.Axes, optional): Axes to plot on. If None, creates new figure
        title (str, optional): Custom title for the map. If None, generates default title
        cmap (str or colormap, optional): Colormap for the choropleth. Default is 'RdBu_r'
    
    Returns:
        tuple: (gdf_merged, country_col)
    """
    # Determine the country name column in the shapefile
    country_col = None
    for col in ['NAME_ENGL', 'CNTR_NAME', 'NAME', 'COUNTRY']:
        if col in gdf.columns:
            country_col = col
            break
    
    if country_col is None:
        print("\nAvailable columns in shapefile:")
        print(gdf.columns.tolist())
        raise ValueError("Could not find country name column in shapefile")
    
    print(f"\nUsing '{country_col}' column for country names")
    
    # Create country name mapping
    country_name_mapping = {
        'Macedonia': 'North Macedonia',
        'Bosnia and Herzegovina': 'Bosnia and Herzegovina',
        'Czech Republic': 'Czechia',
        'United Kingdom': 'United Kingdom',
        'Turkey': 'Türkiye',
    }
    
    # Apply mapping
    country_df['country_name_mapped'] = country_df['country_name'].replace(country_name_mapping)
    
    # Merge the data
    print("\nMerging article data with shapefile...")
    gdf_merged = gdf.merge(
        country_df,
        left_on=country_col,
        right_on='country_name_mapped',
        how='left'
    )
    
    # Calculate difference in proportions as percentage
    print(f"\nCalculating difference: ({numerator_col1}/{denominator_col} - {numerator_col2}/{denominator_col}) * 100")
    
    import numpy as np
    
    # Calculate proportions
    prop1 = np.where(
        gdf_merged[denominator_col] > 0,
        gdf_merged[numerator_col1] / gdf_merged[denominator_col],
        0
    )
    prop2 = np.where(
        gdf_merged[denominator_col] > 0,
        gdf_merged[numerator_col2] / gdf_merged[denominator_col],
        0
    )
    
    # Calculate difference and convert to percentage
    gdf_merged['difference'] = (prop1 - prop2) * 100
    gdf_merged['difference'] = gdf_merged['difference'].replace([np.inf, -np.inf], 0).fillna(0)
    
    print(f"Countries with data: {(gdf_merged[denominator_col] > 0).sum()}")
    print(f"Difference range: {gdf_merged['difference'].min():.2f}% to {gdf_merged['difference'].max():.2f}%")
    
    # Create the map
    print("\nCreating difference map...")
    created_fig = False
    if ax is None:
        fig, ax_main = plt.subplots(figsize=(14, 10))
        created_fig = True
    else:
        ax_main = ax
    
    # Define outlying islands to exclude
    outliers = ['Iceland', 'Malta']
    gdf_main = gdf_merged[~gdf_merged[country_col].isin(outliers)].copy()
    
    # Filter out small island territories
    import warnings
    warnings.filterwarnings('ignore', category=UserWarning)
    
    gdf_exploded = gdf_main.explode(index_parts=True).reset_index(drop=False)
    gdf_exploded['area'] = gdf_exploded.geometry.area
    gdf_exploded['centroid'] = gdf_exploded.geometry.centroid
    gdf_exploded['lon'] = gdf_exploded['centroid'].x
    gdf_exploded['lat'] = gdf_exploded['centroid'].y
    
    # Bounding box for mainland Europe
    min_lon = 2000000
    max_lon = 7500000
    min_lat = 1000000
    max_lat = 7500000
    
    gdf_exploded = gdf_exploded[
        (gdf_exploded['lon'] >= min_lon) &
        (gdf_exploded['lon'] <= max_lon) &
        (gdf_exploded['lat'] >= min_lat) &
        (gdf_exploded['lat'] <= max_lat)
    ]
    
    # Keep only large polygons
    filtered_geoms = []
    for country in gdf_exploded[country_col].unique():
        country_data = gdf_exploded[gdf_exploded[country_col] == country]
        max_area = country_data['area'].max()
        large_polys = country_data[country_data['area'] > max_area * 0.1]
        filtered_geoms.append(large_polys)
    
    gdf_filtered = pd.concat(filtered_geoms, ignore_index=True)
    gdf_main = gdf_filtered.dissolve(by=country_col, aggfunc='first').reset_index()
    
    # Get max absolute value for symmetric colorbar
    vmax = max(abs(gdf_main['difference'].min()), abs(gdf_main['difference'].max()))
    
    # Plot map with symmetric colorbar centered at 0
    gdf_main.plot(
        column='difference',
        ax=ax_main,
        legend=True,
        cmap=cmap,
        edgecolor='black',
        linewidth=0.5,
        vmin=-vmax,
        vmax=vmax,
        legend_kwds={
            'orientation': 'vertical',
            'shrink': 0.3,
            'aspect': 15,
            'pad': 0.02
        }
    )
    
    # Set title with formatting
    if title is None:
        title = f'{numerator_col1} - {numerator_col2} (% of {denominator_col})'
    
    if '\n' in title:
        parts = title.split('\n')
        ax_main.set_title(parts[0], fontsize=12, fontweight='bold', pad=18)
        ax_main.text(0.5, 1.005, parts[1], transform=ax_main.transAxes, 
                     fontsize=12, ha='center', va='top', fontweight='normal')
    else:
        ax_main.set_title(title, fontsize=12, fontweight='bold', pad=10)
    
    ax_main.axis('off')
    
    # Save if we created the figure
    if created_fig:
        import os
        os.makedirs('data/images', exist_ok=True)
        output_file = 'data/images/difference_map.png'
        plt.savefig(output_file, dpi=300, bbox_inches='tight', facecolor='white')
        print(f"\nDifference map saved to: {output_file}")
        plt.close()
    
    return gdf_merged, country_col

def save_summary_table(gdf_merged, country_col, numerator_col, denominator_col):
    """
    Save a summary table of proportions by country.
    
    Args:
        gdf_merged (gpd.GeoDataFrame): Merged GeoDataFrame with proportions
        country_col (str): Name of the country column
        numerator_col (str): Name of the numerator column
        denominator_col (str): Name of the denominator column
    """
    import os
    
    # Create summary DataFrame
    summary_df = gdf_merged[gdf_merged['proportion'] > 0][[
        country_col, numerator_col, denominator_col, 'proportion'
    ]].copy()
    summary_df = summary_df.sort_values('proportion', ascending=False)
    
    # Save to CSV
    os.makedirs('data/images', exist_ok=True)
    output_file = 'data/images/article_proportion_summary.csv'
    summary_df.to_csv(output_file, index=False)
    print(f"Summary table saved to: {output_file}")

def main(numerator_col='climate_health', denominator_col='article_count'):
    """
    Main execution function.
    
    Args:
        numerator_col (str): Column name to use as numerator for proportion
        denominator_col (str): Column name to use as denominator for proportion
    """
    print("=" * 60)
    print("European Climate & Health News Articles Map Visualization")
    print("=" * 60)
    print(f"Plotting proportion: {numerator_col} / {denominator_col}")
    print("=" * 60)
    
    # Use the pre-loaded df_country data
    country_df = df_country
    
    print(f"\nCountry data loaded: {len(country_df)} countries")
    print(f"Available columns: {country_df.columns.tolist()}")
    
    # Load shapefile
    gdf = load_shapefile()
    
    # Create map
    gdf_merged, country_col = create_map(gdf, country_df, numerator_col, denominator_col)
    
    # Save summary table
    save_summary_table(gdf_merged, country_col, numerator_col, denominator_col)
    
    print("\n" + "=" * 60)
    print("Visualization complete!")
    print("=" * 60)
    
    return gdf_merged

def main_two_maps():
    """
    Main execution function for two-map grid visualization.
    Creates a grid with:
    - Map 1: climate / article_count
    - Map 2: health / climate
    """
    print("=" * 60)
    print("European Climate & Health News Articles - Two-Map Grid")
    print("=" * 60)
    
    # Use the pre-loaded df_country data
    country_df = df_country
    
    print(f"\nCountry data loaded: {len(country_df)} countries")
    print(f"Available columns: {country_df.columns.tolist()}")
    
    # Load shapefile
    gdf = load_shapefile()
    
    # Create two maps in grid
    fig, (ax1, ax2), gdf_merged1, gdf_merged2, country_col = create_two_maps(gdf, country_df)
    
    print("\n" + "=" * 60)
    print("Two-map visualization complete!")
    print("=" * 60)
    
    return fig, gdf_merged1, gdf_merged2

def main_combined_with_timeseries():
    """
    Main execution function for combined maps and time series visualization.
    Creates a single figure with:
    - Top: Two maps (climate/article_count and health/climate)
    - Bottom: Two time series plots
    """
    print("=" * 60)
    print("Combined Maps and Time Series Visualization")
    print("=" * 60)
    
    # Load shapefile
    gdf = load_shapefile()
    
    # Load country data
    country_df = df_country
    
    # Import time series data and function
    from analysis.plot_time_series import plot_combined_maps_and_timeseries, df_grouped
    
    # Create combined visualization
    fig = plot_combined_maps_and_timeseries(df_grouped, country_df, gdf)
    
    print("\n" + "=" * 60)
    print("Combined visualization complete!")
    print("=" * 60)
    
    return fig

if __name__ == "__main__":
    # Single map example:
    #df_merged = main(numerator_col='climate', denominator_col='article_count')
    #df_merged = main(numerator_col='health', denominator_col='climate')
    
    # Two-map grid:
    #fig, gdf_merged1, gdf_merged2 = main_two_maps()
    
    # Combined maps and time series:
    fig = main_combined_with_timeseries()
    plt.show()

