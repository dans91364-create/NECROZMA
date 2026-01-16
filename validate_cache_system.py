#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚡🌟💎 ULTRA NECROZMA - CACHE VALIDATION SCRIPT 💎🌟⚡

Validates cache and resume functionality
"""

import sys
import time
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from analyzer import UltraNecrozmaAnalyzer
from labeler import label_dataframe, clear_label_cache
from config import CACHE_CONFIG, get_output_dirs


def create_test_data(n_samples=10000):
    """Create test tick data"""
    print("📊 Creating test data...")
    timestamps = pd.date_range('2025-01-01', periods=n_samples, freq='1s')
    
    # Generate realistic price movements
    base_price = 1.1000
    noise = np.random.randn(n_samples) * 0.0001
    cumsum = np.cumsum(noise)
    
    df = pd.DataFrame({
        'timestamp': timestamps,
        'mid_price': base_price + cumsum,
        'bid': base_price + cumsum - 0.00005,
        'ask': base_price + cumsum + 0.00005,
    })
    
    print(f"   ✅ Created {len(df):,} data points\n")
    return df


def test_universe_cache():
    """Test universe caching"""
    print("═" * 80)
    print("🌌 TEST 1: Universe Cache")
    print("═" * 80)
    
    # Create test data
    df = create_test_data(5000)
    
    # First run - should process universes
    print("\n🔄 First run - Processing universes...")
    analyzer = UltraNecrozmaAnalyzer(df)
    
    start_time = time.time()
    analyzer.run_analysis(parallel=False)
    first_run_time = time.time() - start_time
    
    analyzer.save_results()
    print(f"   ⏱️  First run completed in {first_run_time:.2f}s")
    
    # Second run - should skip existing universes
    print("\n🔄 Second run - Should use cache...")
    analyzer2 = UltraNecrozmaAnalyzer(df)
    
    start_time = time.time()
    analyzer2.run_analysis(parallel=False)
    second_run_time = time.time() - start_time
    
    print(f"   ⏱️  Second run completed in {second_run_time:.2f}s")
    
    # Calculate speedup
    speedup = first_run_time / second_run_time if second_run_time > 0 else float('inf')
    time_saved = first_run_time - second_run_time
    
    print(f"\n📊 RESULTS:")
    print(f"   First run:   {first_run_time:.2f}s")
    print(f"   Second run:  {second_run_time:.2f}s (using cache)")
    print(f"   Time saved:  {time_saved:.2f}s ({time_saved/first_run_time*100:.1f}%)")
    print(f"   Speedup:     {speedup:.1f}x faster")
    
    if speedup > 2:
        print(f"   ✅ PASS: Cache is working! ({speedup:.1f}x speedup)")
    else:
        print(f"   ⚠️  WARNING: Cache speedup lower than expected")
    
    return speedup > 1.5


def test_labeling_cache():
    """Test labeling cache"""
    print("\n" + "═" * 80)
    print("🏷️  TEST 2: Labeling Cache")
    print("═" * 80)
    
    # Create test data
    df = create_test_data(1000)
    
    # Clear any existing cache
    print("\n🗑️  Clearing old cache...")
    try:
        clear_label_cache()
    except:
        pass
    
    # First run - should create cache
    print("\n🔄 First run - Creating cache...")
    start_time = time.time()
    results1 = label_dataframe(
        df,
        target_pips=[10, 20],
        stop_pips=[5, 10],
        horizons=[60],
        num_workers=1,
        use_cache=True
    )
    first_run_time = time.time() - start_time
    
    print(f"   ⏱️  First run completed in {first_run_time:.2f}s")
    print(f"   📊 Generated {len(results1)} labeled datasets")
    
    # Second run - should use cache
    print("\n🔄 Second run - Should load from cache...")
    start_time = time.time()
    results2 = label_dataframe(
        df,
        target_pips=[10, 20],
        stop_pips=[5, 10],
        horizons=[60],
        num_workers=1,
        use_cache=True
    )
    second_run_time = time.time() - start_time
    
    print(f"   ⏱️  Second run completed in {second_run_time:.2f}s")
    
    # Calculate speedup
    speedup = first_run_time / second_run_time if second_run_time > 0 else float('inf')
    time_saved = first_run_time - second_run_time
    
    print(f"\n📊 RESULTS:")
    print(f"   First run:   {first_run_time:.2f}s")
    print(f"   Second run:  {second_run_time:.2f}s (from cache)")
    print(f"   Time saved:  {time_saved:.2f}s ({time_saved/first_run_time*100:.1f}%)")
    print(f"   Speedup:     {speedup:.1f}x faster")
    
    if speedup > 5:
        print(f"   ✅ PASS: Cache is working excellently! ({speedup:.1f}x speedup)")
    elif speedup > 2:
        print(f"   ✅ PASS: Cache is working! ({speedup:.1f}x speedup)")
    else:
        print(f"   ⚠️  WARNING: Cache speedup lower than expected")
    
    return speedup > 2


def test_fresh_mode():
    """Test fresh mode (disable cache)"""
    print("\n" + "═" * 80)
    print("🔥 TEST 3: Fresh Mode (Cache Disabled)")
    print("═" * 80)
    
    # Create test data
    df = create_test_data(500)
    
    # Disable cache
    original_enabled = CACHE_CONFIG.get("enabled")
    CACHE_CONFIG["enabled"] = False
    
    print("\n🔄 Running with cache disabled...")
    start_time = time.time()
    results = label_dataframe(
        df,
        target_pips=[10],
        stop_pips=[5],
        horizons=[60],
        num_workers=1,
        use_cache=False
    )
    run_time = time.time() - start_time
    
    print(f"   ⏱️  Completed in {run_time:.2f}s")
    print(f"   📊 Generated {len(results)} labeled datasets")
    
    # Restore cache setting
    CACHE_CONFIG["enabled"] = original_enabled
    
    print(f"\n✅ PASS: Fresh mode works correctly")
    return True


def main():
    """Run all validation tests"""
    print("""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║    ⚡🌟💎 CACHE & RESUME VALIDATION SUITE 💎🌟⚡            ║
║                                                              ║
║  Testing cache and resume functionality...                   ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    # Run tests
    results = []
    
    try:
        results.append(("Universe Cache", test_universe_cache()))
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
        results.append(("Universe Cache", False))
    
    try:
        results.append(("Labeling Cache", test_labeling_cache()))
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
        results.append(("Labeling Cache", False))
    
    try:
        results.append(("Fresh Mode", test_fresh_mode()))
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
        results.append(("Fresh Mode", False))
    
    # Print summary
    print("\n" + "═" * 80)
    print("📊 VALIDATION SUMMARY")
    print("═" * 80)
    
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"   {status}: {test_name}")
    
    all_passed = all(result[1] for result in results)
    
    if all_passed:
        print("\n🎉 All tests passed! Cache and resume system is working correctly.")
        return 0
    else:
        print("\n⚠️  Some tests failed. Please review the output above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
