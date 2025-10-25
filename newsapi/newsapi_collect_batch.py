from eventregistry import *
import datetime
from typing import Optional, Union, Dict, List, Tuple
import pandas as pd
import os
from dotenv import load_dotenv
from utils import load_sources, save_article_as_json

# Load environment variables
load_dotenv()
PLATFORM = 'newsapi'


class ArticleCollector:
    """
    A class to collect and count news articles from EventRegistry.
    """
    
    def __init__(self):
        """Initialize the ArticleCollector with EventRegistry API connection."""
        api_key = os.getenv('NEWSAPI_KEY')
        if not api_key:
            raise ValueError("NEWSAPI_KEY not found in environment variables")
        
        self.er = EventRegistry(apiKey=api_key)
        self.platform = PLATFORM
    
    def _build_query_params(self,
                           sources: list = None,
                           date_start: Union[str, datetime.date] = None,
                           date_end: Union[str, datetime.date] = None,
                           keywords: list = None,
                           concepts: list = None,
                           exclude_keywords: list = None,
                           exclude_concepts: list = None,
                           lang: str = None) -> dict:
        """
        Build query parameters for EventRegistry queries.
        
        Args:
            sources (list of str, optional): List of source URIs
            date_start (str or datetime.date, optional): Start date
            date_end (str or datetime.date, optional): End date
            keywords (list of str, optional): Keywords to search for
            concepts (list of str, optional): Concepts to include
            exclude_keywords (list of str, optional): Keywords to exclude
            exclude_concepts (list of str, optional): Concepts to exclude
            lang (str, optional): ISO 639-3 language code
            
        Returns:
            dict: Query parameters for EventRegistry
        """
        # Load sources if not provided
        if sources is None or len(sources) == 0:
            print("Loading sources from data/sources/sources.csv")
            sources_df = load_sources()
            # load_sources returns a DataFrame, extract the source_uri column as a list
            if sources_df is None or sources_df.empty:
                raise ValueError("No sources provided and unable to load from data/sources/sources.csv")
            # Extract source URIs from DataFrame
            if 'source_uri' in sources_df.columns:
                sources = sources_df['source_uri'].tolist()
            else:
                raise ValueError("source_uri column not found in sources DataFrame")
        
        print(f"Using {len(sources)} sources")
        
        # Set default dates if not provided
        if date_start is None:
            date_start = datetime.date.today() - datetime.timedelta(days=7)
        if date_end is None:
            date_end = datetime.date.today()
        
        print(f"Date range: {date_start} to {date_end}")
        
        # Build query parameters
        query_params = {
            'sourceUri': QueryItems.OR(sources),
            'dateStart': date_start,
            'dateEnd': date_end,
            'isDuplicateFilter': 'skipDuplicates',
            'dataType': ['news', 'blog']
        }
        
        # Add language filter if specified
        if lang:
            query_params['lang'] = lang
            print(f"Filtering by language: {lang}")
        
        # Add keywords if available
        if keywords:
            # Use QueryItems.OR() as per EventRegistry documentation
            query_params['keywords'] = QueryItems.OR(keywords)
            query_params['keywordSearchMode'] = 'exact'
            print(f"Using keywords (OR): {keywords[:10]}..." if len(keywords) > 10 else f"Using keywords (OR): {keywords}")
        
        # Add excluded keywords if available
        if exclude_keywords:
            # Use QueryItems.OR() for excluded keywords as well
            query_params['ignoreKeywords'] = QueryItems.OR(exclude_keywords)
            print(f"Excluding keywords (OR): {exclude_keywords[:10]}..." if len(exclude_keywords) > 10 else f"Excluding keywords (OR): {exclude_keywords}")
        
        # Add concepts if available
        if concepts:
            print(f"Looking up URIs for {len(concepts)} concepts...")
            concept_uris = []
            for i, concept in enumerate(concepts):
                try:
                    uri = self.er.getConceptUri(concept)
                    concept_uris.append(uri)
                    if (i + 1) % 5 == 0:
                        print(f"  Processed {i + 1}/{len(concepts)} concepts")
                except Exception as e:
                    print(f"  WARNING: Failed to get URI for concept '{concept}': {e}")
            query_params['conceptUri'] = QueryItems.OR(concept_uris)
            print(f"Using {len(concept_uris)} concepts: {concepts[:100]}..." if len(concepts) > 100 else f"Using {len(concept_uris)} concepts: {concepts}")
        
        # Add excluded concepts if available
        if exclude_concepts:
            print(f"Looking up URIs for {len(exclude_concepts)} excluded concepts...")
            exclude_concept_uris = []
            for i, concept in enumerate(exclude_concepts):
                try:
                    uri = self.er.getConceptUri(concept)
                    exclude_concept_uris.append(uri)
                    if (i + 1) % 5 == 0:
                        print(f"  Processed {i + 1}/{len(exclude_concepts)} excluded concepts")
                except Exception as e:
                    print(f"  WARNING: Failed to get URI for excluded concept '{concept}': {e}")
            # For ignoring concepts, use OR to exclude any matching concept
            query_params['ignoreConceptUri'] = QueryItems.OR(exclude_concept_uris)
            print(f"Excluding {len(exclude_concept_uris)} concepts: {exclude_concepts[:100]}..." if len(exclude_concepts) > 100 else f"Excluding {len(exclude_concept_uris)} concepts: {exclude_concepts}")
        
        return query_params
    
    def count_articles(self,
                      sources: list = None,
                      date_start: Union[str, datetime.date] = None,
                      date_end: Union[str, datetime.date] = None,
                      keywords: list = None,
                      concepts: list = None,
                      exclude_keywords: list = None,
                      exclude_concepts: list = None,
                      lang: str = None) -> int:
        """
        Count articles matching the query without retrieving them.
        
        Args:
            sources (list of str, optional): List of source URIs
            date_start (str or datetime.date, optional): Start date
            date_end (str or datetime.date, optional): End date
            keywords (list of str, optional): Keywords to search for
            concepts (list of str, optional): Concepts to include
            exclude_keywords (list of str, optional): Keywords to exclude
            exclude_concepts (list of str, optional): Concepts to exclude
            lang (str, optional): ISO 639-3 language code
            
        Returns:
            int: Number of articles matching the query
        """
        try:
            print("\n=== Counting Articles ===")
            
            # Build query parameters
            query_params = self._build_query_params(
                sources=sources,
                date_start=date_start,
                date_end=date_end,
                keywords=keywords,
                concepts=concepts,
                exclude_keywords=exclude_keywords,
                exclude_concepts=exclude_concepts,
                lang=lang
            )
            
            # Create query for counting
            q = QueryArticles(**query_params)
            
            # Request article count - use page 0 with 0 results to just get the count
            q.setRequestedResult(RequestArticlesInfo(page=1, count=0))
            
            # Execute query to get count
            result = self.er.execQuery(q)
            
            # Extract count from result
            count = result.get('articles', {}).get('totalResults', 0)
            
            print(f"Total articles found: {count}")
            print("=" * 30)
            
            return count
            
        except Exception as e:
            print(f"ERROR counting articles: {e}")
            raise
    
    def collect_batch(self,
                     sources: list = None,
                     date_start: Union[str, datetime.date] = None,
                     date_end: Union[str, datetime.date] = None,
                     keywords: list = None,
                     concepts: list = None,
                     exclude_keywords: list = None,
                     exclude_concepts: list = None,
                     lang: str = None,
                     max_items: int = 10000) -> Tuple[List[Dict], Dict]:
        """
        Collect news articles from EventRegistry for a specific date range.
        
        Args:
            sources (list of str, optional):
                A list of source URIs for relevant newspapers. If None, loads from data/sources.csv.
            date_start (str or datetime.date, optional):
                Start date in "YYYY-MM-DD" format or datetime.date object. If None, defaults to 7 days ago.
            date_end (str or datetime.date, optional):
                End date in "YYYY-MM-DD" format or datetime.date object. If None, defaults to today.
            keywords (list of str, optional):
                A list of keywords to search for. Keywords will be combined with OR logic.
                If None, no keyword filtering is applied.
            concepts (list of str, optional):
                A list of concepts to include in the search.
            exclude_keywords (list of str, optional):
                A list of keywords to exclude from results.
            exclude_concepts (list of str, optional):
                A list of concepts to exclude from results.
            lang (str, optional):
                ISO 639-3 language code to filter articles (e.g., 'eng', 'spa', 'fra').
                If None, no language filtering is applied.
            max_items (int):
                Maximum number of articles to retrieve (default: 10000).
        
        Returns:
            content (list of dict):
                A list of articles with metadata.
            stats (dict):
                A dictionary containing metadata about the collection.
        """
        try:
            print("\n=== Starting Batch Collection ===")
            
            # Build query parameters using shared method
            query_params = self._build_query_params(
                sources=sources,
                date_start=date_start,
                date_end=date_end,
                keywords=keywords,
                concepts=concepts,
                exclude_keywords=exclude_keywords,
                exclude_concepts=exclude_concepts,
                lang=lang
            )
            
            # Create iterator query
            q = QueryArticlesIter(**query_params)
            
            content = []
            article_count = 0

            return_info = ReturnInfo(
                articleInfo=ArticleInfoFlags(
                    concepts=True,           # Include concepts
                    categories=True,         # Include categories
            ))
            
            # Iterate through results
            for article in q.execQuery(self.er, sortBy="date", maxItems=max_items, returnInfo=return_info):
                try:
                    # Add date_time object to article
                    if 'dateTime' in article:
                        article['date_time'] = datetime.datetime.strptime(article['dateTime'], '%Y-%m-%dT%H:%M:%SZ')
                    
                    # Save individual article as JSON file
                    json_file_path = save_article_as_json(article)
                    if json_file_path:
                        print(f"💾 Saved article to: {json_file_path}")
                    
                    content.append(article)
                    article_count += 1
                    
                    # Log progress every 100 articles
                    if article_count % 100 == 0:
                        print(f"Collected {article_count} articles...")
                except Exception as e:
                    print(f"ERROR processing article {article_count + 1}: {e}")
                    continue
            
            print(f'Total articles collected: {article_count}')
            
            # Collect and update stats
            timestamp = datetime.datetime.utcnow().replace(microsecond=0).isoformat()
            stats = {
                'api': 'newsapi_batch',
                'posts_collected_count': article_count,
                'collection_timestamp': timestamp,
                'date_start': str(query_params['dateStart']),
                'date_end': str(query_params['dateEnd']),
                'max_items_requested': max_items,
                'keywords_used': bool(keywords)
            }
            
            # Print final statistics
            print(f"\n=== Collection Statistics ===")
            for key, value in stats.items():
                print(f"{key}: {value}")
            print("=" * 30)
            
            return content, stats
            
        except Exception as e:
            print(f"ERROR in batch collection process: {e}")
            raise


def save_batch_results(content: list, stats: dict, output_dir: str = 'data'):
    """
    Save batch collection results to parquet and JSON files.
    
    Args:
        content (list): List of articles
        stats (dict): Collection statistics  
        output_dir (str): Directory to save results
    """
    try:
        print(f"Saving batch results to {output_dir}")
        
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            print(f"Created output directory: {output_dir}")
        
        timestamp_str = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Save articles to parquet
        if content:
            df = pd.DataFrame(content)
            parquet_file = f'{output_dir}/newsapi_batch_{timestamp_str}.parquet'
            df.to_parquet(parquet_file)
            print(f"Articles saved to: {parquet_file}")
            
            # Save stats to JSON
            import json
            stats_file = f'{output_dir}/newsapi_batch_stats_{timestamp_str}.json'
            with open(stats_file, 'w') as f:
                json.dump(stats, f, indent=4)
            print(f"Statistics saved to: {stats_file}")
        else:
            print("WARNING: No articles to save")
            
    except Exception as e:
        print(f"ERROR saving batch results: {e}")
        raise


# Example usage (commented out)
"""
if __name__ == "__main__":
    # Initialize the collector
    collector = ArticleCollector()
    
    # Example sources - replace with actual EventRegistry source URIs
    example_sources = [
        "bbc.co.uk",
        "reuters.com", 
        "theguardian.com"
    ]
    
    # Example keywords
    keywords = ["climate change", "global warming", "renewable energy"]
    
    # Set date range
    date_end = datetime.date.today()
    date_start = date_end - datetime.timedelta(days=7)
    
    # First, count the articles
    count = collector.count_articles(
        sources=example_sources,
        keywords=keywords,
        lang="eng",
        date_start=date_start,
        date_end=date_end
    )
    print(f"Found {count} articles")
    
    # Then collect them
    content, stats = collector.collect_batch(
        sources=example_sources,
        keywords=keywords,
        exclude_keywords=["sports", "entertainment"],
        lang="eng",
        date_start=date_start,
        date_end=date_end,
        max_items=1000
    )
    
    # Save results
    save_batch_results(content, stats)
"""