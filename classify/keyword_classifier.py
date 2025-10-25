#!/usr/bin/env python3
"""
BM25-based keyword classifier for articles.

This module provides a flexible BM25 classifier that can classify articles
based on keyword matching using the BM25 scoring algorithm.
"""

import pandas as pd
import numpy as np
from rank_bm25 import BM25Okapi
from typing import List, Union, Optional


class BM25KeywordClassifier:
    """
    BM25-based keyword classifier for text classification.
    
    Uses the BM25 algorithm to score documents based on keyword relevance
    and classifies them based on a threshold score.
    """
    
    def __init__(self, keywords: List[str]):
        """
        Initialize the BM25 classifier with keywords.
        
        Args:
            keywords: List of keywords to match against
        """
        self.keywords = keywords
        self.bm25 = None
        
    def _preprocess_text(self, text: str) -> List[str]:
        """
        Preprocess text by converting to lowercase and splitting into tokens.
        
        Args:
            text: Text to preprocess
            
        Returns:
            List of tokens
        """
        if pd.isna(text) or text is None:
            return []
        return str(text).lower().split()
    
    def fit(self, corpus: List[str]) -> 'BM25KeywordClassifier':
        """
        Fit the BM25 model on a corpus of documents.
        
        Args:
            corpus: List of documents to fit on
            
        Returns:
            self
        """
        # Preprocess all documents
        tokenized_corpus = [self._preprocess_text(doc) for doc in corpus]
        
        # Initialize BM25
        self.bm25 = BM25Okapi(tokenized_corpus)
        
        return self
    
    def score(self, text: str) -> float:
        """
        Score a single document against the keywords using BM25.
        
        Args:
            text: Document text to score
            
        Returns:
            BM25 score for the document
        """
        if self.bm25 is None:
            raise ValueError("BM25 model not fitted. Call fit() first.")
        
        # Tokenize query (keywords)
        query_tokens = []
        for keyword in self.keywords:
            query_tokens.extend(self._preprocess_text(keyword))
        
        # Get BM25 score for this document's index
        # Since we need to score against pre-fitted corpus, we'll use a different approach
        # We'll compute scores for all docs and return the relevant one
        # This is handled in classify_dataframe for efficiency
        
        # For single scoring, we tokenize the text and match against keywords
        doc_tokens = self._preprocess_text(text)
        
        # Count keyword matches (simple approach for single doc)
        score = 0.0
        for keyword in self.keywords:
            keyword_tokens = self._preprocess_text(keyword)
            for token in keyword_tokens:
                if token in doc_tokens:
                    score += doc_tokens.count(token)
        
        return score
    
    def classify_dataframe(
        self,
        df: pd.DataFrame,
        text_field: str,
        threshold: float,
        score_column: str = 'bm25_score',
        classification_column: str = 'bm25_classification'
    ) -> pd.DataFrame:
        """
        Classify articles in a dataframe using BM25 keyword matching.
        
        Args:
            df: DataFrame containing articles to classify
            text_field: Name of the column containing text to classify
            threshold: Score threshold for classification (docs >= threshold are classified as True)
            score_column: Name of column to store BM25 scores (default: 'bm25_score')
            classification_column: Name of column to store classifications (default: 'bm25_classification')
            
        Returns:
            DataFrame with added score and classification columns
        """
        # Make a copy to avoid modifying original
        df_copy = df.copy()
        
        # Check if text field exists
        if text_field not in df_copy.columns:
            raise ValueError(f"Text field '{text_field}' not found in dataframe")
        
        # Get corpus from dataframe
        corpus = df_copy[text_field].fillna('').tolist()
        
        # Fit BM25 on the corpus
        self.fit(corpus)
        
        # Tokenize query (keywords)
        query_tokens = []
        for keyword in self.keywords:
            query_tokens.extend(self._preprocess_text(keyword))
        
        # Remove duplicates while preserving order
        query_tokens = list(dict.fromkeys(query_tokens))
        
        # Get BM25 scores for all documents
        scores = self.bm25.get_scores(query_tokens)
        
        # Add scores to dataframe
        df_copy[score_column] = scores
        
        # Add classification based on threshold
        df_copy[classification_column] = df_copy[score_column] >= threshold
        
        return df_copy
    
    def get_top_documents(
        self,
        df: pd.DataFrame,
        text_field: str,
        n: int = 10,
        score_column: str = 'bm25_score'
    ) -> pd.DataFrame:
        """
        Get top N documents by BM25 score.
        
        Args:
            df: DataFrame with BM25 scores
            text_field: Name of the text column
            n: Number of top documents to return
            score_column: Name of the score column
            
        Returns:
            DataFrame with top N documents sorted by score
        """
        if score_column not in df.columns:
            raise ValueError(f"Score column '{score_column}' not found. Run classify_dataframe first.")
        
        return df.nlargest(n, score_column)


def classify_with_keywords(
    df: pd.DataFrame,
    text_field: str,
    keywords: List[str],
    threshold: float,
    score_column: str = 'bm25_score',
    classification_column: str = 'bm25_classification'
) -> pd.DataFrame:
    """
    Convenience function to classify a dataframe with keywords using BM25.
    
    Args:
        df: DataFrame containing articles to classify
        text_field: Name of the column containing text to classify
        keywords: List of keywords to match against
        threshold: Score threshold for classification
        score_column: Name of column to store BM25 scores
        classification_column: Name of column to store classifications
        
    Returns:
        DataFrame with added score and classification columns
        
    Example:
        >>> import pandas as pd
        >>> df = pd.DataFrame({
        ...     'text': ['climate change is real', 'sports news today']
        ... })
        >>> keywords = ['climate change', 'global warming']
        >>> result = classify_with_keywords(df, 'text', keywords, threshold=2.0)
    """
    classifier = BM25KeywordClassifier(keywords)
    return classifier.classify_dataframe(
        df=df,
        text_field=text_field,
        threshold=threshold,
        score_column=score_column,
        classification_column=classification_column
    )


if __name__ == "__main__":
    """
    Example usage of the BM25 keyword classifier.
    """
    # Create sample data
    sample_data = pd.DataFrame({
        'title': [
            'Climate change impacts global temperatures',
            'New research on renewable energy',
            'Sports news: Team wins championship',
            'Global warming threatens ecosystems',
            'Technology advances in smartphones'
        ],
        'body': [
            'Scientists report rising temperatures due to greenhouse gas emissions and climate change.',
            'Solar and wind power are becoming more efficient as renewable energy technology improves.',
            'The local team won the championship game yesterday in a thrilling match.',
            'Ecosystems worldwide face threats from global warming and extreme weather events.',
            'The latest smartphones feature improved cameras and longer battery life.'
        ]
    })
    
    # Combine title and body for classification
    sample_data['text'] = sample_data['title'] + ' ' + sample_data['body']
    
    # Define climate-related keywords
    climate_keywords = [
        'climate change',
        'global warming',
        'greenhouse gas',
        'renewable energy',
        'solar power',
        'wind power',
        'extreme weather'
    ]
    
    # Classify with threshold
    print("Classifying sample articles with BM25...")
    print(f"Keywords: {climate_keywords}")
    print(f"Threshold: 3.0\n")
    
    result = classify_with_keywords(
        df=sample_data,
        text_field='text',
        keywords=climate_keywords,
        threshold=3.0
    )
    
    # Display results
    print("Results:")
    print("="*80)
    for idx, row in result.iterrows():
        print(f"\nArticle {idx + 1}: {row['title']}")
        print(f"  BM25 Score: {row['bm25_score']:.4f}")
        print(f"  Classified: {row['bm25_classification']}")
    
    print("\n" + "="*80)
    print("\nSummary:")
    print(f"Total articles: {len(result)}")
    print(f"Classified as relevant: {result['bm25_classification'].sum()}")
    print(f"Classified as not relevant: {(~result['bm25_classification']).sum()}")
    
    # Show top 3 by score
    print("\n" + "="*80)
    print("\nTop 3 articles by BM25 score:")
    classifier = BM25KeywordClassifier(climate_keywords)
    top_articles = classifier.classify_dataframe(
        sample_data, 'text', threshold=3.0
    ).nlargest(3, 'bm25_score')
    
    for idx, row in top_articles.iterrows():
        print(f"\n{row['title']}")
        print(f"  Score: {row['bm25_score']:.4f}")

