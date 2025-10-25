# Plots & Visualization System

This directory contains the complete visualization system for analyzing European climate-health news coverage. The system generates **4 main figures** that form the core of the Lancet Europe climate-health indicator analysis.

## 🚀 Quick Start

### Generate All Figures
```bash
# From project root directory
python plots/make_figures.py
```

This generates all 4 figures in `plots/images/`:
- **`figure1.png`** - Combined maps and time series visualization
- **`figure2.png`** - Urban/rural framing distribution comparison  
- **`figure3.png`** - Inequality coverage time series
- **`figure4.png`** - Types of inequality coverage

## 📁 Directory Contents

```
plots/
├── images/                      # 🎯 Generated figures
│   ├── figure1.png             # Combined maps and time series  
│   ├── figure2.png             # Urban/rural comparison
│   ├── figure3.png             # Inequality time series
│   └── figure4.png             # Inequality types bar chart
├── make_figures.py             # 🚀 Master script (run this!)
├── plot_climate_health.py      # Climate-health maps & trends
├── plot_inequality.py          # Inequality analysis & time series
├── plot_time_series.py         # Time series functionality
├── plot_urban_rural_barchart.py # Urban/rural framing analysis
└── visualize_article_map.py    # Core mapping functionality
```

## 📊 Figure Details

### Figure 1: Combined Maps and Time Series (`figure1.png`)
**Script**: `plot_climate_health.py`

**Description**: Choropleth maps showing geographic patterns alongside time series trends
- **Left panels**: Two maps showing climate coverage proportions by country
- **Right panel**: Time series showing trends over the study period
- **Data**: Country-level aggregated monthly data
- **Purpose**: Geographic and temporal analysis of climate-health coverage

### Figure 2: Urban/Rural Framing (`figure2.png`)  
**Script**: `plot_urban_rural_barchart.py`

**Description**: Bar chart comparing urban/rural framing between article groups
- **Comparison**: Climate articles without health vs. with health framing
- **Categories**: Urban only, rural only, both, neither
- **Statistics**: Includes significance tests and p-values
- **Purpose**: Shows how health framing correlates with geographic context

### Figure 3: Inequality Time Series (`figure3.png`)
**Script**: `plot_inequality.py`

**Description**: Time series showing inequality coverage trends
- **Y-axis**: Proportion of articles with inequality framing
- **X-axis**: Time (monthly)  
- **Features**: Smoothed trend lines and confidence intervals
- **Purpose**: Temporal analysis of climate justice coverage

### Figure 4: Inequality Types (`figure4.png`)
**Script**: `plot_inequality.py` 

**Description**: Horizontal bar chart of inequality topic types
- **Categories**: Different types of inequality coverage (vulnerability, demographics, etc.)
- **Values**: Proportion of health articles covering each type
- **Purpose**: Breakdown of what inequality topics are most covered

## 🔧 Individual Script Usage

### Generate Specific Figures
```bash
# From project root directory

# Figure 1: Combined maps and time series  
python plots/plot_climate_health.py

# Figure 2: Urban/rural comparison
python plots/plot_urban_rural_barchart.py

# Figures 3 & 4: Inequality analysis
python plots/plot_inequality.py
```

### Core Mapping Functions
```bash
# Use visualize_article_map.py functions in other scripts
python -c "from plots.visualize_article_map import load_shapefile; print('Shapefile loaded')"
```

## 🎨 Visualization Features

### Professional Styling
- **Color schemes**: Carefully chosen for accessibility and clarity
- **Fonts**: Consistent typography across all figures
- **Layout**: Optimized spacing and proportions
- **Export**: High-resolution PNG files (300 DPI)

### Geographic Analysis
- **Shapefile**: European countries with EPSG:3035 projection
- **Country coverage**: 40+ European nations (EU, EEA, UK, etc.)
- **Data joining**: Robust country name mapping and validation
- **Missing data handling**: Clear indication of countries without data

### Statistical Analysis
- **Significance testing**: P-values and confidence intervals where appropriate
- **Trend analysis**: Smoothed time series with uncertainty bands  
- **Proportion comparisons**: Statistical tests for group differences
- **Sample sizes**: Clear reporting of underlying data counts

## 📊 Data Dependencies

### Required Datasets
All datasets must be present in `data/articles/`:
- **`lancet_europe_database.jsonl`** - Raw article data with metadata
- **`lancet_europe_dataset_monthly.parquet`** - Monthly aggregated time series  
- **`lancet_europe_dataset_with_dummies.parquet`** - Full classified dataset
- **`lancet_europe_health_subset_with_dummies.parquet`** - Health articles subset

### Geographic Data
- **`data/europe_shapefile/`** - European countries shapefile (EPSG:3035)
- **`data/sources/sources.csv`** - News source to country mapping

## 🛠️ Technical Requirements

### Python Dependencies
```bash
pip install pandas matplotlib geopandas seaborn numpy scipy
```

### Key Packages
- **`pandas`** - Data manipulation and analysis
- **`matplotlib`** - Core plotting functionality  
- **`geopandas`** - Geographic data handling and mapping
- **`seaborn`** - Statistical visualization enhancements
- **`numpy`** - Numerical computations
- **`scipy`** - Statistical testing

### System Requirements
- **Memory**: ~2GB RAM for large dataset processing
- **Storage**: ~100MB for generated high-resolution figures
- **Runtime**: ~10 seconds for all figures on modern hardware

## ⚙️ Customization Options

### Modify Color Schemes
```python
# In any plotting script, change colormap
cmap='YlOrRd'  # Try: 'Blues', 'Greens', 'viridis', 'plasma'
```

### Adjust Figure Sizes
```python
# Modify figsize parameter
fig, ax = plt.subplots(figsize=(12, 8))  # Width x Height in inches
```

### Change Date Ranges
```python
# Filter data by date in any script
df_filtered = df[df['date'] >= '2023-01-01']
```

### Geographic Filtering
```python
# Modify country selection in visualize_article_map.py
european_countries = ['Germany', 'France', 'Spain']  # Custom list
```

## 🔍 Quality Control

### Data Validation
- **Missing data checks**: Scripts verify required datasets exist
- **Country matching**: Robust mapping between article sources and geographic data
- **Date validation**: Proper handling of time series data and missing periods
- **Statistical validation**: Significance testing and confidence intervals

### Output Verification
- **File generation**: All scripts confirm successful figure creation
- **Resolution**: High-DPI output suitable for publication
- **Format consistency**: Standardized styling across all figures
- **Error handling**: Clear error messages for missing data or configuration issues

## 🚨 Troubleshooting

### Common Issues

**ModuleNotFoundError**
```bash
pip install -r requirements.txt
```

**Missing Data Files**
```bash
# Verify data files exist
ls data/articles/
ls data/europe_shapefile/
```

**Empty or Corrupted Figures**
```bash
# Check data file integrity
python -c "import pandas as pd; print(pd.read_parquet('data/articles/lancet_europe_dataset_monthly.parquet').shape)"
```

**Geographic Projection Issues**
```bash
# Reinstall geopandas with full dependencies
pip install geopandas[complete]
```

### Performance Optimization
- **Large datasets**: Scripts automatically handle memory-efficient processing
- **Parallel processing**: Use `make_figures.py` to generate all figures efficiently
- **Caching**: Intermediate results cached where possible to speed up re-runs

## 📈 Usage Examples

### Basic Workflow
```bash
# Generate all figures (recommended)
python plots/make_figures.py

# View outputs
ls plots/images/
# → figure1.png, figure2.png, figure3.png, figure4.png
```

### Advanced Usage
```python
# Custom analysis using plotting functions
from plots.visualize_article_map import load_shapefile, create_map
from plots.plot_time_series import plot_combined_maps_and_timeseries

# Load data
gdf = load_shapefile()
# ... custom analysis ...
```

### Integration with Other Scripts
```python
# Use plotting functions in external scripts
import sys
sys.path.append('plots/')
from visualize_article_map import df_country
from plot_time_series import df_grouped

# Access processed data for custom analysis
print(f"Countries covered: {len(df_country)}")
```

## 📝 Output Specifications

### Figure Specifications
- **Format**: PNG (Portable Network Graphics)
- **Resolution**: 300 DPI (publication quality)
- **Color space**: sRGB  
- **Transparency**: None (white backgrounds)
- **Compression**: Optimized for file size vs. quality

### File Naming Convention
- **`figure1.png`** - Combined maps and time series
- **`figure2.png`** - Urban/rural framing comparison
- **`figure3.png`** - Inequality time series
- **`figure4.png`** - Inequality types breakdown

### Metadata
Each figure includes:
- **Title**: Descriptive figure title
- **Labels**: Clear axis labels and legends
- **Statistics**: Sample sizes, p-values where relevant
- **Data sources**: Implicit in the analysis pipeline

---

**This visualization system provides publication-ready figures for the Lancet Europe climate-health news analysis. All scripts are designed for reproducibility and can be easily adapted for similar analyses.**