#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚡🌟💎 ULTRA NECROZMA - Universe File Creation Tests 💎🌟⚡

Test that universe files are created correctly with all required fields
"""

import pytest
import json
import tempfile
import shutil
from pathlib import Path
import numpy as np
import pandas as pd

from analyzer import UltraNecrozmaAnalyzer, process_universe
from config import get_output_dirs


@pytest.fixture
def sample_tick_data():
    """Generate sample tick data for testing"""
    np.random.seed(42)
    
    n_ticks = 10000
    timestamps = pd.date_range("2025-01-01", periods=n_ticks, freq="1s")
    base_price = 1.10
    noise = np.random.randn(n_ticks) * 0.0001
    cumsum = np.cumsum(noise)
    
    df = pd.DataFrame({
        'timestamp': timestamps,
        'bid': base_price + cumsum - 0.00005,
        'ask': base_price + cumsum + 0.00005,
        'mid_price': base_price + cumsum,
        'spread_pips': 1.0,
        'pips_change': np.concatenate([[0], np.diff(cumsum) * 10000])
    })
    
    return df


@pytest.fixture
def temp_output_dir():
    """Create temporary output directory"""
    temp_dir = Path(tempfile.mkdtemp())
    yield temp_dir
    # Cleanup
    if temp_dir.exists():
        shutil.rmtree(temp_dir)


def test_process_universe_includes_ohlc_data(sample_tick_data):
    """Test that process_universe includes OHLC data in results"""
    result = process_universe(
        df=sample_tick_data,
        interval=5,
        lookback=10,
        universe_name="test_5m_10lb"
    )
    
    assert result is not None, "process_universe returned None"
    
    # Check required fields
    assert "name" in result
    assert "config" in result
    assert "total_patterns" in result
    assert "ohlc_data" in result, "Missing ohlc_data field"
    assert "metadata" in result, "Missing metadata field"
    
    # Check OHLC data structure
    assert isinstance(result["ohlc_data"], list), "ohlc_data should be a list"
    assert len(result["ohlc_data"]) > 0, "ohlc_data should not be empty"
    
    # Check OHLC data content
    first_candle = result["ohlc_data"][0]
    required_ohlc_fields = ["open", "high", "low", "close", "timestamp"]
    for field in required_ohlc_fields:
        assert field in first_candle, f"Missing {field} in OHLC data"
    
    # Check metadata
    assert "total_candles" in result["metadata"]
    assert "interval_minutes" in result["metadata"]
    assert "lookback_periods" in result["metadata"]
    assert result["metadata"]["interval_minutes"] == 5
    assert result["metadata"]["lookback_periods"] == 10


def test_analyzer_save_results_creates_files(sample_tick_data, temp_output_dir):
    """Test that analyzer.save_results() creates universe files"""
    # Initialize analyzer with custom output dir
    analyzer = UltraNecrozmaAnalyzer(sample_tick_data, output_dir=temp_output_dir)
    
    # Process a single universe (sequential mode)
    analyzer._run_sequential()
    
    # Save results
    save_stats = analyzer.save_results()
    
    # Check that files were created
    assert save_stats["universes_saved"] > 0, "No universes were saved"
    
    # Check that universe files exist
    universes_dir = temp_output_dir / "universes"
    assert universes_dir.exists(), "Universes directory not created"
    
    universe_files = list(universes_dir.glob("universe_*.json"))
    assert len(universe_files) > 0, "No universe JSON files created"
    
    # Verify file structure
    first_file = universe_files[0]
    with open(first_file, 'r') as f:
        universe_data = json.load(f)
    
    # Check required fields in saved file
    required_fields = ["name", "interval", "lookback", "total_patterns", 
                      "ohlc_data", "metadata", "_filepath"]
    for field in required_fields:
        assert field in universe_data, f"Missing {field} in saved universe file"
    
    # Check OHLC data in saved file
    assert isinstance(universe_data["ohlc_data"], list)
    assert len(universe_data["ohlc_data"]) > 0, "Saved file has empty ohlc_data"
    
    # Check that features are included in patterns
    results = universe_data.get("results", {})
    found_features = False
    for level_name, level_data in results.items():
        if isinstance(level_data, dict):
            for direction, direction_data in level_data.items():
                if isinstance(direction_data, dict):
                    top_patterns = direction_data.get("top_patterns", [])
                    for pattern in top_patterns:
                        if "features" in pattern and len(pattern["features"]) > 0:
                            found_features = True
                            break
                if found_features:
                    break
        if found_features:
            break
    
    assert found_features, "No features found in top_patterns"
    
    print(f"\n✅ Test passed: Universe file created at {first_file}")
    print(f"   File size: {first_file.stat().st_size / 1024:.2f} KB")
    print(f"   OHLC candles: {len(universe_data['ohlc_data'])}")
    print(f"   Total patterns: {universe_data['total_patterns']}")


def test_universe_file_format_for_backtesting(sample_tick_data, temp_output_dir):
    """Test that saved universe files have the format expected by backtesting"""
    # Initialize and run analyzer
    analyzer = UltraNecrozmaAnalyzer(sample_tick_data, output_dir=temp_output_dir)
    analyzer._run_sequential()
    analyzer.save_results()
    
    # Load a universe file
    universes_dir = temp_output_dir / "universes"
    universe_files = list(universes_dir.glob("universe_*.json"))
    assert len(universe_files) > 0
    
    with open(universe_files[0], 'r') as f:
        universe_data = json.load(f)
    
    # Verify structure matches backtest expectations
    # (from feature_extractor.py extract_features_from_universe)
    assert "results" in universe_data
    
    results = universe_data["results"]
    if isinstance(results, dict) and len(results) > 0:
        # Check structure: results -> level -> direction -> patterns
        for level_name, level_data in results.items():
            if isinstance(level_data, dict):
                for direction, direction_data in level_data.items():
                    assert "patterns" in direction_data or "top_patterns" in direction_data, \
                        f"Missing patterns in {level_name}/{direction}"
    
    # Verify OHLC data can be used for backtesting
    # (from run_sequential_backtest.py load_ohlc_for_universe)
    assert "interval" in universe_data or ("metadata" in universe_data and "interval_minutes" in universe_data["metadata"])
    assert "lookback" in universe_data or ("metadata" in universe_data and "lookback_periods" in universe_data["metadata"])
    assert "ohlc_data" in universe_data
    
    # Check OHLC fields
    if len(universe_data["ohlc_data"]) > 0:
        candle = universe_data["ohlc_data"][0]
        required_price_fields = ["open", "high", "low", "close"]
        for field in required_price_fields:
            assert field in candle, f"Missing {field} in OHLC candle"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
