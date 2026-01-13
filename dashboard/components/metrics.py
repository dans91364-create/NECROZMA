#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚡🌟💎 NECROZMA DASHBOARD - METRICS 💎🌟⚡

KPI calculation utilities
"""

import pandas as pd
import numpy as np
from typing import Dict, List


def calculate_summary_metrics(strategies_df: pd.DataFrame) -> Dict:
    """
    Calculate summary metrics across all strategies
    
    Args:
        strategies_df: DataFrame with strategy results
        
    Returns:
        Dictionary with summary metrics
    """
    # Add null check to prevent NoneType errors
    if strategies_df is None or strategies_df.empty:
        return {
            'total_strategies': 0,
            'avg_sharpe': 0.0,
            'avg_return': 0.0,
            'avg_win_rate': 0.0,
            'viable_count': 0,
            'max_sharpe': 0.0,
            'max_return': 0.0,
            'min_drawdown': 0.0
        }
    
    # Viable strategies (Sharpe > 1.0, win_rate > 0.5)
    viable_mask = (strategies_df.get('sharpe_ratio', 0) > 1.0) & \
                  (strategies_df.get('win_rate', 0) > 0.5)
    
    return {
        'total_strategies': len(strategies_df),
        'avg_sharpe': strategies_df.get('sharpe_ratio', pd.Series([0])).mean(),
        'avg_return': strategies_df.get('total_return', pd.Series([0])).mean() * 100,
        'avg_win_rate': strategies_df.get('win_rate', pd.Series([0])).mean() * 100,
        'viable_count': viable_mask.sum(),
        'max_sharpe': strategies_df.get('sharpe_ratio', pd.Series([0])).max(),
        'max_return': strategies_df.get('total_return', pd.Series([0])).max() * 100,
        'min_drawdown': strategies_df.get('max_drawdown', pd.Series([0])).min() * 100,
    }


def get_top_strategies(strategies_df: pd.DataFrame, 
                      by: str = 'sharpe_ratio',
                      n: int = 20) -> pd.DataFrame:
    """
    Get top N strategies by metric
    
    Args:
        strategies_df: DataFrame with strategy results
        by: Metric to sort by
        n: Number of strategies to return
        
    Returns:
        DataFrame with top strategies
    """
    if strategies_df.empty or by not in strategies_df.columns:
        return pd.DataFrame()
    
    top = strategies_df.nlargest(n, by).copy()
    
    # Format for display
    if 'total_return' in top.columns:
        top['total_return_pct'] = top['total_return'] * 100
    if 'max_drawdown' in top.columns:
        top['max_drawdown_pct'] = top['max_drawdown'] * 100
    if 'win_rate' in top.columns:
        top['win_rate_pct'] = top['win_rate'] * 100
    
    return top


def calculate_universe_stats(strategies_df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate statistics by universe
    
    Args:
        strategies_df: DataFrame with strategy results
        
    Returns:
        DataFrame with universe statistics
    """
    if strategies_df.empty or 'universe_name' not in strategies_df.columns:
        return pd.DataFrame()
    
    universe_stats = strategies_df.groupby('universe_name').agg({
        'sharpe_ratio': ['mean', 'max', 'count'],
        'total_return': ['mean', 'max'],
        'win_rate': 'mean',
        'n_trades': 'mean',
        'max_drawdown': 'mean'
    }).round(3)
    
    # Flatten column names
    universe_stats.columns = ['_'.join(col).strip() for col in universe_stats.columns.values]
    universe_stats = universe_stats.reset_index()
    
    return universe_stats.sort_values('sharpe_ratio_max', ascending=False)


def create_universe_matrix(strategies_df: pd.DataFrame) -> pd.DataFrame:
    """
    Create matrix of metrics by interval and lookback
    
    Args:
        strategies_df: DataFrame with strategy results
        
    Returns:
        Pivot table with interval x lookback
    """
    if strategies_df.empty:
        return pd.DataFrame()
    
    # Check required columns
    required = ['interval', 'lookback', 'sharpe_ratio']
    if not all(col in strategies_df.columns for col in required):
        return pd.DataFrame()
    
    # Group by interval and lookback, take max Sharpe
    matrix = strategies_df.groupby(['interval', 'lookback'])['sharpe_ratio'].max().unstack(fill_value=0)
    
    return matrix


def calculate_sl_tp_matrix(strategies_df: pd.DataFrame) -> pd.DataFrame:
    """
    Create SL/TP optimization matrix
    
    Args:
        strategies_df: DataFrame with strategy results
        
    Returns:
        Pivot table with SL x TP
    """
    from dashboard.utils.data_loader import extract_sl_tp_from_name
    
    if strategies_df.empty:
        return pd.DataFrame()
    
    if 'strategy_name' in strategies_df.columns:
        # Create a copy to avoid modifying the original DataFrame
        df_copy = strategies_df.copy()
        df_copy[['sl', 'tp']] = df_copy['strategy_name'].apply(
            lambda x: pd.Series(extract_sl_tp_from_name(x))
        )
        
        # Filter rows with SL/TP data
        valid_rows = df_copy.dropna(subset=['sl', 'tp'])
        
        if not valid_rows.empty:
            matrix = valid_rows.groupby(['sl', 'tp'])['total_return'].mean().unstack(fill_value=0)
            return matrix
    
    return pd.DataFrame()


def identify_efficient_frontier(strategies_df: pd.DataFrame) -> pd.DataFrame:
    """
    Identify strategies on the efficient frontier (best return for given risk)
    
    Args:
        strategies_df: DataFrame with strategy results
        
    Returns:
        DataFrame with efficient frontier strategies
    """
    if strategies_df.empty:
        return pd.DataFrame()
    
    required = ['max_drawdown', 'total_return']
    if not all(col in strategies_df.columns for col in required):
        return pd.DataFrame()
    
    # Sort by drawdown
    sorted_df = strategies_df.sort_values('max_drawdown').copy()
    
    # Find strategies on frontier (higher return than all previous at same risk level)
    efficient = []
    max_return_so_far = -np.inf
    
    for idx, row in sorted_df.iterrows():
        if row['total_return'] > max_return_so_far:
            efficient.append(idx)
            max_return_so_far = row['total_return']
    
    return strategies_df.loc[efficient].sort_values('max_drawdown')


def calculate_risk_metrics(strategies_df: pd.DataFrame) -> Dict:
    """
    Calculate risk-related metrics
    
    Args:
        strategies_df: DataFrame with strategy results
        
    Returns:
        Dictionary with risk metrics
    """
    if strategies_df.empty:
        return {}
    
    metrics = {}
    
    if 'max_drawdown' in strategies_df.columns:
        metrics['avg_drawdown'] = strategies_df['max_drawdown'].mean() * 100
        metrics['max_drawdown'] = strategies_df['max_drawdown'].max() * 100
        
    if 'sharpe_ratio' in strategies_df.columns:
        metrics['avg_sharpe'] = strategies_df['sharpe_ratio'].mean()
        
    if 'sortino_ratio' in strategies_df.columns:
        metrics['avg_sortino'] = strategies_df['sortino_ratio'].mean()
        
    if 'calmar_ratio' in strategies_df.columns:
        metrics['avg_calmar'] = strategies_df['calmar_ratio'].mean()
    
    return metrics


def extract_sl_tp_statistics(strategies_df):
    """
    Extract SL/TP from all strategies and create statistics.
    
    Args:
        strategies_df: DataFrame with strategy results
    
    Returns:
        dict: Statistics about SL/TP usage
    """
    from dashboard.utils.data_loader import extract_sl_tp_from_name
    
    sl_tp_data = []
    
    for _, row in strategies_df.iterrows():
        sl, tp = extract_sl_tp_from_name(row['strategy_name'])
        if sl is not None and tp is not None:
            sl_tp_data.append({
                'strategy_name': row['strategy_name'],
                'sl': sl,
                'tp': tp,
                'risk_reward_ratio': tp / sl if sl > 0 else 0,
                'sharpe_ratio': row.get('sharpe_ratio', 0),
                'total_return': row.get('total_return', 0),
                'win_rate': row.get('win_rate', 0),
                'n_trades': row.get('n_trades', 0)
            })
    
    stats = {
        'total_strategies': len(strategies_df),
        'strategies_with_sl_tp': len(sl_tp_data),
        'coverage_pct': (len(sl_tp_data) / len(strategies_df) * 100) if len(strategies_df) > 0 else 0,
        'unique_sl_values': set(d['sl'] for d in sl_tp_data),
        'unique_tp_values': set(d['tp'] for d in sl_tp_data),
        'data': sl_tp_data
    }
    
    return stats
