import pandas as pd
import matplotlib.pyplot as plt
import geopandas as gpd
import numpy as np
import sys
import warnings
import ast
warnings.filterwarnings('ignore', category=UserWarning)
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

df = pd.read_parquet('data/articles/lancet_europe_health_subset_with_dummies.parquet')

# Parse types column if it's stored as string
print("Checking types column format...")
print(f"Sample types value: {df['inequality_types'].iloc[0]}")
print(f"Type: {type(df['inequality_types'].iloc[0])}")

if isinstance(df['inequality_types'].iloc[0], str):
    print("Converting types from string to list...")
    df['inequality_types'] = df['inequality_types'].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) and x else [])
    print("Conversion complete!")

# Parse types lists and count occurrences
total_rows = len(df)
types_exploded = df['inequality_types'].explode()
type_counts = types_exploded.value_counts()
type_percentages = (type_counts / total_rows * 100).sort_values()

# Create bar chart of inequality types
print("\n" + "="*60)
print("CREATING INEQUALITY TYPES BAR CHART")
print("="*60)

# Ensure output directory exists
import os
os.makedirs('plots/images', exist_ok=True)

fig_types, ax_types = plt.subplots(figsize=(10, 8))

# Create horizontal bar chart with thinner bars
bars = ax_types.barh(type_percentages.index, type_percentages.values,
                     height=0.6, color='#0072B2', alpha=0.8, edgecolor='#0072B2', linewidth=2)

# Add percentage labels on bars
for i, (bar, value) in enumerate(zip(bars, type_percentages.values)):
    ax_types.text(value + 0.2, i, f'{value:.1f}%', 
                  va='center', fontsize=10, fontweight='normal')

# Customize chart
ax_types.set_xlabel('Percentage of Articles (%)', fontsize=12, fontweight='bold')
ax_types.set_title('Distribution of Inequality Types in Climate-Health Articles', 
                   fontsize=14, fontweight='bold', pad=20)

# Styling
ax_types.spines['top'].set_visible(False)
ax_types.spines['right'].set_visible(False)
ax_types.spines['left'].set_linewidth(1.5)
ax_types.spines['bottom'].set_linewidth(1.5)
ax_types.grid(axis='x', alpha=0.3, linestyle='--', linewidth=0.8)

plt.tight_layout()
plt.savefig('plots/images/figure4.png', dpi=300, bbox_inches='tight', facecolor='white')
print("\nInequality types bar chart saved to 'plots/images/figure4.png'")
plt.close()

# Create monthly master file
# Convert date to datetime and extract year-month
df['date'] = pd.to_datetime(df['date'])
df['year_month'] = df['date'].dt.to_period('M')

# Count total articles and inequality articles by month
monthly_total = df.groupby('year_month').size().reset_index(name='total_articles')
monthly_inequality = df[df['inequality'] == 1].groupby('year_month').size().reset_index(name='inequality_articles')

# Merge the two dataframes
monthly_master = pd.merge(monthly_total, monthly_inequality, on='year_month', how='left')

# Create complete date range from 2023-01 to 2025-09
date_range = pd.period_range(start='2023-01', end='2025-09', freq='M')
complete_months = pd.DataFrame({'year_month': date_range})

# Merge with complete date range and fill missing values with 0
monthly_master = pd.merge(complete_months, monthly_master, on='year_month', how='left').fillna(0)

# Calculate percentage of inequality articles
monthly_master['inequality_percentage'] = (monthly_master['inequality_articles'] / monthly_master['total_articles'] * 100).fillna(0)

# Convert year_month to timestamp for plotting
monthly_master['date'] = monthly_master['year_month'].dt.to_timestamp()

# Monthly master file created (not saved to disk)

# Create attractive standalone time series plot
print("\n" + "="*60)
print("CREATING INEQUALITY TIME SERIES PLOT")
print("="*60)

def create_inequality_timeseries(monthly_data, figsize=(14, 7)):
    """
    Create an attractive time series plot showing the proportion of 
    climate-health articles discussing inequality over time.
    
    Parameters:
    -----------
    monthly_data : DataFrame
        Monthly data with columns: date, inequality_percentage, total_articles, inequality_articles
    figsize : tuple
        Figure size (width, height)
    
    Returns:
    --------
    fig, ax : matplotlib figure and axis objects
    """
    fig, ax = plt.subplots(figsize=figsize)
    
    # Calculate smooth trendline using polynomial regression
    # Convert dates to numeric values for fitting
    monthly_data_clean = monthly_data.dropna(subset=['inequality_percentage']).copy()
    x_numeric = np.arange(len(monthly_data_clean))
    y = monthly_data_clean['inequality_percentage'].values
    
    # Fit a polynomial (degree 3 for smooth curve)
    z = np.polyfit(x_numeric, y, 3)
    p = np.poly1d(z)
    y_trend = p(x_numeric)
    
    # Plot smooth light grey trendline
    ax.plot(monthly_data_clean['date'], y_trend, 
            linewidth=4.5, color='#CCCCCC', alpha=0.8,
            label='Trend', zorder=1)
    
    # Plot the main line with markers
    ax.plot(monthly_data['date'], monthly_data['inequality_percentage'], 
            marker='o', linewidth=3.5, markersize=7, 
            color='#0072B2', alpha=0.8,
            markerfacecolor='#0072B2', markeredgecolor='white', 
            markeredgewidth=1.5, label='Monthly percentage', zorder=2)
    
    # Customize axes
    ax.set_xlabel('Month', fontsize=13, fontweight='bold')
    ax.set_ylabel('Percentage of Articles (%)', fontsize=13, fontweight='bold')
    
    # Add legend positioned at y=42 on the plot, centered horizontally
    ax.legend(frameon=True, fontsize=11, loc='center', 
             framealpha=0.95, edgecolor='gray', bbox_to_anchor=(0.5, 0.95), ncol=2)
    
    # Styling
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_linewidth(1.5)
    ax.spines['bottom'].set_linewidth(1.5)
    
    # Set x-axis ticks to show all months
    ax.set_xticks(monthly_data['date'])
    
    # Label every other month on x-axis
    labels = []
    for i, date in enumerate(monthly_data['date']):
        if i % 2 == 0:
            labels.append(date.strftime('%Y-%m-%d'))
        else:
            labels.append('')
    ax.set_xticklabels(labels)
    
    # Format x-axis dates
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')
    
    plt.tight_layout()
    
    return fig, ax

# Create and save the time series plot
fig_ts, ax_ts = create_inequality_timeseries(monthly_master)
plt.savefig('plots/images/figure3.png', dpi=300, bbox_inches='tight', facecolor='white')
print("\nInequality time series plot saved to 'plots/images/figure3.png'")
plt.close()

# ============================================================================
# MAP VISUALIZATION CODE (COMMENTED OUT - ONLY TIME SERIES PLOT IS USED)
# ============================================================================
# The map and 2-panel visualization code has been commented out.
# Only the standalone time series plot is generated.

# Analyze relationship between urban/rural framing and inequality
# print("\n" + "="*60)
# print("URBAN/RURAL FRAMING AND INEQUALITY ANALYSIS")
# print("="*60)

# # Create crosstab
# crosstab = pd.crosstab(df['urban_rural_framing'], df['inequality'], 
#                        margins=True, margins_name='Total')
# print("\nCrosstab of Urban/Rural Framing vs Inequality:")
# print(crosstab)

# # Calculate percentages - what % of each urban/rural category discuss inequality
# crosstab_pct = pd.crosstab(df['urban_rural_framing'], df['inequality'], 
#                            normalize='index') * 100
# print("\nPercentage of articles discussing inequality by urban/rural framing:")
# print(crosstab_pct.round(2))

# # What % of inequality articles fall into each urban/rural category
# inequality_by_framing = df[df['inequality']].groupby('urban_rural_framing').size()
# total_inequality = df['inequality'].sum()
# inequality_distribution = (inequality_by_framing / total_inequality * 100).sort_values(ascending=False)
# print(f"\nDistribution of inequality articles by urban/rural framing:")
# print(inequality_distribution.round(2))

# # Create grouped bar chart comparing inequality rates by urban/rural framing
# framing_categories = crosstab_pct.index[:-1] if 'Total' in crosstab_pct.index else crosstab_pct.index
# inequality_pct_by_framing = crosstab_pct.loc[framing_categories, True] if True in crosstab_pct.columns else pd.Series()

# fig, ax = plt.subplots(figsize=(12, 6))
# bars = ax.barh(inequality_pct_by_framing.index, inequality_pct_by_framing.values,
#                color='steelblue', edgecolor='darkblue', linewidth=1.2)

# # Add percentage labels on bars
# for i, (bar, value) in enumerate(zip(bars, inequality_pct_by_framing.values)):
#     ax.text(value + 0.2, i, f'{value:.1f}%', 
#             va='center', fontsize=10, fontweight='bold')

# ax.set_xlabel('Percentage Discussing Inequality (%)', fontsize=12, fontweight='bold')
# ax.set_title('Percentage of Articles Discussing Inequality by Urban/Rural Framing', 
#              fontsize=14, fontweight='bold', pad=20)
# ax.spines['top'].set_visible(False)
# ax.spines['right'].set_visible(False)
# ax.grid(axis='x', alpha=0.3, linestyle='--')
# plt.tight_layout()
# plt.show()

# # Create stacked bar chart showing distribution of urban/rural framing
# fig, ax = plt.subplots(figsize=(10, 6))
# categories = ['Non-Inequality', 'Inequality']
# framing_labels = inequality_distribution.index.tolist()

# # Calculate counts for non-inequality articles
# non_inequality_by_framing = df[~df['inequality']].groupby('urban_rural_framing').size()
# total_non_inequality = (~df['inequality']).sum()

# # Create data for stacked bar
# inequality_counts = [df[~df['inequality']].groupby('urban_rural_framing').size().get(label, 0) 
#                     for label in framing_labels]
# non_inequality_counts = [df[df['inequality']].groupby('urban_rural_framing').size().get(label, 0) 
#                         for label in framing_labels]

# x = range(len(framing_labels))
# width = 0.35

# bars1 = ax.bar(x, inequality_counts, width, label='Non-Inequality', 
#                color='lightgray', edgecolor='gray', linewidth=1)
# bars2 = ax.bar(x, non_inequality_counts, width, bottom=inequality_counts,
#                label='Inequality', color='steelblue', edgecolor='darkblue', linewidth=1)

# ax.set_xlabel('Urban/Rural Framing', fontsize=12, fontweight='bold')
# ax.set_ylabel('Number of Articles', fontsize=12, fontweight='bold')
# ax.set_title('Distribution of Articles by Urban/Rural Framing and Inequality', 
#              fontsize=14, fontweight='bold', pad=20)
# ax.set_xticks(x)
# ax.set_xticklabels(framing_labels, rotation=45, ha='right')
# ax.legend()
# ax.spines['top'].set_visible(False)
# ax.spines['right'].set_visible(False)
# ax.grid(axis='y', alpha=0.3, linestyle='--')
# plt.tight_layout()
# plt.show()



