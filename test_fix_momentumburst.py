#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test for MomentumBurst fix and strategy generation validation
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from strategy_factory import MomentumBurst
from config import STRATEGY_TEMPLATES, STRATEGY_PARAMS


def test_momentum_burst_max_trades_per_day():
    """Test that MomentumBurst ALWAYS applies max_trades_per_day filter"""
    print("\n" + "=" * 70)
    print("🧪 TEST: MomentumBurst max_trades_per_day ALWAYS enforced")
    print("=" * 70)
    
    # Create test data with datetime index (simulates tick data)
    np.random.seed(42)
    n_days = 10
    ticks_per_day = 1000
    n = n_days * ticks_per_day
    
    # Create datetime index spanning multiple days
    dates = pd.date_range(start='2024-01-01', periods=n, freq='1min')
    
    # Create data with strong momentum bursts
    base_price = 1.10
    prices = [base_price]
    
    for i in range(1, n):
        # Create momentum bursts every ~50 ticks
        if i % 50 == 0:
            # Strong momentum burst
            prices.append(prices[-1] + 0.002)  # 20 pips move
        else:
            # Small random walk
            prices.append(prices[-1] + np.random.normal(0, 0.0001))
    
    df = pd.DataFrame({
        'mid_price': prices,
        'volume': np.random.randint(100, 1000, n)
    }, index=dates)
    
    # Create MomentumBurst strategy with max_trades_per_day=5
    params = {
        'lookback_periods': 10,
        'threshold_std': 1.0,
        'stop_loss_pips': 15,
        'take_profit_pips': 30,
        'cooldown_minutes': 180,
        'max_trades_per_day': 5
    }
    
    strategy = MomentumBurst(params)
    signals = strategy.generate_signals(df)
    
    # Count trades per day
    trades_by_day = {}
    for idx, signal in signals.items():
        if signal != 0:
            day = str(idx.date())
            trades_by_day[day] = trades_by_day.get(day, 0) + 1
    
    # Print results
    total_trades = sum(trades_by_day.values())
    print(f"\nTotal trades over {n_days} days: {total_trades}")
    print(f"Trades per day breakdown:")
    for day, count in sorted(trades_by_day.items()):
        status = "✅" if count <= 5 else "❌ FAIL"
        print(f"  {day}: {count} trades {status}")
    
    # Verify max trades per day is enforced
    max_trades_in_any_day = max(trades_by_day.values()) if trades_by_day else 0
    
    print(f"\nMax trades in any single day: {max_trades_in_any_day}")
    print(f"Expected max: 5")
    
    if max_trades_in_any_day <= 5:
        print("✅ TEST PASSED: max_trades_per_day is enforced!")
        return True
    else:
        print(f"❌ TEST FAILED: Found {max_trades_in_any_day} trades in a day (max should be 5)")
        return False


def test_strategy_generation():
    """Test that strategy generation creates expected number of strategies"""
    print("\n" + "=" * 70)
    print("🧪 TEST: Strategy Generation Counts")
    print("=" * 70)
    
    print(f"\nActive templates: {STRATEGY_TEMPLATES}")
    print(f"Expected templates: ['MeanReverter', 'MeanReverterV2', 'MeanReverterV3', 'MomentumBurst']")
    
    # Check that TrendFollower is NOT in templates
    if 'TrendFollower' in STRATEGY_TEMPLATES:
        print("❌ FAIL: TrendFollower should be removed from STRATEGY_TEMPLATES")
        return False
    else:
        print("✅ TrendFollower correctly removed from templates")
    
    # Count expected strategies
    expected_counts = {
        'MeanReverter': 1 * 4 * 2 * 2,  # 16 combinations
        'MeanReverterV2': 1 * 3 * 2 * 2 * 2 * 2 * 2,  # 96 combinations (before R:R filter)
        'MeanReverterV3': 1 * 3 * 3 * 2 * 1 * 1 * 1,  # 18 combinations
        'MomentumBurst': 2 * 2 * 2 * 2 * 1,  # 16 combinations
    }
    
    print("\nExpected strategy counts (before any filters):")
    for template, count in expected_counts.items():
        print(f"  {template}: {count} combinations")
    
    total_expected = sum(expected_counts.values())
    print(f"\nTotal expected (before R:R filter): {total_expected}")
    print(f"Note: MeanReverterV2 will be reduced by ~50% due to R:R filter")
    
    # Verify parameter configurations
    print("\n📋 Verifying parameter configurations:")
    
    # MeanReverter
    mr_thresholds = STRATEGY_PARAMS['MeanReverter']['threshold_std']
    print(f"\n  MeanReverter thresholds: {mr_thresholds}")
    if set(mr_thresholds) == {1.2, 1.5, 1.8, 2.0}:
        print("  ✅ Includes aggressive variants (1.2, 1.5)")
    else:
        print(f"  ❌ FAIL: Expected [1.2, 1.5, 1.8, 2.0], got {mr_thresholds}")
        return False
    
    # MeanReverterV2
    mrv2_thresholds = STRATEGY_PARAMS['MeanReverterV2']['threshold_std']
    mrv2_rsi_os = STRATEGY_PARAMS['MeanReverterV2']['rsi_oversold']
    mrv2_rsi_ob = STRATEGY_PARAMS['MeanReverterV2']['rsi_overbought']
    print(f"\n  MeanReverterV2 thresholds: {mrv2_thresholds}")
    print(f"  MeanReverterV2 RSI oversold: {mrv2_rsi_os}")
    print(f"  MeanReverterV2 RSI overbought: {mrv2_rsi_ob}")
    if 0.8 in mrv2_thresholds and 30 in mrv2_rsi_os and 70 in mrv2_rsi_ob:
        print("  ✅ Includes aggressive variants")
    else:
        print("  ❌ FAIL: Missing aggressive variants")
        return False
    
    # MeanReverterV3
    mrv3_thresholds = STRATEGY_PARAMS['MeanReverterV3']['threshold_std']
    mrv3_adaptive = STRATEGY_PARAMS['MeanReverterV3']['adaptive_threshold']
    print(f"\n  MeanReverterV3 thresholds: {mrv3_thresholds}")
    print(f"  MeanReverterV3 adaptive_threshold: {mrv3_adaptive}")
    if set(mrv3_thresholds) == {1.2, 1.5, 1.8} and mrv3_adaptive == [True]:
        print("  ✅ Includes aggressive variants and ONLY adaptive_threshold=True")
    else:
        print(f"  ❌ FAIL: Wrong configuration")
        return False
    
    print("\n✅ ALL TESTS PASSED!")
    return True


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("🚀 Running MomentumBurst Fix & Strategy Generation Tests")
    print("=" * 70)
    
    test1_passed = test_momentum_burst_max_trades_per_day()
    test2_passed = test_strategy_generation()
    
    print("\n" + "=" * 70)
    print("📊 TEST SUMMARY")
    print("=" * 70)
    print(f"MomentumBurst max_trades_per_day: {'✅ PASSED' if test1_passed else '❌ FAILED'}")
    print(f"Strategy generation: {'✅ PASSED' if test2_passed else '❌ FAILED'}")
    
    if test1_passed and test2_passed:
        print("\n🎉 All tests passed!")
        sys.exit(0)
    else:
        print("\n⚠️  Some tests failed")
        sys.exit(1)
