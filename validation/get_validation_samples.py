"""
Compare classification performance of keyword-based and LLM-based classifiers.

This script first gets the keyword-based classifications and then take a random
sample for human annotation.
"""

import pandas as pd
import numpy as np
from classify.keyword_classifier import classify_with_keywords
from utils import load_keywords


def stratified_sample_from_crosstab(
    df: pd.DataFrame,
    var1: str,
    var2: str,
    n_per_cell: int,
    sample_label_col: str = 'sample_label',
    random_state: int = None
) -> pd.DataFrame:
    """
    Take a random sample from each cell of a crosstab and label samples by cell.
    
    Args:
        df: DataFrame containing data to sample from
        var1: Name of first variable (row variable in crosstab)
        var2: Name of second variable (column variable in crosstab)
        n_per_cell: Number of samples to take from each cell
        sample_label_col: Name of column to store sample labels (default: 'sample_label')
        random_state: Random seed for reproducibility
        
    Returns:
        DataFrame containing sampled rows with added sample_label column
        
    Example:
        >>> df_sample = stratified_sample_from_crosstab(
        ...     df, 'health', 'bm25_classification', n_per_cell=10
        ... )
    """
    # Check if variables exist
    if var1 not in df.columns:
        raise ValueError(f"Variable '{var1}' not found in dataframe")
    if var2 not in df.columns:
        raise ValueError(f"Variable '{var2}' not found in dataframe")
    
    # Get unique values for each variable
    var1_values = df[var1].dropna().unique()
    var2_values = df[var2].dropna().unique()
    
    print(f"Crosstab sampling: {var1} x {var2}")
    print(f"  {var1} values: {sorted(var1_values)}")
    print(f"  {var2} values: {sorted(var2_values)}")
    print(f"  Samples per cell: {n_per_cell}")
    print(f"\nCell counts:")
    
    # Show crosstab before sampling
    crosstab = pd.crosstab(df[var1], df[var2], margins=True)
    print(crosstab)
    
    # Store sampled dataframes
    sampled_dfs = []
    
    # Sample from each cell
    for val1 in var1_values:
        for val2 in var2_values:
            # Filter to this cell
            cell_df = df[(df[var1] == val1) & (df[var2] == val2)].copy()
            cell_size = len(cell_df)
            
            # Create label for this cell
            label = f"{var1}_{val1}_{var2}_{val2}"
            
            # Sample from this cell
            if cell_size == 0:
                print(f"\n  {label}: 0 rows (skipping)")
                continue
            elif cell_size < n_per_cell:
                print(f"\n  {label}: {cell_size} rows (taking all, requested {n_per_cell})")
                sample_df = cell_df.copy()
            else:
                print(f"\n  {label}: {cell_size} rows (sampling {n_per_cell})")
                sample_df = cell_df.sample(n=n_per_cell, random_state=random_state)
            
            # Add sample label
            sample_df[sample_label_col] = label
            sampled_dfs.append(sample_df)
    
    # Combine all samples
    if not sampled_dfs:
        print("\nWARNING: No samples collected")
        result_df = pd.DataFrame()
    else:
        result_df = pd.concat(sampled_dfs, ignore_index=True)
    
    print(f"\n{'='*60}")
    print(f"SAMPLING SUMMARY")
    print(f"{'='*60}")
    print(f"Total samples collected: {len(result_df)}")
    print(f"Expected samples: {len(var1_values) * len(var2_values) * n_per_cell}")
    if len(result_df) > 0:
        print(f"\nSamples by label:")
        print(result_df[sample_label_col].value_counts().sort_index())
    print(f"{'='*60}")
    
    return result_df


def classify_by_language(
    df: pd.DataFrame,
    text_field: str,
    threshold: float,
    lang_column: str = 'lang',
    keywords_file: str = 'data/translations/climate_official_translations.json',
    score_column: str = 'bm25_score',
    classification_column: str = 'bm25_classification'
) -> pd.DataFrame:
    """
    Classify articles by grouping by language, applying language-specific keywords,
    and combining results back together.
    
    Args:
        df: DataFrame containing articles to classify
        text_field: Name of the column containing text to classify
        threshold: Score threshold for classification
        lang_column: Name of the column containing language codes (default: 'lang')
        keywords_file: Path to keywords JSON file
        score_column: Name of column to store BM25 scores
        classification_column: Name of column to store classifications
        
    Returns:
        DataFrame with added score and classification columns for all languages
        
    Example:
        >>> df = pd.read_parquet('articles.parquet')
        >>> df_classified = classify_by_language(df, 'body', threshold=2.0)
    """
    # Check if language column exists
    if lang_column not in df.columns:
        raise ValueError(f"Language column '{lang_column}' not found in dataframe")
    
    # Get unique languages in the dataframe
    languages = df[lang_column].dropna().unique()
    print(f"Found {len(languages)} languages in dataframe: {sorted(languages)}")
    
    # Store classified dataframes for each language
    classified_dfs = []
    
    # Process each language group
    for lang in languages:
        print(f"\nProcessing language: {lang}")
        
        # Filter dataframe for this language
        lang_df = df[df[lang_column] == lang].copy()
        print(f"  Articles in {lang}: {len(lang_df)}")
        
        # Load keywords for this language
        keywords = load_keywords(lang, keywords_file)
        
        if not keywords:
            print(f"  WARNING: No keywords found for {lang}, skipping classification")
            # Add empty classification columns for this language
            lang_df[score_column] = 0.0
            lang_df[classification_column] = False
        else:
            # Classify with language-specific keywords
            lang_df = classify_with_keywords(
                df=lang_df,
                text_field=text_field,
                keywords=keywords,
                threshold=threshold,
                score_column=score_column,
                classification_column=classification_column
            )
            
            # Report classification results
            num_classified = lang_df[classification_column].sum()
            pct_classified = (num_classified / len(lang_df) * 100) if len(lang_df) > 0 else 0
            print(f"  Classified: {num_classified} / {len(lang_df)} ({pct_classified:.1f}%)")
        
        classified_dfs.append(lang_df)
    
    # Handle rows with missing language
    missing_lang_df = df[df[lang_column].isna()]
    if len(missing_lang_df) > 0:
        print(f"\nWARNING: {len(missing_lang_df)} articles have missing language codes")
        print("  These articles will not be classified")
        missing_lang_df = missing_lang_df.copy()
        missing_lang_df[score_column] = 0.0
        missing_lang_df[classification_column] = False
        classified_dfs.append(missing_lang_df)
    
    # Combine all classified dataframes
    df_combined = pd.concat(classified_dfs, ignore_index=False)
    
    # Sort by original index to maintain order
    df_combined = df_combined.sort_index()
    
    print(f"\n{'='*60}")
    print(f"TOTAL CLASSIFICATION SUMMARY")
    print(f"{'='*60}")
    print(f"Total articles: {len(df_combined)}")
    print(f"Total classified: {df_combined[classification_column].sum()}")
    print(f"Overall percentage: {(df_combined[classification_column].sum() / len(df_combined) * 100):.1f}%")
    print(f"{'='*60}")
    
    return df_combined


#if __name__ == "__main__":
# Load data
df = pd.read_parquet('data/database/lancet_europe_dataset_with_dummies.parquet')

# Classify with language-specific keywords
df = classify_by_language(
    df, 
    'body', 
    keywords_file='data/translations/health_official_translations.json', 
    threshold=2.0
)

# Create crosstab of health and bm25_classification
print("\nCrosstab of health and BM25 classification:")
print(pd.crosstab(df['health'], df['bm25_classification'], margins=True))

# Plot histogram of BM25 scores
import matplotlib.pyplot as plt

plt.figure(figsize=(10, 6))
plt.hist(df['bm25_score'], bins=50, edgecolor='black')
plt.title('Distribution of BM25 Scores')
plt.xlabel('BM25 Score')
plt.ylabel('Number of Articles')
plt.grid(True, alpha=0.3)

# Add vertical line at threshold
plt.axvline(x=2.0, color='red', linestyle='--', label='Classification Threshold')
plt.legend()

plt.tight_layout()
plt.savefig('data/images/bm25_score_distribution.png')
plt.close()

print("\nPlot saved to: data/images/bm25_score_distribution.png")

# Take stratified sample from crosstab
print("\n" + "="*60)
print("STRATIFIED SAMPLING")
print("="*60)

df_sample = stratified_sample_from_crosstab(
    df=df,
    var1='health',
    var2='bm25_classification',
    n_per_cell=25,  # 25 samples per cell
    sample_label_col='sample_label',
    random_state=42  # For reproducibility
)

# Save the sample for human annotation
if len(df_sample) > 0:
    output_file = 'data/samples/validation_sample.parquet'
    df_sample.to_parquet(output_file)
    print(f"\nSample saved to: {output_file}")
    
    # Also save as CSV for easier manual annotation
    csv_file = 'data/samples/validation_sample.csv'
    # Select relevant columns for annotation
    annotation_cols = ['uri', 'title', 'body', 'health', 'bm25_score', 
                        'bm25_classification', 'sample_label', 'lang', 'source_uri']
    df_sample[annotation_cols].to_csv(csv_file, index=False)
    print(f"Sample (CSV) saved to: {csv_file}")
else:
    print("\nNo samples collected - skipping save")

# Get validation sample for inquality
df = pd.read_parquet('data/database/lancet_europe_health_subset_with_dummies.parquet')

# Take stratified sample for inequality validation
print("\n" + "="*60)
print("INEQUALITY VALIDATION SAMPLING")
print("="*60)

# Sample 15 articles from each inequality class
inequality_sample = pd.concat([
    df[df['inequality'] == 0].sample(n=15, random_state=42),
    df[df['inequality'] == 1].sample(n=15, random_state=42)
])

# Save the inequality validation sample
if len(inequality_sample) > 0:
    output_file = 'data/samples/inequality_validation_sample.parquet'
    inequality_sample.to_parquet(output_file)
    print(f"\nInequality sample saved to: {output_file}")
    
    # Also save as CSV for easier manual annotation
    csv_file = 'data/samples/inequality_validation_sample.csv'
    # Select relevant columns for annotation
    annotation_cols = ['uri', 'title', 'body', 'inequality', 'source_uri']
    inequality_sample[annotation_cols].to_csv(csv_file, index=False)
    print(f"Inequality sample (CSV) saved to: {csv_file}")
else:
    print("\nNo inequality samples collected - skipping save")


