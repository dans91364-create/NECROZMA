#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚡🌟💎 ULTRA NECROZMA - FEATURE EXTRACTION TESTS 💎🌟⚡

Tests for feature_extractor.py
"""

import pytest
import sys
from pathlib import Path
import pandas as pd
import numpy as np

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from feature_extractor import (
    extract_features_from_universe,
    combine_ohlc_with_features,
    validate_dataframe_for_backtesting,
    _aggregate_features,
)


@pytest.fixture
def mock_universe_data():
    """Create mock universe data for testing"""
    return {
        "name": "test_universe",
        "config": {"interval": 5, "lookback": 5},
        "results": {
            "Pequeno": {
                "up": {
                    "patterns": {
                        "pattern_1": {
                            "count": 10,
                            "features": [
                                {
                                    "ohlc_body_mean": -1.02,
                                    "ohlc_range_mean": 2.46,
                                    "ohlc_trend_efficiency": 0.76,
                                    "ohlc_volume_mean": 81.8,
                                    "ohlc_volume_trend": 1.05,
                                    "ohlc_spread_mean": 0.5,
                                    "ohlc_up_ratio": 0.6,
                                    "ohlc_down_ratio": 0.4,
                                },
                                {
                                    "ohlc_body_mean": -0.98,
                                    "ohlc_range_mean": 2.50,
                                    "ohlc_trend_efficiency": 0.78,
                                    "ohlc_volume_mean": 85.2,
                                    "ohlc_volume_trend": 1.02,
                                    "ohlc_spread_mean": 0.48,
                                    "ohlc_up_ratio": 0.65,
                                    "ohlc_down_ratio": 0.35,
                                }
                            ]
                        }
                    }
                },
                "down": {
                    "patterns": {}
                }
            },
            "Médio": {
                "up": {
                    "patterns": {}
                },
                "down": {
                    "patterns": {}
                }
            }
        }
    }


@pytest.fixture
def mock_ohlc_data():
    """Create mock OHLC data for testing"""
    return pd.DataFrame({
        "timestamp": pd.date_range("2025-01-01", periods=10, freq="5min"),
        "open": [1.10 + i * 0.001 for i in range(10)],
        "high": [1.101 + i * 0.001 for i in range(10)],
        "low": [1.099 + i * 0.001 for i in range(10)],
        "close": [1.100 + i * 0.001 for i in range(10)],
        "volume": [100 + i * 5 for i in range(10)],
    })


def test_extract_features_from_universe(mock_universe_data):
    """Test feature extraction from universe data"""
    features_df = extract_features_from_universe(mock_universe_data)
    
    # Should return DataFrame with features
    assert isinstance(features_df, pd.DataFrame)
    assert not features_df.empty
    assert len(features_df) == 1  # Single row with aggregated features
    
    # Should have derived features
    assert "momentum" in features_df.columns
    assert "trend" in features_df.columns
    assert "volatility" in features_df.columns
    
    # Should have base features
    assert "body_mean" in features_df.columns
    assert "range_mean" in features_df.columns
    assert "trend_efficiency" in features_df.columns


def test_extract_features_empty_universe():
    """Test feature extraction with empty universe data"""
    empty_universe = {
        "name": "empty",
        "config": {},
        "results": {}
    }
    
    features_df = extract_features_from_universe(empty_universe)
    
    # Should return empty DataFrame
    assert isinstance(features_df, pd.DataFrame)
    assert features_df.empty


def test_aggregate_features():
    """Test feature aggregation"""
    feature_list = [
        {"ohlc_body_mean": 1.0, "ohlc_range_mean": 2.0},
        {"ohlc_body_mean": 2.0, "ohlc_range_mean": 3.0},
        {"ohlc_body_mean": 3.0, "ohlc_range_mean": 4.0},
    ]
    
    aggregated = _aggregate_features(feature_list)
    
    # Should calculate mean
    assert aggregated["ohlc_body_mean"] == 2.0  # (1+2+3)/3
    assert aggregated["ohlc_range_mean"] == 3.0  # (2+3+4)/3
    
    # Should have derived features
    assert "momentum" in aggregated
    assert "trend" in aggregated
    assert "volatility" in aggregated


def test_aggregate_features_empty():
    """Test feature aggregation with empty list"""
    aggregated = _aggregate_features([])
    assert aggregated == {}


def test_combine_ohlc_with_features(mock_ohlc_data, mock_universe_data):
    """Test combining OHLC with features"""
    # Extract features
    features_df = extract_features_from_universe(mock_universe_data)
    
    # Combine
    combined = combine_ohlc_with_features(mock_ohlc_data, features_df)
    
    # Should have all OHLC columns
    assert "open" in combined.columns
    assert "high" in combined.columns
    assert "low" in combined.columns
    assert "close" in combined.columns
    assert "volume" in combined.columns
    
    # Should have feature columns
    assert "momentum" in combined.columns
    assert "trend" in combined.columns
    assert "volatility" in combined.columns
    
    # Should have same number of rows as OHLC
    assert len(combined) == len(mock_ohlc_data)
    
    # Features should be broadcast to all rows
    assert combined["momentum"].iloc[0] == combined["momentum"].iloc[-1]


def test_combine_ohlc_with_empty_features(mock_ohlc_data):
    """Test combining OHLC with empty features"""
    empty_features = pd.DataFrame()
    
    combined = combine_ohlc_with_features(mock_ohlc_data, empty_features)
    
    # Should return original OHLC
    assert len(combined) == len(mock_ohlc_data)
    assert "open" in combined.columns
    assert "close" in combined.columns


def test_validate_dataframe_valid(mock_ohlc_data, mock_universe_data):
    """Test validation with valid DataFrame"""
    features_df = extract_features_from_universe(mock_universe_data)
    combined = combine_ohlc_with_features(mock_ohlc_data, features_df)
    
    validation = validate_dataframe_for_backtesting(combined)
    
    assert validation["valid"] == True
    assert len(validation["missing_required"]) == 0
    assert len(validation["missing_recommended"]) == 0


def test_validate_dataframe_missing_required():
    """Test validation with missing required columns"""
    df = pd.DataFrame({
        "open": [1.0, 2.0],
        "close": [1.1, 2.1],
        # Missing: high, low, volume
    })
    
    validation = validate_dataframe_for_backtesting(df)
    
    assert validation["valid"] == False
    assert "high" in validation["missing_required"]
    assert "low" in validation["missing_required"]
    assert "volume" in validation["missing_required"]


def test_validate_dataframe_missing_recommended():
    """Test validation with missing recommended columns"""
    df = pd.DataFrame({
        "open": [1.0, 2.0],
        "high": [1.1, 2.1],
        "low": [0.9, 1.9],
        "close": [1.0, 2.0],
        "volume": [100, 200],
        # Missing: momentum, trend, volatility
    })
    
    validation = validate_dataframe_for_backtesting(df)
    
    assert validation["valid"] == True  # Valid for basic backtesting
    assert "momentum" in validation["missing_recommended"]
    assert "trend" in validation["missing_recommended"]
    assert "volatility" in validation["missing_recommended"]


def test_validate_dataframe_with_nans():
    """Test validation with NaN values"""
    df = pd.DataFrame({
        "open": [1.0, np.nan, 3.0],
        "high": [1.1, 2.1, 3.1],
        "low": [0.9, 1.9, 2.9],
        "close": [1.0, 2.0, 3.0],
        "volume": [100, 200, 300],
    })
    
    validation = validate_dataframe_for_backtesting(df)
    
    assert validation["valid"] == True  # Still valid, but with warnings
    assert any("NaN" in w for w in validation["warnings"])


def test_derived_features_calculation(mock_universe_data):
    """Test that derived features are calculated correctly"""
    features_df = extract_features_from_universe(mock_universe_data)
    
    # Get values
    trend_efficiency = features_df["trend_efficiency"].iloc[0]
    range_mean = features_df["range_mean"].iloc[0]
    momentum = features_df["momentum"].iloc[0]
    
    # Momentum should be trend_efficiency * range_mean
    expected_momentum = trend_efficiency * range_mean
    assert abs(momentum - expected_momentum) < 1e-6
    
    # Trend should be up_ratio - down_ratio
    up_ratio = features_df["up_ratio"].iloc[0]
    down_ratio = features_df["down_ratio"].iloc[0]
    trend = features_df["trend"].iloc[0]
    expected_trend = up_ratio - down_ratio
    assert abs(trend - expected_trend) < 1e-6
    
    # Volatility should be range_mean / body_mean (with div by zero protection)
    body_mean = features_df["body_mean"].iloc[0]
    volatility = features_df["volatility"].iloc[0]
    if abs(body_mean) > 1e-10:
        expected_volatility = range_mean / abs(body_mean)
        assert abs(volatility - expected_volatility) < 1e-6


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
