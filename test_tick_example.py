#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test the example from the problem statement
"""

import numpy as np
import pandas as pd
from backtester import Backtester


# Create a simple strategy for testing
class TestStrategy:
    def __init__(self):
        self.name = "TestStrategy"
        self.params = {
            "stop_loss_pips": 20,
            "take_profit_pips": 40
        }
    
    def generate_signals(self, df):
        """Simple momentum strategy"""
        signals = pd.Series(0, index=df.index)
        
        # Buy when momentum is positive
        signals[df['momentum'] > 0.5] = 1
        
        # Sell when momentum is negative
        signals[df['momentum'] < -0.5] = -1
        
        return signals


# Generate test data with tick structure
np.random.seed(42)
n = 1000

# Simulate tick data
mid_prices = 1.0500 + np.cumsum(np.random.randn(n) * 0.0001)
spread = 0.00008  # 0.8 pips

df = pd.DataFrame({
    'timestamp': pd.date_range('2025-01-01', periods=n, freq='1min'),
    'bid': mid_prices - spread/2,
    'ask': mid_prices + spread/2,
    'mid_price': mid_prices,
    'spread_pips': np.ones(n) * 0.8,
    'pips_change': np.diff(mid_prices, prepend=mid_prices[0]) / 0.0001,
})

# Add features
df['momentum'] = df['pips_change'].rolling(100, min_periods=1).sum()
df['volatility'] = df['pips_change'].rolling(100, min_periods=1).std().fillna(0)
df['trend_strength'] = df['momentum'].abs() / (df['volatility'] + 1e-10)
df['close'] = df['mid_price']

df = df.set_index('timestamp')

# Create strategy
strategy = TestStrategy()

# Run backtest
backtester = Backtester()
results = backtester.backtest(strategy, df)

# Display results for each lot size
print("\n" + "="*80)
print("TICK DATA BACKTESTER TEST RESULTS")
print("="*80)

for lot_size, result in results.items():
    print(f"\n{'='*80}")
    print(f"LOT SIZE: {lot_size}")
    print(f"{'='*80}")
    print(f"  Trades:            {result.n_trades}")
    print(f"  Win Rate:          {result.win_rate:.1%}")
    print(f"  Gross PnL:         ${result.gross_pnl:.2f}")
    print(f"  Total Commission:  ${result.total_commission:.2f}")
    print(f"  Net PnL:           ${result.net_pnl:.2f}")
    print(f"  Profit Factor:     {result.profit_factor:.2f}")
    print(f"  Sharpe Ratio:      {result.sharpe_ratio:.2f}")
    print(f"  Max Drawdown:      {result.max_drawdown:.2%}")
    print(f"  Total Return:      {result.total_return:.2%}")

print("\n" + "="*80)
print("✅ Test complete!")
print("="*80)
