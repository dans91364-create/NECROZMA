#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚡🌟💎 NECROZMA - NUMBA BACKTESTER TESTS 💎🌟⚡

Tests to validate Numba-accelerated backtester produces identical results
"""

import numpy as np
import pandas as pd
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backtester import Backtester, NUMBA_AVAILABLE


# ═══════════════════════════════════════════════════════════════
# 🧪 TEST HELPERS
# ═══════════════════════════════════════════════════════════════

class SimpleStrategy:
    """Simple test strategy for validation"""
    
    def __init__(self, name="TestStrategy", stop_loss=20, take_profit=40):
        self.name = name
        self.params = {
            "stop_loss_pips": stop_loss,
            "take_profit_pips": take_profit
        }
    
    def generate_signals(self, df):
        """Generate simple signals for testing"""
        signals = pd.Series(0, index=df.index)
        n = len(signals)
        
        if n > 100:
            # Generate some buy and sell signals
            signals.iloc[10] = 1   # Buy
            signals.iloc[50] = -1  # Exit/Sell
            signals.iloc[60] = -1  # Sell
            signals.iloc[90] = 1   # Exit/Buy
        
        return signals


# ═══════════════════════════════════════════════════════════════
# 🧪 TESTS
# ═══════════════════════════════════════════════════════════════

def test_numba_availability():
    """Test that Numba is available"""
    print(f"\n✅ Numba Available: {NUMBA_AVAILABLE}")
    assert NUMBA_AVAILABLE, "Numba should be installed for optimization"


def test_numba_backtester_basic():
    """Test basic Numba backtester functionality"""
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
    
    # Create realistic test data (1000 ticks)
    np.random.seed(42)
    n = 1000
    df = pd.DataFrame({
        'bid': 1.0500 + np.cumsum(np.random.randn(n) * 0.00005),
        'ask': 1.0510 + np.cumsum(np.random.randn(n) * 0.00005),
        'mid_price': 1.0505 + np.cumsum(np.random.randn(n) * 0.00005),
        'momentum': np.random.randn(n) * 0.1
    })
    
    strategy = SimpleStrategy()
    
    # Run backtest
    results = backtester.backtest(strategy, df, multi_lot=False)
    
    # Validate results
    assert results.n_trades > 0, "Should have at least one trade"
    assert isinstance(results.sharpe_ratio, float), "Sharpe ratio should be float"
    assert isinstance(results.total_return, float), "Total return should be float"
    
    print(f"\n   Trades: {results.n_trades}")
    print(f"   Win Rate: {results.win_rate:.2%}")
    print(f"   Total Return: {results.total_return:.2%}")


def test_numba_backtester_consistency():
    """Test that Numba backtester produces consistent results across multiple runs"""
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
    n = 1000
    df = pd.DataFrame({
        'bid': 1.0500 + np.cumsum(np.random.randn(n) * 0.00005),
        'ask': 1.0510 + np.cumsum(np.random.randn(n) * 0.00005),
        'mid_price': 1.0505 + np.cumsum(np.random.randn(n) * 0.00005),
        'momentum': np.random.randn(n) * 0.1
    })
    
    strategy = SimpleStrategy()
    
    # Run backtest multiple times
    results_list = []
    for _ in range(3):
        backtester = Backtester(config=config)
        results = backtester.backtest(strategy, df, multi_lot=False)
        results_list.append(results)
    
    # All runs should produce identical results
    for i in range(1, len(results_list)):
        assert results_list[i].n_trades == results_list[0].n_trades, "Trade count should be consistent"
        assert abs(results_list[i].total_return - results_list[0].total_return) < 1e-10, "Returns should be identical"
        assert abs(results_list[i].sharpe_ratio - results_list[0].sharpe_ratio) < 1e-10, "Sharpe should be identical"


def test_numba_backtester_multi_lot():
    """Test Numba backtester with multiple lot sizes"""
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
    n = 1000
    df = pd.DataFrame({
        'bid': 1.0500 + np.cumsum(np.random.randn(n) * 0.00005),
        'ask': 1.0510 + np.cumsum(np.random.randn(n) * 0.00005),
        'mid_price': 1.0505 + np.cumsum(np.random.randn(n) * 0.00005),
        'momentum': np.random.randn(n) * 0.1
    })
    
    strategy = SimpleStrategy()
    
    # Run backtest with multi-lot
    results_dict = backtester.backtest(strategy, df, multi_lot=True)
    
    # Should have results for each lot size
    assert len(results_dict) == 3, "Should have 3 lot size results"
    assert 0.01 in results_dict, "Should have 0.01 lot results"
    assert 0.1 in results_dict, "Should have 0.1 lot results"
    assert 1.0 in results_dict, "Should have 1.0 lot results"
    
    # All should have same number of trades
    n_trades_001 = results_dict[0.01].n_trades
    n_trades_01 = results_dict[0.1].n_trades
    n_trades_10 = results_dict[1.0].n_trades
    
    assert n_trades_001 == n_trades_01 == n_trades_10, "All lot sizes should have same trade count"
    
    print(f"\n   Lot 0.01: {n_trades_001} trades, Return: {results_dict[0.01].total_return:.2%}")
    print(f"   Lot 0.1:  {n_trades_01} trades, Return: {results_dict[0.1].total_return:.2%}")
    print(f"   Lot 1.0:  {n_trades_10} trades, Return: {results_dict[1.0].total_return:.2%}")


def test_numba_backtester_detailed_trades():
    """Test that detailed trades work with Numba backtester"""
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
    n = 1000
    df = pd.DataFrame({
        'bid': 1.0500 + np.cumsum(np.random.randn(n) * 0.00005),
        'ask': 1.0510 + np.cumsum(np.random.randn(n) * 0.00005),
        'mid_price': 1.0505 + np.cumsum(np.random.randn(n) * 0.00005),
        'momentum': np.random.randn(n) * 0.1
    })
    
    strategy = SimpleStrategy()
    
    # Run with save_detailed_trades=True
    results = backtester.backtest(strategy, df, multi_lot=False, save_detailed_trades=True)
    
    # Should have detailed trades
    assert len(results.trades_detailed) > 0, "Should have detailed trades"
    assert len(results.trades_detailed) == results.n_trades, "Detailed trades should match trade count"
    
    # Check first detailed trade structure
    first_trade = results.trades_detailed[0]
    assert 'entry_time' in first_trade, "Should have entry_time"
    assert 'exit_time' in first_trade, "Should have exit_time"
    assert 'direction' in first_trade, "Should have direction"
    assert 'pnl_pips' in first_trade, "Should have pnl_pips"
    assert 'pnl_usd' in first_trade, "Should have pnl_usd"
    assert 'exit_reason' in first_trade, "Should have exit_reason"


def test_numba_backtester_exit_reasons():
    """Test that exit reasons are correctly tracked"""
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
    
    # Create test data with clear patterns
    np.random.seed(42)
    n = 500
    df = pd.DataFrame({
        'bid': 1.0500 + np.cumsum(np.random.randn(n) * 0.00005),
        'ask': 1.0510 + np.cumsum(np.random.randn(n) * 0.00005),
        'mid_price': 1.0505 + np.cumsum(np.random.randn(n) * 0.00005),
        'momentum': np.random.randn(n) * 0.1
    })
    
    strategy = SimpleStrategy(stop_loss=10, take_profit=20)
    
    # Run backtest
    results = backtester.backtest(strategy, df, multi_lot=False)
    
    # Check that trades have exit reasons
    trades_df = results.trades
    if len(trades_df) > 0:
        exit_reasons = trades_df['exit_reason'].unique()
        print(f"\n   Exit reasons found: {list(exit_reasons)}")
        
        # Valid exit reasons
        valid_reasons = {'stop_loss', 'take_profit', 'signal'}
        assert all(reason in valid_reasons for reason in exit_reasons), "All exit reasons should be valid"


if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════════╗
║         ⚡ NUMBA BACKTESTER VALIDATION TESTS ⚡              ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    # Run all tests
    tests = [
        ("Numba Availability", test_numba_availability),
        ("Basic Functionality", test_numba_backtester_basic),
        ("Consistency", test_numba_backtester_consistency),
        ("Multi-Lot Support", test_numba_backtester_multi_lot),
        ("Detailed Trades", test_numba_backtester_detailed_trades),
        ("Exit Reasons", test_numba_backtester_exit_reasons),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            print(f"\n{'='*60}")
            print(f"Testing: {test_name}")
            print('='*60)
            test_func()
            print(f"✅ PASSED: {test_name}")
            passed += 1
        except AssertionError as e:
            print(f"❌ FAILED: {test_name}")
            print(f"   Error: {e}")
            failed += 1
        except Exception as e:
            print(f"💥 ERROR: {test_name}")
            print(f"   Error: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    print(f"\n{'='*60}")
    print(f"📊 TEST SUMMARY")
    print('='*60)
    print(f"   Passed: {passed}/{len(tests)}")
    print(f"   Failed: {failed}/{len(tests)}")
    
    if failed == 0:
        print(f"\n   ✅ ALL TESTS PASSED!")
    else:
        print(f"\n   ❌ SOME TESTS FAILED")
        sys.exit(1)
