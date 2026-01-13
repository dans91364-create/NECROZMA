#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚡🌟💎 NECROZMA DASHBOARD - TABLES 💎🌟⚡

Data table formatting utilities
"""

import pandas as pd
import streamlit as st
from typing import List, Optional


def format_strategies_table(strategies_df: pd.DataFrame, 
                           columns: Optional[List[str]] = None) -> pd.DataFrame:
    """
    Format strategies DataFrame for display
    
    Args:
        strategies_df: DataFrame with strategy data
        columns: Optional list of columns to include
        
    Returns:
        Formatted DataFrame
    """
    if strategies_df.empty:
        return pd.DataFrame()
    
    # Default columns if not specified
    if columns is None:
        columns = [
            'strategy_name', 'universe_name', 'sharpe_ratio', 
            'total_return', 'win_rate', 'max_drawdown', 
            'n_trades', 'profit_factor'
        ]
    
    # Filter to available columns
    available_cols = [col for col in columns if col in strategies_df.columns]
    
    if not available_cols:
        return strategies_df
    
    display_df = strategies_df[available_cols].copy()
    
    # Format percentage columns
    pct_cols = ['total_return', 'win_rate', 'max_drawdown']
    for col in pct_cols:
        if col in display_df.columns:
            display_df[col] = display_df[col] * 100
            display_df = display_df.rename(columns={col: f"{col} (%)"})
    
    # Round numeric columns
    numeric_cols = display_df.select_dtypes(include=['float64', 'float32']).columns
    display_df[numeric_cols] = display_df[numeric_cols].round(2)
    
    return display_df


def create_sortable_table(df: pd.DataFrame, 
                         key: str = "table",
                         height: int = 400) -> None:
    """
    Create sortable, scrollable table
    
    Args:
        df: DataFrame to display
        key: Unique key for widget
        height: Table height in pixels
    """
    if df.empty:
        st.info("No data available")
        return
    
    st.dataframe(
        df,
        use_container_width=True,
        height=height,
        key=key
    )


def create_metric_cards(metrics: dict, columns: int = 4) -> None:
    """
    Create metric cards layout
    
    Args:
        metrics: Dictionary of metric_name: value
        columns: Number of columns
    """
    cols = st.columns(columns)
    
    items = list(metrics.items())
    for i, (name, value) in enumerate(items):
        col_idx = i % columns
        
        # Format value
        if isinstance(value, float):
            if abs(value) < 1 and value != 0:
                formatted_value = f"{value:.3f}"
            else:
                formatted_value = f"{value:.2f}"
        else:
            formatted_value = str(value)
        
        # Display in column
        with cols[col_idx]:
            st.metric(
                label=name.replace('_', ' ').title(),
                value=formatted_value
            )


def format_trades_table(trades_df: pd.DataFrame) -> pd.DataFrame:
    """
    Format trades DataFrame for display
    
    Args:
        trades_df: DataFrame with trade data
        
    Returns:
        Formatted DataFrame
    """
    if trades_df.empty:
        return pd.DataFrame()
    
    display_df = trades_df.copy()
    
    # Select relevant columns
    display_cols = []
    for col in ['entry_time', 'exit_time', 'direction', 'entry_price', 
                'exit_price', 'pnl_pips', 'pnl_usd', 'pnl_pct', 
                'duration_minutes', 'exit_reason']:
        if col in display_df.columns:
            display_cols.append(col)
    
    if display_cols:
        display_df = display_df[display_cols]
    
    # Round numeric columns
    numeric_cols = display_df.select_dtypes(include=['float64', 'float32']).columns
    display_df[numeric_cols] = display_df[numeric_cols].round(2)
    
    return display_df


def highlight_top_performers(df: pd.DataFrame, 
                            column: str = 'sharpe_ratio',
                            top_n: int = 5) -> pd.DataFrame:
    """
    Highlight top N rows by column value
    
    Args:
        df: DataFrame to style
        column: Column to use for highlighting
        top_n: Number of top rows to highlight
        
    Returns:
        Styled DataFrame
    """
    if df.empty or column not in df.columns:
        return df
    
    # Get indices of top N
    top_indices = df.nlargest(top_n, column).index
    
    def highlight_row(row):
        if row.name in top_indices:
            return ['background-color: #90EE9044'] * len(row)
        return [''] * len(row)
    
    return df.style.apply(highlight_row, axis=1)


def create_comparison_table(strategies: List[pd.Series], 
                           strategy_names: List[str]) -> pd.DataFrame:
    """
    Create side-by-side comparison table
    
    Args:
        strategies: List of strategy Series
        strategy_names: List of strategy names
        
    Returns:
        Comparison DataFrame
    """
    if not strategies:
        return pd.DataFrame()
    
    comparison = pd.DataFrame({
        name: strategy 
        for name, strategy in zip(strategy_names, strategies)
    })
    
    return comparison.T
