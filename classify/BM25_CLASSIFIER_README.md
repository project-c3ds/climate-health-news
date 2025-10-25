# BM25 Keyword Classifier

A flexible BM25-based keyword classifier for article classification. This classifier uses the BM25 ranking algorithm to score documents based on keyword relevance and classifies them based on a configurable threshold.

## Overview

The BM25 (Best Matching 25) algorithm is a probabilistic ranking function used in information retrieval. It scores documents based on the query terms appearing in each document, taking into account:
- Term frequency (TF): How often query terms appear in the document
- Inverse document frequency (IDF): How rare/common the query terms are across all documents
- Document length normalization: Adjusts for document length variations

This implementation uses the `rank-bm25` library and provides a simple interface for article classification.

## Installation

The required dependencies are already in `requirements.txt`:
```bash
pip install rank-bm25 pandas
```

## Basic Usage

### Quick Start: Function Interface

The simplest way to use the classifier is with the `classify_with_keywords()` function:

```python
import pandas as pd
from classify.keyword_classifier import classify_with_keywords

# Create a dataframe with articles
df = pd.DataFrame({
    'text': [
        'Climate change is affecting global temperatures',
        'Sports team wins championship',
        'Renewable energy costs are falling'
    ]
})

# Define keywords
keywords = ['climate change', 'renewable energy', 'global warming']

# Classify with a threshold
result = classify_with_keywords(
    df=df,
    text_field='text',
    keywords=keywords,
    threshold=2.0
)

# Result contains two new columns:
# - bm25_score: The BM25 score for each document
# - bm25_classification: True/False based on threshold
```

### Class Interface

For more control, use the `BM25KeywordClassifier` class:

```python
from classify.keyword_classifier import BM25KeywordClassifier

# Initialize classifier with keywords
classifier = BM25KeywordClassifier(keywords=['climate change', 'solar power'])

# Classify a dataframe
result = classifier.classify_dataframe(
    df=df,
    text_field='text',
    threshold=3.0,
    score_column='climate_score',  # Custom column names
    classification_column='is_climate_related'
)

# Get top N documents by score
top_docs = classifier.get_top_documents(result, 'text', n=10)
```

## Parameters

### `classify_with_keywords()` and `classify_dataframe()`

- **df** (pd.DataFrame): DataFrame containing the articles to classify
- **text_field** (str): Name of the column containing the text to analyze
- **keywords** (List[str]): List of keywords to match against
- **threshold** (float): Minimum score for classification as positive (True)
- **score_column** (str, optional): Name for the BM25 score column (default: 'bm25_score')
- **classification_column** (str, optional): Name for the classification column (default: 'bm25_classification')

## How to Choose a Threshold

The threshold determines which documents are classified as positive. Here are some guidelines:

1. **Start with exploratory analysis**: Run classification with different thresholds and examine the score distribution
2. **Manual inspection**: Look at documents near your candidate threshold to see if they should be included
3. **Consider your use case**:
   - **High precision needed**: Use a higher threshold (fewer false positives)
   - **High recall needed**: Use a lower threshold (fewer false negatives)

Example of threshold exploration:
```python
# Test multiple thresholds
for threshold in [1.0, 2.0, 5.0, 10.0]:
    result = classify_with_keywords(df, 'text', keywords, threshold)
    print(f"Threshold {threshold}: {result['bm25_classification'].sum()} classified")
```

## Working with Project Data

### Example 1: Using Climate Keywords from Translations

```python
import json
import pandas as pd
from classify.keyword_classifier import classify_with_keywords

# Load official climate keywords
with open('data/translations/climate_official_translations.json', 'r') as f:
    translations = json.load(f)

# Use English keywords
keywords = translations['eng']  # or 'deu', 'fra', etc.

# Load articles from JSONL
articles = []
with open('data/climate_articles.jsonl', 'r') as f:
    for line in f:
        articles.append(json.loads(line))

df = pd.DataFrame(articles)

# Classify
result = classify_with_keywords(
    df=df,
    text_field='body',  # or combine title + body
    keywords=keywords,
    threshold=5.0
)

# Save results
result.to_parquet('data/classified_articles.parquet')
```

### Example 2: Multi-language Classification

```python
# Classify articles by language
with open('data/translations/climate_official_translations.json', 'r') as f:
    translations = json.load(f)

# Map language codes
lang_keywords = {
    'en': translations['eng'],
    'de': translations['deu'],
    'fr': translations['fra']
}

# Classify each language separately
for lang, keywords in lang_keywords.items():
    lang_df = df[df['language'] == lang]
    
    result = classify_with_keywords(
        df=lang_df,
        text_field='text',
        keywords=keywords,
        threshold=3.0
    )
    
    print(f"{lang}: {result['bm25_classification'].sum()} classified")
```

## Understanding BM25 Scores

- **Score = 0**: None of the keywords appear in the document
- **Low scores (0-5)**: Few keyword matches or matches in very common terms
- **Medium scores (5-15)**: Multiple keyword matches or strong matches
- **High scores (15+)**: Many keyword matches or very strong relevance

Scores are relative and depend on:
- Your keyword list size and specificity
- The document corpus size and diversity
- Document lengths

## Comparison with Other Classification Methods

| Method | Pros | Cons | Best For |
|--------|------|------|----------|
| **BM25 Keyword** | Fast, interpretable, no training needed | Requires good keywords, threshold tuning | Quick classification, exploratory analysis |
| **LLM (GPT)** | Very accurate, flexible | Slow, expensive, requires API | High-quality classification, complex criteria |
| **Concept URI** | Domain-specific, structured | Requires concept database | Articles with concept annotations |

## Tips and Best Practices

1. **Keyword Selection**:
   - Use domain-specific terminology
   - Include synonyms and variations
   - Consider multi-word phrases
   - Use official translations for multi-language support

2. **Text Preprocessing**:
   - Combine relevant fields (title + body)
   - Handle missing values
   - Consider removing very short documents

3. **Threshold Selection**:
   - Examine score distributions
   - Manually inspect borderline cases
   - Consider using multiple thresholds for different use cases

4. **Performance**:
   - BM25 is fast for large datasets
   - No API calls or GPU required
   - Can process thousands of documents per second

## Examples

See `example_bm25_usage.py` for complete working examples:

```bash
# Run all examples
python classify/example_bm25_usage.py
```

## Troubleshooting

### Issue: All scores are zero
- Check that keywords match the text (case is handled automatically)
- Verify text_field contains actual text
- Try more general keywords

### Issue: Classification seems wrong
- Examine score distribution: `df['bm25_score'].describe()`
- Try different thresholds
- Manually inspect high and low scoring documents
- Consider adding/removing keywords

### Issue: Too many/few classifications
- Adjust the threshold up (fewer) or down (more)
- Review keyword list for specificity
- Check if documents are in expected language

## API Reference

### `BM25KeywordClassifier`

Class for BM25-based keyword classification.

**Methods:**
- `__init__(keywords: List[str])`: Initialize with keywords
- `fit(corpus: List[str])`: Fit BM25 model on corpus (called automatically)
- `score(text: str)`: Score a single document
- `classify_dataframe(df, text_field, threshold, ...)`: Classify all documents
- `get_top_documents(df, text_field, n)`: Get top N documents by score

### `classify_with_keywords()`

Convenience function for one-step classification.

**Returns:** DataFrame with added score and classification columns

## Related Files

- `classify/keyword_classifier.py`: Main classifier implementation
- `classify/example_bm25_usage.py`: Working examples
- `data/translations/climate_official_translations.json`: Climate keywords by language
- `data/translations/health_official_translations.json`: Health keywords by language

## License

Part of the climate-health-news project.

