"""
Count total articles available for each source URI by month using EventRegistry API.
This script queries the API without any keyword or concept filters to get the total article counts.
"""

import os
import json
import pandas as pd
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from newsapi_batch import ArticleCollector
from utils import load_sources

def generate_month_ranges(start_date: str, end_date: str):
    """
    Generate a list of (start, end) date tuples for each month in the date range.
    
    Args:
        start_date (str): Start date in 'YYYY-MM-DD' format
        end_date (str): End date in 'YYYY-MM-DD' format
    
    Returns:
        list: List of tuples containing (month_start, month_end, month_label)
    """
    start = datetime.strptime(start_date, '%Y-%m-%d')
    end = datetime.strptime(end_date, '%Y-%m-%d')
    
    month_ranges = []
    current = start
    
    while current <= end:
        # First day of current month
        month_start = current.replace(day=1)
        
        # Last day of current month
        next_month = month_start + relativedelta(months=1)
        month_end = next_month - timedelta(days=1)
        
        # Don't go beyond the end date
        if month_end > end:
            month_end = end
        
        # Create month label (YYYY-MM format)
        month_label = month_start.strftime('%Y-%m')
        
        month_ranges.append((
            month_start.strftime('%Y-%m-%d'),
            month_end.strftime('%Y-%m-%d'),
            month_label
        ))
        
        # Move to next month
        current = next_month
    
    return month_ranges


def count_articles_by_source_and_month(sources_df: pd.DataFrame, 
                                       date_start: str = '2023-01-01',
                                       date_end: str = '2025-09-30',
                                       output_dir: str = 'data/source_counts',
                                       force_reprocess: bool = False):
    """
    Count total articles for each source by month using EventRegistry API.
    
    Args:
        sources_df (pd.DataFrame): DataFrame containing source information
        date_start (str): Start date in 'YYYY-MM-DD' format
        date_end (str): End date in 'YYYY-MM-DD' format
        output_dir (str): Directory to save the count results
        force_reprocess (bool): If True, reprocess sources even if output file exists (default: False)
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Initialize the collector
    collector = ArticleCollector()
    
    # Generate month ranges
    month_ranges = generate_month_ranges(date_start, date_end)
    print(f"\nProcessing {len(month_ranges)} months from {date_start} to {date_end}")
    print(f"Processing {len(sources_df)} sources")
    
    # Process each source
    all_results = []
    skipped_count = 0
    processed_count = 0
    
    for idx, source_row in sources_df.iterrows():
        source_uri = source_row['source_uri']
        source_filename = f"{source_uri}.json"
        source_filepath = os.path.join(output_dir, source_filename)
        
        # Check if source has already been processed
        if os.path.exists(source_filepath) and not force_reprocess:
            print(f"\n⏭️  Skipping source {idx+1}/{len(sources_df)}: {source_uri} (already processed)")
            skipped_count += 1
            
            # Load existing results for summary
            try:
                with open(source_filepath, 'r', encoding='utf-8') as f:
                    existing_result = json.load(f)
                    all_results.append(existing_result)
            except Exception as e:
                print(f"  ⚠️  Warning: Could not load existing file: {e}")
            continue
        
        print(f"\n{'='*60}")
        print(f"Processing source {idx+1}/{len(sources_df)}: {source_uri}")
        print(f"{'='*60}")
        processed_count += 1
        
        source_counts = {
            'source_uri': source_uri,
            'domain_url': source_row.get('domain_url', ''),
            'newspaper_name': source_row.get('newspaper_name', ''),
            'country_name': source_row.get('country_name', ''),
            'dominant_language': source_row.get('dominant_language', ''),
            'monthly_counts': []
        }
        
        # Count articles for each month
        for month_start, month_end, month_label in month_ranges:
            try:
                print(f"\n  Month: {month_label} ({month_start} to {month_end})")
                
                # Count articles without any keyword or concept filters
                count = collector.count_articles(
                    sources=[source_uri],
                    date_start=month_start,
                    date_end=month_end,
                    # No keywords, concepts, or filters - just get total count
                )
                
                source_counts['monthly_counts'].append({
                    'month': month_label,
                    'start_date': month_start,
                    'end_date': month_end,
                    'count': count
                })
                
                print(f"  ✓ Found {count:,} articles for {month_label}")
                
            except Exception as e:
                print(f"  ✗ ERROR counting articles for {month_label}: {e}")
                source_counts['monthly_counts'].append({
                    'month': month_label,
                    'start_date': month_start,
                    'end_date': month_end,
                    'count': 0,
                    'error': str(e)
                })
        
        # Calculate total articles
        total_articles = sum(m['count'] for m in source_counts['monthly_counts'])
        source_counts['total_articles'] = total_articles
        
        # Save individual source file
        source_filename = f"{source_uri}.json"
        source_filepath = os.path.join(output_dir, source_filename)
        
        with open(source_filepath, 'w', encoding='utf-8') as f:
            json.dump(source_counts, f, indent=2, ensure_ascii=False)
        
        print(f"\n  💾 Saved: {source_filepath}")
        print(f"  📊 Total articles: {total_articles:,}")
        
        all_results.append(source_counts)
    
    # Save summary file with all sources
    summary_filepath = os.path.join(output_dir, 'all_sources_summary.json')
    with open(summary_filepath, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)
    
    print(f"\n{'='*60}")
    print(f"✅ Processing complete!")
    print(f"{'='*60}")
    print(f"📊 Summary:")
    print(f"   - Sources processed: {processed_count}")
    print(f"   - Sources skipped (already completed): {skipped_count}")
    print(f"   - Total sources: {len(sources_df)}")
    print(f"\n💾 Output:")
    print(f"   - Individual source files saved to: {output_dir}/")
    print(f"   - Summary file saved to: {summary_filepath}")
    
    # Create a summary CSV for easy viewing
    summary_data = []
    for result in all_results:
        summary_data.append({
            'source_uri': result['source_uri'],
            'newspaper_name': result['newspaper_name'],
            'country_name': result['country_name'],
            'dominant_language': result['dominant_language'],
            'total_articles': result['total_articles']
        })
    
    summary_df = pd.DataFrame(summary_data)
    summary_csv_path = os.path.join(output_dir, 'sources_summary.csv')
    summary_df.to_csv(summary_csv_path, index=False)
    print(f"Summary CSV saved to: {summary_csv_path}")
    
    return all_results


if __name__ == "__main__":
    # Load all sources
    print("Loading sources...")
    sources = load_sources()
    
    # Optional: Filter sources by status
    # sources = sources[sources['status'] == 'success']
    
    print(f"Loaded {len(sources)} sources")

    # Filter sources by country
    sources = sources[sources['country_name'] == 'Cyprus']
    
    # Count articles by source and month
    # Set force_reprocess=True to recount sources that have already been processed
    results = count_articles_by_source_and_month(
        sources_df=sources,
        date_start='2023-01-01',
        date_end='2025-09-30',
        output_dir='data/source_counts',
        force_reprocess=True  # Set to True to reprocess all sources
    )
    
    print("\n✨ Done!")

