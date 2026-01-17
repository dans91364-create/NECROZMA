#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚡🌟💎 NECROZMA - BACKTESTER OPTIMIZATION TESTS 💎🌟⚡

Tests for save_detailed_trades flag and performance optimizations
"""

import pytest
import numpy as np
import pandas as pd
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backtester import Backtester


# ═══════════════════════════════════════════════════════════════
# 🧪 TEST HELPERS
# ═══════════════════════════════════════════════════════════════

class SimpleStrategy:
    """Simple test strategy"""
    
    def __init__(self, name="TestStrategy", stop_loss=20, take_profit=40):
        self.name = name
        self.params = {
            "stop_loss_pips": stop_loss,
            "take_profit_pips": take_profit
        }
    
    def generate_signals(self, df):
        """Generate simple signals for testing"""
        signals = pd.Series(0, index=df.index)
        if len(signals) > 50:
            signals.iloc[10] = 1   # Buy
            signals.iloc[30] = -1  # Exit
            signals.iloc[40] = -1  # Sell
            signals.iloc[50] = 1   # Exit
        return signals


# ═══════════════════════════════════════════════════════════════
# 🧪 TESTS
# ═══════════════════════════════════════════════════════════════

def test_save_detailed_trades_flag_default_false():
    """Test that save_detailed_trades defaults to False"""
    backtester = Backtester()
    assert backtester.save_detailed_trades is False, "save_detailed_trades should default to False"


def test_save_detailed_trades_disabled():
    """Test that detailed trades are not saved when flag is False"""
    config = {
        'capital': {
            'initial_capital': 10000,
            'default_lot_size': 0.1,
            'pip_value_per_lot': 10,
            'pip_decimal_places': 4
        },
        'backtester': {
            'lot_sizes': [0.1],
            'commission_per_lot': 0.05
        }
    }
    
    backtester = Backtester(config=config)
    
    # Create test data
    np.random.seed(42)
    n = 100
    df = pd.DataFrame({
        'bid': 1.0500 + np.cumsum(np.random.randn(n) * 0.0001),
        'ask': 1.0510 + np.cumsum(np.random.randn(n) * 0.0001),
        'mid_price': 1.0505 + np.cumsum(np.random.randn(n) * 0.0001),
        'momentum': np.random.randn(n) * 0.1
    })
    
    strategy = SimpleStrategy()
    
    # Run backtest with save_detailed_trades=False (default)
    results = backtester.backtest(strategy, df, save_detailed_trades=False)
    
    result = results[0.1]
    
    # Detailed trades should be empty
    assert len(result.trades_detailed) == 0, "trades_detailed should be empty when save_detailed_trades=False"
    
    # But regular trades should still be recorded
    assert result.n_trades > 0, "Should still have trades"


def test_save_detailed_trades_enabled():
    """Test that detailed trades are saved when flag is True"""
    config = {
        'capital': {
            'initial_capital': 10000,
            'default_lot_size': 0.1,
            'pip_value_per_lot': 10,
            'pip_decimal_places': 4
        },
        'backtester': {
            'lot_sizes': [0.1],
            'commission_per_lot': 0.05
        }
    }
    
    backtester = Backtester(config=config)
    
    # Create test data
    np.random.seed(42)
    n = 100
    df = pd.DataFrame({
        'bid': 1.0500 + np.cumsum(np.random.randn(n) * 0.0001),
        'ask': 1.0510 + np.cumsum(np.random.randn(n) * 0.0001),
        'mid_price': 1.0505 + np.cumsum(np.random.randn(n) * 0.0001),
        'momentum': np.random.randn(n) * 0.1,
        'volume': np.random.randint(100, 1000, n)
    })
    
    strategy = SimpleStrategy()
    
    # Run backtest with save_detailed_trades=True
    results = backtester.backtest(strategy, df, save_detailed_trades=True)
    
    result = results[0.1]
    
    # Detailed trades should be populated
    assert len(result.trades_detailed) > 0, "trades_detailed should be populated when save_detailed_trades=True"
    assert len(result.trades_detailed) == result.n_trades, "Should have same number of detailed trades as trades"
    
    # Check structure of detailed trades
    for trade in result.trades_detailed:
        assert 'entry_time' in trade
        assert 'exit_time' in trade
        assert 'entry_price' in trade
        assert 'exit_price' in trade
        assert 'direction' in trade
        assert 'pnl_pips' in trade
        assert 'pnl_usd' in trade
        assert 'exit_reason' in trade
        assert 'market_context' in trade
        assert 'price_history' in trade


def test_numerical_results_identical_regardless_of_flag():
    """Test that PnL calculations are identical whether save_detailed_trades is True or False"""
    config = {
        'capital': {
            'initial_capital': 10000,
            'default_lot_size': 0.1,
            'pip_value_per_lot': 10,
            'pip_decimal_places': 4
        },
        'backtester': {
            'lot_sizes': [0.1],
            'commission_per_lot': 0.05
        }
    }
    
    # Create test data
    np.random.seed(42)
    n = 200
    df = pd.DataFrame({
        'bid': 1.0500 + np.cumsum(np.random.randn(n) * 0.0001),
        'ask': 1.0510 + np.cumsum(np.random.randn(n) * 0.0001),
        'mid_price': 1.0505 + np.cumsum(np.random.randn(n) * 0.0001),
        'momentum': np.random.randn(n) * 0.1
    })
    
    strategy = SimpleStrategy()
    
    # Run with save_detailed_trades=False
    backtester1 = Backtester(config=config)
    results1 = backtester1.backtest(strategy, df, save_detailed_trades=False)
    result1 = results1[0.1]
    
    # Run with save_detailed_trades=True
    backtester2 = Backtester(config=config)
    results2 = backtester2.backtest(strategy, df, save_detailed_trades=True)
    result2 = results2[0.1]
    
    # All numerical metrics should be identical
    assert result1.n_trades == result2.n_trades, "n_trades should be identical"
    assert abs(result1.win_rate - result2.win_rate) < 1e-10, "win_rate should be identical"
    assert abs(result1.profit_factor - result2.profit_factor) < 1e-10, "profit_factor should be identical"
    assert abs(result1.total_return - result2.total_return) < 1e-10, "total_return should be identical"
    assert abs(result1.sharpe_ratio - result2.sharpe_ratio) < 1e-10, "sharpe_ratio should be identical"
    assert abs(result1.max_drawdown - result2.max_drawdown) < 1e-10, "max_drawdown should be identical"
    assert abs(result1.gross_pnl - result2.gross_pnl) < 1e-10, "gross_pnl should be identical"
    assert abs(result1.total_commission - result2.total_commission) < 1e-10, "total_commission should be identical"
    assert abs(result1.net_pnl - result2.net_pnl) < 1e-10, "net_pnl should be identical"
    
    # Only difference: detailed trades
    assert len(result1.trades_detailed) == 0, "result1 should have no detailed trades"
    assert len(result2.trades_detailed) > 0, "result2 should have detailed trades"


def test_backward_compatibility_default_behavior():
    """Test that default behavior (no save_detailed_trades param) works as before"""
    config = {
        'capital': {
            'initial_capital': 10000,
            'default_lot_size': 0.1,
            'pip_value_per_lot': 10,
            'pip_decimal_places': 4
        },
        'backtester': {
            'lot_sizes': [0.1],
            'commission_per_lot': 0.05
        }
    }
    
    backtester = Backtester(config=config)
    
    # Create test data
    np.random.seed(42)
    n = 100
    df = pd.DataFrame({
        'mid_price': 1.0505 + np.cumsum(np.random.randn(n) * 0.0001),
        'momentum': np.random.randn(n) * 0.1
    })
    
    strategy = SimpleStrategy()
    
    # Call backtest without save_detailed_trades parameter (backward compatibility)
    results = backtester.backtest(strategy, df)
    
    # Should work without errors
    assert isinstance(results, dict), "Should return dict"
    assert 0.1 in results, "Should have results for 0.1 lot"
    
    result = results[0.1]
    
    # Default behavior is save_detailed_trades=False
    assert len(result.trades_detailed) == 0, "Default should not save detailed trades"


def test_multi_lot_with_save_detailed_trades():
    """Test that save_detailed_trades works with multi-lot testing"""
    config = {
        'capital': {
            'initial_capital': 10000,
            'default_lot_size': 0.1,
            'pip_value_per_lot': 10,
            'pip_decimal_places': 4
        },
        'backtester': {
            'lot_sizes': [0.01, 0.1, 1.0],
            'commission_per_lot': 0.05
        }
    }
    
    backtester = Backtester(config=config)
    
    # Create test data
    np.random.seed(42)
    n = 100
    df = pd.DataFrame({
        'mid_price': 1.0505 + np.cumsum(np.random.randn(n) * 0.0001),
        'momentum': np.random.randn(n) * 0.1
    })
    
    strategy = SimpleStrategy()
    
    # Run with multiple lots and save_detailed_trades=True
    results = backtester.backtest(strategy, df, multi_lot=True, save_detailed_trades=True)
    
    # Check all lot sizes have detailed trades
    for lot_size in [0.01, 0.1, 1.0]:
        assert lot_size in results, f"Should have results for {lot_size} lot"
        result = results[lot_size]
        
        # Each lot size should have detailed trades when enabled
        if result.n_trades > 0:
            assert len(result.trades_detailed) > 0, f"Lot {lot_size} should have detailed trades"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
