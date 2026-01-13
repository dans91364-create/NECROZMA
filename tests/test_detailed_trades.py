#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚡🌟💎 ULTRA NECROZMA - DETAILED TRADE TRACKING TESTS 💎🌟⚡

Tests for detailed trade tracking with market context and price history
"""

import pytest
import numpy as np
import pandas as pd
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backtester import Backtester


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


def create_test_dataframe(n_samples=1000, with_datetime=True):
    """Create test DataFrame with OHLCV data"""
    np.random.seed(42)
    
    # Generate OHLC data
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
        'volume': np.random.randint(50, 500, n_samples),
        'pattern': ['ohl:H' if i % 3 == 0 else 'ohl:L' for i in range(n_samples)],
    })
    
    # Add datetime index if requested
    if with_datetime:
        start_date = datetime(2025, 1, 1, 9, 0)  # Start at 9 AM
        dates = [start_date + timedelta(minutes=5*i) for i in range(n_samples)]
        df.index = pd.DatetimeIndex(dates)
    
    return df


# ═══════════════════════════════════════════════════════════════
# 🧪 TESTS
# ═══════════════════════════════════════════════════════════════

def test_detailed_trades_basic():
    """Test basic detailed trade tracking"""
    df = create_test_dataframe(n_samples=1000, with_datetime=False)
    strategy = SimpleStrategy()
    backtester = Backtester()
    
    results = backtester.backtest(strategy, df)
    
    # Verify detailed trades are recorded
    assert hasattr(results, 'trades_detailed'), "BacktestResults should have trades_detailed"
    assert isinstance(results.trades_detailed, list), "trades_detailed should be a list"
    assert len(results.trades_detailed) == results.n_trades, "Detailed trades count should match n_trades"
    
    print(f"✅ Basic test: {len(results.trades_detailed)} detailed trades recorded")


def test_detailed_trades_with_datetime():
    """Test detailed trade tracking with datetime index"""
    df = create_test_dataframe(n_samples=1000, with_datetime=True)
    strategy = SimpleStrategy()
    backtester = Backtester()
    
    results = backtester.backtest(strategy, df)
    
    assert len(results.trades_detailed) > 0, "Should have recorded detailed trades"
    
    # Check first trade
    first_trade = results.trades_detailed[0]
    
    # Verify all required fields
    required_fields = [
        'entry_time', 'exit_time', 'entry_price', 'exit_price', 'direction',
        'pnl_pips', 'pnl_usd', 'pnl_pct', 'duration_minutes', 'exit_reason',
        'market_context', 'price_history'
    ]
    
    for field in required_fields:
        assert field in first_trade, f"Trade should have {field} field"
    
    # Verify entry/exit times are datetime strings
    assert '2025-01-01' in first_trade['entry_time'], "Entry time should be a datetime string"
    assert '2025-01-01' in first_trade['exit_time'], "Exit time should be a datetime string"
    
    # Verify duration is calculated
    assert first_trade['duration_minutes'] >= 0, "Duration should be non-negative"
    
    print(f"✅ Datetime test: Entry={first_trade['entry_time']}, Duration={first_trade['duration_minutes']}m")


def test_market_context():
    """Test market context extraction"""
    df = create_test_dataframe(n_samples=1000, with_datetime=True)
    strategy = SimpleStrategy()
    backtester = Backtester()
    
    results = backtester.backtest(strategy, df)
    
    assert len(results.trades_detailed) > 0, "Should have recorded detailed trades"
    
    # Check market context
    first_trade = results.trades_detailed[0]
    market_context = first_trade['market_context']
    
    # Verify market context fields
    required_context_fields = [
        'volatility', 'trend_strength', 'volume_relative', 'spread_pips',
        'pattern_detected', 'pattern_sequence', 'hour_of_day', 'day_of_week'
    ]
    
    for field in required_context_fields:
        assert field in market_context, f"Market context should have {field} field"
    
    # Verify types
    assert isinstance(market_context['volatility'], float), "Volatility should be float"
    assert isinstance(market_context['hour_of_day'], int), "Hour should be int"
    assert isinstance(market_context['day_of_week'], str), "Day of week should be string"
    assert isinstance(market_context['pattern_sequence'], list), "Pattern sequence should be list"
    
    # Verify pattern detection
    assert market_context['pattern_detected'] in ['ohl:H', 'ohl:L', 'unknown'], "Pattern should be recognized"
    
    print(f"✅ Market context: Pattern={market_context['pattern_detected']}, "
          f"Hour={market_context['hour_of_day']}, Day={market_context['day_of_week']}")


def test_price_history():
    """Test price history extraction"""
    df = create_test_dataframe(n_samples=1000, with_datetime=True)
    strategy = SimpleStrategy()
    backtester = Backtester()
    
    results = backtester.backtest(strategy, df)
    
    assert len(results.trades_detailed) > 0, "Should have recorded detailed trades"
    
    # Check price history
    first_trade = results.trades_detailed[0]
    price_history = first_trade['price_history']
    
    # Verify price history fields
    required_history_fields = ['timestamps', 'open', 'high', 'low', 'close', 'volume']
    
    for field in required_history_fields:
        assert field in price_history, f"Price history should have {field} field"
    
    # Verify all arrays have same length
    timestamps_len = len(price_history['timestamps'])
    assert len(price_history['open']) == timestamps_len, "Open prices should match timestamps"
    assert len(price_history['high']) == timestamps_len, "High prices should match timestamps"
    assert len(price_history['low']) == timestamps_len, "Low prices should match timestamps"
    assert len(price_history['close']) == timestamps_len, "Close prices should match timestamps"
    
    # Verify price history has reasonable length (50 before + trade duration + 20 after)
    # Should be more than just the trade itself
    assert timestamps_len > 20, "Price history should include context bars"
    
    print(f"✅ Price history: {timestamps_len} bars captured")


def test_to_dict_includes_detailed_trades():
    """Test that to_dict() includes trades_detailed"""
    df = create_test_dataframe(n_samples=1000, with_datetime=False)
    strategy = SimpleStrategy()
    backtester = Backtester()
    
    results = backtester.backtest(strategy, df)
    result_dict = results.to_dict()
    
    # Verify trades_detailed is in dict
    assert 'trades_detailed' in result_dict, "to_dict() should include trades_detailed"
    assert isinstance(result_dict['trades_detailed'], list), "trades_detailed should be a list"
    assert len(result_dict['trades_detailed']) == results.n_trades, "Dict should have all trades"
    
    # Verify dict structure is JSON-serializable
    import json
    try:
        json_str = json.dumps(result_dict)
        assert len(json_str) > 0, "Should be serializable to JSON"
        print(f"✅ to_dict() includes {len(result_dict['trades_detailed'])} detailed trades (JSON-serializable)")
    except (TypeError, ValueError) as e:
        pytest.fail(f"Result dict is not JSON serializable: {e}")


def test_exit_reasons():
    """Test that exit reasons are correctly recorded"""
    df = create_test_dataframe(n_samples=1000, with_datetime=False)
    strategy = SimpleStrategy(stop_loss=10, take_profit=20)
    backtester = Backtester()
    
    results = backtester.backtest(strategy, df)
    
    assert len(results.trades_detailed) > 0, "Should have recorded detailed trades"
    
    # Check exit reasons
    exit_reasons = set(trade['exit_reason'] for trade in results.trades_detailed)
    
    # Should have at least one of the valid exit reasons
    valid_reasons = {'stop_loss', 'take_profit', 'signal'}
    assert exit_reasons.issubset(valid_reasons), f"Invalid exit reasons found: {exit_reasons - valid_reasons}"
    
    print(f"✅ Exit reasons: {exit_reasons}")


def test_multiple_strategies():
    """Test that detailed trades are reset between backtests"""
    df = create_test_dataframe(n_samples=500, with_datetime=False)
    backtester = Backtester()
    
    # Run first backtest
    strategy1 = SimpleStrategy(name="Strategy1")
    results1 = backtester.backtest(strategy1, df)
    n_trades1 = len(results1.trades_detailed)
    
    # Run second backtest
    strategy2 = SimpleStrategy(name="Strategy2")
    results2 = backtester.backtest(strategy2, df)
    n_trades2 = len(results2.trades_detailed)
    
    # Verify trades are independent
    assert results1.strategy_name == "Strategy1", "First strategy name should be preserved"
    assert results2.strategy_name == "Strategy2", "Second strategy name should be preserved"
    
    # Each result should have its own trades
    assert n_trades1 > 0, "First backtest should have trades"
    assert n_trades2 > 0, "Second backtest should have trades"
    
    print(f"✅ Multiple strategies: Strategy1={n_trades1} trades, Strategy2={n_trades2} trades")


# ═══════════════════════════════════════════════════════════════
# 🎯 MAIN
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════════╗
║         🧪 DETAILED TRADE TRACKING TESTS 🧪                  ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    # Run all tests
    test_detailed_trades_basic()
    test_detailed_trades_with_datetime()
    test_market_context()
    test_price_history()
    test_to_dict_includes_detailed_trades()
    test_exit_reasons()
    test_multiple_strategies()
    
    print("\n✅ All tests passed!")
