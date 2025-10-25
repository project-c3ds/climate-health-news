import pandas as pd
import numpy as np
from sklearn.metrics import precision_score, recall_score, f1_score, classification_report, hamming_loss, accuracy_score
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

# Start with health, urban, and rural
df = pd.read_parquet('data/articles/lancet_europe_dataset_with_dummies.parquet')

df_predictions = df[['uri', 'health', 'urban_rural_framing']]

df_validation = pd.read_csv('data/samples/lancet_validation_health_urban_rural.csv')

df_combined = pd.merge(df_validation, df_predictions, on='uri', how='left')


# Rename columns to clarify predicted vs actual
df_combined = df_combined.rename(columns={
    'health_code': 'health_actual',
    'health': 'health_pred',
    'bm25_classification': 'bm25_pred',
    'urban_rural_framing': 'urban_rural_framing_pred'
})

# Break up urban_rural_framing_pred into binary columns
df_combined['urban_pred'] = 0
df_combined['rural_pred'] = 0
df_combined['not_urban_rural_pred'] = 0

# Set values based on urban_rural_framing_pred
df_combined.loc[df_combined['urban_rural_framing_pred'] == 'urban', 'urban_pred'] = 1
df_combined.loc[df_combined['urban_rural_framing_pred'] == 'rural', 'rural_pred'] = 1
df_combined.loc[df_combined['urban_rural_framing_pred'] == 'both', ['urban_pred', 'rural_pred']] = 1
df_combined.loc[df_combined['urban_rural_framing_pred'] == 'neither', 'not_urban_rural_pred'] = 1

# Reformat bm25_pred to int
df_combined['bm25_pred'] = df_combined['bm25_pred'].astype(int)

# Functions to calculate performance metrics
def calculate_metrics(y_true, y_pred, labels=None, average='binary'):
    """
    Calculate precision, recall, and F1 score.
    
    Parameters:
    - y_true: actual labels
    - y_pred: predicted labels
    - labels: list of labels (for multiclass)
    - average: 'binary' for binary classification, 'weighted' or 'macro' for multiclass
    
    Returns:
    - Dictionary with precision, recall, and F1 scores
    """
    precision = precision_score(y_true, y_pred, labels=labels, average=average, zero_division=0)
    recall = recall_score(y_true, y_pred, labels=labels, average=average, zero_division=0)
    f1 = f1_score(y_true, y_pred, labels=labels, average=average, zero_division=0)
    
    return {
        'precision': precision,
        'recall': recall,
        'f1': f1
    }

def print_performance_report(df, actual_col, pred_col, task_name, labels=None, average='binary'):
    """
    Print performance metrics for a classification task.
    
    Parameters:
    - df: dataframe with actual and predicted columns
    - actual_col: column name for actual labels
    - pred_col: column name for predicted labels
    - task_name: name of the task (for display)
    - labels: list of labels (for multiclass)
    - average: averaging method for metrics
    """
    # Remove any NaN values
    df_clean = df[[actual_col, pred_col]].dropna()
    
    print(f"\n{'='*60}")
    print(f"{task_name} Performance Metrics")
    print(f"{'='*60}")
    
    metrics = calculate_metrics(df_clean[actual_col], df_clean[pred_col], labels=labels, average=average)
    
    print(f"Precision: {metrics['precision']:.4f}")
    print(f"Recall:    {metrics['recall']:.4f}")
    print(f"F1 Score:  {metrics['f1']:.4f}")
    
    print(f"\nDetailed Classification Report:")
    print(classification_report(df_clean[actual_col], df_clean[pred_col], labels=labels, zero_division=0))
    
    return metrics

def print_multilabel_performance(df, actual_cols, pred_cols, task_name):
    """
    Print performance metrics for multilabel classification.
    
    Parameters:
    - df: dataframe with actual and predicted columns
    - actual_cols: list of column names for actual labels
    - pred_cols: list of column names for predicted labels
    - task_name: name of the task (for display)
    """
    # Remove rows with NaN values in any of the columns
    all_cols = actual_cols + pred_cols
    df_clean = df[all_cols].dropna()
    
    # Create multilabel arrays
    y_true = df_clean[actual_cols].values
    y_pred = df_clean[pred_cols].values
    
    print(f"\n{'='*60}")
    print(f"{task_name} Multilabel Performance Metrics")
    print(f"{'='*60}")
    
    # Calculate multilabel metrics
    # Samples-based metrics (macro-averaged across samples)
    precision_samples = precision_score(y_true, y_pred, average='samples', zero_division=0)
    recall_samples = recall_score(y_true, y_pred, average='samples', zero_division=0)
    f1_samples = f1_score(y_true, y_pred, average='samples', zero_division=0)
    
    # Micro-averaged metrics (aggregate over all label-sample pairs)
    precision_micro = precision_score(y_true, y_pred, average='micro', zero_division=0)
    recall_micro = recall_score(y_true, y_pred, average='micro', zero_division=0)
    f1_micro = f1_score(y_true, y_pred, average='micro', zero_division=0)
    
    # Macro-averaged metrics (unweighted mean of per-label metrics)
    precision_macro = precision_score(y_true, y_pred, average='macro', zero_division=0)
    recall_macro = recall_score(y_true, y_pred, average='macro', zero_division=0)
    f1_macro = f1_score(y_true, y_pred, average='macro', zero_division=0)
    
    # Subset accuracy (exact match)
    subset_accuracy = accuracy_score(y_true, y_pred)
    
    # Hamming loss (fraction of labels that are incorrectly predicted)
    hamming = hamming_loss(y_true, y_pred)
    
    print(f"\nSample-based Metrics (macro-averaged across samples):")
    print(f"  Precision: {precision_samples:.4f}")
    print(f"  Recall:    {recall_samples:.4f}")
    print(f"  F1 Score:  {f1_samples:.4f}")
    
    print(f"\nMicro-averaged Metrics (aggregate over all label-sample pairs):")
    print(f"  Precision: {precision_micro:.4f}")
    print(f"  Recall:    {recall_micro:.4f}")
    print(f"  F1 Score:  {f1_micro:.4f}")
    
    print(f"\nMacro-averaged Metrics (unweighted mean per label):")
    print(f"  Precision: {precision_macro:.4f}")
    print(f"  Recall:    {recall_macro:.4f}")
    print(f"  F1 Score:  {f1_macro:.4f}")
    
    print(f"\nOther Metrics:")
    print(f"  Subset Accuracy (exact match): {subset_accuracy:.4f}")
    print(f"  Hamming Loss:                   {hamming:.4f}")
    
    print(f"\nPer-Label Metrics:")
    for i, (actual_col, pred_col) in enumerate(zip(actual_cols, pred_cols)):
        label_name = actual_col.replace('_code', '').replace('not_urban_rural', 'neither')
        precision = precision_score(df_clean[actual_col], df_clean[pred_col], average='binary', zero_division=0)
        recall = recall_score(df_clean[actual_col], df_clean[pred_col], average='binary', zero_division=0)
        f1 = f1_score(df_clean[actual_col], df_clean[pred_col], average='binary', zero_division=0)
        print(f"  {label_name:20s} - Precision: {precision:.4f}, Recall: {recall:.4f}, F1: {f1:.4f}")
    
    return {
        'precision_samples': precision_samples,
        'recall_samples': recall_samples,
        'f1_samples': f1_samples,
        'precision_micro': precision_micro,
        'recall_micro': recall_micro,
        'f1_micro': f1_micro,
        'precision_macro': precision_macro,
        'recall_macro': recall_macro,
        'f1_macro': f1_macro,
        'subset_accuracy': subset_accuracy,
        'hamming_loss': hamming
    }

# Calculate and print performance for health classification
health_metrics = print_performance_report(
    df_combined, 
    'health_actual', 
    'health_pred', 
    'Health Classification',
    average='binary'
)

# Calculate and print performance for bm25 classification
bm25_metrics = print_performance_report(
    df_combined, 
    'health_actual', 
    'bm25_pred', 
    'BM25 Classification',
    average='binary'
)

# Calculate and print performance for urban/rural multilabel classification
urban_rural_metrics = print_multilabel_performance(
    df_combined,
    actual_cols=['urban_code', 'rural_code', 'not_urban_rural'],
    pred_cols=['urban_pred', 'rural_pred', 'not_urban_rural_pred'],
    task_name='Urban/Rural Framing'
)

# Examine validation of inquality 
df_inequality = pd.read_csv('data/samples/lancet_validation_inequality.csv')

df_predictions = pd.read_parquet('data/articles/lancet_europe_health_subset_with_dummies.parquet')[['uri', 'inequality']]

df_inequality_combined = pd.merge(df_inequality, df_predictions, on='uri', how='left')

df_inequality_combined = df_inequality_combined.rename(columns={
    'inequality_code': 'inequality_actual',
    'inequality_y': 'inequality_pred'
})

# Calculate and print performance for inequality classification
inequality_metrics = print_performance_report(
    df_inequality_combined,
    'inequality_actual',
    'inequality_pred',
    'Inequality Classification',
    average='binary'
)
