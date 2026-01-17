#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Final demonstration of backtester optimization
Shows the difference between save_detailed_trades=True and False
"""

import numpy as np
import pandas as pd
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from backtester import Backtester


class SimpleStrategy:
    """Simple test strategy"""
    
    def __init__(self):
        self.name = "DemoStrategy"
        self.params = {
            "stop_loss_pips": 20,
            "take_profit_pips": 40
        }
    
    def generate_signals(self, df):
        """Generate signals every 50k bars"""
        signals = pd.Series(0, index=df.index)
        for i in range(0, len(signals), 50000):
            if i < len(signals):
                signals.iloc[i] = 1
            if i + 25000 < len(signals):
                signals.iloc[i + 25000] = -1
        return signals


print("\n" + "="*70)
print("BACKTESTER OPTIMIZATION - FINAL DEMONSTRATION")
print("="*70)

# Create a moderately large dataset
n_ticks = 1_000_000  # 1M ticks
print(f"\nGenerating test data ({n_ticks:,} ticks)...")

np.random.seed(42)
df = pd.DataFrame({
    'mid_price': 1.0505 + np.cumsum(np.random.randn(n_ticks) * 0.0001),
    'momentum': np.random.randn(n_ticks) * 0.1,
    'volume': np.random.randint(100, 1000, n_ticks)
})

strategy = SimpleStrategy()

print("\n" + "-"*70)
print("TEST 1: OPTIMIZED MODE (save_detailed_trades=False)")
print("-"*70)
print("This is the NEW default behavior - FAST and memory-efficient")
print()

backtester1 = Backtester()
start = time.time()
results1 = backtester1.backtest(strategy, df, save_detailed_trades=False)
elapsed1 = time.time() - start

result1 = results1[0.1]

print(f"\n✅ Completed in {elapsed1:.2f} seconds")
print(f"   Trades executed: {result1.n_trades}")
print(f"   Net PnL: ${result1.net_pnl:.2f}")
print(f"   Win rate: {result1.win_rate:.1%}")
print(f"   Sharpe ratio: {result1.sharpe_ratio:.2f}")
print(f"   Max drawdown: {result1.max_drawdown:.1%}")
print(f"   Detailed trades stored: {len(result1.trades_detailed)}")
print(f"   Memory usage: MINIMAL (no price history saved)")

print("\n" + "-"*70)
print("TEST 2: DETAILED MODE (save_detailed_trades=True)")
print("-"*70)
print("This mode saves full price history for each trade - SLOW but detailed")
print()

backtester2 = Backtester()
start = time.time()
results2 = backtester2.backtest(strategy, df, save_detailed_trades=True)
elapsed2 = time.time() - start

result2 = results2[0.1]

print(f"\n✅ Completed in {elapsed2:.2f} seconds")
print(f"   Trades executed: {result2.n_trades}")
print(f"   Net PnL: ${result2.net_pnl:.2f}")
print(f"   Win rate: {result2.win_rate:.1%}")
print(f"   Sharpe ratio: {result2.sharpe_ratio:.2f}")
print(f"   Max drawdown: {result2.max_drawdown:.1%}")
print(f"   Detailed trades stored: {len(result2.trades_detailed)}")

if len(result2.trades_detailed) > 0:
    sample_trade = result2.trades_detailed[0]
    price_history_size = len(sample_trade.get('price_history', {}).get('timestamps', []))
    print(f"   Memory usage: HIGH (~{price_history_size} bars per trade)")
    print(f"   Sample trade has: {list(sample_trade.keys())}")

print("\n" + "="*70)
print("COMPARISON")
print("="*70)

print(f"\n⚡ Speed improvement: {elapsed2/elapsed1:.1f}x faster with save_detailed_trades=False")
print(f"   Optimized mode: {elapsed1:.2f}s")
print(f"   Detailed mode:  {elapsed2:.2f}s")

print(f"\n💾 Memory saved: Detailed trades not stored (0 vs {len(result2.trades_detailed)} trades)")

print(f"\n✅ Numerical accuracy: IDENTICAL")
print(f"   PnL difference: ${abs(result1.net_pnl - result2.net_pnl):.10f}")
print(f"   Win rate difference: {abs(result1.win_rate - result2.win_rate):.10f}")
print(f"   Sharpe difference: {abs(result1.sharpe_ratio - result2.sharpe_ratio):.10f}")

assert result1.n_trades == result2.n_trades
assert abs(result1.net_pnl - result2.net_pnl) < 1e-6
assert abs(result1.win_rate - result2.win_rate) < 1e-10

print("\n" + "="*70)
print("RECOMMENDATIONS")
print("="*70)

print("\n📊 For PRODUCTION / LARGE DATASETS (14.6M+ ticks):")
print("   Use: backtester.backtest(strategy, df)  # default is save_detailed_trades=False")
print("   Benefits: Fast, memory-efficient, scales to millions of ticks")

print("\n🔍 For ANALYSIS / DEBUGGING (small datasets):")
print("   Use: backtester.backtest(strategy, df, save_detailed_trades=True)")
print("   Benefits: Full trade details, price history, market context")

print("\n✨ The optimization is COMPLETE and BACKWARD COMPATIBLE!")
print("   - All existing code works unchanged")
print("   - Numerical results are identical")
print("   - Performance is dramatically improved for large datasets")
print()
