"""
Generate bar chart comparing urban/rural framing distribution.

This script creates a bar chart showing:
- Distribution of urban_rural_framing categories in all climate articles
- Distribution of urban_rural_framing categories in health articles (climate+health)
"""

import sys
import os
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def create_urban_rural_barchart(figsize=(10, 6)):
    """
    Create a grouped bar chart comparing urban/rural framing distribution
    between all climate articles and health articles.
    
    Parameters:
    -----------
    figsize : tuple, optional
        Figure size (width, height)
    
    Returns:
    --------
    fig, ax : matplotlib figure and axis objects
    """
    print("=" * 70)
    print("Creating Urban/Rural Framing Distribution Bar Chart (All vs Health)")
    print("=" * 70)
    
    # Load raw datasets to get urban_rural_framing column with all categories
    print("\nLoading datasets...")
    # Load only the column we need to save memory
    df_climate = pd.read_parquet('data/database/lancet_europe_dataset_with_dummies.parquet', 
                                  columns=['urban_rural_framing'])
    df_health = pd.read_parquet('data/database/lancet_europe_health_subset_with_dummies.parquet', 
                                 columns=['urban_rural_framing'])
    
    print(f"Climate articles total: {len(df_climate)}")
    print(f"Health articles total: {len(df_health)}")
    
    # Count urban_rural_framing categories for climate articles
    climate_counts = df_climate['urban_rural_framing'].value_counts()
    climate_total = len(df_climate)
    
    # Count urban_rural_framing categories for health articles
    health_counts = df_health['urban_rural_framing'].value_counts()
    health_total = len(df_health)
    
    # Calculate percentages for all categories
    climate_pct = {
        'neither': (climate_counts.get('neither', 0) / climate_total * 100) if climate_total > 0 else 0,
        'urban': (climate_counts.get('urban', 0) / climate_total * 100) if climate_total > 0 else 0,
        'rural': (climate_counts.get('rural', 0) / climate_total * 100) if climate_total > 0 else 0,
        'both': (climate_counts.get('both', 0) / climate_total * 100) if climate_total > 0 else 0,
    }
    
    health_pct = {
        'neither': (health_counts.get('neither', 0) / health_total * 100) if health_total > 0 else 0,
        'urban': (health_counts.get('urban', 0) / health_total * 100) if health_total > 0 else 0,
        'rural': (health_counts.get('rural', 0) / health_total * 100) if health_total > 0 else 0,
        'both': (health_counts.get('both', 0) / health_total * 100) if health_total > 0 else 0,
    }
    
    print("\nClimate articles distribution:")
    for cat, pct in sorted(climate_pct.items()):
        print(f"  {cat}: {pct:.2f}%")
    
    print("\nHealth articles distribution:")
    for cat, pct in sorted(health_pct.items()):
        print(f"  {cat}: {pct:.2f}%")
    
    # Define categories in order
    categories = ['neither', 'urban', 'rural', 'both']
    
    # Get percentages for each category
    climate_values = [climate_pct[cat] for cat in categories]
    health_values = [health_pct[cat] for cat in categories]
    
    # Create bar chart
    fig, ax = plt.subplots(figsize=figsize)
    
    x = np.arange(len(categories))
    width = 0.35
    gap = 0.05  # Small gap between bars
    
    # Create bars with borders and transparency for visual depth
    bars1 = ax.bar(x - width/2 - gap/2, climate_values, width, label='All Climate Articles', 
                   color='#0072B2', alpha=0.7, edgecolor='#0072B2', linewidth=2)
    bars2 = ax.bar(x + width/2 + gap/2, health_values, width, label='Climate & Health Articles', 
                   color='#E69F00', alpha=0.7, edgecolor='#E69F00', linewidth=2)
    
    # Customize chart
    ax.set_xlabel('Urban/Rural Framing', fontsize=12, fontweight='bold')
    ax.set_ylabel('Percentage of Articles (%)', fontsize=12, fontweight='bold')
    #ax.set_title('', fontsize=14, fontweight='bold', pad=20)
    ax.set_xticks(x)
    
    # Custom descriptive labels for display
    category_labels = ['Neither', 'Urban only', 'Rural only', 'Both urban and rural']
    ax.set_xticklabels(category_labels)
    
    # Add legend
    ax.legend(frameon=False, fontsize=11, loc='upper right')
    
    # Styling
    ax.grid(False)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_linewidth(1.5)
    ax.spines['bottom'].set_linewidth(1.5)
    
    # Add value labels on top of bars
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:.1f}%',
                   ha='center', va='bottom', fontsize=9)
    
    plt.tight_layout()
    
    # Save figure
    os.makedirs('data/images', exist_ok=True)
    output_file = 'data/images/urban_rural_barchart.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"\nBar chart saved to: {output_file}")
    
    return fig, ax


def create_urban_rural_barchart_no_health_vs_health(figsize=(10, 6)):
    """
    Create a grouped bar chart comparing urban/rural framing distribution
    between climate articles without health and climate articles with health.
    
    Parameters:
    -----------
    figsize : tuple, optional
        Figure size (width, height)
    
    Returns:
    --------
    fig, ax : matplotlib figure and axis objects
    """
    print("=" * 70)
    print("Creating Urban/Rural Framing Distribution Bar Chart (No Health vs Health)")
    print("=" * 70)
    
    # Load raw datasets
    print("\nLoading datasets...")
    # Load climate dataset with both urban_rural_framing and health columns
    df_climate_all = pd.read_parquet('data/database/lancet_europe_dataset_with_dummies.parquet', 
                                      columns=['urban_rural_framing', 'health'])
    df_health = pd.read_parquet('data/database/lancet_europe_health_subset_with_dummies.parquet', 
                                 columns=['urban_rural_framing'])
    
    # Filter climate articles to get only those WITHOUT health (health != 1)
    df_climate_no_health = df_climate_all[df_climate_all['health'] != 1]
    
    print(f"Climate articles without health: {len(df_climate_no_health)}")
    print(f"Climate articles with health: {len(df_health)}")
    
    # Count urban_rural_framing categories for climate articles without health
    no_health_counts = df_climate_no_health['urban_rural_framing'].value_counts()
    no_health_total = len(df_climate_no_health)
    
    # Count urban_rural_framing categories for health articles
    health_counts = df_health['urban_rural_framing'].value_counts()
    health_total = len(df_health)
    
    # Calculate percentages for all categories
    no_health_pct = {
        'neither': (no_health_counts.get('neither', 0) / no_health_total * 100) if no_health_total > 0 else 0,
        'urban': (no_health_counts.get('urban', 0) / no_health_total * 100) if no_health_total > 0 else 0,
        'rural': (no_health_counts.get('rural', 0) / no_health_total * 100) if no_health_total > 0 else 0,
        'both': (no_health_counts.get('both', 0) / no_health_total * 100) if no_health_total > 0 else 0,
    }
    
    health_pct = {
        'neither': (health_counts.get('neither', 0) / health_total * 100) if health_total > 0 else 0,
        'urban': (health_counts.get('urban', 0) / health_total * 100) if health_total > 0 else 0,
        'rural': (health_counts.get('rural', 0) / health_total * 100) if health_total > 0 else 0,
        'both': (health_counts.get('both', 0) / health_total * 100) if health_total > 0 else 0,
    }
    
    print("\nClimate articles without health distribution:")
    for cat, pct in sorted(no_health_pct.items()):
        print(f"  {cat}: {pct:.2f}%")
    
    print("\nClimate articles with health distribution:")
    for cat, pct in sorted(health_pct.items()):
        print(f"  {cat}: {pct:.2f}%")
    
    # Define categories in order
    categories = ['neither', 'urban', 'rural', 'both']
    
    # Get percentages for each category
    no_health_values = [no_health_pct[cat] for cat in categories]
    health_values = [health_pct[cat] for cat in categories]
    
    # Create bar chart
    fig, ax = plt.subplots(figsize=figsize)
    
    x = np.arange(len(categories))
    width = 0.35
    gap = 0.05  # Small gap between bars
    
    # Create bars with borders and transparency for visual depth
    bars1 = ax.bar(x - width/2 - gap/2, no_health_values, width, 
                   label=r'Climate articles $\mathit{without}$ health', 
                   color='#0072B2', alpha=0.7, edgecolor='#0072B2', linewidth=2)
    bars2 = ax.bar(x + width/2 + gap/2, health_values, width, 
                   label=r'Climate articles $\mathit{with}$ health', 
                   color='#E69F00', alpha=0.7, edgecolor='#E69F00', linewidth=2)
    
    # Customize chart
    ax.set_xlabel('Urban/Rural Framing', fontsize=12, fontweight='bold')
    ax.set_ylabel('Percentage of Articles (%)', fontsize=12, fontweight='bold')
    #ax.set_title('', fontsize=14, fontweight='bold', pad=20)
    ax.set_xticks(x)
    
    # Custom descriptive labels for display
    category_labels = ['Neither', 'Urban only', 'Rural only', 'Both urban and rural']
    ax.set_xticklabels(category_labels)
    
    # Add legend
    ax.legend(frameon=False, fontsize=11, loc='upper right')
    
    # Styling
    ax.grid(False)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_linewidth(1.5)
    ax.spines['bottom'].set_linewidth(1.5)
    
    # Add value labels on top of bars
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:.1f}%',
                   ha='center', va='bottom', fontsize=9)
    
    plt.tight_layout()
    
    # Save figure
    os.makedirs('data/images', exist_ok=True)
    output_file = 'data/images/urban_rural_barchart_no_health_vs_health.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"\nBar chart saved to: {output_file}")
    
    return fig, ax


def test_urban_rural_proportions():
    """
    Perform difference in proportions tests comparing urban/rural framing
    between climate articles with and without health.
    
    Tests performed:
    1. Proportion with any urban-rural framing (urban, rural, or both) 
       vs. no framing (neither)
    2. Proportion for each individual category (neither, urban, rural, both)
    
    Returns:
    --------
    results : dict
        Dictionary containing test results for each comparison
    """
    print("=" * 70)
    print("Difference in Proportions Tests: Urban/Rural Framing")
    print("=" * 70)
    
    # Load datasets
    print("\nLoading datasets...")
    df_climate_all = pd.read_parquet('data/database/lancet_europe_dataset_with_dummies.parquet', 
                                      columns=['urban_rural_framing', 'health'])
    df_health = pd.read_parquet('data/database/lancet_europe_health_subset_with_dummies.parquet', 
                                 columns=['urban_rural_framing'])
    
    # Filter to get climate articles without health
    df_no_health = df_climate_all[df_climate_all['health'] != 1]
    
    print(f"Climate articles without health: {len(df_no_health)}")
    print(f"Climate articles with health: {len(df_health)}")
    
    results = {}
    
    # =========================================================================
    # Test 1: Any urban-rural framing vs. neither
    # =========================================================================
    print("\n" + "=" * 70)
    print("Test 1: Proportion with ANY urban-rural framing")
    print("(urban only, rural only, or both urban and rural)")
    print("=" * 70)
    
    # Count articles with any framing (not 'neither')
    no_health_any_framing = (df_no_health['urban_rural_framing'] != 'neither').sum()
    health_any_framing = (df_health['urban_rural_framing'] != 'neither').sum()
    
    no_health_total = len(df_no_health)
    health_total = len(df_health)
    
    # Calculate proportions
    prop_no_health = no_health_any_framing / no_health_total
    prop_health = health_any_framing / health_total
    
    print(f"\nWithout health: {no_health_any_framing}/{no_health_total} = {prop_no_health:.4f} ({prop_no_health*100:.2f}%)")
    print(f"With health: {health_any_framing}/{health_total} = {prop_health:.4f} ({prop_health*100:.2f}%)")
    print(f"Difference: {(prop_health - prop_no_health):.4f} ({(prop_health - prop_no_health)*100:.2f} percentage points)")
    
    # Two-proportion z-test
    # Using pooled proportion for standard error
    pooled_prop = (no_health_any_framing + health_any_framing) / (no_health_total + health_total)
    se = np.sqrt(pooled_prop * (1 - pooled_prop) * (1/no_health_total + 1/health_total))
    z_stat = (prop_health - prop_no_health) / se
    p_value = 2 * (1 - stats.norm.cdf(abs(z_stat)))  # Two-tailed test
    
    print(f"\nZ-statistic: {z_stat:.4f}")
    print(f"P-value: {p_value:.6f}")
    
    if p_value < 0.001:
        print("Result: HIGHLY SIGNIFICANT (p < 0.001) ***")
    elif p_value < 0.01:
        print("Result: VERY SIGNIFICANT (p < 0.01) **")
    elif p_value < 0.05:
        print("Result: SIGNIFICANT (p < 0.05) *")
    else:
        print("Result: NOT SIGNIFICANT (p >= 0.05)")
    
    results['any_framing'] = {
        'prop_no_health': prop_no_health,
        'prop_health': prop_health,
        'difference': prop_health - prop_no_health,
        'z_statistic': z_stat,
        'p_value': p_value,
        'count_no_health': no_health_any_framing,
        'total_no_health': no_health_total,
        'count_health': health_any_framing,
        'total_health': health_total
    }
    
    # =========================================================================
    # Test 2: Individual category proportions
    # =========================================================================
    print("\n" + "=" * 70)
    print("Test 2: Proportions for Each Individual Category")
    print("=" * 70)
    
    categories = ['neither', 'urban', 'rural', 'both']
    category_labels = {
        'neither': 'Neither urban nor rural',
        'urban': 'Urban only',
        'rural': 'Rural only',
        'both': 'Both urban and rural'
    }
    
    for category in categories:
        print(f"\n{'-' * 70}")
        print(f"Category: {category_labels[category]}")
        print(f"{'-' * 70}")
        
        # Count articles in this category
        no_health_count = (df_no_health['urban_rural_framing'] == category).sum()
        health_count = (df_health['urban_rural_framing'] == category).sum()
        
        # Calculate proportions
        prop_no_health_cat = no_health_count / no_health_total
        prop_health_cat = health_count / health_total
        
        print(f"Without health: {no_health_count}/{no_health_total} = {prop_no_health_cat:.4f} ({prop_no_health_cat*100:.2f}%)")
        print(f"With health: {health_count}/{health_total} = {prop_health_cat:.4f} ({prop_health_cat*100:.2f}%)")
        print(f"Difference: {(prop_health_cat - prop_no_health_cat):.4f} ({(prop_health_cat - prop_no_health_cat)*100:.2f} percentage points)")
        
        # Two-proportion z-test
        pooled_prop_cat = (no_health_count + health_count) / (no_health_total + health_total)
        se_cat = np.sqrt(pooled_prop_cat * (1 - pooled_prop_cat) * (1/no_health_total + 1/health_total))
        
        if se_cat > 0:  # Avoid division by zero
            z_stat_cat = (prop_health_cat - prop_no_health_cat) / se_cat
            p_value_cat = 2 * (1 - stats.norm.cdf(abs(z_stat_cat)))  # Two-tailed test
            
            print(f"\nZ-statistic: {z_stat_cat:.4f}")
            print(f"P-value: {p_value_cat:.6f}")
            
            if p_value_cat < 0.001:
                print("Result: HIGHLY SIGNIFICANT (p < 0.001) ***")
            elif p_value_cat < 0.01:
                print("Result: VERY SIGNIFICANT (p < 0.01) **")
            elif p_value_cat < 0.05:
                print("Result: SIGNIFICANT (p < 0.05) *")
            else:
                print("Result: NOT SIGNIFICANT (p >= 0.05)")
        else:
            z_stat_cat = np.nan
            p_value_cat = np.nan
            print("\nCannot compute test (zero variance)")
        
        results[category] = {
            'prop_no_health': prop_no_health_cat,
            'prop_health': prop_health_cat,
            'difference': prop_health_cat - prop_no_health_cat,
            'z_statistic': z_stat_cat,
            'p_value': p_value_cat,
            'count_no_health': no_health_count,
            'total_no_health': no_health_total,
            'count_health': health_count,
            'total_health': health_total
        }
    
    print("\n" + "=" * 70)
    print("Summary of P-values:")
    print("=" * 70)
    print(f"{'Category':<30} {'P-value':<15} {'Significance'}")
    print("-" * 70)
    print(f"{'Any framing':<30} {results['any_framing']['p_value']:<15.6f} {'***' if results['any_framing']['p_value'] < 0.001 else '**' if results['any_framing']['p_value'] < 0.01 else '*' if results['any_framing']['p_value'] < 0.05 else 'ns'}")
    for category in categories:
        sig = '***' if results[category]['p_value'] < 0.001 else '**' if results[category]['p_value'] < 0.01 else '*' if results[category]['p_value'] < 0.05 else 'ns'
        print(f"{category_labels[category]:<30} {results[category]['p_value']:<15.6f} {sig}")
    
    print("\nNote: *** p<0.001, ** p<0.01, * p<0.05, ns = not significant")
    
    return results


if __name__ == "__main__":
    # Create both visualizations
    fig1, ax1 = create_urban_rural_barchart()
    
    print("\n")
    
    fig2, ax2 = create_urban_rural_barchart_no_health_vs_health()
    
    print("\n")
    
    # Perform statistical tests
    test_results = test_urban_rural_proportions()
    
    print("\n" + "=" * 70)
    print("All visualizations and statistical tests complete!")
    print("=" * 70)

