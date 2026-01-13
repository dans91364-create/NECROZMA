#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚡🌟💎 NECROZMA DASHBOARD - FILTERS 💎🌟⚡

Interactive filter components
"""

import streamlit as st
import pandas as pd
from typing import Tuple, List, Optional


def create_metric_filter(df: pd.DataFrame, 
                        column: str,
                        label: str = None,
                        default_range: Tuple[float, float] = None) -> Tuple[float, float]:
    """
    Create slider filter for numeric metric
    
    Args:
        df: DataFrame with data
        column: Column to filter
        label: Filter label (uses column name if None)
        default_range: Default range (uses min/max if None)
        
    Returns:
        Tuple of (min_value, max_value)
    """
    if df.empty or column not in df.columns:
        return (0.0, 0.0)
    
    if label is None:
        label = column.replace('_', ' ').title()
    
    col_min = float(df[column].min())
    col_max = float(df[column].max())
    
    if default_range is None:
        default_range = (col_min, col_max)
    
    # Handle edge case where min == max
    if col_min == col_max:
        st.info(f"{label}: {col_min:.2f} (constant)")
        return (col_min, col_max)
    
    values = st.slider(
        label,
        min_value=col_min,
        max_value=col_max,
        value=default_range,
        step=(col_max - col_min) / 100
    )
    
    return values


def create_multiselect_filter(df: pd.DataFrame,
                              column: str,
                              label: str = None,
                              default: str = "all") -> List[str]:
    """
    Create multi-select filter
    
    Args:
        df: DataFrame with data
        column: Column to filter
        label: Filter label (uses column name if None)
        default: "all" to select all, "none" for none, or list of defaults
        
    Returns:
        List of selected values
    """
    if df.empty or column not in df.columns:
        return []
    
    if label is None:
        label = f"Select {column.replace('_', ' ').title()}"
    
    options = sorted(df[column].unique().tolist())
    
    if default == "all":
        default_selection = options
    elif default == "none":
        default_selection = []
    else:
        default_selection = default if isinstance(default, list) else [default]
    
    selected = st.multiselect(
        label,
        options=options,
        default=default_selection
    )
    
    return selected


def create_search_filter(label: str = "Search", 
                        placeholder: str = "Enter search term...") -> str:
    """
    Create text search filter
    
    Args:
        label: Filter label
        placeholder: Placeholder text
        
    Returns:
        Search string
    """
    search = st.text_input(label, placeholder=placeholder)
    return search.lower().strip()


def apply_filters(df: pd.DataFrame, filters: dict) -> pd.DataFrame:
    """
    Apply multiple filters to DataFrame
    
    Args:
        df: DataFrame to filter
        filters: Dictionary of {column: filter_value}
        
    Returns:
        Filtered DataFrame
    """
    if df.empty:
        return df
    
    filtered_df = df.copy()
    
    for column, filter_value in filters.items():
        if column not in filtered_df.columns:
            continue
        
        if isinstance(filter_value, tuple) and len(filter_value) == 2:
            # Range filter
            min_val, max_val = filter_value
            filtered_df = filtered_df[
                (filtered_df[column] >= min_val) & 
                (filtered_df[column] <= max_val)
            ]
        elif isinstance(filter_value, list):
            # Multi-select filter
            if filter_value:  # Only filter if list is not empty
                filtered_df = filtered_df[filtered_df[column].isin(filter_value)]
        elif isinstance(filter_value, str):
            # Text search
            if filter_value:  # Only filter if string is not empty
                filtered_df = filtered_df[
                    filtered_df[column].astype(str).str.lower().str.contains(filter_value)
                ]
        else:
            # Single value filter
            filtered_df = filtered_df[filtered_df[column] == filter_value]
    
    return filtered_df


def create_sidebar_filters(df: pd.DataFrame, 
                           numeric_cols: List[str] = None,
                           categorical_cols: List[str] = None) -> dict:
    """
    Create comprehensive filter panel in sidebar
    
    Args:
        df: DataFrame to filter
        numeric_cols: List of numeric columns for sliders
        categorical_cols: List of categorical columns for multi-select
        
    Returns:
        Dictionary of filters
    """
    st.sidebar.header("🔍 Filters")
    
    filters = {}
    
    if numeric_cols:
        st.sidebar.subheader("Numeric Filters")
        for col in numeric_cols:
            if col in df.columns:
                filters[col] = create_metric_filter(df, col)
    
    if categorical_cols:
        st.sidebar.subheader("Category Filters")
        for col in categorical_cols:
            if col in df.columns:
                filters[col] = create_multiselect_filter(df, col)
    
    # Reset filters button
    if st.sidebar.button("🔄 Reset Filters"):
        st.rerun()
    
    return filters


def show_filter_summary(original_count: int, filtered_count: int):
    """
    Show summary of filtering results
    
    Args:
        original_count: Original number of rows
        filtered_count: Filtered number of rows
    """
    if filtered_count == original_count:
        st.info(f"📊 Showing all {original_count} items")
    else:
        pct = (filtered_count / original_count * 100) if original_count > 0 else 0
        st.info(f"📊 Showing {filtered_count} of {original_count} items ({pct:.1f}%)")
