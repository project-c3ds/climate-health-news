# NewsAPI Data Collection

This directory contains the data collection system used to gather European climate news articles via the EventRegistry API. The scripts here represent the **reference implementation** showing how the ~300,000 articles in the main dataset were collected.

## 📋 Overview

The collection system supports:
- **Multi-language article collection** across European countries
- **Keyword-based filtering** with translated climate terminology
- **Source management** for European news outlets
- **Batch processing** with progress tracking and error handling
- **Article counting** and validation workflows

## 📁 Scripts

### 🎯 `collect_articles_example.py` - **Main Reference**
**Complete walkthrough** of the data collection process used for this project.

This script demonstrates the full workflow:
- Loading and filtering European news sources
- Multi-language keyword translation
- Article counting and collection via EventRegistry API
- Saving results in structured formats

**Usage:**
```bash
python newsapi/collect_articles_example.py
```

*Note: This runs in demonstration mode showing the process without making API calls. Actual collection requires EventRegistry API key.*

### 🔧 `newsapi_collect_batch.py` - Core Functionality
The main `ArticleCollector` class providing:
- EventRegistry API integration
- Batch article collection with progress tracking
- Multi-language keyword support
- Error handling and retry logic
- Article metadata extraction and processing

### 📊 `count_articles_by_source.py` - Source Analysis  
Utility for analyzing article availability by source and time period:
- Monthly article counts per news source
- Source performance validation
- Coverage gap identification
- Results saved as JSON and CSV for analysis

### 🔍 `newsapi_uri_finder.py` - Source Discovery
Tool for finding and validating EventRegistry source URIs:
- Convert domain URLs to EventRegistry source identifiers  
- Concurrent source validation
- Sample article fetching for source verification
- Source status tracking (success/error/partial)

## 🚀 Data Collection Workflow

The collection process follows these steps:

### 1. **Source Preparation**
```python
# Load European news sources
sources = load_sources()

# Filter by target languages  
target_languages = ['srp', 'ukr', 'isl', 'rus', 'mkd', 'sqi', 'tur']
filtered_sources = filter_sources_by_languages(sources, target_languages)
```

### 2. **Keyword Translation**
```python
# Load language-specific climate keywords
available_keywords = {}
for lang in target_languages:
    keywords = load_keywords(lang)
    if keywords:
        available_keywords[lang] = keywords
```

### 3. **Article Collection**
```python
# Initialize collector and collect articles
collector = ArticleCollector()
articles, stats = collector.collect_batch(
    sources=source_list,
    keywords=keywords,
    date_start='2023-01-01',
    date_end='2025-09-01',
    lang=language_code,
    max_items=500000
)
```

### 4. **Data Processing**
Articles are saved in JSONL format with standardized structure:
```json
{
  "uri": "article_id",
  "title": "Article Title", 
  "body": "Article content...",
  "date": "2023-01-01",
  "source": {"uri": "source_uri", "title": "Source Name"},
  "lang": "language_code",
  "concepts": [...],
  "categories": [...]
}
```

## 📊 Collection Results

The data collection produced:
- **~300,000 climate-related articles**
- **40+ European countries** covered
- **Multiple languages** with translated keywords
- **Time period**: January 2023 - September 2025
- **Final dataset**: `data/articles/lancet_europe_database.jsonl`

## 🔑 API Requirements

**EventRegistry API Key Required**
- Set `NEWSAPI_KEY` environment variable
- Free tier available with rate limits
- Commercial license needed for large-scale collection

**Setup:**
```bash
# Add to .env file
NEWSAPI_KEY=your_api_key_here
```

## 🛠️ Dependencies

Key packages used:
- `eventregistry` - EventRegistry API client
- `pandas` - Data manipulation
- `python-dotenv` - Environment variable management  
- `tqdm` - Progress tracking
- `concurrent.futures` - Parallel processing

## 📝 Usage Notes

### Running the Example
The example script can be run without an API key to see the workflow:
```bash
cd newsapi/
python collect_articles_example.py
```

### Actual Collection
For real data collection:
1. Obtain EventRegistry API key
2. Set `NEWSAPI_KEY` environment variable
3. Modify date ranges and parameters as needed
4. Run collection scripts with appropriate rate limiting

### Source Management
News sources are managed via:
- `data/sources/sources.csv` - Source configuration
- `utils.py` functions for loading and filtering sources
- Built-in language detection and country mapping

## ⚠️ Important Notes

- **Rate Limiting**: EventRegistry has API rate limits
- **Data Usage**: Respect news source terms of service
- **Language Support**: Keywords available for major European languages
- **Quality Control**: Includes validation and error handling
- **Backup Strategy**: Save progress frequently during large collections

---

**This collection system successfully gathered the dataset used for the Lancet Europe climate-health news analysis. The scripts provide a complete, reproducible workflow for similar large-scale news analysis projects.**