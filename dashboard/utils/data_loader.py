"""
Data loader utilities for the trading strategy dashboard.
Handles loading and processing of strategy backtest results.
"""

import json
import pandas as pd
import numpy as np
from pathlib import Path
from typing import List, Dict, Any, Optional


def load_json_file(file_path: Path) -> Optional[Dict[str, Any]]:
    """
    Load a single JSON file with error handling.
    
    Args:
        file_path: Path to the JSON file
        
    Returns:
        Dictionary containing the JSON data, or None if error
    """
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print(f"JSON decode error in {file_path}: {e}")
        return None
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
        return None


def extract_strategy_data(data: Any) -> Optional[Dict[str, Any]]:
    """
    Extract strategy data from various JSON structures.
    
    Args:
        data: JSON data that could be dict, list, or other structure
        
    Returns:
        Dictionary with strategy metrics, or None if invalid
    """
    if isinstance(data, dict):
        # Check if this is already a strategy result with the expected fields
        if 'strategy_name' in data:
            return data
        # Check for common wrapper keys
        for key in ['results', 'strategy', 'metrics', 'data']:
            if key in data and isinstance(data[key], dict):
                if 'strategy_name' in data[key]:
                    return data[key]
    return None


def load_all_results(base_path: str = "results") -> pd.DataFrame:
    """
    Load all strategy results from JSON files.
    
    Args:
        base_path: Directory containing result JSON files
        
    Returns:
        DataFrame with all strategy results and metrics
    """
    all_results = []
    results_path = Path(base_path)
    
    if not results_path.exists():
        print(f"Warning: Results directory '{base_path}' does not exist")
        return pd.DataFrame()
    
    # Find all JSON files in the results directory
    json_files = list(results_path.glob("*.json"))
    print(f"Found {len(json_files)} JSON files in {base_path}")
    
    for file_path in json_files:
        data = load_json_file(file_path)
        if data is None:
            continue
            
        # Extract strategy data from the JSON structure
        if isinstance(data, list):
            # Handle array of results
            for item in data:
                strategy_data = extract_strategy_data(item)
                if strategy_data:
                    all_results.append(strategy_data)
        else:
            # Handle single result
            strategy_data = extract_strategy_data(data)
            if strategy_data:
                all_results.append(strategy_data)
    
    if not all_results:
        print("Warning: No valid strategy results found")
        return pd.DataFrame()
    
    print(f"Loaded {len(all_results)} strategy results")
    
    # Create DataFrame from the results
    # Use pd.DataFrame constructor which properly handles nested dicts
    strategies_df = pd.DataFrame(all_results)
    
    # Debug: Print available columns
    print(f"DataFrame shape: {strategies_df.shape}")
    print(f"Available columns: {list(strategies_df.columns)}")
    
    # Define expected columns based on the JSON structure
    expected_columns = [
        'strategy_name',
        'n_trades',
        'win_rate',
        'profit_factor',
        'total_return',
        'sharpe_ratio',
        'sortino_ratio',
        'calmar_ratio',
        'max_drawdown',
        'avg_win',
        'avg_loss',
        'largest_win',
        'largest_loss',
        'expectancy',
        'recovery_factor',
        'ulcer_index',
        'trades_detailed'
    ]
    
    # Check for missing columns
    missing_columns = [col for col in expected_columns if col not in strategies_df.columns]
    if missing_columns:
        print(f"Warning: Missing expected columns: {missing_columns}")
        # Add missing columns with NaN values
        for col in missing_columns:
            if col != 'trades_detailed':  # Don't add NaN for trades_detailed
                strategies_df[col] = np.nan
    
    # Convert numeric columns to appropriate types
    numeric_columns = [
        'n_trades', 'win_rate', 'profit_factor', 'total_return',
        'sharpe_ratio', 'sortino_ratio', 'calmar_ratio', 'max_drawdown',
        'avg_win', 'avg_loss', 'largest_win', 'largest_loss',
        'expectancy', 'recovery_factor', 'ulcer_index'
    ]
    
    for col in numeric_columns:
        if col in strategies_df.columns:
            try:
                strategies_df[col] = pd.to_numeric(strategies_df[col], errors='coerce')
            except Exception as e:
                print(f"Warning: Could not convert column '{col}' to numeric: {e}")
    
    return strategies_df


def get_strategy_metrics(strategies_df: pd.DataFrame, strategy_name: str) -> Optional[Dict[str, Any]]:
    """
    Get metrics for a specific strategy.
    
    Args:
        strategies_df: DataFrame with all strategies
        strategy_name: Name of the strategy to retrieve
        
    Returns:
        Dictionary with strategy metrics, or None if not found
    """
    if strategies_df.empty:
        return None
    
    if 'strategy_name' not in strategies_df.columns:
        print("Error: 'strategy_name' column not found in DataFrame")
        return None
    
    strategy_data = strategies_df[strategies_df['strategy_name'] == strategy_name]
    
    if strategy_data.empty:
        print(f"Warning: Strategy '{strategy_name}' not found")
        return None
    
    return strategy_data.iloc[0].to_dict()


def get_top_strategies(strategies_df: pd.DataFrame, metric: str = 'sharpe_ratio', n: int = 10) -> pd.DataFrame:
    """
    Get top N strategies by a specific metric.
    
    Args:
        strategies_df: DataFrame with all strategies
        metric: Metric to rank by (default: 'sharpe_ratio')
        n: Number of top strategies to return
        
    Returns:
        DataFrame with top N strategies
    """
    if strategies_df.empty:
        return pd.DataFrame()
    
    if metric not in strategies_df.columns:
        print(f"Error: Metric '{metric}' not found in DataFrame")
        print(f"Available columns: {list(strategies_df.columns)}")
        # Fallback to sharpe_ratio or first numeric column
        numeric_cols = strategies_df.select_dtypes(include=[np.number]).columns
        if 'sharpe_ratio' in numeric_cols:
            metric = 'sharpe_ratio'
        elif len(numeric_cols) > 0:
            metric = numeric_cols[0]
        else:
            return strategies_df.head(n)
    
    # Sort by metric (descending) and return top N
    try:
        return strategies_df.nlargest(n, metric)
    except Exception as e:
        print(f"Error sorting by '{metric}': {e}")
        return strategies_df.head(n)


def validate_dataframe(df: pd.DataFrame) -> bool:
    """
    Validate that the DataFrame has the required structure.
    
    Args:
        df: DataFrame to validate
        
    Returns:
        True if valid, False otherwise
    """
    if df.empty:
        print("Validation failed: DataFrame is empty")
        return False
    
    required_columns = ['strategy_name', 'sharpe_ratio', 'total_return', 'max_drawdown']
    missing = [col for col in required_columns if col not in df.columns]
    
    if missing:
        print(f"Validation failed: Missing required columns: {missing}")
        print(f"Available columns: {list(df.columns)}")
        return False
    
    return True


# Main loading function for dashboard
def load_dashboard_data(base_path: str = "results") -> pd.DataFrame:
    """
    Load and validate data for the dashboard.
    
    Args:
        base_path: Directory containing result JSON files
        
    Returns:
        Validated DataFrame ready for dashboard use
    """
    print(f"Loading dashboard data from: {base_path}")
    df = load_all_results(base_path)
    
    if validate_dataframe(df):
        print("Data loaded and validated successfully")
        print(f"Total strategies: {len(df)}")
        if 'sharpe_ratio' in df.columns:
            print(f"Sharpe ratio range: {df['sharpe_ratio'].min():.2f} to {df['sharpe_ratio'].max():.2f}")
    else:
        print("Warning: Data validation failed, dashboard may not work correctly")
    
    return df


if __name__ == "__main__":
    # Test the data loader
    print("Testing data loader...")
    df = load_dashboard_data()
    print(f"\nLoaded {len(df)} strategies")
    if not df.empty:
        print(f"\nColumns: {list(df.columns)}")
        print(f"\nFirst strategy:\n{df.iloc[0]}")
