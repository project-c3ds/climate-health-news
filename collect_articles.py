from newsapi_batch import ArticleCollector
from utils import load_sources, load_keywords, filter_sources_by_languages
from constants import keywords_climate_eng_reduced, concepts_climate
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

# Re-run for select sources
sources_to_rerun = sources[sources['rerun'] == 'Yes']
target_languages = sources_to_rerun['dominant_language'].unique()

# Get languages that have keyword translations
articles, stats = collector.collect_batch(
    sources=sources_to_rerun['source_uri'].tolist(),
    date_start='2023-01-01',
    date_end='2025-09-01', 
    concepts=concepts_climate,
    download_images=False,
    max_items=500000
)

# all_articles = articles
# all_stats = stats
sources_dict = sources_to_rerun.to_dict(orient='records')

all_articles = []
all_stats = []

for source in sources_dict[1:]:
    print(f"\nCollecting articles for source: {source['source_uri']}")
    keywords = load_keywords(source['dominant_language'])
    articles, stats = collector.collect_batch(
        sources=[source['source_uri']],
        keywords=keywords,
        date_start='2023-01-01', 
        date_end='2025-09-01',
        lang=source['dominant_language'],
        exclude_concepts=concepts_climate,
        download_images=False,
        max_items=500000
    )
    all_articles.extend(articles)
    all_stats.append(stats)
    print(f"Collected {len(articles)} articles for {source['source_uri']}")

articles = all_articles
stats = all_stats

# Collect re-run jsons and save
import glob
import json

files = glob.glob('data/articles/*.json')
articles = []
for file in files:
    with open(file, 'r', encoding='utf-8') as f:
        article = json.load(f)
        articles.append(article)

print(f"Collected {len(articles)} articles")

# Write jsonl file
with open('data/lancet_european_articles_rerun.jsonl', 'w', encoding='utf-8') as f:
    for article in articles:
        f.write(json.dumps(article, ensure_ascii=False) + '\n')

print("Articles saved successfully!")

# Rerun for Cyprus sources
cyprus_sources = sources[sources['country_name'] == 'Cyprus']
target_languages = cyprus_sources['dominant_language'].unique().tolist()

# Get languages that have keyword translations
available_keywords = {}
for lang in target_languages:
    keywords = load_keywords(lang)
    if keywords:  # Only keep languages that return keywords
        available_keywords[lang] = keywords

# Get languages that have keyword translations
collector = ArticleCollector()
articles, stats = collector.collect_batch(
    sources=cyprus_sources['source_uri'].tolist(),
    date_start='2023-01-01',
    date_end='2025-09-01', 
    concepts=concepts_climate,
    download_images=False,
    max_items=500000
)

sources_dict = cyprus_sources.to_dict(orient='records')

all_articles = []
all_stats = []

for source in sources_dict:
    print(f"\nCollecting articles for source: {source['source_uri']}")
    keywords = load_keywords(source['dominant_language'])
    articles, stats = collector.collect_batch(
        sources=[source['source_uri']],
        keywords=keywords,
        date_start='2023-01-01', 
        date_end='2025-09-01',
        lang=source['dominant_language'],
        exclude_concepts=concepts_climate,
        download_images=False,
        max_items=500000
    )
    all_articles.extend(articles)
    all_stats.append(stats)
    print(f"Collected {len(articles)} articles for {source['source_uri']}")

articles = all_articles
stats = all_stats

# Collect Cyprus re-run jsons and save
import glob
import json

files = glob.glob('data/articles/*.json')
articles = []
for file in files:
    with open(file, 'r', encoding='utf-8') as f:
        article = json.load(f)
        articles.append(article)

print(f"Collected {len(articles)} articles")

# Write jsonl file
with open('data/lancet_european_articles_cyprus.jsonl', 'w', encoding='utf-8') as f:
    for article in articles:
        f.write(json.dumps(article, ensure_ascii=False) + '\n')

print("Articles saved successfully!")

for concept in concepts_climate:
    print(concept)

for keyword in load_keywords('eng'):
    print(keyword)