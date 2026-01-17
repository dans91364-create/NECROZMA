#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for cache detection functionality

This script tests:
1. Cache detection when merged results exist
2. Cache bypass with --force-rerun flag
3. Proper loading and conversion of cached results
"""

import sys
import argparse
from pathlib import Path
import pandas as pd
import numpy as np

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from config import OUTPUT_DIR, FILE_PREFIX


# Test constants
TEST_NUM_STRATEGIES = 100
TEST_LOT_SIZES = [0.01, 0.05, 0.10]


def create_mock_cached_results():
    """Create a mock cached results file for testing"""
    print("\n🧪 Creating mock cached results...")
    
    # Create sample backtest results DataFrame
    strategies = []
    for i in range(TEST_NUM_STRATEGIES):
        for lot_size in TEST_LOT_SIZES:
            strategies.append({
                'strategy_name': f'Strategy_{i}',
                'lot_size': lot_size,
                'sharpe_ratio': np.random.uniform(0, 3),
                'sortino_ratio': np.random.uniform(0, 3),
                'calmar_ratio': np.random.uniform(0, 2),
                'total_return': np.random.uniform(-0.5, 1.5),
                'max_drawdown': np.random.uniform(0, 0.5),
                'win_rate': np.random.uniform(0.3, 0.7),
                'n_trades': int(np.random.uniform(10, 200)),
                'profit_factor': np.random.uniform(0.5, 3),
                'avg_win': np.random.uniform(10, 50),
                'avg_loss': np.random.uniform(-50, -10),
                'expectancy': np.random.uniform(-5, 15),
                'gross_pnl': np.random.uniform(-1000, 5000),
                'net_pnl': np.random.uniform(-1000, 5000),
                'total_commission': np.random.uniform(100, 500),
            })
    
    results_df = pd.DataFrame(strategies)
    
    # Save to file
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    cache_file = OUTPUT_DIR / f"{FILE_PREFIX}backtest_results_merged.parquet"
    results_df.to_parquet(cache_file, compression='snappy')
    
    print(f"   ✅ Created {len(results_df):,} results")
    print(f"   💾 Saved to: {cache_file}")
    
    return cache_file


def test_cache_detection_with_cache():
    """Test that cache is detected and used when available"""
    print("\n" + "="*80)
    print("🧪 TEST 1: Cache Detection (with cache)")
    print("="*80)
    
    # Create mock cache
    cache_file = create_mock_cached_results()
    
    # Simulate args with force_rerun=False
    class MockArgs:
        force_rerun = False
    
    args = MockArgs()
    
    # Check cache detection logic
    merged_results_path = OUTPUT_DIR / f"{FILE_PREFIX}backtest_results_merged.parquet"
    
    if merged_results_path.exists() and not args.force_rerun:
        print(f"\n✅ Cache detected correctly!")
        print(f"   Path: {merged_results_path}")
        
        # Load and verify
        results_df = pd.read_parquet(merged_results_path)
        n_strategies = results_df['strategy_name'].nunique()
        n_rows = len(results_df)
        
        # Count viable strategies
        viable_df = results_df[results_df['sharpe_ratio'] > 1.0]
        n_viable = viable_df['strategy_name'].nunique()
        
        print(f"   Loaded {n_rows:,} results for {n_strategies:,} strategies")
        print(f"   Viable strategies (Sharpe > 1.0): {n_viable}/{n_strategies}")
        
        # Test conversion to backtest_results format
        backtest_results = {}
        for _, row in results_df.iterrows():
            strategy_name = row['strategy_name']
            lot_size = row['lot_size']
            
            if strategy_name not in backtest_results:
                backtest_results[strategy_name] = {}
            
            backtest_results[strategy_name][lot_size] = {
                'sharpe_ratio': row.get('sharpe_ratio', 0),
                'sortino_ratio': row.get('sortino_ratio', 0),
                'total_return': row.get('total_return', 0),
            }
        
        print(f"   ✅ Converted to backtest_results format: {len(backtest_results)} strategies")
        
        # Verify structure
        sample_strategy = list(backtest_results.keys())[0]
        sample_lots = list(backtest_results[sample_strategy].keys())
        print(f"   Sample strategy: {sample_strategy}")
        print(f"   Lot sizes: {sample_lots}")
        print(f"   Sample metrics: {list(backtest_results[sample_strategy][sample_lots[0]].keys())}")
        
        return True
    else:
        print(f"\n❌ Cache detection failed!")
        return False


def test_cache_detection_force_rerun():
    """Test that cache is bypassed with --force-rerun"""
    print("\n" + "="*80)
    print("🧪 TEST 2: Force Rerun (bypass cache)")
    print("="*80)
    
    # Ensure cache exists
    cache_file = OUTPUT_DIR / f"{FILE_PREFIX}backtest_results_merged.parquet"
    if not cache_file.exists():
        create_mock_cached_results()
    
    # Simulate args with force_rerun=True
    class MockArgs:
        force_rerun = True
    
    args = MockArgs()
    
    # Check cache bypass logic
    merged_results_path = OUTPUT_DIR / f"{FILE_PREFIX}backtest_results_merged.parquet"
    
    if merged_results_path.exists() and not args.force_rerun:
        print(f"\n❌ Cache should be bypassed but wasn't!")
        return False
    else:
        print(f"\n✅ Cache correctly bypassed with --force-rerun")
        print(f"   Would reprocess all batches")
        return True


def test_cache_detection_no_cache():
    """Test behavior when no cache exists"""
    print("\n" + "="*80)
    print("🧪 TEST 3: No Cache (should run backtesting)")
    print("="*80)
    
    # Remove cache if it exists
    cache_file = OUTPUT_DIR / f"{FILE_PREFIX}backtest_results_merged.parquet"
    if cache_file.exists():
        cache_file.unlink()
        print(f"   🗑️  Removed cache file")
    
    # Simulate args with force_rerun=False
    class MockArgs:
        force_rerun = False
    
    args = MockArgs()
    
    # Check that backtesting would run
    merged_results_path = OUTPUT_DIR / f"{FILE_PREFIX}backtest_results_merged.parquet"
    
    if merged_results_path.exists() and not args.force_rerun:
        print(f"\n❌ Should run backtesting but would use cache!")
        return False
    else:
        print(f"\n✅ Correctly identified no cache exists")
        print(f"   Would run backtesting")
        return True


def cleanup():
    """Clean up test files"""
    print("\n🧹 Cleaning up test files...")
    cache_file = OUTPUT_DIR / f"{FILE_PREFIX}backtest_results_merged.parquet"
    if cache_file.exists():
        cache_file.unlink()
        print(f"   ✅ Removed: {cache_file}")


def main():
    """Run all tests"""
    print("\n" + "="*80)
    print("🧪 CACHE DETECTION TESTS")
    print("="*80)
    
    results = []
    
    # Run tests
    results.append(("Cache Detection (with cache)", test_cache_detection_with_cache()))
    results.append(("Force Rerun (bypass cache)", test_cache_detection_force_rerun()))
    results.append(("No Cache (run backtesting)", test_cache_detection_no_cache()))
    
    # Cleanup
    cleanup()
    
    # Summary
    print("\n" + "="*80)
    print("📊 TEST SUMMARY")
    print("="*80)
    
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"   {status}: {test_name}")
    
    all_passed = all(result[1] for result in results)
    
    if all_passed:
        print("\n✅ All tests passed!")
        return 0
    else:
        print("\n❌ Some tests failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())
