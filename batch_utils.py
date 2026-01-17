#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚡🌟💎 NECROZMA - BATCH UTILITIES 💎🌟⚡

Shared utilities for batch processing
"""

import pandas as pd


# Constants
EPSILON = 1e-10
PIPS_MULTIPLIER = 10000


def prepare_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add required features to dataframe if they don't exist
    
    Args:
        df: DataFrame with price data
    
    Returns:
        DataFrame with added features
    """
    if 'momentum' not in df.columns:
        df['momentum'] = df['pips_change'].rolling(window=100, min_periods=1).sum()
    
    if 'volatility' not in df.columns:
        df['volatility'] = df['pips_change'].rolling(window=100, min_periods=1).std().fillna(0)
    
    if 'trend_strength' not in df.columns:
        df['trend_strength'] = df['momentum'].abs() / (df['volatility'] + EPSILON)
    
    if 'close' not in df.columns:
        df['close'] = df['mid_price']
    
    return df
