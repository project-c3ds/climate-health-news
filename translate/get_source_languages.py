import pandas as pd
from collections import Counter

def get_dominant_language(newsapi_results):
    """
    Extract the dominant language from newsapi_results articles.
    
    Returns:
        tuple: (dominant_language, percentage)
    """
    if not newsapi_results or 'articles' not in newsapi_results:
        return (None, 0.0)
    
    articles = newsapi_results['articles']
    if not articles:
        return (None, 0.0)
    
    # Extract all languages
    languages = [article.get('lang') for article in articles if article.get('lang')]
    
    if not languages:
        return (None, 0.0)
    
    # Count language occurrences
    lang_counter = Counter(languages)
    
    # Get most common language
    dominant_lang, count = lang_counter.most_common(1)[0]
    
    # Calculate percentage
    percentage = (count / len(languages)) * 100
    
    return (dominant_lang, round(percentage, 2))

# Load the data
df_sources = pd.read_json('data/sources/input_data/eea_38_top5_newsapi_results.jsonl', lines=True)

# Apply the function to extract dominant language and percentage
df_sources[['dominant_language', 'language_percentage']] = df_sources['newsapi_results'].apply(
    lambda x: pd.Series(get_dominant_language(x))
)

# Display results
print("Source languages extracted:")
print(df_sources[['domain_url', 'dominant_language', 'language_percentage']].head(10))
print(f"\nTotal sources: {len(df_sources)}")
print(f"\nLanguage distribution:")
print(df_sources['dominant_language'].value_counts())

df_sources = pd.read_json('data/sources/input_data/eea_38_top5_newsapi_results_with_languages.jsonl', lines=True)

# List domains with missing source_uri
missing_source_uri = df_sources[df_sources['source_uri'].isna() | (df_sources['source_uri'] == '')]
if len(missing_source_uri) > 0:
    print(f"\nDomains with missing source_uri ({len(missing_source_uri)}):")
    for idx, row in missing_source_uri.iterrows():
        print(f"  - {row['domain_url']}")
        # Print the source from first article if available
        if 'newsapi_results' in row and row['newsapi_results']:
            articles = row['newsapi_results'].get('articles', [])
            if articles and len(articles) > 0:
                source = articles[0].get('source')
                print(f"    First article source: {source}")
            else:
                print(f"    No articles found")
        else:
            print(f"    No newsapi_results found")
else:
    print("\nNo missing source_uri values found")

# Remove sources with missing source_uri
df_sources = df_sources[df_sources['source_uri'].notna() & (df_sources['source_uri'] != '')]

# Save results to CSV with selected columns
columns_to_save = [
    'source_uri', 'domain_url', 'newspaper_name', 'newspaper_url', 'country_name',
    'country_url', 'rank_in_country', 'status', 'dominant_language',
    'language_percentage'
]

output_file = 'data/sources/sources.csv'
df_sources[columns_to_save].to_csv(output_file, index=False)
print(f"\nResults saved to {output_file}")
