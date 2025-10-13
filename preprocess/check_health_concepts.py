#!/usr/bin/env python3
"""
Check articles for health-related concepts.

This script loads health concepts and checks which articles contain them
by matching Wikipedia URIs in the article concepts field.
"""

import json
from pathlib import Path
from typing import List, Dict, Set
from tqdm import tqdm


def load_health_concepts(health_concepts_file: str = "data/health_concepts.json") -> Set[str]:
    """
    Load health concept URIs from JSON file.
    
    Args:
        health_concepts_file: Path to health concepts JSON file
        
    Returns:
        Set of health concept URIs
    """
    with open(health_concepts_file, 'r', encoding='utf-8') as f:
        health_concepts = json.load(f)
    
    # Extract just the URIs into a set for fast lookup
    health_uris = {concept["concept_uri"] for concept in health_concepts}
    
    return health_uris


def has_health_concept(article: Dict, health_uris: Set[str]) -> bool:
    """
    Check if an article contains any health-related concepts.
    
    Args:
        article: Article dictionary with 'concepts' field
        health_uris: Set of health concept URIs to check against
        
    Returns:
        True if article has at least one health concept, False otherwise
    """
    concepts = article.get("concepts", [])
    
    if not concepts:
        return False
    
    # Check if any concept URI matches a health URI
    for concept in concepts:
        concept_uri = concept.get("uri", "")
        if concept_uri in health_uris:
            return True
    
    return False


def get_health_concepts_in_article(article: Dict, health_uris: Set[str]) -> List[Dict]:
    """
    Get all health concepts found in an article.
    
    Args:
        article: Article dictionary with 'concepts' field
        health_uris: Set of health concept URIs to check against
        
    Returns:
        List of health concept objects found in the article
    """
    concepts = article.get("concepts", [])
    
    if not concepts:
        return []
    
    # Return all concepts that match health URIs
    health_concepts_found = []
    for concept in concepts:
        concept_uri = concept.get("uri", "")
        if concept_uri in health_uris:
            health_concepts_found.append(concept)
    
    return health_concepts_found


def filter_articles_by_health_concepts(
    input_file: str,
    output_file: str,
    health_concepts_file: str = "data/health_concepts.json",
    id_field: str = "uri"
) -> Dict[str, int]:
    """
    Filter articles that contain health concepts and save to new file.
    
    Args:
        input_file: Path to input JSONL file
        output_file: Path to output JSONL file (articles with health concepts only)
        health_concepts_file: Path to health concepts JSON file
        id_field: Field to use as article identifier
        
    Returns:
        Dictionary with statistics
    """
    print(f"📖 Loading health concepts from {health_concepts_file}...")
    health_uris = load_health_concepts(health_concepts_file)
    print(f"✅ Loaded {len(health_uris)} health concept URIs")
    
    print(f"\n📊 Processing articles from {input_file}...")
    
    # Count articles
    with open(input_file, 'r', encoding='utf-8') as f:
        total_articles = sum(1 for _ in f)
    
    print(f"   Found {total_articles:,} articles")
    
    # Process articles
    articles_with_health = 0
    articles_without_concepts = 0
    
    with open(input_file, 'r', encoding='utf-8') as infile:
        with open(output_file, 'w', encoding='utf-8') as outfile:
            for line in tqdm(infile, total=total_articles, desc="🔍 Checking articles"):
                try:
                    article = json.loads(line.strip())
                    
                    # Check if article has health concepts
                    if has_health_concept(article, health_uris):
                        # Get the health concepts found
                        health_concepts_found = get_health_concepts_in_article(article, health_uris)
                        
                        # Add health concepts info to article
                        article["health_concepts"] = health_concepts_found
                        article["has_health_concept"] = True
                        
                        # Write to output
                        outfile.write(json.dumps(article) + '\n')
                        articles_with_health += 1
                    
                    # Track articles without any concepts
                    if not article.get("concepts"):
                        articles_without_concepts += 1
                        
                except json.JSONDecodeError:
                    continue
    
    # Statistics
    stats = {
        "total_articles": total_articles,
        "articles_with_health_concepts": articles_with_health,
        "articles_without_concepts": articles_without_concepts,
        "percentage_with_health": (articles_with_health / total_articles * 100) if total_articles > 0 else 0
    }
    
    print(f"\n✅ Filtering complete!")
    print(f"   Total articles: {stats['total_articles']:,}")
    print(f"   Articles with health concepts: {stats['articles_with_health_concepts']:,} ({stats['percentage_with_health']:.2f}%)")
    print(f"   Articles without any concepts: {stats['articles_without_concepts']:,}")
    print(f"   Output saved to: {output_file}")
    
    return stats


def add_health_flags_to_articles(
    input_file: str,
    output_file: str,
    health_concepts_file: str = "data/health_concepts.json"
) -> Dict[str, int]:
    """
    Add health concept flags to all articles (doesn't filter, adds flag to all).
    
    Args:
        input_file: Path to input JSONL file
        output_file: Path to output JSONL file (all articles with health flags added)
        health_concepts_file: Path to health concepts JSON file
        
    Returns:
        Dictionary with statistics
    """
    print(f"📖 Loading health concepts from {health_concepts_file}...")
    health_uris = load_health_concepts(health_concepts_file)
    print(f"✅ Loaded {len(health_uris)} health concept URIs")
    
    print(f"\n📊 Processing articles from {input_file}...")
    
    # Count articles
    with open(input_file, 'r', encoding='utf-8') as f:
        total_articles = sum(1 for _ in f)
    
    print(f"   Found {total_articles:,} articles")
    
    # Process articles
    articles_with_health = 0
    
    with open(input_file, 'r', encoding='utf-8') as infile:
        with open(output_file, 'w', encoding='utf-8') as outfile:
            for line in tqdm(infile, total=total_articles, desc="🏥 Adding health flags"):
                try:
                    article = json.loads(line.strip())
                    
                    # Get health concepts (if any)
                    health_concepts_found = get_health_concepts_in_article(article, health_uris)
                    
                    # Add health info to article
                    article["has_health_concept"] = len(health_concepts_found) > 0
                    article["health_concepts"] = health_concepts_found
                    article["health_concept_count"] = len(health_concepts_found)
                    
                    if health_concepts_found:
                        articles_with_health += 1
                    
                    # Write to output
                    outfile.write(json.dumps(article) + '\n')
                        
                except json.JSONDecodeError:
                    continue
    
    # Statistics
    stats = {
        "total_articles": total_articles,
        "articles_with_health_concepts": articles_with_health,
        "percentage_with_health": (articles_with_health / total_articles * 100) if total_articles > 0 else 0
    }
    
    print(f"\n✅ Processing complete!")
    print(f"   Total articles: {stats['total_articles']:,}")
    print(f"   Articles with health concepts: {stats['articles_with_health_concepts']:,} ({stats['percentage_with_health']:.2f}%)")
    print(f"   Output saved to: {output_file}")
    
    return stats


def main():
    """Example usage."""
    
    INPUT_FILE = "data/climate_articles_keywords.jsonl"
    
    # Option 1: Filter to only articles with health concepts
    OUTPUT_FILE_FILTERED = "data/climate_health_articles.jsonl"
    
    print("="*70)
    print("OPTION 1: Filter articles with health concepts only")
    print("="*70)
    
    stats = filter_articles_by_health_concepts(
        input_file=INPUT_FILE,
        output_file=OUTPUT_FILE_FILTERED
    )
    
    print("\n" + "="*70)
    print("OPTION 2: Add health flags to all articles")
    print("="*70)
    
    # Option 2: Add health flags to all articles (keeps all articles)
    OUTPUT_FILE_FLAGGED = "data/climate_articles_with_health_flags.jsonl"
    
    stats2 = add_health_flags_to_articles(
        input_file=INPUT_FILE,
        output_file=OUTPUT_FILE_FLAGGED
    )
    
    print("\n🎉 All done!")


if __name__ == "__main__":
    main()

