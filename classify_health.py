import json
from dotenv import load_dotenv
import os

load_dotenv(override=True)

# Load health concepts
with open('data/health_concepts.json', 'r') as f:
    health_concepts = json.load(f)

with open('data/climate_articles_concepts.jsonl', 'r') as f:
    articles = [json.loads(line) for line in f]


def classify_health_articles(articles, health_concepts):
    """
    Loop over articles and check if their concept URIs match health concept URIs.
    
    Args:
        articles: List of article dictionaries with 'concepts' field
        health_concepts: List of health concept dictionaries with 'concept_uri' field
    
    Returns:
        List of articles that match health concepts, with added 'matched_health_concepts' field
    """
    # Extract health concept URIs into a set for efficient lookup
    health_concept_uris = {concept['concept_uri'] for concept in health_concepts}
    
    # Also create a mapping from URI to keyword for reference
    uri_to_keyword = {concept['concept_uri']: concept['keyword'] for concept in health_concepts}
    
    health_articles = []
    
    for article in articles:
        # Get concepts from article
        article_concepts = article.get('concepts', [])
        
        # Store matched health concepts
        matched_concepts = []
        
        # Loop over concept URIs in the article
        for concept in article_concepts:
            concept_uri = concept.get('uri', '')
            
            # Compare with health concept URIs
            if concept_uri in health_concept_uris:
                matched_concepts.append({
                    'uri': concept_uri,
                    'keyword': uri_to_keyword[concept_uri],
                    'label': concept.get('label', {}),
                    'score': concept.get('score', 0)
                })
        
        # If article has matching health concepts, add it to results
        if matched_concepts:
            article_copy = article.copy()
            article_copy['matched_health_concepts'] = matched_concepts
            article_copy['health_concept_count'] = len(matched_concepts)
            health_articles.append(article_copy)
    
    return health_articles


def concept_uri_frequency_distribution(articles):
    """
    Create a frequency distribution of unique concept URIs in articles.
    
    Args:
        articles: List of article dictionaries with 'concepts' field
    
    Returns:
        List of tuples (uri, frequency) sorted from largest to smallest frequency
    """
    from collections import Counter
    
    # Count all concept URIs across all articles
    uri_counts = Counter()
    
    for article in articles:
        # Get concepts from article
        article_concepts = article.get('concepts', [])
        
        # Extract URIs and count them
        for concept in article_concepts:
            concept_uri = concept.get('uri', '')
            if concept_uri:  # Only count non-empty URIs
                uri_counts[concept_uri] += 1
    
    # Sort by frequency (descending) and return as list of tuples
    sorted_frequencies = uri_counts.most_common()
    
    return sorted_frequencies


health_articles = classify_health_articles(articles, health_concepts)
uri_frequencies = concept_uri_frequency_distribution(articles)

print(f"Total unique concept URIs: {len(uri_frequencies)}")
print("\nTop 20 most frequent concept URIs:")
for i, (uri, count) in enumerate(uri_frequencies[200:300], 1):
    print(f"{i:2d}. {uri}")
    print(f"    Frequency: {count}")

# http://en.wikipedia.org/wiki/Coronavirus

if __name__ == "__main__":
    # Classify articles
    health_articles = classify_health_articles(articles, health_concepts)
    
    print(f"Total articles: {len(articles)}")
    print(f"Articles with health concepts: {len(health_articles)}")
    
    # Show first few matches as examples
    if health_articles:
        print("\nExample matches:")
        for i, article in enumerate(health_articles[:3]):
            print(f"\n{i+1}. {article.get('title', 'No title')}")
            print(f"   Matched health concepts: {article['health_concept_count']}")
            for concept in article['matched_health_concepts']:
                print(f"   - {concept['keyword']} (score: {concept['score']})")
    
    # Save results
    output_file = 'data/climate_health_articles.jsonl'
    with open(output_file, 'w') as f:
        for article in health_articles:
            f.write(json.dumps(article) + '\n')
    
    print(f"\nResults saved to {output_file}")
    
    # Get frequency distribution of all concept URIs
    print("\n" + "="*60)
    print("CONCEPT URI FREQUENCY DISTRIBUTION")
    print("="*60)
    uri_frequencies = concept_uri_frequency_distribution(articles)
    
    print(f"\nTotal unique concept URIs: {len(uri_frequencies)}")
    print("\nTop 20 most frequent concept URIs:")
    for i, (uri, count) in enumerate(uri_frequencies[:20], 1):
        print(f"{i:2d}. {uri}")
        print(f"    Frequency: {count}")
