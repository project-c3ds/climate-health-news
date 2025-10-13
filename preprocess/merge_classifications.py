#!/usr/bin/env python3
"""
Merge classification results back with original article data.

This script takes the minimal classification output (uri + classification)
and merges it back with the original article JSONL file.

Usage:
    python merge_classifications.py
"""

import json
from pathlib import Path
from tqdm import tqdm


def merge_classifications(
    articles_file: str,
    classifications_file: str,
    output_file: str,
    id_field: str = "uri"
):
    """
    Merge classification results with original articles.
    
    Args:
        articles_file: Path to original articles JSONL file
        classifications_file: Path to classifications JSONL file (uri + results)
        output_file: Path to output merged JSONL file
        id_field: Field name used as identifier. Default: "uri"
    """
    print("🔄 Loading classifications into memory...")
    
    # Load all classifications into a dictionary for fast lookup
    classifications = {}
    with open(classifications_file, 'r', encoding='utf-8') as f:
        for line in tqdm(f, desc="Reading classifications"):
            try:
                record = json.loads(line.strip())
                uri = record.get(id_field)
                if uri:
                    classifications[uri] = {
                        "is_climate_or_energy": record.get("is_climate_or_energy"),
                        "justification": record.get("justification"),
                        "error": record.get("error")
                    }
            except json.JSONDecodeError:
                continue
    
    print(f"✅ Loaded {len(classifications):,} classifications")
    
    # Count total articles
    print("\n📊 Counting articles...")
    with open(articles_file, 'r', encoding='utf-8') as f:
        total = sum(1 for _ in f)
    print(f"   Found {total:,} articles")
    
    # Merge and write
    print("\n🔗 Merging classifications with articles...")
    matched = 0
    unmatched = 0
    
    with open(articles_file, 'r', encoding='utf-8') as infile:
        with open(output_file, 'w', encoding='utf-8') as outfile:
            for line in tqdm(infile, total=total, desc="Merging"):
                try:
                    article = json.loads(line.strip())
                    uri = article.get(id_field)
                    
                    if uri and uri in classifications:
                        # Add classification to article
                        article["classification"] = classifications[uri]
                        matched += 1
                    else:
                        # No classification found
                        article["classification"] = {
                            "is_climate_or_energy": None,
                            "justification": None,
                            "error": "Not classified"
                        }
                        unmatched += 1
                    
                    outfile.write(json.dumps(article) + '\n')
                    
                except json.JSONDecodeError:
                    continue
    
    print(f"\n✅ Merge complete!")
    print(f"   Matched: {matched:,} articles")
    print(f"   Unmatched: {unmatched:,} articles")
    print(f"   Output: {output_file}")


def main():
    """Merge classifications with original articles."""
    
    # Configuration
    ARTICLES_FILE = "data/climate_articles_keywords.jsonl"
    CLASSIFICATIONS_FILE = "data/climate_articles_keywords_classified.jsonl"
    OUTPUT_FILE = "data/climate_articles_keywords_with_classifications.jsonl"
    
    print(f"""
📋 Merge Configuration:
   Articles:        {ARTICLES_FILE}
   Classifications: {CLASSIFICATIONS_FILE}
   Output:          {OUTPUT_FILE}
    """)
    
    merge_classifications(
        articles_file=ARTICLES_FILE,
        classifications_file=CLASSIFICATIONS_FILE,
        output_file=OUTPUT_FILE,
        id_field="uri"
    )
    
    print("\n🎉 All done!")


if __name__ == "__main__":
    main()

