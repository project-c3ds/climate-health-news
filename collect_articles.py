from newsapi_batch import ArticleCollector
from utils import load_sources, load_keywords, filter_sources_by_languages
from constants import keywords_climate_eng_reduced, concepts_climate
import pickle
import pandas as pd
# from eventregistry import *
# from dotenv import load_dotenv

# load_dotenv()
# api_key = os.getenv('NEWSAPI_KEY')
# er = EventRegistry(apiKey=api_key)
# er.getConceptUri("climate justice")

sources = load_sources()


# Language codes from terminal output mapped to countries
# target_languages = ['lav', 'mkd', 'ell', 'sqi', 'fin', 'ces', 'slk', 'srp', 'lit', 'bul', 'swe', 'isl', 'ukr']
# Get all unique languages from sources, excluding 'eng'
target_languages = ['srp', 'ukr', 'isl', 'rus', 'mkd', 'sqi', 'tur']

# Get languages that have keyword translations
available_keywords = {}
for lang in target_languages:
    keywords = load_keywords(lang)
    if keywords:  # Only keep languages that return keywords
        available_keywords[lang] = keywords

# Filter sources for the target language countries with successful status
sources = filter_sources_by_languages(sources, target_languages)

print(f"Filtered sources by languages: {sources['dominant_language'].value_counts()}")
print(f"Total sources selected: {len(sources)}")
print(f"Countries included: {sources['country_name'].unique()}")

collector = ArticleCollector()
counts = {}
for lang in target_languages:
    keywords = available_keywords[lang]
    count = collector.count_articles(
        sources=sources['source_uri'].tolist(),
        keywords=keywords,
        date_start='2023-01-01',
        date_end='2025-09-01',
        lang=lang,
        exclude_concepts=concepts_climate,
    )
    counts[lang] = count
    print(f"Found {count} articles for language {lang}")

print("\nTotal article counts by language:")
for lang, count in counts.items():
    print(f"{lang}: {count:,} articles")

all_articles = []
all_stats = []

for lang, keywords in available_keywords.items():
    print(f"\nCollecting articles for language: {lang}")
    articles, stats = collector.collect_batch(
        sources=sources['source_uri'].tolist(),
        keywords=keywords,
        date_start='2023-01-01', 
        date_end='2025-09-01',
        lang=lang,
        exclude_concepts=concepts_climate,
        download_images=False,
        max_items=500000
    )
    all_articles.extend(articles)
    all_stats.append(stats)
    print(f"Collected {len(articles)} articles for {lang}")

articles = all_articles
stats = all_stats

# Create filename with ISO codes
iso_codes_str = '_'.join(target_languages)
filename = f'data/articles_{iso_codes_str}.pkl'

# Save articles to pickle file for later analysis
with open(filename, 'wb') as f:
    pickle.dump(articles, f)

print(f"\nSaved {len(articles)} articles to {filename}")


# Track which keywords were found in each article
article_keywords = []

for article in articles:
    # Get the article text content
    text = article.get('body', '').lower() + ' ' + article.get('title', '').lower()
    
    # Find which keywords appear in this article
    found_keywords = []
    for keyword in keywords_climate_eng_reduced:
        if keyword.lower() in text:
            found_keywords.append(keyword)
            
    # Store the keywords found for this article
    article_keywords.append({
        'title': article.get('title'),
        'keywords_found': found_keywords,
        'num_keywords': len(found_keywords),
        'source_uri': article.get('source_uri'),
        'text': text
    })

print(f"\nAnalyzed keyword matches across {len(articles)} articles")
print(f"Average keywords per article: {sum(k['num_keywords'] for k in article_keywords) / len(articles):.1f}")

for article in article_keywords:
    print(f"Article: {article['title']}")
    print(f"Keywords found: {article['keywords_found']}")
    print(f"Number of keywords: {article['num_keywords']}")
    print(f"Source URI: {article['source_uri']}")
    print("-" * 100)

import glob
import json
import pandas as pd

files = glob.glob('data/articles/*.json')
file = files[0]
with open(file, 'r') as f:
    articles = json.load(f)

lang_codes = []
for file in files:
    with open(file, 'r') as f:
        articles = json.load(f)
        lang_codes.append(articles['lang'])
        
counts = pd.DataFrame(lang_codes, columns=['lang']).value_counts()



