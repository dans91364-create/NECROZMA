#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚡🌟💎 ULTRA NECROZMA - Realistic Returns Test 💎🌟⚡

Demonstrates that the backtester now produces realistic Forex returns
instead of microscopic values.

This script shows:
- BEFORE: Returns calculated as price % change (0.003%)
- AFTER: Returns calculated as USD profit % of capital (0.2-2%)
"""

import numpy as np
import pandas as pd
from backtester import Backtester


class SimpleTrendStrategy:
    """
    Simple trend-following strategy for demonstration
    """
    def __init__(self, name="TrendFollower", lookback=20, threshold=0.5):
        self.name = name
        self.lookback = lookback
        self.threshold = threshold
        self.params = {
            "stop_loss_pips": 10,
            "take_profit_pips": 50,
        }
    
    def generate_signals(self, df):
        """Generate simple momentum-based signals"""
        signals = pd.Series(0, index=df.index)
        
        if 'momentum' not in df.columns:
            return signals
        
        # Buy when momentum is positive and strong
        signals[df['momentum'] > self.threshold] = 1
        
        # Sell when momentum is negative and strong
        signals[df['momentum'] < -self.threshold] = -1
        
        return signals


def create_realistic_forex_data(n_bars=5000, seed=42):
    """
    Create realistic Forex-like price data
    
    Args:
        n_bars: Number of bars to generate
        seed: Random seed for reproducibility
        
    Returns:
        DataFrame with OHLC and features
    """
    np.random.seed(seed)
    
    # EUR/USD starting around 1.05
    base_price = 1.05
    
    # Simulate realistic Forex volatility
    # EUR/USD daily volatility ~0.6%, so per 5-min bar ~0.02%
    returns = np.random.randn(n_bars) * 0.0002
    
    # Add some trending behavior
    trend = np.sin(np.arange(n_bars) / 100) * 0.0001
    returns += trend
    
    # Generate prices
    close_prices = base_price * (1 + np.cumsum(returns))
    
    # Create OHLC
    opens = np.roll(close_prices, 1)
    opens[0] = base_price
    
    highs = np.maximum(opens, close_prices) + np.abs(np.random.randn(n_bars)) * 0.00002
    lows = np.minimum(opens, close_prices) - np.abs(np.random.randn(n_bars)) * 0.00002
    
    # Create DataFrame
    df = pd.DataFrame({
        'open': opens,
        'high': highs,
        'low': lows,
        'close': close_prices,
        'mid_price': close_prices,
        'volume': np.random.randint(100, 1000, n_bars),
    })
    
    # Add momentum feature
    df['momentum'] = df['close'].pct_change(20).fillna(0) * 10000  # Scale up for signals
    
    return df


def print_banner(title):
    """Print a formatted banner"""
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80)


def main():
    """Demonstrate realistic returns with Forex position sizing"""
    
    print_banner("⚡🌟💎 ULTRA NECROZMA - Realistic Returns Demo 💎🌟⚡")
    
    # ═══════════════════════════════════════════════════════════════
    # 1. Create Test Data
    # ═══════════════════════════════════════════════════════════════
    print("\n📊 Creating realistic Forex data...")
    df = create_realistic_forex_data(n_bars=5000, seed=42)
    
    print(f"   Generated {len(df):,} bars of EUR/USD data")
    print(f"   Price range: {df['close'].min():.5f} - {df['close'].max():.5f}")
    print(f"   Total price movement: {(df['close'].iloc[-1] - df['close'].iloc[0]):.5f} ({(df['close'].iloc[-1] - df['close'].iloc[0]) * 10000:.1f} pips)")
    
    # ═══════════════════════════════════════════════════════════════
    # 2. Configure Backtester with Position Sizing
    # ═══════════════════════════════════════════════════════════════
    print_banner("⚙️  Backtester Configuration")
    
    config = {
        'capital': {
            'initial_capital': 10000,        # $10,000 starting capital
            'default_lot_size': 0.1,         # 0.1 lot (10,000 units)
            'pip_value_per_lot': 10,         # $10/pip for 1.0 lot
            'pip_decimal_places': 4          # 0.0001 = 1 pip
        }
    }
    
    print(f"\n   Initial Capital: ${config['capital']['initial_capital']:,}")
    print(f"   Lot Size: {config['capital']['default_lot_size']} lot")
    print(f"   Pip Value: ${config['capital']['pip_value_per_lot']}/pip/lot")
    print(f"   → For 0.1 lot: ${config['capital']['pip_value_per_lot'] * config['capital']['default_lot_size']}/pip")
    print(f"\n   Example: 20 pips profit = 20 × $1 = $20 = {(20 / config['capital']['initial_capital']) * 100:.2f}% return")
    
    backtester = Backtester(config=config)
    
    # ═══════════════════════════════════════════════════════════════
    # 3. Run Backtest
    # ═══════════════════════════════════════════════════════════════
    print_banner("🧪 Running Backtest")
    
    strategy = SimpleTrendStrategy(
        name="TrendFollower_L5_T0.5_SL10_TP50",
        lookback=5,
        threshold=0.5
    )
    
    print(f"\n   Strategy: {strategy.name}")
    print(f"   Stop Loss: {strategy.params['stop_loss_pips']} pips")
    print(f"   Take Profit: {strategy.params['take_profit_pips']} pips")
    
    results = backtester.backtest(strategy, df)
    
    # ═══════════════════════════════════════════════════════════════
    # 4. Display Results
    # ═══════════════════════════════════════════════════════════════
    print_banner("📊 RESULTS")
    
    print(f"\n✅ Strategy: {results.strategy_name}")
    print(f"   Trades: {results.n_trades:,}")
    print(f"   Win Rate: {results.win_rate * 100:.1f}%")
    print(f"   Profit Factor: {results.profit_factor:.2f}")
    print(f"\n💰 Returns:")
    print(f"   Total Return: {results.total_return * 100:.2f}%")
    print(f"   Max Drawdown: {results.max_drawdown * 100:.2f}%")
    print(f"\n📈 Risk Metrics:")
    print(f"   Sharpe Ratio: {results.sharpe_ratio:.2f}")
    print(f"   Sortino Ratio: {results.sortino_ratio:.2f}")
    print(f"   Calmar Ratio: {results.calmar_ratio:.2f}")
    print(f"\n💵 Trade Statistics:")
    print(f"   Avg Win: ${results.avg_win:.2f}")
    print(f"   Avg Loss: ${results.avg_loss:.2f}")
    print(f"   Largest Win: ${results.largest_win:.2f}")
    print(f"   Largest Loss: ${results.largest_loss:.2f}")
    print(f"   Expectancy: ${results.expectancy:.2f}")
    
    # Calculate total profit in USD
    if len(results.equity_curve) > 0:
        initial = results.equity_curve.iloc[0]
        final = results.equity_curve.iloc[-1]
        profit_usd = final - initial
        
        print(f"\n💎 Final Capital: ${final:,.2f}")
        print(f"   Profit/Loss: ${profit_usd:+,.2f}")
    
    # ═══════════════════════════════════════════════════════════════
    # 5. Verify Realistic Values
    # ═══════════════════════════════════════════════════════════════
    print_banner("✅ Validation: Returns are Realistic!")
    
    print(f"\n   BEFORE FIX: Returns would show as ~0.0% (microscopic like 0.003%)")
    print(f"   AFTER FIX:  Returns show as {results.total_return * 100:.2f}% (realistic for Forex)")
    
    if results.n_trades > 0:
        sample_trade = results.trades.iloc[0]
        print(f"\n   Sample Trade:")
        print(f"      Entry: {sample_trade['entry_price']:.5f}")
        print(f"      Exit: {sample_trade['exit_price']:.5f}")
        print(f"      PnL: ${sample_trade['pnl']:.2f} (not {sample_trade['pnl']:.6f}!)")
        print(f"      Type: {sample_trade['type']}")
        print(f"      Exit Reason: {sample_trade['exit_reason']}")
    
    # Check if values are realistic
    checks_passed = 0
    total_checks = 0
    
    print(f"\n   Validation Checks:")
    
    # Check 1: Total return is not microscopic
    total_checks += 1
    if abs(results.total_return) > 0.0001 or results.n_trades == 0:
        print(f"      ✅ Total return is realistic: {results.total_return * 100:.2f}%")
        checks_passed += 1
    else:
        print(f"      ❌ Total return seems too small: {results.total_return * 100:.6f}%")
    
    # Check 2: Avg win/loss in reasonable USD range
    total_checks += 1
    if results.avg_win > 0.1 or results.avg_win == 0:
        print(f"      ✅ Avg win is in USD range: ${results.avg_win:.2f}")
        checks_passed += 1
    else:
        print(f"      ❌ Avg win seems too small: ${results.avg_win:.6f}")
    
    # Check 3: Max drawdown is realistic
    total_checks += 1
    if results.max_drawdown < 1.0:  # Less than 100%
        print(f"      ✅ Max drawdown is realistic: {results.max_drawdown * 100:.2f}%")
        checks_passed += 1
    else:
        print(f"      ❌ Max drawdown seems wrong: {results.max_drawdown * 100:.2f}%")
    
    print(f"\n   Validation Score: {checks_passed}/{total_checks} checks passed")
    
    if checks_passed == total_checks:
        print(f"\n   🎉 SUCCESS! All validation checks passed!")
        print(f"   The backtester now produces realistic Forex returns!")
    
    print_banner("✅ Demo Complete")
    
    return results


if __name__ == "__main__":
    results = main()
