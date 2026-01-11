#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚡🌟💎 ULTRA NECROZMA - LOOKBACK PATTERN GENERATION TESTS 💎🌟⚡

Tests to verify that all lookback periods generate patterns.
This test was added to prevent regression of the bug where lookback < 30
returned 0 patterns due to MIN_SAMPLES being set to 30.
"""

import pytest
import numpy as np
import pandas as pd
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import MIN_SAMPLES, LOOKBACKS
from analyzer import process_universe


@pytest.fixture
def synthetic_tick_data():
    """Generate synthetic tick data for testing"""
    np.random.seed(42)
    
    n_ticks = 100000  # 100k ticks
    timestamps = pd.date_range("2025-01-01", periods=n_ticks, freq="1s")
    
    # Create price movements with patterns
    base_price = 1.10
    trend = np.linspace(0, 0.005, n_ticks)
    noise = np.random.randn(n_ticks) * 0.0001
    cycles = 0.001 * np.sin(np.linspace(0, 30 * np.pi, n_ticks))
    
    prices = base_price + trend + noise + cycles
    
    df = pd.DataFrame({
        "timestamp": timestamps,
        "bid": prices - 0.00005,
        "ask": prices + 0.00005,
        "mid_price": prices,
        "spread_pips": 1.0,
        "pips_change": np.concatenate([[0], np.diff(prices) * 10000])
    })
    
    return df


def test_min_samples_allows_all_lookbacks():
    """Test that MIN_SAMPLES is low enough to allow all configured lookbacks"""
    # MIN_SAMPLES should be <= minimum lookback
    min_lookback = min(LOOKBACKS)
    assert MIN_SAMPLES <= min_lookback, (
        f"MIN_SAMPLES ({MIN_SAMPLES}) should be <= minimum lookback ({min_lookback}) "
        f"to allow all lookback periods to work"
    )


def test_lookback_5_generates_patterns(synthetic_tick_data):
    """Test that lookback=5 generates patterns (previously failed)"""
    result = process_universe(synthetic_tick_data, interval=5, lookback=5, 
                             universe_name="test_5m_5lb")
    
    assert result is not None, "process_universe should return a result"
    assert result["total_patterns"] > 0, (
        "Lookback=5 should generate patterns (bug: was returning 0)"
    )


def test_lookback_10_generates_patterns(synthetic_tick_data):
    """Test that lookback=10 generates patterns (previously failed)"""
    result = process_universe(synthetic_tick_data, interval=5, lookback=10,
                             universe_name="test_5m_10lb")
    
    assert result is not None, "process_universe should return a result"
    assert result["total_patterns"] > 0, (
        "Lookback=10 should generate patterns (bug: was returning 0)"
    )


def test_lookback_15_generates_patterns(synthetic_tick_data):
    """Test that lookback=15 generates patterns (previously failed)"""
    result = process_universe(synthetic_tick_data, interval=5, lookback=15,
                             universe_name="test_5m_15lb")
    
    assert result is not None, "process_universe should return a result"
    assert result["total_patterns"] > 0, (
        "Lookback=15 should generate patterns (bug: was returning 0)"
    )


def test_lookback_20_generates_patterns(synthetic_tick_data):
    """Test that lookback=20 generates patterns (previously failed)"""
    result = process_universe(synthetic_tick_data, interval=5, lookback=20,
                             universe_name="test_5m_20lb")
    
    assert result is not None, "process_universe should return a result"
    assert result["total_patterns"] > 0, (
        "Lookback=20 should generate patterns (bug: was returning 0)"
    )


def test_lookback_30_generates_patterns(synthetic_tick_data):
    """Test that lookback=30 generates patterns (this always worked)"""
    result = process_universe(synthetic_tick_data, interval=5, lookback=30,
                             universe_name="test_5m_30lb")
    
    assert result is not None, "process_universe should return a result"
    assert result["total_patterns"] > 0, "Lookback=30 should generate patterns"


def test_all_configured_lookbacks_work(synthetic_tick_data):
    """Test that all configured lookback periods generate patterns"""
    test_interval = 5
    
    for lookback in LOOKBACKS:
        result = process_universe(
            synthetic_tick_data, 
            interval=test_interval, 
            lookback=lookback,
            universe_name=f"test_{test_interval}m_{lookback}lb"
        )
        
        assert result is not None, (
            f"process_universe should return a result for lookback={lookback}"
        )
        assert result["total_patterns"] > 0, (
            f"Lookback={lookback} should generate patterns. "
            f"If this fails, MIN_SAMPLES ({MIN_SAMPLES}) may be too high."
        )


def test_pattern_counts_reasonable(synthetic_tick_data):
    """Test that pattern counts are in a reasonable range"""
    test_interval = 5
    results = {}
    
    for lookback in LOOKBACKS:
        result = process_universe(
            synthetic_tick_data,
            interval=test_interval,
            lookback=lookback,
            universe_name=f"test_{test_interval}m_{lookback}lb"
        )
        results[lookback] = result["total_patterns"]
    
    # All should generate patterns
    for lookback, count in results.items():
        assert count > 0, f"Lookback {lookback} generated 0 patterns"
    
    # Pattern counts should be in a reasonable range (not all identical)
    # With different lookback periods, we expect slightly different counts
    unique_counts = len(set(results.values()))
    assert unique_counts > 1, (
        "Pattern counts should vary slightly across lookbacks, "
        f"but got identical counts: {results}"
    )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
