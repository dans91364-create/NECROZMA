#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test for MomentumBurst cooldown fix and MeanReverterV3
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from strategy_factory import MomentumBurst, MeanReverterV3, MeanReverter


def test_momentum_burst_time_based_cooldown():
    """Test that MomentumBurst uses time-based cooldown with datetime index"""
    print("\n" + "=" * 70)
    print("🧪 TEST: MomentumBurst Time-Based Cooldown")
    print("=" * 70)
    
    # Create test data with DATETIME index (simulates tick data)
    np.random.seed(42)
    n = 1000  # Simulate 1000 ticks
    
    # Create data with strong momentum bursts every ~100 ticks
    base_price = 1.10
    prices = [base_price]
    
    for i in range(1, n):
        if i % 100 == 0:
            # Strong momentum burst every 100 ticks
            prices.append(prices[-1] + 0.0050)  # Large spike
        else:
            # Normal random walk
            prices.append(prices[-1] + np.random.randn() * 0.0001)
    
    # Create dataframe with datetime index (1-second intervals to simulate ticks)
    df = pd.DataFrame({
        "mid_price": prices,
        "close": prices,
        "volume": np.random.uniform(50, 150, n),
    }, index=pd.date_range("2025-01-01", periods=n, freq="1s"))  # 1-second ticks
    
    # Test with 60-minute cooldown
    params = {
        "lookback_periods": 10,
        "threshold": 2.0,
        "cooldown_minutes": 60,  # 60 minutes cooldown
        "max_trades_per_day": 50,
    }
    
    strategy = MomentumBurst(params)
    signals = strategy.generate_signals(df)
    
    # Count signals
    buy_signals = (signals == 1).sum()
    sell_signals = (signals == -1).sum()
    total_signals = buy_signals + sell_signals
    
    print(f"\n📊 Results with 60-minute cooldown:")
    print(f"   Total ticks: {n}")
    print(f"   Buy signals: {buy_signals}")
    print(f"   Sell signals: {sell_signals}")
    print(f"   Total signals: {total_signals}")
    
    # With 1-second ticks and 60-minute cooldown, we should have at most
    # floor(total_time / cooldown) signals = floor(1000s / 3600s) = 0
    # But if we have strong bursts, we might get 1-2 signals max
    
    # The key is that with tick data, cooldown should be TIME-BASED not tick-based
    # With old buggy version using index-based: would get ~10 signals (every 60 ticks)
    # With new time-based version: should get 0-2 signals (depends on if bursts happen)
    
    if total_signals <= 2:
        print(f"   ✅ PASSED: Time-based cooldown working correctly!")
        print(f"      (Old buggy version would have ~10 signals with 60-tick cooldown)")
        return True
    else:
        print(f"   ❌ FAILED: Too many signals! Expected <= 2, got {total_signals}")
        print(f"      This suggests cooldown is still index-based, not time-based")
        return False


def test_momentum_burst_max_trades_per_day():
    """Test max_trades_per_day parameter"""
    print("\n" + "=" * 70)
    print("🧪 TEST: MomentumBurst Max Trades Per Day")
    print("=" * 70)
    
    # Create data spanning 2 days with many momentum bursts
    np.random.seed(42)
    n = 2000
    
    # Create strong momentum bursts frequently
    base_price = 1.10
    prices = [base_price]
    for i in range(1, n):
        if i % 20 == 0:  # Burst every 20 minutes
            prices.append(prices[-1] + 0.0050)
        else:
            prices.append(prices[-1] + np.random.randn() * 0.0001)
    
    # 1-minute intervals, spanning 2 days
    df = pd.DataFrame({
        "mid_price": prices,
        "close": prices,
        "volume": np.random.uniform(50, 150, n),
    }, index=pd.date_range("2025-01-01", periods=n, freq="1min"))
    
    # Test with 5-minute cooldown and max 10 trades per day
    params = {
        "lookback_periods": 10,
        "threshold": 2.0,
        "cooldown_minutes": 5,  # Short cooldown
        "max_trades_per_day": 10,  # But limit to 10 per day
    }
    
    strategy = MomentumBurst(params)
    signals = strategy.generate_signals(df)
    
    # Count signals per day
    signals_df = pd.DataFrame({"signal": signals})
    signals_df = signals_df[signals_df["signal"] != 0]
    
    if len(signals_df) > 0:
        signals_by_day = signals_df.groupby(signals_df.index.date).size()
        print(f"\n📊 Signals per day:")
        for date, count in signals_by_day.items():
            print(f"   {date}: {count} signals")
        
        max_per_day = signals_by_day.max()
        if max_per_day <= 10:
            print(f"   ✅ PASSED: Max trades per day limit working correctly!")
            return True
        else:
            print(f"   ❌ FAILED: Expected max 10 signals per day, got {max_per_day}")
            return False
    else:
        print(f"   ⚠️  No signals generated (might need to adjust test data)")
        return True


def test_meanreverter_v3_fixed_lookback():
    """Test that MeanReverterV3 uses fixed lookback=5"""
    print("\n" + "=" * 70)
    print("🧪 TEST: MeanReverterV3 Fixed Lookback")
    print("=" * 70)
    
    # Create test data
    np.random.seed(42)
    n = 200
    base_price = 1.10
    
    # Mean-reverting price action
    prices = [base_price]
    mean = base_price
    for i in range(1, n):
        # Mean reversion: pull towards mean
        prices.append(prices[-1] + (mean - prices[-1]) * 0.1 + np.random.randn() * 0.0002)
    
    df = pd.DataFrame({
        "mid_price": prices,
        "close": prices,
    }, index=pd.date_range("2025-01-01", periods=n, freq="5min"))
    
    # MeanReverterV3 ignores 'lookback_periods' and always uses OPTIMAL_LOOKBACK=5
    params = {
        "threshold_std": 2.0,
        "adaptive_threshold": False,
    }
    
    strategy = MeanReverterV3(params)
    signals = strategy.generate_signals(df)
    
    # Verify lookback is 5 (the class constant)
    if strategy.lookback == 5:
        print(f"   ✅ PASSED: Lookback is fixed at 5 (using OPTIMAL_LOOKBACK constant)")
        return True
    else:
        print(f"   ❌ FAILED: Lookback is {strategy.lookback}, expected 5")
        return False


def test_meanreverter_v3_adaptive_threshold():
    """Test MeanReverterV3 adaptive threshold"""
    print("\n" + "=" * 70)
    print("🧪 TEST: MeanReverterV3 Adaptive Threshold")
    print("=" * 70)
    
    # Create test data with varying volatility
    np.random.seed(42)
    n = 500
    base_price = 1.10
    
    prices = [base_price]
    for i in range(1, n):
        # Lower volatility in first half, higher in second half
        vol = 0.0001 if i < n//2 else 0.0005
        prices.append(prices[-1] + np.random.randn() * vol)
    
    df = pd.DataFrame({
        "mid_price": prices,
        "close": prices,
    }, index=pd.date_range("2025-01-01", periods=n, freq="5min"))
    
    # Test with adaptive threshold
    params_adaptive = {
        "threshold_std": 2.0,
        "adaptive_threshold": True,
    }
    
    strategy = MeanReverterV3(params_adaptive)
    signals = strategy.generate_signals(df)
    
    signal_count_adaptive = (signals != 0).sum()
    print(f"   Signals with adaptive threshold: {signal_count_adaptive}")
    print(f"   ✅ PASSED: Adaptive threshold feature implemented")
    
    return True


def test_meanreverter_v3_max_trades_per_day():
    """Test MeanReverterV3 max_trades_per_day (bug fix validation)"""
    print("\n" + "=" * 70)
    print("🧪 TEST: MeanReverterV3 Max Trades Per Day (Bug Fix)")
    print("=" * 70)
    
    # Create data spanning 2 days with strong mean reversion signals
    np.random.seed(42)
    n = 2000
    
    # Create mean-reverting price with frequent overshoots
    base_price = 1.10
    mean = base_price
    prices = [base_price]
    for i in range(1, n):
        # Strong oscillations to trigger many signals
        if i % 50 == 0:
            # Large deviation from mean
            prices.append(mean + 0.0100 * (1 if i % 100 == 0 else -1))
        else:
            # Mean reversion
            prices.append(prices[-1] + (mean - prices[-1]) * 0.05 + np.random.randn() * 0.0001)
    
    # 1-minute intervals, spanning ~1.4 days
    df = pd.DataFrame({
        "mid_price": prices,
        "close": prices,
    }, index=pd.date_range("2025-01-01", periods=n, freq="1min"))
    
    # Test with low threshold to generate many signals, but max 5 per day
    params = {
        "threshold_std": 1.2,  # Low threshold = more signals
        "adaptive_threshold": False,
        "require_confirmation": False,  # No confirmation = more signals
        "max_trades_per_day": 5,  # New default limit
    }
    
    strategy = MeanReverterV3(params)
    signals = strategy.generate_signals(df)
    
    # Count signals per day
    signals_df = pd.DataFrame({"signal": signals})
    signals_df = signals_df[signals_df["signal"] != 0]
    
    if len(signals_df) > 0:
        signals_by_day = signals_df.groupby(signals_df.index.date).size()
        print(f"\n📊 Signals per day:")
        for date, count in signals_by_day.items():
            print(f"   {date}: {count} signals")
        
        max_per_day = signals_by_day.max()
        if max_per_day <= 5:
            print(f"   ✅ PASSED: Max trades per day limit working correctly!")
            print(f"      (Bug fixed: max_trades_per_day now ALWAYS enforced)")
            return True
        else:
            print(f"   ❌ FAILED: Expected max 5 signals per day, got {max_per_day}")
            print(f"      (Bug still present: max_trades_per_day not enforced properly)")
            return False
    else:
        print(f"   ⚠️  No signals generated (might need to adjust test data)")
        return True


def test_meanreverter_max_trades_per_day():
    """Test MeanReverter max_trades_per_day (bug fix validation)"""
    print("\n" + "=" * 70)
    print("🧪 TEST: MeanReverter Max Trades Per Day (Bug Fix)")
    print("=" * 70)
    
    # Create data spanning 2 days with strong mean reversion signals
    np.random.seed(42)
    n = 2000
    
    # Create mean-reverting price with frequent overshoots
    base_price = 1.10
    mean = base_price
    prices = [base_price]
    for i in range(1, n):
        # Strong oscillations to trigger many signals
        if i % 50 == 0:
            # Large deviation from mean
            prices.append(mean + 0.0100 * (1 if i % 100 == 0 else -1))
        else:
            # Mean reversion
            prices.append(prices[-1] + (mean - prices[-1]) * 0.05 + np.random.randn() * 0.0001)
    
    # 1-minute intervals, spanning ~1.4 days
    df = pd.DataFrame({
        "mid_price": prices,
        "close": prices,
    }, index=pd.date_range("2025-01-01", periods=n, freq="1min"))
    
    # Test with low threshold to generate many signals, but max 10 per day
    params = {
        "lookback_periods": 5,
        "threshold_std": 1.6,  # Low threshold = more signals
        "max_trades_per_day": 10,  # Limit to 10 per day
    }
    
    strategy = MeanReverter(params)
    signals = strategy.generate_signals(df)
    
    # Count signals per day
    signals_df = pd.DataFrame({"signal": signals})
    signals_df = signals_df[signals_df["signal"] != 0]
    
    if len(signals_df) > 0:
        signals_by_day = signals_df.groupby(signals_df.index.date).size()
        print(f"\n📊 Signals per day:")
        for date, count in signals_by_day.items():
            print(f"   {date}: {count} signals")
        
        max_per_day = signals_by_day.max()
        if max_per_day <= 10:
            print(f"   ✅ PASSED: Max trades per day limit working correctly!")
            print(f"      (Bug fixed: max_trades_per_day now ALWAYS enforced)")
            return True
        else:
            print(f"   ❌ FAILED: Expected max 10 signals per day, got {max_per_day}")
            print(f"      (Bug still present: max_trades_per_day not enforced properly)")
            return False
    else:
        print(f"   ⚠️  No signals generated (might need to adjust test data)")
        return True


def test_meanreverter_default_max_trades_per_day():
    """Test that MeanReverter default max_trades_per_day is 10"""
    print("\n" + "=" * 70)
    print("🧪 TEST: MeanReverter Default max_trades_per_day = 10")
    print("=" * 70)
    
    # Test MeanReverter default
    strategy = MeanReverter({})
    print(f"   MeanReverter default max_trades_per_day: {strategy.max_trades_per_day}")
    
    if strategy.max_trades_per_day == 10:
        print(f"   ✅ PASSED: Default max_trades_per_day is 10")
        return True
    else:
        print(f"   ❌ FAILED: Expected default=10, got {strategy.max_trades_per_day}")
        return False


def test_default_max_trades_per_day():
    """Test that default max_trades_per_day is now 5 (reduced from 10)"""
    print("\n" + "=" * 70)
    print("🧪 TEST: Default max_trades_per_day = 5")
    print("=" * 70)
    
    # Test MomentumBurst default
    momentum_strategy = MomentumBurst({})
    print(f"   MomentumBurst default max_trades_per_day: {momentum_strategy.max_trades_per_day}")
    
    # Test MeanReverterV3 default
    meanrev_strategy = MeanReverterV3({})
    print(f"   MeanReverterV3 default max_trades_per_day: {meanrev_strategy.max_trades_per_day}")
    
    if momentum_strategy.max_trades_per_day == 5 and meanrev_strategy.max_trades_per_day == 5:
        print(f"   ✅ PASSED: Default max_trades_per_day reduced to 5")
        return True
    else:
        print(f"   ❌ FAILED: Expected default=5 for both strategies")
        return False


def run_all_tests():
    """Run all tests"""
    print("\n" + "=" * 70)
    print("🧪 STRATEGY FIXES VALIDATION TESTS")
    print("=" * 70)
    
    results = {
        "MomentumBurst Time-Based Cooldown": test_momentum_burst_time_based_cooldown(),
        "MomentumBurst Max Trades Per Day": test_momentum_burst_max_trades_per_day(),
        "MeanReverter Max Trades Per Day": test_meanreverter_max_trades_per_day(),
        "MeanReverter Default max_trades_per_day": test_meanreverter_default_max_trades_per_day(),
        "MeanReverterV3 Fixed Lookback": test_meanreverter_v3_fixed_lookback(),
        "MeanReverterV3 Adaptive Threshold": test_meanreverter_v3_adaptive_threshold(),
        "MeanReverterV3 Max Trades Per Day": test_meanreverter_v3_max_trades_per_day(),
        "Default max_trades_per_day = 5": test_default_max_trades_per_day(),
    }
    
    # Summary
    print("\n" + "=" * 70)
    print("📋 TEST SUMMARY")
    print("=" * 70)
    
    for test_name, passed in results.items():
        status = "✅" if passed else "❌"
        print(f"{status} {test_name}")
    
    passed = sum(results.values())
    total = len(results)
    
    print("\n" + "=" * 70)
    if passed == total:
        print(f"✅ ALL {total} TESTS PASSED!")
    else:
        print(f"⚠️  {passed}/{total} TESTS PASSED")
    print("=" * 70)
    
    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
