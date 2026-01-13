#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚡🌟💎 ULTRA NECROZMA - SMART STORAGE TESTS 💎🌟⚡

Tests for core.storage.smart_storage module
"""

import pytest
import json
from pathlib import Path
import tempfile
import shutil
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.storage.smart_storage import SmartBacktestStorage


@pytest.fixture
def temp_dir():
    """Create temporary directory for tests"""
    temp = tempfile.mkdtemp()
    yield Path(temp)
    shutil.rmtree(temp)


@pytest.fixture
def mock_results():
    """Create mock backtest results"""
    return [
        {
            "strategy_name": f"Strategy_{i}",
            "sharpe_ratio": 3.0 - (i * 0.1),  # Decreasing Sharpe
            "total_return": 0.5 - (i * 0.02),
            "win_rate": 0.6,
            "composite_score": 3.0 - (i * 0.1),
            "trades_detailed": [{"pnl": 10}] * 100,  # Mock trades
            "equity_curve": list(range(100))
        }
        for i in range(100)  # 100 strategies
    ]


def test_smart_storage_initialization(temp_dir):
    """Test storage initialization"""
    storage = SmartBacktestStorage(output_dir=str(temp_dir))
    
    assert storage.metrics_file.parent.exists()  # Directory created
    assert storage.trades_dir.exists()  # Trades directory created


def test_save_universe_results_creates_metrics(temp_dir, mock_results):
    """Test that metrics file is created with all strategies"""
    storage = SmartBacktestStorage(output_dir=str(temp_dir))
    
    storage.save_universe_results("test_universe", mock_results, top_n=10)
    
    # Check metrics file exists
    assert storage.metrics_file.exists()
    
    # Load and verify
    with open(storage.metrics_file) as f:
        data = json.load(f)
    
    assert data["total_strategies"] == 100  # ALL strategies
    assert len(data["strategies"]) == 100


def test_save_universe_results_saves_top_n_trades(temp_dir, mock_results):
    """Test that only top N strategies get detailed trades saved"""
    storage = SmartBacktestStorage(output_dir=str(temp_dir))
    
    storage.save_universe_results("test_universe", mock_results, top_n=10)
    
    # Check that exactly 10 trade files were created
    trade_files = list(storage.trades_dir.glob("*.json"))
    assert len(trade_files) == 10
    
    # Verify they are the top 10
    expected_names = [f"Strategy_{i}.json" for i in range(10)]
    actual_names = sorted([f.name for f in trade_files])
    assert actual_names == sorted(expected_names)


def test_load_strategy_trades(temp_dir, mock_results):
    """Test loading individual strategy trades"""
    storage = SmartBacktestStorage(output_dir=str(temp_dir))
    
    storage.save_universe_results("test_universe", mock_results, top_n=10)
    
    # Load existing strategy
    data = storage.load_strategy_trades("Strategy_0")
    assert data is not None
    assert data["strategy_name"] == "Strategy_0"
    assert "trades" in data
    assert len(data["trades"]) == 100
    
    # Try loading non-existent strategy (rank 50, not in top 10)
    data = storage.load_strategy_trades("Strategy_50")
    assert data is None


def test_get_available_detailed_strategies(temp_dir, mock_results):
    """Test getting list of strategies with trades"""
    storage = SmartBacktestStorage(output_dir=str(temp_dir))
    
    storage.save_universe_results("test_universe", mock_results, top_n=10)
    
    available = storage.get_available_detailed_strategies()
    assert len(available) == 10
    assert "Strategy_0" in available
    assert "Strategy_50" not in available


def test_multiple_universes(temp_dir, mock_results):
    """Test saving multiple universes"""
    storage = SmartBacktestStorage(output_dir=str(temp_dir))
    
    # Save 3 universes
    for i in range(3):
        storage.save_universe_results(f"universe_{i}", mock_results, top_n=5)
    
    # Check metrics file has all strategies
    with open(storage.metrics_file) as f:
        data = json.load(f)
    
    assert data["total_strategies"] == 300  # 100 × 3
    
    # Check trade files (5 per universe × 3 universes, but names might overlap)
    # Since same strategy names used, should have 100 unique files max
    trade_files = list(storage.trades_dir.glob("*.json"))
    assert len(trade_files) <= 100  # Could be less due to overwrites


def test_metrics_only_extraction(temp_dir, mock_results):
    """Test that metrics don't include heavy data"""
    storage = SmartBacktestStorage(output_dir=str(temp_dir))
    
    storage.save_universe_results("test_universe", mock_results, top_n=10)
    
    # Load metrics file
    with open(storage.metrics_file) as f:
        data = json.load(f)
    
    # Check first strategy
    first_strategy = data["strategies"][0]
    metrics = first_strategy["metrics"]
    
    # Metrics should NOT have trades/curves
    assert "trades_detailed" not in metrics
    assert "equity_curve" not in metrics
    assert "drawdown_curve" not in metrics
    
    # Should have standard metrics
    assert "sharpe_ratio" in metrics
    assert "total_return" in metrics


def test_ranking_by_composite_score(temp_dir):
    """Test that strategies are ranked correctly"""
    results = [
        {"strategy_name": "Low", "composite_score": 1.0, "sharpe_ratio": 2.0, "trades_detailed": []},
        {"strategy_name": "High", "composite_score": 3.0, "sharpe_ratio": 1.0, "trades_detailed": []},
        {"strategy_name": "Med", "composite_score": 2.0, "sharpe_ratio": 1.5, "trades_detailed": []}
    ]
    
    storage = SmartBacktestStorage(output_dir=str(temp_dir))
    storage.save_universe_results("test", results, top_n=2)
    
    # Load trade files
    trade_files = sorted(storage.trades_dir.glob("*.json"))
    assert len(trade_files) == 2
    
    # Check that High and Med were saved (top 2 by composite_score)
    names = [f.stem for f in trade_files]
    assert "High" in names
    assert "Med" in names
    assert "Low" not in names


def test_fallback_to_sharpe_ratio(temp_dir):
    """Test ranking falls back to sharpe_ratio if composite_score not present"""
    results = [
        {"strategy_name": "Low", "sharpe_ratio": 1.0, "trades_detailed": []},
        {"strategy_name": "High", "sharpe_ratio": 3.0, "trades_detailed": []},
        {"strategy_name": "Med", "sharpe_ratio": 2.0, "trades_detailed": []}
    ]
    
    storage = SmartBacktestStorage(output_dir=str(temp_dir))
    storage.save_universe_results("test", results, top_n=2)
    
    # Check that High and Med were saved (top 2 by sharpe_ratio)
    names = [f.stem for f in storage.trades_dir.glob("*.json")]
    assert "High" in names
    assert "Med" in names
    assert "Low" not in names


def test_equity_curve_serialization(temp_dir):
    """Test that equity curves are properly serialized"""
    try:
        import pandas as pd
        has_pandas = True
    except ImportError:
        has_pandas = False
    
    if has_pandas:
        results = [
            {
                "strategy_name": "TestStrat",
                "sharpe_ratio": 2.0,
                "trades_detailed": [],
                "equity_curve": pd.Series([100, 105, 110, 115])  # Pandas Series
            }
        ]
    else:
        # Test with plain list if pandas not available
        results = [
            {
                "strategy_name": "TestStrat",
                "sharpe_ratio": 2.0,
                "trades_detailed": [],
                "equity_curve": [100, 105, 110, 115]  # Plain list
            }
        ]
    
    storage = SmartBacktestStorage(output_dir=str(temp_dir))
    storage.save_universe_results("test", results, top_n=1)
    
    # Load and verify equity curve was serialized
    data = storage.load_strategy_trades("TestStrat")
    assert data is not None
    assert "equity_curve" in data
    assert isinstance(data["equity_curve"], list)
    assert len(data["equity_curve"]) == 4
    assert data["equity_curve"][0] == 100


def test_upsert_strategy_updates_existing(temp_dir, mock_results):
    """Test that re-saving a strategy updates rather than duplicates"""
    storage = SmartBacktestStorage(output_dir=str(temp_dir))
    
    # Save first time
    storage.save_universe_results("test_universe", mock_results[:10], top_n=5)
    
    # Update Strategy_0 with different metrics
    updated_results = mock_results[:10].copy()
    updated_results[0]["sharpe_ratio"] = 10.0
    updated_results[0]["composite_score"] = 10.0
    
    # Save again
    storage.save_universe_results("test_universe", updated_results, top_n=5)
    
    # Check that there's only one entry for Strategy_0 in test_universe
    with open(storage.metrics_file) as f:
        data = json.load(f)
    
    strategy_0_count = sum(
        1 for s in data["strategies"] 
        if s["strategy_name"] == "Strategy_0" and s["universe"] == "test_universe"
    )
    assert strategy_0_count == 1
    
    # Verify the sharpe was updated
    strategy_0_data = next(
        s for s in data["strategies"] 
        if s["strategy_name"] == "Strategy_0" and s["universe"] == "test_universe"
    )
    assert strategy_0_data["metrics"]["sharpe_ratio"] == 10.0


def test_empty_results(temp_dir):
    """Test handling of empty results list"""
    storage = SmartBacktestStorage(output_dir=str(temp_dir))
    
    storage.save_universe_results("empty_universe", [], top_n=10)
    
    # Should create metrics file with 0 strategies
    with open(storage.metrics_file) as f:
        data = json.load(f)
    
    assert data["total_strategies"] == 0
    
    # No trade files should be created
    trade_files = list(storage.trades_dir.glob("*.json"))
    assert len(trade_files) == 0


def test_load_nonexistent_strategy(temp_dir):
    """Test loading a strategy that doesn't exist"""
    storage = SmartBacktestStorage(output_dir=str(temp_dir))
    
    data = storage.load_strategy_trades("NonExistent")
    assert data is None


def test_metadata_in_saved_trades(temp_dir, mock_results):
    """Test that saved trade files contain all expected metadata"""
    storage = SmartBacktestStorage(output_dir=str(temp_dir))
    
    storage.save_universe_results("test_universe", mock_results, top_n=5)
    
    # Load a trade file
    data = storage.load_strategy_trades("Strategy_0")
    
    # Verify all expected fields are present
    assert "strategy_name" in data
    assert "universe" in data
    assert "rank" in data
    assert "metrics" in data
    assert "trades" in data
    assert "equity_curve" in data
    
    # Verify values
    assert data["strategy_name"] == "Strategy_0"
    assert data["universe"] == "test_universe"
    assert data["rank"] == 1  # Best strategy


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
