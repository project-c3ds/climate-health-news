# European Climate & Health News Article Visualization

This documentation explains how to use the visualization scripts to view and analyze article frequencies across European countries.

## Overview

Two main scripts are provided:

1. **`visualize_article_map.py`** - Generates a choropleth map showing article frequencies by country
2. **`explore_shapefile_data.py`** - Interactive tool for exploring the shapefile and article data

## Requirements

Install the required packages:

```bash
pip install -r requirements.txt
```

Key dependencies:
- `geopandas` - For working with geospatial data
- `matplotlib` - For creating maps and visualizations
- `pandas` - For data manipulation

## 1. Visualize Article Map

### Quick Start

Run the main visualization script:

```bash
python visualize_article_map.py
```

### What It Does

1. **Loads article data** from `data/climate_articles.jsonl`
2. **Counts articles by country** using the sources mapping
3. **Filters to European countries only** (46 countries)
4. **Generates a choropleth map** showing article frequencies
5. **Saves outputs**:
   - Map: `data/images/article_frequency_map.png`
   - Summary table: `data/images/article_frequency_summary.csv`

### Output

The script produces:

- **Map visualization** - Color-coded map with article counts labeled on each country
- **Summary CSV** - Table of countries and their article counts, sorted by frequency

### European Countries Included

The visualization includes 46 European countries:
- All EU member states
- EFTA countries (Norway, Iceland, Switzerland, Liechtenstein)
- Other European countries (UK, Ukraine, Turkey, Serbia, etc.)

## 2. Explore Shapefile Data

### Interactive Exploration

The explore script provides multiple ways to analyze the data:

#### View Shapefile Information

```bash
python explore_shapefile_data.py --action explore
```

Shows:
- Total regions in shapefile
- Coordinate reference system
- Available columns
- Sample European countries

#### Get Article Statistics

```bash
python explore_shapefile_data.py --action stats
```

Displays:
- Total articles by country
- Top 10 countries by article count
- Language distribution

#### Query Specific Country

```bash
python explore_shapefile_data.py --action query --country "Ireland"
```

Shows:
- News sources in the country
- Total articles
- Date range
- Sample articles

Available countries include: Albania, Austria, Belgium, Bulgaria, Croatia, Cyprus, Czechia, Denmark, Estonia, Finland, France, Germany, Greece, Hungary, Iceland, Ireland, Italy, Latvia, Lithuania, Luxembourg, Malta, Moldova, Netherlands, Norway, Poland, Portugal, Romania, Serbia, Slovakia, Slovenia, Spain, Sweden, Switzerland, Turkey, Ukraine, United Kingdom, and more.

#### Create Custom Map

Highlight specific countries:

```bash
python explore_shapefile_data.py --action map --countries "Ireland" "United Kingdom" "France" --title "UK and Ireland Focus"
```

#### Export Data

Export the merged data in different formats:

```bash
# Export as CSV
python explore_shapefile_data.py --action export --format csv

# Export as GeoJSON (includes geometry)
python explore_shapefile_data.py --action export --format geojson

# Export as JSON
python explore_shapefile_data.py --action export --format json
```

Exports are saved to `data/exports/`

## Data Sources

### Shapefile
- **Location**: `data/europe_shapefile/CNTR_RG_20M_2024_3035.shp`
- **Source**: European countries shapefile
- **Projection**: EPSG:3035 (ETRS89-extended / LAEA Europe)

### Articles
- **Location**: `data/climate_articles.jsonl`
- **Format**: JSONL (one JSON object per line)
- **Fields**: uri, lang, date, title, body, source, url, etc.
- **Total**: ~389,151 articles

### Sources Mapping
- **Location**: `data/sources/sources.csv`
- **Purpose**: Maps news sources to countries
- **Total**: 184 sources across 38 European countries

## Article Frequency Summary

Top 10 countries by article count:

1. **United Kingdom**: 109,393 articles
2. **Spain**: 41,349 articles
3. **Germany**: 39,158 articles
4. **Turkey**: 28,409 articles
5. **Ireland**: 21,449 articles
6. **Greece**: 19,678 articles
7. **Austria**: 15,349 articles
8. **France**: 12,287 articles
9. **Netherlands**: 10,518 articles
10. **Romania**: 10,186 articles

## Customization

### Modify European Country List

Edit the `european_iso_codes` set in either script to add/remove countries:

```python
european_iso_codes = {
    'AUT', 'BEL', 'BGR', 'HRV', 'CYP', 'CZE', 'DNK', 'EST', 'FIN', 'FRA',
    'DEU', 'GRC', 'HUN', 'IRL', 'ITA', 'LVA', 'LTU', 'LUX', 'MLT', 'NLD',
    'POL', 'PRT', 'ROU', 'SVK', 'SVN', 'ESP', 'SWE', 'GBR', 'NOR', 'CHE',
    'ISL', 'ALB', 'BIH', 'MKD', 'MNE', 'SRB', 'TUR', 'UKR', 'MDA', 'LIE',
    # Add more ISO3 codes as needed
}
```

### Change Color Scheme

Modify the `cmap` parameter in `create_map()`:

```python
gdf_merged.plot(
    column='article_count',
    cmap='YlOrRd',  # Try: 'Blues', 'Greens', 'viridis', 'plasma'
    ...
)
```

### Adjust Map Size

Change figure size in `create_map()`:

```python
fig, ax = plt.subplots(1, 1, figsize=(15, 12))  # Width x Height in inches
```

## Troubleshooting

### Module Not Found Error

If you get `ModuleNotFoundError: No module named 'geopandas'`:

```bash
pip install geopandas matplotlib
```

### Country Name Mismatch

If a country isn't appearing on the map, check the country name mapping in `create_map()`:

```python
country_name_mapping = {
    'Macedonia': 'North Macedonia',
    'Czech Republic': 'Czechia',
    # Add more mappings if needed
}
```

### Empty Map

Ensure your articles file path is correct and contains data:

```bash
wc -l data/climate_articles.jsonl
```

## Examples

### Generate all visualizations

```bash
# Create the main map
python visualize_article_map.py

# View statistics
python explore_shapefile_data.py --action stats

# Export data
python explore_shapefile_data.py --action export --format csv
```

### Focus on specific regions

```bash
# Query a country
python explore_shapefile_data.py --action query --country "Germany"

# Create custom map of Nordic countries
python explore_shapefile_data.py --action map \
  --countries "Sweden" "Norway" "Denmark" "Finland" "Iceland" \
  --title "Nordic Countries Article Coverage"
```

## Output Files

After running the scripts, you'll find:

```
data/
├── images/
│   ├── article_frequency_map.png          # Main choropleth map
│   ├── article_frequency_summary.csv      # Country counts table
│   └── custom_map.png                     # Custom maps (if created)
└── exports/
    ├── article_data.csv                   # Exported article counts
    ├── article_data.json                  # JSON format
    └── article_data.geojson               # GeoJSON with geometries
```

## Notes

- The shapefile contains 260 global regions, but scripts filter to 46 European countries
- Article counts are based on the source country, not article content location
- Some countries (like Turkey) span Europe and Asia but are included for completeness
- The map uses EPSG:3035 projection, optimized for European visualization


