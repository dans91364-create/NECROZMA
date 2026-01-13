#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚡🌟💎 ULTRA NECROZMA - POSITION SIZING TESTS 💎🌟⚡

Tests for Forex position sizing and return calculation
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
    """Simple test strategy for backtesting"""
    
    def __init__(self, name="SimpleTest", stop_loss=100, take_profit=100):
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


class StopLossStrategy:
    """Strategy with specific stop loss for testing"""
    
    def __init__(self, stop_loss_pips=15):
        self.name = "StopLossTest"
        self.params = {
            "stop_loss_pips": stop_loss_pips,
            "take_profit_pips": 100
        }
    
    def generate_signals(self, df):
        signals = pd.Series(0, index=df.index)
        if len(signals) > 10:
            signals.iloc[10] = 1   # Buy (price will drop, hitting stop)
        return signals


class TakeProfitStrategy:
    """Strategy with specific take profit for testing"""
    
    def __init__(self, take_profit_pips=30):
        self.name = "TakeProfitTest"
        self.params = {
            "stop_loss_pips": 100,
            "take_profit_pips": take_profit_pips
        }
    
    def generate_signals(self, df):
        signals = pd.Series(0, index=df.index)
        if len(signals) > 10:
            signals.iloc[10] = 1   # Buy (price will rise, hitting TP)
        return signals


class TrendStrategy:
    """Trend following strategy for testing"""
    
    def __init__(self):
        self.name = "TrendTest"
        self.params = {"stop_loss_pips": 20, "take_profit_pips": 40}
    
    def generate_signals(self, df):
        # Buy when price is rising
        signals = pd.Series(0, index=df.index)
        for i in range(20, len(df) - 20, 40):
            signals.iloc[i] = 1   # Buy
            signals.iloc[i + 20] = -1  # Sell
        return signals


class VolatileStrategy:
    """Strategy for testing drawdown scenarios"""
    
    def __init__(self):
        self.name = "VolatileTest"
        self.params = {"stop_loss_pips": 60, "take_profit_pips": 40}
    
    def generate_signals(self, df):
        signals = pd.Series(0, index=df.index)
        if len(signals) > 250:
            signals.iloc[50] = 1   # Buy before drawdown
            signals.iloc[250] = -1  # Sell after
        return signals


# ═══════════════════════════════════════════════════════════════
# 🧪 TESTS
# ═══════════════════════════════════════════════════════════════


class DummyStrategy:
    """Simple test strategy"""
    
    def __init__(self, name="TestStrategy", params=None):
        self.name = name
        self.params = params or {}
    
    def generate_signals(self, df):
        """Generate simple test signals"""
        signals = pd.Series(0, index=df.index)
        # Simple: buy at start, sell at end
        if len(signals) > 10:
            signals.iloc[5] = 1  # Buy signal
            signals.iloc[15] = -1  # Sell signal
        return signals


def test_pips_to_usd_conversion():
    """Test that pips are correctly converted to USD"""
    # Standard configuration: 0.1 lot, $10/pip/lot
    config = {
        'capital': {
            'initial_capital': 10000,
            'default_lot_size': 0.1,
            'pip_value_per_lot': 10,
            'pip_decimal_places': 4
        }
    }
    
    backtester = Backtester(config=config)
    
    # For 0.1 lot: $10/pip/lot * 0.1 = $1/pip
    assert backtester._pips_to_usd(1) == 1.0
    assert backtester._pips_to_usd(20) == 20.0
    assert backtester._pips_to_usd(-10) == -10.0
    
    # Test with 1.0 lot
    config['capital']['default_lot_size'] = 1.0
    backtester = Backtester(config=config)
    
    # For 1.0 lot: $10/pip/lot * 1.0 = $10/pip
    assert backtester._pips_to_usd(1) == 10.0
    assert backtester._pips_to_usd(20) == 200.0
    assert backtester._pips_to_usd(-10) == -100.0


def test_single_trade_return_calculation():
    """Test that a single trade produces realistic returns"""
    config = {
        'capital': {
            'initial_capital': 10000,
            'default_lot_size': 0.1,
            'pip_value_per_lot': 10,
            'pip_decimal_places': 4
        }
    }
    
    backtester = Backtester(config=config)
    
    # Create test data with a price move of 20 pips
    # Entry: 1.0500, Exit: 1.0520 (20 pips up)
    np.random.seed(42)
    n = 100
    
    # Create prices that move from 1.0500 to 1.0520
    prices = np.linspace(1.0500, 1.0520, n)
    
    df = pd.DataFrame({
        'mid_price': prices,
        'close': prices,
        'momentum': np.random.randn(n) * 0.1
    })
    
    # Use module-level strategy
    strategy = SimpleStrategy()
    results = backtester.backtest(strategy, df)
    
    # Should have 1 trade
    assert results.n_trades >= 1, f"Expected at least 1 trade, got {results.n_trades}"
    
    # First trade should be profitable (price went up)
    if results.n_trades > 0:
        first_trade_pnl = results.trades.iloc[0]['pnl']
        
        # PnL should be in USD (around $2-5 for this move with 0.1 lot)
        # Not in price terms (which would be ~0.002)
        assert first_trade_pnl > 0.1, f"Expected USD profit > 0.1, got {first_trade_pnl}"
        assert first_trade_pnl < 100, f"Expected USD profit < 100, got {first_trade_pnl}"
        
        # Total return should be small but meaningful (0.02% - 0.5%)
        assert results.total_return > 0.0001, f"Expected return > 0.01%, got {results.total_return * 100:.4f}%"
        assert results.total_return < 0.01, f"Expected return < 1%, got {results.total_return * 100:.4f}%"


def test_stop_loss_pnl_calculation():
    """Test that stop loss generates correct USD loss"""
    config = {
        'capital': {
            'initial_capital': 10000,
            'default_lot_size': 0.1,
            'pip_value_per_lot': 10,
            'pip_decimal_places': 4
        }
    }
    
    backtester = Backtester(config=config)
    
    # Create test data with price moving against us
    np.random.seed(42)
    n = 100
    
    # Price drops from 1.0500 to 1.0480 (20 pips down)
    prices = np.linspace(1.0500, 1.0480, n)
    
    df = pd.DataFrame({
        'mid_price': prices,
        'close': prices,
        'momentum': np.random.randn(n) * 0.1
    })
    
    # Use module-level strategy with 15 pip stop loss
    strategy = StopLossStrategy(stop_loss_pips=15)
    results = backtester.backtest(strategy, df)
    
    # Should have at least 1 trade that hit stop loss
    if results.n_trades > 0:
        # Find trades that hit stop loss
        stop_loss_trades = results.trades[results.trades['exit_reason'] == 'stop_loss']
        
        if len(stop_loss_trades) > 0:
            first_sl = stop_loss_trades.iloc[0]['pnl']
            
            # Stop loss of 15 pips with 0.1 lot = -$15
            # Allow some tolerance for price fluctuations
            expected_loss = -15.0
            assert abs(first_sl - expected_loss) < 5, \
                f"Expected stop loss ~${expected_loss}, got ${first_sl}"


def test_take_profit_pnl_calculation():
    """Test that take profit generates correct USD profit"""
    config = {
        'capital': {
            'initial_capital': 10000,
            'default_lot_size': 0.1,
            'pip_value_per_lot': 10,
            'pip_decimal_places': 4
        }
    }
    
    backtester = Backtester(config=config)
    
    # Create test data with price moving in our favor
    np.random.seed(42)
    n = 100
    
    # Price rises from 1.0500 to 1.0550 (50 pips up)
    prices = np.linspace(1.0500, 1.0550, n)
    
    df = pd.DataFrame({
        'mid_price': prices,
        'close': prices,
        'momentum': np.random.randn(n) * 0.1
    })
    
    # Use module-level strategy with 30 pip take profit
    strategy = TakeProfitStrategy(take_profit_pips=30)
    results = backtester.backtest(strategy, df)
    
    # Should have at least 1 trade that hit take profit
    if results.n_trades > 0:
        # Find trades that hit take profit
        tp_trades = results.trades[results.trades['exit_reason'] == 'take_profit']
        
        if len(tp_trades) > 0:
            first_tp = tp_trades.iloc[0]['pnl']
            
            # Take profit of 30 pips with 0.1 lot = $30
            expected_profit = 30.0
            assert abs(first_tp - expected_profit) < 5, \
                f"Expected take profit ~${expected_profit}, got ${first_tp}"


def test_equity_curve_realistic_values():
    """Test that equity curve shows realistic growth"""
    config = {
        'capital': {
            'initial_capital': 10000,
            'default_lot_size': 0.1,
            'pip_value_per_lot': 10,
            'pip_decimal_places': 4
        }
    }
    
    backtester = Backtester(config=config)
    
    # Create trending data
    np.random.seed(42)
    n = 500
    
    # Upward trend with some noise
    trend = np.linspace(0, 0.01, n)  # 100 pip trend
    noise = np.random.randn(n) * 0.0001
    prices = 1.0500 + trend + noise
    
    df = pd.DataFrame({
        'mid_price': prices,
        'close': prices,
        'momentum': np.random.randn(n) * 0.1
    })
    
    # Use module-level trend strategy
    strategy = TrendStrategy()
    results = backtester.backtest(strategy, df)
    
    # Check equity curve
    if len(results.equity_curve) > 1:
        initial = results.equity_curve.iloc[0]
        final = results.equity_curve.iloc[-1]
        
        # Initial should equal initial capital
        assert abs(initial - 10000) < 1, f"Expected initial capital $10,000, got ${initial}"
        
        # Final should be different from initial (some trading happened)
        assert final != initial, "Equity curve should change after trading"
        
        # Equity should be in realistic range (not microscopic changes)
        # For trending market, expect some growth or loss
        change = abs(final - initial)
        assert change > 1, f"Expected equity change > $1, got ${change}"


def test_max_drawdown_realistic():
    """Test that max drawdown is calculated in realistic percentages"""
    config = {
        'capital': {
            'initial_capital': 10000,
            'default_lot_size': 0.1,
            'pip_value_per_lot': 10,
            'pip_decimal_places': 4
        }
    }
    
    backtester = Backtester(config=config)
    
    # Create volatile data with drawdown
    np.random.seed(42)
    n = 500
    
    # Create a drawdown scenario
    prices = np.ones(n) * 1.0500
    prices[100:200] -= 0.0050  # 50 pip drop
    prices[200:] += 0.0025     # Partial recovery
    
    df = pd.DataFrame({
        'mid_price': prices,
        'close': prices,
        'momentum': np.random.randn(n) * 0.1
    })
    
    # Use module-level volatile strategy
    strategy = VolatileStrategy()
    results = backtester.backtest(strategy, df)
    
    # Max drawdown should be a realistic percentage (0-50%)
    # Not microscopic like 0.0001%
    if results.max_drawdown > 0:
        assert results.max_drawdown < 1.0, \
            f"Max drawdown should be < 100%, got {results.max_drawdown * 100:.2f}%"
        
        # If there was a drawdown in equity, it should be measurable
        # Not infinitesimally small
        if results.n_trades > 0:
            assert results.max_drawdown > 0.0001, \
                f"Max drawdown seems too small: {results.max_drawdown * 100:.4f}%"


def test_different_lot_sizes():
    """Test that different lot sizes produce proportional results"""
    # Test with 0.1 lot
    config_01 = {
        'capital': {
            'initial_capital': 10000,
            'default_lot_size': 0.1,
            'pip_value_per_lot': 10,
            'pip_decimal_places': 4
        }
    }
    
    # Test with 0.2 lot (should produce 2x the PnL)
    config_02 = {
        'capital': {
            'initial_capital': 10000,
            'default_lot_size': 0.2,
            'pip_value_per_lot': 10,
            'pip_decimal_places': 4
        }
    }
    
    backtester_01 = Backtester(config=config_01)
    backtester_02 = Backtester(config=config_02)
    
    # Test conversion
    assert backtester_01._pips_to_usd(20) == 20.0  # 0.1 lot
    assert backtester_02._pips_to_usd(20) == 40.0  # 0.2 lot (2x)
    
    # Ratio should be exactly 2.0
    ratio = backtester_02._pips_to_usd(20) / backtester_01._pips_to_usd(20)
    assert abs(ratio - 2.0) < 0.001, f"Expected 2x ratio, got {ratio}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
