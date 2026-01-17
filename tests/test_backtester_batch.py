#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚡🌟💎 NECROZMA - BATCH BACKTESTER TESTS 💎🌟⚡

Tests for the test_strategies batch backtesting method
"""

import pytest
import numpy as np
import pandas as pd
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backtester import Backtester, BacktestResults


# ═══════════════════════════════════════════════════════════════
# 🧪 TEST HELPERS
# ═══════════════════════════════════════════════════════════════

class SimpleStrategy:
    """Simple test strategy for backtesting"""
    
    def __init__(self, name="SimpleTest", stop_loss=15, take_profit=30):
        self.name = name
        self.params = {
            "stop_loss_pips": stop_loss,
            "take_profit_pips": take_profit
        }
    
    def generate_signals(self, df):
        """Generate simple buy/sell signals"""
        signals = pd.Series(0, index=df.index)
        if len(signals) > 30:
            signals.iloc[10] = 1   # Buy
            signals.iloc[30] = -1  # Sell
        return signals


class BrokenStrategy:
    """Strategy that raises an error during signal generation"""
    
    def __init__(self, name="BrokenTest"):
        self.name = name
        self.params = {
            "stop_loss_pips": 15,
            "take_profit_pips": 30
        }
    
    def generate_signals(self, df):
        """Intentionally raise an error"""
        raise ValueError("Intentional error for testing")


def create_test_dataframe(n_samples=100):
    """Create test DataFrame with price data"""
    np.random.seed(42)
    
    base_price = 1.10
    returns = np.random.randn(n_samples) * 0.0001
    close_prices = base_price + np.cumsum(returns)
    
    opens = np.roll(close_prices, 1)
    opens[0] = base_price
    
    highs = np.maximum(opens, close_prices) + np.abs(np.random.randn(n_samples)) * 0.00005
    lows = np.minimum(opens, close_prices) - np.abs(np.random.randn(n_samples)) * 0.00005
    
    df = pd.DataFrame({
        'open': opens,
        'high': highs,
        'low': lows,
        'close': close_prices,
        'mid_price': close_prices,
        'momentum': np.random.randn(n_samples),
    })
    
    return df


# ═══════════════════════════════════════════════════════════════
# 🧪 TESTS
# ═══════════════════════════════════════════════════════════════

def test_test_strategies_single_strategy():
    """Test batch backtesting with a single strategy"""
    backtester = Backtester()
    df = create_test_dataframe(100)
    
    strategies = [SimpleStrategy(name="Test1")]
    
    results = backtester.test_strategies(strategies, df, verbose=False)
    
    assert len(results) == 1
    assert isinstance(results[0], BacktestResults)
    assert results[0].strategy_name == "Test1"


def test_test_strategies_multiple_strategies():
    """Test batch backtesting with multiple strategies"""
    backtester = Backtester()
    df = create_test_dataframe(100)
    
    strategies = [
        SimpleStrategy(name="Test1", stop_loss=10, take_profit=20),
        SimpleStrategy(name="Test2", stop_loss=15, take_profit=30),
        SimpleStrategy(name="Test3", stop_loss=20, take_profit=40),
    ]
    
    results = backtester.test_strategies(strategies, df, verbose=False)
    
    assert len(results) == 3
    assert all(isinstance(r, BacktestResults) for r in results)
    assert results[0].strategy_name == "Test1"
    assert results[1].strategy_name == "Test2"
    assert results[2].strategy_name == "Test3"


def test_test_strategies_with_errors():
    """Test batch backtesting handles errors gracefully"""
    backtester = Backtester()
    df = create_test_dataframe(100)
    
    strategies = [
        SimpleStrategy(name="Test1"),
        BrokenStrategy(name="Broken"),
        SimpleStrategy(name="Test2"),
    ]
    
    # Should continue despite error in middle strategy
    results = backtester.test_strategies(strategies, df, verbose=False)
    
    # Should have results from the two working strategies
    assert len(results) == 2
    assert results[0].strategy_name == "Test1"
    assert results[1].strategy_name == "Test2"


def test_test_strategies_empty_list():
    """Test batch backtesting with empty strategy list"""
    backtester = Backtester()
    df = create_test_dataframe(100)
    
    strategies = []
    
    results = backtester.test_strategies(strategies, df, verbose=False)
    
    assert len(results) == 0
    assert isinstance(results, list)


def test_test_strategies_verbose_progress():
    """Test that verbose mode shows progress (smoke test)"""
    backtester = Backtester()
    df = create_test_dataframe(100)
    
    # Create 150 strategies to trigger progress messages
    strategies = [
        SimpleStrategy(name=f"Test{i}") 
        for i in range(150)
    ]
    
    # This should print progress at 100 strategies (smoke test - just ensure no crashes)
    results = backtester.test_strategies(strategies, df, verbose=True)
    
    assert len(results) == 150


def test_test_strategies_results_have_metrics():
    """Test that backtest results contain expected metrics"""
    backtester = Backtester()
    df = create_test_dataframe(100)
    
    strategies = [SimpleStrategy(name="Test1")]
    
    results = backtester.test_strategies(strategies, df, verbose=False)
    
    assert len(results) == 1
    result = results[0]
    
    # Check that key metrics are present
    assert hasattr(result, 'n_trades')
    assert hasattr(result, 'win_rate')
    assert hasattr(result, 'profit_factor')
    assert hasattr(result, 'sharpe_ratio')
    assert hasattr(result, 'max_drawdown')
    assert hasattr(result, 'total_return')


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
