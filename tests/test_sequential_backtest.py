#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚡🌟💎 ULTRA NECROZMA - SEQUENTIAL BACKTEST TESTS 💎🌟⚡

Tests for run_sequential_backtest.py
"""

import pytest
import json
import sys
from pathlib import Path
import tempfile
import shutil

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from run_sequential_backtest import (
    parse_universe_selection,
    load_universe_results,
    get_system_stats,
)


def test_parse_universe_selection_single():
    """Test parsing single universe ID"""
    result = parse_universe_selection("5")
    assert result == [5]


def test_parse_universe_selection_multiple():
    """Test parsing multiple universe IDs"""
    result = parse_universe_selection("1,5,10")
    assert result == [1, 5, 10]


def test_parse_universe_selection_range():
    """Test parsing universe range"""
    result = parse_universe_selection("10-15")
    assert result == [10, 11, 12, 13, 14, 15]


def test_parse_universe_selection_mixed():
    """Test parsing mixed selection"""
    result = parse_universe_selection("1,5,10-13,20")
    assert result == [1, 5, 10, 11, 12, 13, 20]


def test_parse_universe_selection_duplicates():
    """Test that duplicates are removed"""
    result = parse_universe_selection("1,5,1,5")
    assert result == [1, 5]


def test_load_universe_results_empty_dir():
    """Test loading from empty directory"""
    with tempfile.TemporaryDirectory() as tmpdir:
        results = load_universe_results(Path(tmpdir))
        assert len(results) == 0


def test_load_universe_results_with_files():
    """Test loading from directory with universe files"""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)
        
        # Create mock universe files
        universe_data_1 = {
            "universe_name": "universe_001_5min_5lb",
            "interval": 5,
            "lookback": 5,
            "total_patterns": 100,
            "features": {"momentum": 0.5}
        }
        
        universe_data_2 = {
            "universe_name": "universe_002_5min_10lb",
            "interval": 5,
            "lookback": 10,
            "total_patterns": 200,
            "features": {"volatility": 0.3}
        }
        
        # Write files
        with open(tmpdir_path / "universe_001_5min_5lb.json", 'w') as f:
            json.dump(universe_data_1, f)
        
        with open(tmpdir_path / "universe_002_5min_10lb.json", 'w') as f:
            json.dump(universe_data_2, f)
        
        # Load results
        results = load_universe_results(tmpdir_path)
        
        assert len(results) == 2
        assert results[0]["universe_name"] == "universe_001_5min_5lb"
        assert results[1]["universe_name"] == "universe_002_5min_10lb"


def test_load_universe_results_with_filter():
    """Test loading with specific universe filter"""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)
        
        # Create mock universe files
        for i in range(1, 4):
            universe_data = {
                "universe_name": f"universe_{i:03d}_5min_{i*5}lb",
                "interval": 5,
                "lookback": i * 5,
                "total_patterns": i * 100,
            }
            
            with open(tmpdir_path / f"universe_{i:03d}_5min_{i*5}lb.json", 'w') as f:
                json.dump(universe_data, f)
        
        # Load only universe 1 and 3
        results = load_universe_results(tmpdir_path, universe_ids=[1, 3])
        
        assert len(results) == 2
        assert any("001" in r["universe_name"] for r in results)
        assert any("003" in r["universe_name"] for r in results)
        assert not any("002" in r["universe_name"] for r in results)


def test_get_system_stats():
    """Test system stats retrieval"""
    stats = get_system_stats()
    
    # Should return dict with cpu_percent and ram_gb
    assert "cpu_percent" in stats
    assert "ram_gb" in stats
    
    # Values should be non-negative
    assert stats["cpu_percent"] >= 0
    assert stats["ram_gb"] >= 0


def test_parse_universe_selection_invalid():
    """Test parsing with invalid input"""
    # Should skip invalid entries but still parse valid ones
    result = parse_universe_selection("1,invalid,5")
    assert 1 in result
    assert 5 in result


def test_load_universe_results_invalid_json():
    """Test loading directory with invalid JSON"""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)
        
        # Create valid file
        with open(tmpdir_path / "universe_001_5min_5lb.json", 'w') as f:
            json.dump({"universe_name": "test", "interval": 5}, f)
        
        # Create invalid JSON file
        with open(tmpdir_path / "universe_002_5min_10lb.json", 'w') as f:
            f.write("{ invalid json }")
        
        # Should load only the valid file
        results = load_universe_results(tmpdir_path)
        assert len(results) == 1


def test_load_universe_results_nonexistent_dir():
    """Test loading from non-existent directory"""
    results = load_universe_results(Path("/nonexistent/directory"))
    assert len(results) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
