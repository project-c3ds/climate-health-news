import json
import glob
from pathlib import Path
from rank_bm25 import BM25Okapi
import re
import os

# Change to project root directory
script_dir = Path(__file__).parent
project_root = script_dir.parent
os.chdir(project_root)

# Load climate keywords
with open('data/keywords_climate.json', 'r', encoding='utf-8') as f:
    climate_keywords = json.load(f)

def tokenize_text(text):
    """Tokenize text into words (lowercase)"""
    if not text:
        return []
    return re.findall(r'\b\w+\b', text.lower())

def calculate_bm25_score(text, keywords):
    """
    Calculate BM25 relevance score.
    Tokenizes both text and keywords to handle inflected languages properly.
    Each keyword phrase is tokenized and treated as a document in the corpus.
    """
    if not text or not keywords:
        return 0.0
    
    # Tokenize the article text
    doc_tokens = tokenize_text(text)
    if not doc_tokens:
        return 0.0
    
    # Tokenize each keyword phrase to create the corpus
    # Each keyword phrase becomes a "document" of tokens
    keyword_corpus = []
    for kw in keywords:
        if kw and kw.strip():
            kw_tokens = tokenize_text(kw)
            if kw_tokens:
                keyword_corpus.append(kw_tokens)
    
    if not keyword_corpus:
        return 0.0
    
    # Create BM25 index with keyword phrases as corpus
    bm25 = BM25Okapi(keyword_corpus)
    
    # Score: how well does the article text match against the keyword corpus
    scores = bm25.get_scores(doc_tokens)
    
    # Return the sum of scores (total relevance across all keywords)
    return sum(scores) if len(scores) > 0 else 0.0

# -----------------------------------------------------------------
# Process articles extracted based on *concepts*
#
# All of these articles are relevant to climate
# change and will be used in the analysis.
# -----------------------------------------------------------------

# Get all JSON file paths
paths = glob.glob('data/articles_concepts/*.json')
print(f"Found {len(paths)} JSON files")

# Dictionary to store unique articles by URI
unique_articles = {}

# Loop over all JSON files
for i, path in enumerate(paths):
    try:
        with open(path, 'r') as f:
            data = json.load(f)
        
        # Get the URI
        uri = data.get('uri')
        lang = data.get('lang')
        
        if uri:
            # Only keep the first occurrence of each URI (remove duplicates)
            if uri not in unique_articles:
                data['collection_method'] = 'concepts'
                unique_articles[uri] = data
        else:
            print(f"Warning: No URI found in {path}")
        
        # Progress update every 10000 files
        if (i + 1) % 10000 == 0:
            print(f"Processed {i + 1}/{len(paths)} files, {len(unique_articles)} unique articles")
    
    except Exception as e:
        print(f"Error processing {path}: {e}")

print(f"\nTotal files processed: {len(paths)}")
print(f"Unique articles (by URI): {len(unique_articles)}")

# -----------------------------------------------------------------
# Process articles extracted based on *keywords*
#
# Need to check relevance based on bm25
# -----------------------------------------------------------------

# Process keyword-based articles
paths = glob.glob('data/articles/*.json')
print(f"\nFound {len(paths)} keyword-based articles")

# Dictionary to store articles with BM25 scores
articles_with_scores = {}

# BM25 score threshold for relevance
# Based on testing: climate articles typically score 50-500+
# Non-climate articles score much lower
BM25_THRESHOLD = 15.0  # Adjust based on your data

for i, path in enumerate(paths):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        uri = data.get('uri')
        lang = data.get('lang')
        
        if not uri:
            print(f"Warning: No URI found in {path}")
            continue
        
        # Skip if already in concept-based articles (no duplicates)
        if uri in unique_articles:
            continue
        
        # Get keywords for this language
        if lang not in climate_keywords:
            continue
        
        keywords = climate_keywords[lang]
        
        # Calculate BM25 score based on title and body
        title = data.get('title', '')
        body = data.get('body', '')
        combined_text = f"{title} {body}"
        
        bm25_score = calculate_bm25_score(combined_text, keywords)
        
        # Only keep articles above threshold
        if bm25_score >= BM25_THRESHOLD:
            data['collection_method'] = 'keywords'
            articles_with_scores[uri] = data
        
        # Progress update every 10000 files
        if (i + 1) % 10000 == 0:
            print(f"Processed {i + 1}/{len(paths)} files, {len(articles_with_scores)} relevant articles found")
    
    except Exception as e:
        print(f"Error processing {path}: {e}")

print(f"\nTotal keyword-based files processed: {len(paths)}")
print(f"Relevant articles (BM25 >= {BM25_THRESHOLD}): {len(articles_with_scores)}")

# Combine concept-based and keyword-based articles
all_articles = {**unique_articles, **articles_with_scores}
print(f"\nTotal unique climate articles: {len(all_articles)}")

# Count articles by collection method
concepts_count = sum(1 for a in all_articles.values() if a.get('collection_method') == 'concepts')
keywords_count = sum(1 for a in all_articles.values() if a.get('collection_method') == 'keywords')
print(f"  - From concepts: {concepts_count}")
print(f"  - From keywords: {keywords_count}")

# Write combined results to JSONL file
output_file = 'data/climate_articles.jsonl'
with open(output_file, 'w', encoding='utf-8') as f:
    for uri, article in all_articles.items():
        f.write(json.dumps(article, ensure_ascii=False) + '\n')

print(f"\nWritten {len(all_articles)} unique articles to {output_file}")

# Split articles by collection method into separate files
concepts_file = 'data/climate_articles_concepts.jsonl'
keywords_file = 'data/climate_articles_keywords.jsonl'

print("\nSplitting articles by collection method...")

concepts_count = 0
keywords_count = 0

with open(concepts_file, 'w', encoding='utf-8') as cf, \
     open(keywords_file, 'w', encoding='utf-8') as kf:
    
    with open('data/climate_articles.jsonl', 'r', encoding='utf-8') as f:
        for line in f:
            article = json.loads(line)
            if article.get('collection_method') == 'concepts':
                cf.write(line)
                concepts_count += 1
            elif article.get('collection_method') == 'keywords':
                kf.write(line)
                keywords_count += 1

print(f"Written {concepts_count} concept-based articles to {concepts_file}")
print(f"Written {keywords_count} keyword-based articles to {keywords_file}")

# -----------------------------------------------------------------
# Append relevant keyword articles
#
# Add back in in keyword articles classified as climate
# -----------------------------------------------------------------

import pandas as pd

df = pd.read_json('data/climate_articles_keywords_with_classifications.jsonl', lines=True)
df = pd.read_json('data/climate_articles_concepts.jsonl', lines=True)

articles = []
path = 'data/climate_articles_concepts.jsonl'
with open(path, 'r', encoding='utf-8') as f:
    for line in f:
        article = json.loads(line)
        articles.append(article)

with open('data/climate_articles_keywords_with_classifications.jsonl', 'r', encoding='utf-8') as f:
    for line in f:
        article = json.loads(line)
        if article.get('classification').get('is_climate_or_energy'):
            del article['classification']
            articles.append(article)

# Create simplified version with just uri, url and combined text
simplified_file = 'data/lancet_european_articles.jsonl'

print("\nCreating simplified articles file...")
with open(simplified_file, 'w', encoding='utf-8') as f:
    for article in articles:
        # Combine title and body text
        title = article.get('title', '')
        body = article.get('body', '')
        combined_text = f"{title}\n\n{body}".strip()
        
        # Create simplified article object
        simple_article = {
            'uri': article.get('uri'),
            'url': article.get('url'),
            'text': combined_text
        }
        
        # Write to file
        f.write(json.dumps(simple_article, ensure_ascii=False) + '\n')

print(f"Written {len(articles)} simplified articles to {simplified_file}")
