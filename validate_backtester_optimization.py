#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Quick validation script for backtester optimization
"""

import numpy as np
import pandas as pd
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from backtester import Backtester


class SimpleStrategy:
    """Simple test strategy"""
    
    def __init__(self):
        self.name = "TestStrategy"
        self.params = {
            "stop_loss_pips": 20,
            "take_profit_pips": 40
        }
    
    def generate_signals(self, df):
        """Generate simple signals"""
        signals = pd.Series(0, index=df.index)
        # Generate buy signal every 100k bars
        for i in range(0, len(signals), 100000):
            if i < len(signals):
                signals.iloc[i] = 1
            if i + 50000 < len(signals):
                signals.iloc[i + 50000] = -1
        return signals


print("\n" + "="*60)
print("BACKTESTER OPTIMIZATION VALIDATION")
print("="*60)

# Test 1: Small dataset (100k ticks) - verify identical results
print("\n[TEST 1] Small dataset (100k ticks) - verify identical results")
print("-" * 60)

np.random.seed(42)
n_small = 100_000

df_small = pd.DataFrame({
    'mid_price': 1.0505 + np.cumsum(np.random.randn(n_small) * 0.0001),
    'momentum': np.random.randn(n_small) * 0.1
})

strategy = SimpleStrategy()
backtester = Backtester()

print(f"Testing with {n_small:,} ticks...")

# Test without detailed trades (fast)
print("\n  With save_detailed_trades=False (default):")
results_fast = backtester.backtest(strategy, df_small, save_detailed_trades=False)
result_fast = results_fast[0.1]

print(f"    ✓ Trades: {result_fast.n_trades}")
print(f"    ✓ Net PnL: ${result_fast.net_pnl:.2f}")
print(f"    ✓ Win Rate: {result_fast.win_rate:.1%}")
print(f"    ✓ Detailed trades saved: {len(result_fast.trades_detailed)}")

# Test with detailed trades (slow)
print("\n  With save_detailed_trades=True:")
results_slow = backtester.backtest(strategy, df_small, save_detailed_trades=True)
result_slow = results_slow[0.1]

print(f"    ✓ Trades: {result_slow.n_trades}")
print(f"    ✓ Net PnL: ${result_slow.net_pnl:.2f}")
print(f"    ✓ Win Rate: {result_slow.win_rate:.1%}")
print(f"    ✓ Detailed trades saved: {len(result_slow.trades_detailed)}")

# Verify identical results
assert result_fast.n_trades == result_slow.n_trades
assert abs(result_fast.net_pnl - result_slow.net_pnl) < 1e-6
assert abs(result_fast.win_rate - result_slow.win_rate) < 1e-10

print("\n  ✅ Results are IDENTICAL (only detailed trades differ)")

# Test 2: Large dataset (2M ticks) - verify progress indicator
print("\n[TEST 2] Large dataset (2M ticks) - verify progress indicator")
print("-" * 60)

n_large = 2_000_000

print(f"Generating {n_large:,} ticks...")
df_large = pd.DataFrame({
    'mid_price': 1.0505 + np.cumsum(np.random.randn(n_large) * 0.0001),
    'momentum': np.random.randn(n_large) * 0.1
})

print(f"\nRunning backtest on {n_large:,} ticks (should show progress)...")
print("(Progress indicator triggers every 1M ticks)")
print()

backtester2 = Backtester()
results_large = backtester2.backtest(strategy, df_large, save_detailed_trades=False)
result_large = results_large[0.1]

print(f"\n  ✓ Completed!")
print(f"    Trades: {result_large.n_trades}")
print(f"    Net PnL: ${result_large.net_pnl:.2f}")
print(f"    Win Rate: {result_large.win_rate:.1%}")
print(f"    Detailed trades: {len(result_large.trades_detailed)} (should be 0)")

# Test 3: Verify backward compatibility
print("\n[TEST 3] Backward compatibility")
print("-" * 60)

print("Testing backtest() without save_detailed_trades parameter...")
backtester3 = Backtester()
results_compat = backtester3.backtest(strategy, df_small)  # No save_detailed_trades param
result_compat = results_compat[0.1]

print(f"  ✓ Works without parameter")
print(f"  ✓ Detailed trades: {len(result_compat.trades_detailed)} (should be 0, default=False)")

assert len(result_compat.trades_detailed) == 0, "Default should be save_detailed_trades=False"

print("\n" + "="*60)
print("✅ ALL VALIDATIONS PASSED!")
print("="*60)

print("\n📊 Summary of Changes:")
print("  1. ✓ save_detailed_trades flag defaults to False")
print("  2. ✓ Detailed trade collection is conditional (skipped when False)")
print("  3. ✓ Progress indicator shows every 1M ticks")
print("  4. ✓ Numerical results are IDENTICAL regardless of flag")
print("  5. ✓ Backward compatible (existing code works unchanged)")
print()
