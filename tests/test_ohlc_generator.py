#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚡🌟💎 ULTRA NECROZMA - OHLC GENERATOR TESTS 💎🌟⚡

Tests for ohlc_generator.py
"""

import pytest
import sys
from pathlib import Path
import pandas as pd
import numpy as np
import tempfile

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from ohlc_generator import (
    generate_ohlc_bars,
    load_parquet_for_backtest,
    validate_ohlc_data
)


@pytest.fixture
def synthetic_tick_data():
    """Create synthetic tick data for testing"""
    np.random.seed(42)
    
    n_ticks = 10000
    base_time = pd.Timestamp("2025-01-01", tz="UTC")
    timestamps = pd.date_range(base_time, periods=n_ticks, freq="1s")
    
    # Random walk for prices
    base_price = 1.10
    price_changes = np.random.randn(n_ticks) * 0.00001
    mid_prices = base_price + np.cumsum(price_changes)
    
    # Create tick dataframe
    tick_df = pd.DataFrame({
        "timestamp": timestamps,
        "bid": mid_prices - 0.00002,
        "ask": mid_prices + 0.00002,
        "mid_price": mid_prices
    })
    
    return tick_df


def test_generate_ohlc_bars_basic(synthetic_tick_data):
    """Test basic OHLC bar generation"""
    ohlc = generate_ohlc_bars(synthetic_tick_data, interval_minutes=5)
    
    # Check that bars were generated
    assert len(ohlc) > 0
    
    # Check required columns exist
    required_cols = ["timestamp", "open", "high", "low", "close", "mid_price", "volume"]
    for col in required_cols:
        assert col in ohlc.columns, f"Missing column: {col}"
    
    # Check OHLC logic
    assert (ohlc["high"] >= ohlc["low"]).all(), "High should be >= low"
    assert (ohlc["high"] >= ohlc["open"]).all(), "High should be >= open"
    assert (ohlc["high"] >= ohlc["close"]).all(), "High should be >= close"
    assert (ohlc["low"] <= ohlc["open"]).all(), "Low should be <= open"
    assert (ohlc["low"] <= ohlc["close"]).all(), "Low should be <= close"


def test_generate_ohlc_bars_different_intervals(synthetic_tick_data):
    """Test OHLC generation with different intervals"""
    intervals = [1, 5, 15, 60]
    
    prev_bars = None
    for interval in intervals:
        ohlc = generate_ohlc_bars(synthetic_tick_data, interval_minutes=interval)
        
        # Larger intervals should produce fewer bars
        if prev_bars is not None:
            assert len(ohlc) < prev_bars, f"Interval {interval} should have fewer bars than previous"
        
        prev_bars = len(ohlc)
        
        # All should have data
        assert len(ohlc) > 0


def test_generate_ohlc_bars_with_bid_ask_only(synthetic_tick_data):
    """Test OHLC generation when only bid/ask columns exist"""
    # Remove mid_price column
    df = synthetic_tick_data.drop(columns=["mid_price"])
    
    ohlc = generate_ohlc_bars(df, interval_minutes=5)
    
    # Should still generate bars
    assert len(ohlc) > 0
    
    # mid_price should be calculated
    assert "mid_price" in ohlc.columns


def test_generate_ohlc_bars_empty_data():
    """Test that empty data raises error"""
    empty_df = pd.DataFrame()
    
    with pytest.raises(ValueError, match="empty"):
        generate_ohlc_bars(empty_df, interval_minutes=5)


def test_generate_ohlc_bars_missing_timestamp():
    """Test that missing timestamp raises error"""
    df = pd.DataFrame({
        "bid": [1.1, 1.2, 1.3],
        "ask": [1.11, 1.21, 1.31]
    })
    
    with pytest.raises(ValueError, match="timestamp"):
        generate_ohlc_bars(df, interval_minutes=5)


def test_generate_ohlc_bars_missing_price_columns():
    """Test that missing price columns raises error"""
    df = pd.DataFrame({
        "timestamp": pd.date_range("2025-01-01", periods=100, freq="1s", tz="UTC"),
        "volume": [100] * 100
    })
    
    with pytest.raises(ValueError, match="price"):
        generate_ohlc_bars(df, interval_minutes=5)


def test_validate_ohlc_data_valid(synthetic_tick_data):
    """Test validation of valid OHLC data"""
    ohlc = generate_ohlc_bars(synthetic_tick_data, interval_minutes=5)
    
    validation = validate_ohlc_data(ohlc)
    
    assert validation["valid"] == True
    assert len(validation["errors"]) == 0
    assert "n_bars" in validation["stats"]
    assert "price_mean" in validation["stats"]
    assert "price_std" in validation["stats"]


def test_validate_ohlc_data_constant_prices():
    """Test validation detects constant prices"""
    ohlc = pd.DataFrame({
        "timestamp": pd.date_range("2025-01-01", periods=100, freq="5min", tz="UTC"),
        "open": [1.1] * 100,
        "high": [1.1] * 100,
        "low": [1.1] * 100,
        "close": [1.1] * 100
    })
    
    validation = validate_ohlc_data(ohlc)
    
    assert validation["valid"] == False
    assert any("constant" in str(err).lower() for err in validation["errors"])


def test_validate_ohlc_data_invalid_high_low():
    """Test validation detects invalid high/low relationships"""
    ohlc = pd.DataFrame({
        "timestamp": pd.date_range("2025-01-01", periods=100, freq="5min", tz="UTC"),
        "open": [1.1] * 100,
        "high": [1.09] * 100,  # Invalid: high < low
        "low": [1.1] * 100,
        "close": [1.1] * 100
    })
    
    validation = validate_ohlc_data(ohlc)
    
    assert validation["valid"] == False
    assert any("high < low" in str(err).lower() for err in validation["errors"])


def test_validate_ohlc_data_low_bar_count():
    """Test validation warns about low bar count"""
    ohlc = pd.DataFrame({
        "timestamp": pd.date_range("2025-01-01", periods=50, freq="5min", tz="UTC"),
        "open": np.random.randn(50) * 0.001 + 1.1,
        "high": np.random.randn(50) * 0.001 + 1.11,
        "low": np.random.randn(50) * 0.001 + 1.09,
        "close": np.random.randn(50) * 0.001 + 1.1
    })
    
    # Ensure OHLC logic is valid
    ohlc["high"] = ohlc[["open", "high", "low", "close"]].max(axis=1)
    ohlc["low"] = ohlc[["open", "high", "low", "close"]].min(axis=1)
    
    validation = validate_ohlc_data(ohlc)
    
    # Should be valid but have warning
    assert validation["valid"] == True
    assert any("low bar count" in str(warn).lower() for warn in validation["warnings"])


def test_ohlc_has_additional_metrics(synthetic_tick_data):
    """Test that OHLC includes additional calculated metrics"""
    ohlc = generate_ohlc_bars(synthetic_tick_data, interval_minutes=5)
    
    # Check for additional metrics
    assert "body" in ohlc.columns
    assert "body_pips" in ohlc.columns
    assert "range_pips" in ohlc.columns
    
    # Verify calculations
    assert (ohlc["body"] == ohlc["close"] - ohlc["open"]).all()
    
    # Body pips should be body * 10000 (for EURUSD)
    np.testing.assert_array_almost_equal(
        ohlc["body_pips"].values,
        (ohlc["body"] * 10000).values,
        decimal=2
    )


def test_ohlc_timestamp_ordering(synthetic_tick_data):
    """Test that OHLC bars are in chronological order"""
    ohlc = generate_ohlc_bars(synthetic_tick_data, interval_minutes=5)
    
    # Check timestamps are sorted
    timestamps = ohlc["timestamp"].values
    assert (timestamps[1:] >= timestamps[:-1]).all(), "Timestamps should be in ascending order"


def test_ohlc_volume_calculation(synthetic_tick_data):
    """Test that volume (tick count) is calculated correctly"""
    ohlc = generate_ohlc_bars(synthetic_tick_data, interval_minutes=5)
    
    # Volume should be positive
    assert (ohlc["volume"] > 0).all(), "Volume should be positive for all bars"
    
    # Volume should be reasonable (ticks per 5-min bar)
    assert ohlc["volume"].mean() > 0


def test_load_parquet_for_backtest_fallback():
    """Test that load_parquet_for_backtest handles missing file gracefully"""
    # This should fall back to synthetic data or raise clear error
    nonexistent_path = Path("/nonexistent/file.parquet")
    
    # Should either raise FileNotFoundError or similar
    with pytest.raises((FileNotFoundError, ValueError)):
        load_parquet_for_backtest(nonexistent_path, interval_minutes=5)


def test_generate_ohlc_with_spread_data(synthetic_tick_data):
    """Test OHLC generation with spread data"""
    # Add spread_pips column
    df = synthetic_tick_data.copy()
    df["spread_pips"] = (df["ask"] - df["bid"]) * 10000
    
    ohlc = generate_ohlc_bars(df, interval_minutes=5)
    
    # Should include average spread
    assert "spread_avg" in ohlc.columns
    assert (ohlc["spread_avg"] > 0).all()


def test_ohlc_price_range_validation(synthetic_tick_data):
    """Test that OHLC validates price ranges"""
    ohlc = generate_ohlc_bars(synthetic_tick_data, interval_minutes=5)
    
    # Price range should be calculated
    assert "range_pips" in ohlc.columns
    
    # Range should equal (high - low) * 10000
    expected_range = (ohlc["high"] - ohlc["low"]) * 10000
    np.testing.assert_array_almost_equal(
        ohlc["range_pips"].values,
        expected_range.values,
        decimal=2
    )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
