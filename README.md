# Climate-Health News Analysis

**Code to generate the climate and health news indicator for the Lancet Europe report.**

This repository contains a complete pipeline for collecting, processing, and analyzing European climate and health news coverage. The analysis produces visualizations showing how climate issues are framed in relation to health, urban/rural contexts, and inequality across European countries.

## 🎯 Project Overview

This project analyzes **~300,000 climate-related news articles** from **40+ European countries** to understand:
- **Health framing**: How often climate issues are connected to health impacts
- **Urban/rural framing**: Geographic context of climate reporting  
- **Inequality framing**: Coverage of climate justice and vulnerable populations
- **Temporal trends**: Changes in coverage patterns over time (2023-2025)

## 📊 Key Outputs

**Four main figures** are generated showing:
1. **`figure1.png`** - Combined maps and time series visualization
2. **`figure2.png`** - Urban/rural framing distribution comparison  
3. **`figure3.png`** - Inequality coverage time series
4. **`figure4.png`** - Types of inequality coverage

## 🚀 Quick Start

### Generate All Figures
```bash
# Generate all analysis figures at once
python plots/make_figures.py
```

### Generate Individual Figures  
```bash
# Individual plotting scripts
python plots/plot_climate_health.py      # → figure1.png
python plots/plot_urban_rural_barchart.py # → figure2.png  
python plots/plot_inequality.py          # → figure3.png, figure4.png
```

## 📁 Project Structure

```
climate-health-news/
├── plots/                    # 📈 Visualization and analysis
│   ├── images/              # Generated figures (figure1-4.png)
│   ├── make_figures.py      # Master script to generate all plots
│   ├── plot_*.py            # Individual plotting scripts
│   └── plot_time_series.py  # Time series functionality
├── data/                    # 📊 Datasets and resources  
│   ├── articles/            # Main datasets (parquet & jsonl)
│   ├── europe_shapefile/    # Geographic data for mapping
│   ├── sources/             # News source configuration
│   └── translations/        # Multi-language keyword translations
├── newsapi/                 # 🔍 Data collection (reference implementation)
│   ├── collect_articles_example.py  # How data was collected
│   ├── newsapi_collect_batch.py     # Collection functionality  
│   └── *.py                # Other collection utilities
├── classify/                # 🏷️ Content classification
│   ├── keyword_classifier.py       # Multi-language keyword classification
│   └── BM25_CLASSIFIER_README.md   # Classification documentation
├── validation/              # ✅ Quality assurance
│   ├── calculate_performance.py    # Classification performance metrics
│   └── get_validation_samples.py   # Sampling for human validation
└── utils.py                # 🛠️ Shared utilities
```

## 📊 Data Overview

### Main Datasets
- **`lancet_europe_database.jsonl`** - Raw article data with metadata
- **`lancet_europe_dataset_with_dummies.parquet`** - Full dataset with classifications  
- **`lancet_europe_health_subset_with_dummies.parquet`** - Health-focused articles
- **`lancet_europe_dataset_monthly.parquet`** - Time series data

### Coverage
- **Countries**: 40+ European nations (EU, EEA, UK)
- **Languages**: Multiple European languages with translated keywords
- **Time Period**: January 2023 - September 2025
- **Article Count**: ~300,000 climate-related articles
- **Health Subset**: ~68,000 articles with health framing

## 🔧 Key Components

### Data Collection (`newsapi/`)
- **EventRegistry API integration** for comprehensive news coverage
- **Multi-language keyword translation** for consistent cross-country analysis
- **Reference implementation** showing how data was collected
- **Source management** for European news outlets

### Content Classification (`classify/`)
- **Keyword-based classification** using BM25 algorithm
- **Multi-language support** with translated climate/health terms
- **Binary classification** for health, urban/rural, and inequality framing
- **Validation framework** for accuracy assessment

### Visualization (`plots/`)
- **Choropleth maps** showing country-level patterns
- **Time series analysis** of coverage trends
- **Statistical comparisons** between article subsets
- **Combined visualizations** with maps and trends

## 🎨 Visualization System

The plotting system is designed for reproducibility and clarity:

### Master Script
```bash
python plots/make_figures.py
```
- Generates all 4 figures in one command
- Provides progress tracking and error handling
- Outputs timing and file size information

### Individual Scripts
Each figure can be generated independently:
- **Climate-Health Maps**: `plot_climate_health.py`
- **Urban/Rural Analysis**: `plot_urban_rural_barchart.py` 
- **Inequality Analysis**: `plot_inequality.py`

## 🛠️ Dependencies

Key Python packages required:
- `pandas` - Data manipulation and analysis
- `matplotlib` - Plotting and visualization  
- `geopandas` - Geographic data and mapping
- `scikit-learn` - Classification and validation
- `eventregistry` - News data collection (API key required)

See `requirements.txt` for complete dependency list.

## 📝 Documentation

- **`plots/README.md`** - Complete visualization system documentation
- **`newsapi/README.md`** - Data collection system overview  
- **`classify/BM25_CLASSIFIER_README.md`** - Classification methodology

## 🔬 Validation & Quality Control

The project includes comprehensive validation:
- **Human annotation** of sample articles for ground truth
- **Performance metrics** (precision, recall, F1-score) for classifications
- **Cross-validation** across different languages and countries
- **Statistical significance testing** for all comparisons

## 📊 Usage Examples

### Quick Analysis
```bash
# Generate all figures
python plots/make_figures.py

# View results in plots/images/
ls plots/images/
# → figure1.png, figure2.png, figure3.png, figure4.png
```

### Custom Analysis
```python
import pandas as pd
from utils import load_sources

# Load processed data
df = pd.read_parquet('data/articles/lancet_europe_dataset_with_dummies.parquet')

# Analyze health framing by country
health_by_country = df.groupby('country_name')['health'].mean()
print(health_by_country.sort_values(ascending=False))
```

## 🤝 Contributing

This codebase serves as the analysis pipeline for the Lancet Europe climate-health indicator. The methodology and code are designed to be reproducible and extensible for future analyses.

## 📄 License

See `LICENSE` file for details.

---

**For questions about the analysis methodology or technical implementation, please refer to the documentation files or examine the well-commented source code.**