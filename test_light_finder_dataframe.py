#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Integration test demonstrating light_finder.py DataFrame support

This test simulates the batch processing workflow:
1. Create a DataFrame with batch results (like from backtest_batch.py)
2. Use LightFinder to rank strategies
3. Verify the output
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from light_finder import LightFinder


def create_mock_batch_results():
    """
    Create a DataFrame that simulates the output from backtest_batch.py
    
    This matches the format from batch processing with columns:
    strategy_name, lot_size, sharpe_ratio, sortino_ratio, calmar_ratio,
    total_return, max_drawdown, win_rate, n_trades, profit_factor,
    avg_win, avg_loss, expectancy, gross_pnl, net_pnl, total_commission
    """
    np.random.seed(42)
    
    # Create sample strategies with varying performance
    strategies = [
        "MACD_Cross_20_50_9",
        "RSI_Oversold_30",
        "BB_Breakout_20_2",
        "EMA_Cross_12_26",
        "Stochastic_14_3_3",
        "ADX_Trend_14_25",
        "Ichimoku_Cloud_9_26_52",
        "CCI_Reversal_20_100",
        "Williams_R_14_20",
        "PSAR_0.02_0.2"
    ]
    
    data = []
    
    for strategy in strategies:
        # Each strategy tested with 3 different lot sizes
        for lot_size in [0.01, 0.1, 1.0]:
            # Generate realistic metrics
            base_return = np.random.uniform(0.05, 0.50)
            
            # Larger lot sizes may have slightly different metrics due to slippage
            lot_multiplier = 1.0 - (lot_size * 0.02)  # Small degradation for larger lots
            
            data.append({
                'strategy_name': strategy,
                'lot_size': lot_size,
                'sharpe_ratio': np.random.uniform(0.5, 2.5) * lot_multiplier,
                'sortino_ratio': np.random.uniform(0.8, 3.0) * lot_multiplier,
                'calmar_ratio': np.random.uniform(0.5, 3.5) * lot_multiplier,
                'total_return': base_return * lot_multiplier,
                'max_drawdown': np.random.uniform(0.08, 0.25),
                'win_rate': np.random.uniform(0.45, 0.70),
                'n_trades': np.random.randint(40, 120),
                'profit_factor': np.random.uniform(1.1, 2.3),
                'avg_win': np.random.uniform(0.002, 0.006),
                'avg_loss': np.random.uniform(-0.005, -0.001),
                'expectancy': np.random.uniform(0.0001, 0.003),
                'gross_pnl': base_return * 10000 * lot_size,
                'net_pnl': base_return * 10000 * lot_size * 0.95,  # After commissions
                'total_commission': base_return * 10000 * lot_size * 0.05,
            })
    
    return pd.DataFrame(data)


def main():
    """Run the integration test"""
    print("=" * 70)
    print("🌟 LIGHT FINDER - DataFrame Integration Test")
    print("=" * 70)
    
    # Step 1: Create mock batch results
    print("\n📊 Creating mock batch results...")
    results_df = create_mock_batch_results()
    print(f"   ✅ Created {len(results_df)} backtest results")
    print(f"   ✅ {results_df['strategy_name'].nunique()} unique strategies")
    print(f"   ✅ {len(results_df['lot_size'].unique())} lot sizes per strategy")
    
    print(f"\n📋 Sample data:")
    print(results_df.head(10).to_string(index=False))
    
    # Step 2: Initialize LightFinder
    print(f"\n⚡ Initializing LightFinder...")
    finder = LightFinder()
    
    # Step 3: Rank strategies using DataFrame input
    print(f"\n🎯 Ranking strategies from DataFrame...")
    ranked_strategies = finder.rank_strategies(results_df, top_n=10)
    
    # Step 4: Display results
    print(f"\n" + "=" * 70)
    print("📊 RANKING RESULTS")
    print("=" * 70)
    
    print(f"\n🏆 Top 10 Strategies (from DataFrame input):\n")
    
    display_cols = [
        'rank', 'strategy_name', 'composite_score', 
        'total_return', 'sharpe_ratio', 'max_drawdown', 'win_rate'
    ]
    
    for _, row in ranked_strategies[display_cols].iterrows():
        print(f"   #{row['rank']:2d} {row['strategy_name']:30s}")
        print(f"       Composite Score: {row['composite_score']:6.3f}")
        print(f"       Return: {row['total_return']:6.1%} | "
              f"Sharpe: {row['sharpe_ratio']:5.2f} | "
              f"Max DD: {row['max_drawdown']:5.1%} | "
              f"Win Rate: {row['win_rate']:5.1%}")
        print()
    
    # Step 5: Verify the output
    print("=" * 70)
    print("✅ VERIFICATION")
    print("=" * 70)
    
    # Check that we got results
    assert len(ranked_strategies) > 0, "No ranked strategies returned!"
    
    # Check required columns exist
    required_cols = ['rank', 'strategy_name', 'composite_score', 'total_return', 'sharpe_ratio']
    for col in required_cols:
        assert col in ranked_strategies.columns, f"Missing column: {col}"
    
    # Check ranking is in descending order
    assert ranked_strategies['composite_score'].is_monotonic_decreasing, \
        "Strategies not ranked in descending order!"
    
    # Check ranks are sequential
    assert list(ranked_strategies['rank']) == list(range(1, len(ranked_strategies) + 1)), \
        "Ranks are not sequential!"
    
    print("\n✅ All verification checks passed!")
    print("✅ DataFrame input format works correctly!")
    print("✅ LightFinder successfully ranks strategies from batch results!")
    
    print(f"\n" + "=" * 70)
    print("🎉 Integration test PASSED!")
    print("=" * 70)
    
    return ranked_strategies


if __name__ == "__main__":
    ranked = main()
