#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚡🌟💎 ULTRA NECROZMA - TICK DATA BACKTESTER TESTS 💎🌟⚡

Tests for tick data backtesting with bid/ask execution and commissions
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

class SimpleTickStrategy:
    """Simple test strategy for tick data backtesting"""
    
    def __init__(self, name="TickTest", stop_loss=20, take_profit=40):
        self.name = name
        self.params = {
            "stop_loss_pips": stop_loss,
            "take_profit_pips": take_profit
        }
    
    def generate_signals(self, df):
        """Generate simple buy signal for testing"""
        signals = pd.Series(0, index=df.index)
        if len(signals) > 30:
            signals.iloc[10] = 1   # Buy
            signals.iloc[30] = -1  # Sell
        return signals


# ═══════════════════════════════════════════════════════════════
# 🧪 TESTS
# ═══════════════════════════════════════════════════════════════

def test_tick_data_with_bid_ask():
    """Test that backtester works with tick data (bid/ask/mid_price)"""
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
    
    # Create tick data with bid/ask spread
    np.random.seed(42)
    n = 100
    
    mid_prices = 1.0500 + np.cumsum(np.random.randn(n) * 0.0001)
    spread = 0.00010  # 1 pip spread
    
    df = pd.DataFrame({
        'bid': mid_prices - spread/2,
        'ask': mid_prices + spread/2,
        'mid_price': mid_prices,
        'spread_pips': np.ones(n) * 1.0,
        'pips_change': np.random.randn(n) * 0.5,
        'momentum': np.random.randn(n) * 0.1
    })
    
    strategy = SimpleTickStrategy()
    results = backtester.backtest(strategy, df)
    
    # Should return dict with one lot size
    assert isinstance(results, dict), "Should return dict of results"
    assert 0.1 in results, "Should have results for 0.1 lot"
    
    result = results[0.1]
    assert result.lot_size == 0.1


def test_multi_lot_testing():
    """Test that backtester runs multiple lot sizes"""
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
    
    prices = 1.0500 + np.cumsum(np.random.randn(n) * 0.0001)
    
    df = pd.DataFrame({
        'mid_price': prices,
        'close': prices,
        'pips_change': np.random.randn(n) * 0.5,
        'momentum': np.random.randn(n) * 0.1
    })
    
    strategy = SimpleTickStrategy()
    results = backtester.backtest(strategy, df)
    
    # Should have results for all 3 lot sizes
    assert len(results) == 3, f"Expected 3 results, got {len(results)}"
    assert 0.01 in results, "Missing results for 0.01 lot"
    assert 0.1 in results, "Missing results for 0.1 lot"
    assert 1.0 in results, "Missing results for 1.0 lot"
    
    # Check lot sizes are correct
    assert results[0.01].lot_size == 0.01
    assert results[0.1].lot_size == 0.1
    assert results[1.0].lot_size == 1.0


def test_commission_calculation():
    """Test that commissions are calculated correctly"""
    config = {
        'capital': {
            'initial_capital': 10000,
            'default_lot_size': 0.1,
            'pip_value_per_lot': 10,
            'pip_decimal_places': 4
        },
        'backtester': {
            'lot_sizes': [0.1, 1.0],
            'commission_per_lot': 0.05  # $0.05 per side per lot
        }
    }
    
    backtester = Backtester(config=config)
    
    # Create uptrending data to ensure profitable trade
    np.random.seed(42)
    n = 100
    
    prices = np.linspace(1.0500, 1.0550, n)  # 50 pip uptrend
    
    df = pd.DataFrame({
        'mid_price': prices,
        'close': prices,
        'pips_change': np.diff(prices, prepend=prices[0]) / 0.0001,
        'momentum': np.random.randn(n) * 0.1
    })
    
    strategy = SimpleTickStrategy(take_profit=30)
    results = backtester.backtest(strategy, df)
    
    # Check 0.1 lot commission
    if results[0.1].n_trades > 0:
        # Commission per trade = 2 * $0.05 * 0.1 = $0.01
        expected_commission_per_trade = 2 * 0.05 * 0.1
        total_commission_01 = results[0.1].total_commission
        
        # Should be close to expected (may have multiple trades)
        commission_per_trade = total_commission_01 / results[0.1].n_trades
        assert abs(commission_per_trade - expected_commission_per_trade) < 0.001, \
            f"Expected ~${expected_commission_per_trade} per trade, got ${commission_per_trade}"
    
    # Check 1.0 lot commission (should be 10x larger)
    if results[1.0].n_trades > 0:
        # Commission per trade = 2 * $0.05 * 1.0 = $0.10
        expected_commission_per_trade = 2 * 0.05 * 1.0
        total_commission_10 = results[1.0].total_commission
        
        commission_per_trade = total_commission_10 / results[1.0].n_trades
        assert abs(commission_per_trade - expected_commission_per_trade) < 0.001, \
            f"Expected ~${expected_commission_per_trade} per trade, got ${commission_per_trade}"


def test_gross_vs_net_pnl():
    """Test that gross and net PnL are calculated correctly"""
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
    
    # Create data with profitable trade
    np.random.seed(42)
    n = 100
    
    prices = np.linspace(1.0500, 1.0530, n)  # 30 pip uptrend
    
    df = pd.DataFrame({
        'mid_price': prices,
        'pips_change': np.diff(prices, prepend=prices[0]) / 0.0001,
        'momentum': np.random.randn(n) * 0.1
    })
    
    strategy = SimpleTickStrategy(take_profit=25)
    results = backtester.backtest(strategy, df)
    
    result = results[0.1]
    
    # Net PnL should equal Gross PnL - Commission
    if result.n_trades > 0:
        assert result.net_pnl == result.gross_pnl - result.total_commission, \
            "Net PnL should equal Gross PnL minus Commission"
        
        # Net should be less than gross (commission reduces profit)
        assert result.net_pnl < result.gross_pnl, \
            "Net PnL should be less than Gross PnL"


def test_bid_ask_realistic_execution():
    """Test that long entries use ask and exits use bid"""
    config = {
        'capital': {
            'initial_capital': 10000,
            'default_lot_size': 0.1,
            'pip_value_per_lot': 10,
            'pip_decimal_places': 4
        },
        'backtester': {
            'lot_sizes': [0.1],
            'commission_per_lot': 0.0  # No commission for cleaner testing
        }
    }
    
    backtester = Backtester(config=config)
    
    # Create tick data with known bid/ask
    n = 100
    mid_price = 1.0500
    spread = 0.00010  # 1 pip spread
    
    df = pd.DataFrame({
        'bid': np.ones(n) * (mid_price - spread/2),
        'ask': np.ones(n) * (mid_price + spread/2),
        'mid_price': np.ones(n) * mid_price,
        'pips_change': np.zeros(n),
        'momentum': np.zeros(n)
    })
    
    # Modify to create a profitable scenario after entry
    df.loc[11:, 'bid'] = mid_price + 0.0010  # Bid rises 10 pips
    df.loc[11:, 'ask'] = mid_price + 0.0011
    df.loc[11:, 'mid_price'] = mid_price + 0.00105
    
    strategy = SimpleTickStrategy(take_profit=5)
    results = backtester.backtest(strategy, df)
    
    result = results[0.1]
    
    # Should have at least one trade
    if result.n_trades > 0 and len(result.trades) > 0:
        first_trade = result.trades.iloc[0]
        
        # Long entry should be at ask price
        expected_entry = mid_price + spread/2  # ask price
        assert abs(first_trade['entry_price'] - expected_entry) < 1e-6, \
            f"Long entry should be at ask ({expected_entry}), got {first_trade['entry_price']}"


def test_volatility_with_pips_change():
    """Test that volatility calculation uses pips_change"""
    config = {
        'capital': {
            'initial_capital': 10000,
            'default_lot_size': 0.1,
            'pip_value_per_lot': 10,
            'pip_decimal_places': 4
        },
        'backtester': {
            'lot_sizes': [0.1],
            'commission_per_lot': 0.0
        }
    }
    
    backtester = Backtester(config=config)
    
    # Create tick data with pips_change
    np.random.seed(42)
    n = 100
    
    pips_change = np.random.randn(n) * 2.0  # Volatile pips_change
    
    df = pd.DataFrame({
        'mid_price': 1.0500 + np.cumsum(pips_change * 0.0001),
        'pips_change': pips_change,
        'momentum': np.random.randn(n) * 0.1
    })
    
    backtester.df = df
    
    # Get market context at index 50
    context = backtester._get_market_context(50)
    
    # Should have volatility calculated from pips_change
    assert 'volatility' in context
    assert context['volatility'] > 0, "Volatility should be positive"
    
    # Volatility should be close to std of last 20 pips_change
    expected_vol = df['pips_change'].iloc[31:51].std()
    assert abs(context['volatility'] - expected_vol) < 0.1, \
        f"Volatility should be ~{expected_vol}, got {context['volatility']}"


def test_fallback_to_ohlc():
    """Test that backtester still works with OHLC data (backward compatibility)"""
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
    
    # Create OHLC data (no bid/ask)
    np.random.seed(42)
    n = 100
    
    close_prices = 1.0500 + np.cumsum(np.random.randn(n) * 0.0001)
    
    df = pd.DataFrame({
        'open': close_prices,
        'high': close_prices + 0.0001,
        'low': close_prices - 0.0001,
        'close': close_prices,
        'momentum': np.random.randn(n) * 0.1
    })
    
    strategy = SimpleTickStrategy()
    results = backtester.backtest(strategy, df)
    
    # Should still work
    assert isinstance(results, dict)
    assert 0.1 in results


def test_result_structure():
    """Test that result structure includes all required fields"""
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
        'mid_price': 1.0500 + np.cumsum(np.random.randn(n) * 0.0001),
        'pips_change': np.random.randn(n) * 0.5,
        'momentum': np.random.randn(n) * 0.1
    })
    
    strategy = SimpleTickStrategy()
    results = backtester.backtest(strategy, df)
    
    # Check each result has required fields
    for lot_size, result in results.items():
        assert hasattr(result, 'lot_size')
        assert hasattr(result, 'gross_pnl')
        assert hasattr(result, 'total_commission')
        assert hasattr(result, 'net_pnl')
        assert hasattr(result, 'n_trades')
        assert hasattr(result, 'win_rate')
        assert hasattr(result, 'sharpe_ratio')
        assert hasattr(result, 'max_drawdown')
        assert hasattr(result, 'profit_factor')


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
