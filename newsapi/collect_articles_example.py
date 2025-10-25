"""
Climate-Health News Article Collection Example

This script demonstrates how to collect climate-related news articles from European sources
using the EventRegistry API. It shows the complete workflow from filtering sources by
language to collecting and saving articles.

This is a REFERENCE IMPLEMENTATION - the actual data collection has already been completed.
"""

import sys
import os

# Add parent directory to path to import utils
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from newsapi_collect_batch import ArticleCollector
from utils import load_sources, load_keywords, filter_sources_by_languages
import pandas as pd
import json

# Climate concepts
CONCEPTS_CLIMATE = [
    "climate change",
    "global warming", 
    "climate impacts",
    "climate effects",
    "renewable energy",
    "electric vehicle",
    "energy policy",
    "emissions trading",
    "climate politics",
    "climate justice",
    "energy transition",
    "european green deal", 
    "climate finance",
    "climate legislation",
    "climate governance"
]

def main():
    """
    Main function demonstrating the article collection workflow.
    """
    print("=" * 70)
    print("CLIMATE-HEALTH NEWS ARTICLE COLLECTION EXAMPLE")
    print("=" * 70)
    print("This is a reference implementation showing how data was collected.")
    print("The actual collection has been completed and data is available in data/")
    print("=" * 70)
    
    # Load sources from CSV
    sources = load_sources()
    print(f"Loaded {len(sources)} total news sources")
    
    # Define target languages (non-English European languages)
    target_languages = ['srp', 'ukr', 'isl', 'rus', 'mkd', 'sqi', 'tur']
    print(f"Target languages: {target_languages}")
    
    # Get languages that have keyword translations available
    available_keywords = {}
    for lang in target_languages:
        keywords = load_keywords(lang)
        if keywords:  # Only keep languages that return keywords
            available_keywords[lang] = keywords
            print(f"  - {lang}: {len(keywords)} keywords available")
    
    # Filter sources for the target language countries with successful status
    filtered_sources = filter_sources_by_languages(sources, target_languages)
    
    print(f"\nFiltered sources by language:")
    print(filtered_sources['dominant_language'].value_counts())
    print(f"Total sources selected: {len(filtered_sources)}")
    print(f"Countries included: {sorted(filtered_sources['country_name'].unique())}")

    
    # Example: Count articles for each language (without actually making API calls)
    print(f"\n{'='*50}")
    print("STEP 1: Count Available Articles")
    print(f"{'='*50}")
    print("This would count articles available for each language/source combination:")
    
    # Initialize collector (requires API key in environment)
    try:
        collector = ArticleCollector()
        print("✅ EventRegistry collector initialized")
        
        # Example counting (commented out to avoid API calls)
        print("\nExample counting process:")
        for lang in available_keywords.keys():
            keywords = available_keywords[lang]
            print(f"  - {lang}: Would count articles using {len(keywords)} keywords")
            print(f"    Keywords: {', '.join(keywords[:3])}{'...' if len(keywords) > 3 else ''}")
            
            # Actual API call would be:
            # count = collector.count_articles(
            #     sources=filtered_sources['source_uri'].tolist(),
            #     keywords=keywords,
            #     date_start='2023-01-01',
            #     date_end='2025-09-01', 
            #     lang=lang,
            #     exclude_concepts=CONCEPTS_CLIMATE,
            # )
            # print(f"Found {count} articles for {lang}")
            
    except ValueError as e:
        print(f"⚠️  Collector not initialized: {e}")
        print("   (This is expected in demo mode - API key required for actual collection)")

    
    # Example: Collect articles for each language  
    print(f"\n{'='*50}")
    print("STEP 2: Collect Articles")
    print(f"{'='*50}")
    print("This would collect articles from each source:")
    
    example_collection_code = """
    # Example collection process:
    all_articles = []
    all_stats = []
    
    for lang, keywords in available_keywords.items():
        print(f"Collecting articles for language: {lang}")
        articles, stats = collector.collect_batch(
            sources=filtered_sources['source_uri'].tolist(),
            keywords=keywords,
            date_start='2023-01-01', 
            date_end='2025-09-01',
            lang=lang,
            exclude_concepts=CONCEPTS_CLIMATE,
            download_images=False,
            max_items=500000  # Large limit to get all available articles
        )
        all_articles.extend(articles)
        all_stats.append(stats)
        print(f"Collected {len(articles)} articles for {lang}")
    """
    print(example_collection_code)
    
    # Example: Save collected articles
    print(f"\n{'='*50}")
    print("STEP 3: Save Articles")  
    print(f"{'='*50}")
    print("Articles would be saved in JSONL format:")
    
    example_save_code = """
    # Save articles to JSONL file
    output_file = 'data/articles/lancet_european_articles.jsonl'
    with open(output_file, 'w', encoding='utf-8') as f:
        for article in all_articles:
            f.write(json.dumps(article, ensure_ascii=False) + '\\n')
    
    print(f"Saved {len(all_articles)} articles to {output_file}")
    
    # Example of saved article structure:
    # {
    #   "uri": "article_id", 
    #   "title": "Article Title",
    #   "body": "Article content...",
    #   "date": "2023-01-01",
    #   "source": {"uri": "source_uri", "title": "Source Name"},
    #   "lang": "language_code",
    #   "concepts": [...],  # Extracted concepts
    #   "categories": [...]  # Article categories
    # }
    """
    print(example_save_code)
    
    print(f"\n{'='*70}")
    print("COLLECTION COMPLETE")
    print(f"{'='*70}")
    print("The actual data collection produced:")
    print("  - ~300,000+ climate-related articles")
    print("  - Coverage of 40+ European countries") 
    print("  - Multiple languages with translated climate keywords")
    print("  - Time period: January 2023 - September 2025")
    print("  - Final dataset: data/articles/lancet_europe_database.jsonl")
    print(f"{'='*70}")


if __name__ == "__main__":
    main()