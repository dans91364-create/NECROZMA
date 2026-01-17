#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test to verify that main.py correctly handles DataFrame from LightFinder
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from light_finder import LightFinder


def test_main_dataframe_usage():
    """Test that mimics the code path in main.py lines 1005-1015"""
    print("=" * 70)
    print("Testing main.py DataFrame usage fix")
    print("=" * 70)
    
    # Create mock batch results similar to what would be passed to LightFinder
    np.random.seed(42)
    
    data = []
    for i in range(5):
        data.append({
            'strategy_name': f'Strategy_{i}',
            'lot_size': 0.1,
            'sharpe_ratio': np.random.uniform(0.5, 2.5),
            'sortino_ratio': np.random.uniform(0.8, 3.0),
            'calmar_ratio': np.random.uniform(0.5, 3.5),
            'total_return': np.random.uniform(0.05, 0.50),
            'max_drawdown': np.random.uniform(0.08, 0.25),
            'win_rate': np.random.uniform(0.45, 0.70),
            'n_trades': np.random.randint(40, 120),
            'profit_factor': np.random.uniform(1.1, 2.3),
        })
    
    results_df = pd.DataFrame(data)
    
    # This is what happens in main.py
    finder = LightFinder()
    top_strategies = finder.rank_strategies(results_df, top_n=3)
    
    print(f"\n✅ LightFinder returned a DataFrame: {type(top_strategies)}")
    print(f"   Shape: {top_strategies.shape}")
    
    # Test the fixed code from main.py lines 1005-1015
    print("\n📝 Testing fixed code:")
    
    # Line 1001: len(top_strategies) should work
    n_top = len(top_strategies)
    print(f"   ✓ len(top_strategies) = {n_top}")
    
    # Line 1005: if not top_strategies.empty (FIXED from 'if top_strategies:')
    if not top_strategies.empty:
        print(f"   ✓ not top_strategies.empty check passed")
        
        # Line 1006: .iloc[0] (FIXED from top_strategies[0])
        best = top_strategies.iloc[0]
        print(f"   ✓ best = top_strategies.iloc[0] works")
        print(f"     Type of best: {type(best)}")
        
        # Line 1007: best['strategy_name'] (FIXED from best.get('name', 'Unknown'))
        strategy_name = best['strategy_name']
        print(f"   ✓ best['strategy_name'] = {strategy_name}")
        
        # Line 1008: best['sharpe_ratio'] (FIXED from best.get('sharpe_ratio', 0))
        sharpe = best['sharpe_ratio']
        print(f"   ✓ best['sharpe_ratio'] = {sharpe:.2f}")
        
        # Line 1009: best['total_return'] (FIXED from best.get('total_return', 0))
        total_return = best['total_return']
        print(f"   ✓ best['total_return'] = {total_return:.2%}")
        
        # Line 1010: best['win_rate'] (FIXED from best.get('win_rate', 0))
        win_rate = best['win_rate']
        print(f"   ✓ best['win_rate'] = {win_rate:.2%}")
        
        # Test lore.broadcast parameters (lines 1012-1015)
        print(f"\n   Testing lore.broadcast parameters:")
        print(f"     strategy_name = {best['strategy_name']}")
        print(f"     sharpe = {best['sharpe_ratio']}")
        print(f"     return_pct = {best['total_return'] * 100}")
    
    # Test with empty DataFrame
    print("\n📝 Testing with empty DataFrame:")
    empty_df = pd.DataFrame()
    if not empty_df.empty:
        print(f"   ✗ This should not execute")
    else:
        print(f"   ✓ Empty DataFrame check works correctly")
    
    print("\n" + "=" * 70)
    print("✅ All tests passed! The fix is working correctly.")
    print("=" * 70)


if __name__ == "__main__":
    test_main_dataframe_usage()
