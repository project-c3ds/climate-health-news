import pandas as pd
import os
from dotenv import load_dotenv
from eventregistry import EventRegistry, QueryArticlesIter
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
from utils import get_eea38_plus_uk_countries

EEA38_PLUS_UK_COUNTRIES = get_eea38_plus_uk_countries()

load_dotenv()
API_KEY = os.getenv('NEWSAPI_KEY')
er = EventRegistry(apiKey=API_KEY)

def load_newspaper_data(csv_path='newspaper_rankings_all_countries_4imn_with_domain.csv'):
    """Load newspaper data and filter for top 5 newspapers per EEA country."""
    df = pd.read_csv(csv_path)
    df_eea = df[df.country_name.isin(EEA38_PLUS_UK_COUNTRIES)]
    return df_eea.groupby('country_name').head(5)

def get_source_uri(website_name):
    """Get EventRegistry source URI for a website."""
    return er.getNewsSourceUri(website_name)

def fetch_articles(website_name, max_articles=50):
    """Fetch articles from a news source."""
    try:
        source_uri = get_source_uri(website_name)
        
        if not source_uri:
            return {
                'source_uri': None,
                'articles': [],
                'total_found': 0,
                'status': 'error'
            }
        
        query = QueryArticlesIter(sourceUri=source_uri)
        articles = []
        
        for article in query.execQuery(er, sortBy="date", maxItems=max_articles, dataType=['news', 'blog']):
            articles.append(article)
        
        status = 'success' if len(articles) == max_articles else 'partial'
        
        return {
            'source_uri': source_uri,
            'articles': articles,
            'total_found': len(articles),
            'status': status
        }
        
    except Exception:
        return {
            'source_uri': None,
            'articles': [],
            'total_found': 0,
            'status': 'error'
        }

def fetch_articles_concurrent(domain_urls, max_workers=10):
    """Fetch articles for multiple domains concurrently."""
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(fetch_articles, url): url for url in domain_urls}
        results = [None] * len(domain_urls)
        url_to_index = {url: i for i, url in enumerate(domain_urls)}
        
        for future in tqdm(as_completed(futures), total=len(futures), desc="Fetching articles"):
            url = futures[future]
            index = url_to_index[url]
            try:
                results[index] = future.result()
            except Exception:
                results[index] = {
                    'source_uri': None,
                    'articles': [],
                    'total_found': 0,
                    'status': 'error'
                }
        
        return results

def add_article_data(df):
    """Add article data to dataframe using concurrent processing."""
    results = fetch_articles_concurrent(df['domain_url'].tolist())
    
    df['newsapi_results'] = results
    df['source_uri'] = df['newsapi_results'].apply(lambda x: x['source_uri'])
    df['articles'] = df['newsapi_results'].apply(lambda x: x['articles'])
    df['articles_count'] = df['newsapi_results'].apply(lambda x: x['total_found'])
    df['status'] = df['newsapi_results'].apply(lambda x: x['status'])
    
    return df

def main():
    """Main execution function."""
    df_top5 = load_newspaper_data()
    df_with_articles = add_article_data(df_top5)
    
    print(f"Status distribution: {df_with_articles.status.value_counts().to_dict()}")
    
    df_with_articles.to_json('eea_38_top5_newsapi_results.jsonl', orient='records', lines=True)
    print("Results saved to eea_38_top5_newsapi_results.jsonl")

if __name__ == "__main__":
    main()