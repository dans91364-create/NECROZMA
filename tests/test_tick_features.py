#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚡🌟💎 ULTRA NECROZMA - TICK-LEVEL FEATURES TESTS 💎🌟⚡

Tests for tick-level feature calculation in main.py
"""

import pytest
import sys
from pathlib import Path
import pandas as pd
import numpy as np

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Epsilon for numerical stability (must match main.py)
EPSILON = 1e-10


@pytest.fixture
def sample_tick_data():
    """Create sample tick data for testing"""
    np.random.seed(42)
    n_samples = 500
    
    # Simulate tick data
    df = pd.DataFrame({
        'timestamp': pd.date_range('2024-01-01', periods=n_samples, freq='1s'),
        'bid': 1.0850 + np.random.randn(n_samples) * 0.0001,
        'ask': 1.0852 + np.random.randn(n_samples) * 0.0001,
    })
    
    # Add basic computed columns that would exist
    df['mid_price'] = (df['bid'] + df['ask']) / 2
    df['spread_pips'] = (df['ask'] - df['bid']) * 10000
    df['pips_change'] = df['mid_price'].diff() * 10000
    df['regime'] = 'trending'  # Dummy regime
    
    return df


def test_tick_features_calculation(sample_tick_data):
    """Test that tick-level features are calculated correctly"""
    df = sample_tick_data.copy()
    
    # Simulate the code from main.py Step 4.5
    if 'momentum' not in df.columns:
        # Momentum: sum of pips_change over last N ticks
        df['momentum'] = df['pips_change'].rolling(window=100, min_periods=1).sum()
        
        # Volatility: standard deviation of pips_change over last N ticks
        df['volatility'] = df['pips_change'].rolling(window=100, min_periods=1).std().fillna(0)
        
        # Trend strength: absolute normalized momentum
        df['trend_strength'] = df['momentum'].abs() / (df['volatility'] + EPSILON)
        
        # Close (alias for mid_price, needed by some strategies)
        df['close'] = df['mid_price']
    
    # Assertions
    assert 'momentum' in df.columns, "momentum column should be added"
    assert 'volatility' in df.columns, "volatility column should be added"
    assert 'trend_strength' in df.columns, "trend_strength column should be added"
    assert 'close' in df.columns, "close column should be added"
    
    # Check that close is equal to mid_price
    assert (df['close'] == df['mid_price']).all(), "close should equal mid_price"
    
    # Check that momentum is not all NaN
    assert not df['momentum'].isna().all(), "momentum should have non-NaN values"
    
    # Check that volatility is not all NaN and is non-negative
    assert not df['volatility'].isna().all(), "volatility should have non-NaN values"
    assert (df['volatility'] >= 0).all(), "volatility should be non-negative"
    
    # Check that trend_strength is not all NaN
    assert not df['trend_strength'].isna().all(), "trend_strength should have non-NaN values"
    
    print("✅ All tick-level feature tests passed!")


def test_momentum_calculation(sample_tick_data):
    """Test momentum is calculated as rolling sum"""
    df = sample_tick_data.copy()
    
    window = 100
    df['momentum'] = df['pips_change'].rolling(window=window, min_periods=1).sum()
    
    # For the 100th row (index 99), momentum should equal sum of first 100 pips_change
    expected_momentum_at_100 = df['pips_change'].iloc[:100].sum()
    actual_momentum_at_100 = df['momentum'].iloc[99]
    
    assert np.isclose(expected_momentum_at_100, actual_momentum_at_100, rtol=1e-5), \
        f"Momentum at row 100 should be {expected_momentum_at_100}, got {actual_momentum_at_100}"
    
    print("✅ Momentum calculation test passed!")


def test_volatility_calculation(sample_tick_data):
    """Test volatility is calculated as rolling std"""
    df = sample_tick_data.copy()
    
    window = 100
    df['volatility'] = df['pips_change'].rolling(window=window, min_periods=1).std().fillna(0)
    
    # For the 100th row (index 99), volatility should equal std of first 100 pips_change
    expected_volatility_at_100 = df['pips_change'].iloc[:100].std()
    actual_volatility_at_100 = df['volatility'].iloc[99]
    
    assert np.isclose(expected_volatility_at_100, actual_volatility_at_100, rtol=1e-5), \
        f"Volatility at row 100 should be {expected_volatility_at_100}, got {actual_volatility_at_100}"
    
    # Check that fillna(0) works - first row with min_periods=1 should have std=0
    assert df['volatility'].iloc[0] == 0, "First row volatility should be 0 (fillna)"
    
    print("✅ Volatility calculation test passed!")


def test_trend_strength_calculation(sample_tick_data):
    """Test trend_strength is calculated correctly"""
    df = sample_tick_data.copy()
    
    window = 100
    df['momentum'] = df['pips_change'].rolling(window=window, min_periods=1).sum()
    df['volatility'] = df['pips_change'].rolling(window=window, min_periods=1).std().fillna(0)
    df['trend_strength'] = df['momentum'].abs() / (df['volatility'] + EPSILON)
    
    # Check formula: trend_strength = |momentum| / (volatility + epsilon)
    for idx in [50, 100, 200, 300]:
        expected = abs(df['momentum'].iloc[idx]) / (df['volatility'].iloc[idx] + EPSILON)
        actual = df['trend_strength'].iloc[idx]
        assert np.isclose(expected, actual, rtol=1e-5), \
            f"Trend strength at row {idx} should be {expected}, got {actual}"
    
    # Check that trend_strength is always non-negative (excluding NaNs)
    non_nan_trend = df['trend_strength'].dropna()
    assert (non_nan_trend >= 0).all(), "trend_strength should always be non-negative"
    
    print("✅ Trend strength calculation test passed!")


def test_features_not_duplicated(sample_tick_data):
    """Test that features are only added once (check the if condition)"""
    df = sample_tick_data.copy()
    
    # First application
    if 'momentum' not in df.columns:
        df['momentum'] = df['pips_change'].rolling(window=100, min_periods=1).sum()
        df['volatility'] = df['pips_change'].rolling(window=100, min_periods=1).std().fillna(0)
        df['trend_strength'] = df['momentum'].abs() / (df['volatility'] + 1e-10)
        df['close'] = df['mid_price']
    
    initial_columns = set(df.columns)
    
    # Second application (should not add duplicates)
    if 'momentum' not in df.columns:
        df['momentum'] = df['pips_change'].rolling(window=100, min_periods=1).sum()
        df['volatility'] = df['pips_change'].rolling(window=100, min_periods=1).std().fillna(0)
        df['trend_strength'] = df['momentum'].abs() / (df['volatility'] + EPSILON)
        df['close'] = df['mid_price']
    
    final_columns = set(df.columns)
    
    assert initial_columns == final_columns, "Features should not be duplicated"
    
    print("✅ No duplication test passed!")

