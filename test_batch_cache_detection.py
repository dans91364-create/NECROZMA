#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for batch cache detection functionality

This script tests:
1. Cache detection - skips existing batches
2. Force rerun - reprocesses all batches when --force-rerun is used
3. Proper tracking of cached vs processed batches
"""

import sys
import time
import shutil
from pathlib import Path
import pandas as pd
import numpy as np
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from batch_runner import BatchRunner
from config import OUTPUT_DIR
from batch_utils import prepare_features


def create_test_data():
    """Create synthetic test data for backtesting"""
    print("\n🧪 Creating synthetic test data...")
    
    n_samples = 5000  # Small dataset for fast testing
    start_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    timestamps = pd.date_range(start_date, periods=n_samples, freq='1s')
    
    base_price = 1.1000
    noise = np.random.randn(n_samples) * 0.0001
    cumsum = np.cumsum(noise)
    
    df = pd.DataFrame({
        'timestamp': timestamps,
        'bid': base_price + cumsum - 0.00005,
        'ask': base_price + cumsum + 0.00005,
        'mid_price': base_price + cumsum,
        'spread_pips': 1.0,
        'pips_change': np.concatenate([[0], np.diff(cumsum) * 10000])
    })
    
    df.set_index('timestamp', inplace=True)
    
    # Add required features
    df = prepare_features(df)
    
    # Save to parquet
    test_data_path = OUTPUT_DIR / "test_cache_batch_data.parquet"
    test_data_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(test_data_path, compression='snappy')
    
    print(f"   ✅ Created {len(df):,} rows")
    print(f"   💾 Saved to: {test_data_path}")
    
    return test_data_path


def test_cache_detection():
    """Test that cache detection works correctly"""
    print("\n" + "="*80)
    print("🧪 TEST 1: Cache Detection")
    print("="*80)
    
    # Create test data
    test_data_path = create_test_data()
    
    # Use very small batches (5 strategies per batch)
    batch_size = 5
    
    print(f"\n📦 Testing with batch size: {batch_size}")
    
    # Clean up any existing batch results
    batch_results_dir = OUTPUT_DIR / "batch_results"
    if batch_results_dir.exists():
        shutil.rmtree(batch_results_dir)
        print(f"   🗑️  Cleaned up previous batch results")
    
    try:
        # ===== FIRST RUN: Process all batches =====
        print(f"\n{'─'*80}")
        print(f"📝 FIRST RUN: Processing all batches")
        print(f"{'─'*80}")
        
        runner1 = BatchRunner(batch_size=batch_size, parquet_file=test_data_path, skip_existing=True)
        
        start_time = time.time()
        successful_files1 = runner1.run_all_batches()
        elapsed1 = time.time() - start_time
        
        n_batches = runner1.num_batches
        n_cached1 = len(runner1.cached_batches)
        n_processed1 = len(successful_files1) - n_cached1
        
        print(f"\n   ✅ First run complete:")
        print(f"      Time: {elapsed1:.1f}s")
        print(f"      Total batches: {n_batches}")
        print(f"      Cached: {n_cached1}")
        print(f"      Processed: {n_processed1}")
        
        # Verify no batches were cached on first run
        assert n_cached1 == 0, f"Expected 0 cached batches on first run, got {n_cached1}"
        assert n_processed1 == n_batches, f"Expected {n_batches} processed batches, got {n_processed1}"
        print(f"\n   ✅ Assertion passed: No cached batches on first run")
        
        # ===== SECOND RUN: Should use cache =====
        print(f"\n{'─'*80}")
        print(f"📦 SECOND RUN: Should detect and skip cached batches")
        print(f"{'─'*80}")
        
        runner2 = BatchRunner(batch_size=batch_size, parquet_file=test_data_path, skip_existing=True)
        
        start_time = time.time()
        successful_files2 = runner2.run_all_batches()
        elapsed2 = time.time() - start_time
        
        n_cached2 = len(runner2.cached_batches)
        n_processed2 = len(successful_files2) - n_cached2
        
        print(f"\n   ✅ Second run complete:")
        print(f"      Time: {elapsed2:.1f}s (was {elapsed1:.1f}s)")
        print(f"      Cached: {n_cached2}")
        print(f"      Processed: {n_processed2}")
        
        # Verify all batches were cached on second run
        assert n_cached2 == n_batches, f"Expected {n_batches} cached batches on second run, got {n_cached2}"
        assert n_processed2 == 0, f"Expected 0 processed batches on second run, got {n_processed2}"
        assert elapsed2 < elapsed1 / 2, f"Second run should be much faster (cached), but {elapsed2:.1f}s vs {elapsed1:.1f}s"
        print(f"\n   ✅ Assertion passed: All batches cached on second run")
        print(f"   ✅ Assertion passed: Second run significantly faster ({elapsed2:.1f}s vs {elapsed1:.1f}s)")
        
        # ===== THIRD RUN: Force rerun =====
        print(f"\n{'─'*80}")
        print(f"🔄 THIRD RUN: Force rerun (ignore cache)")
        print(f"{'─'*80}")
        
        runner3 = BatchRunner(batch_size=batch_size, parquet_file=test_data_path, force_rerun=True)
        
        start_time = time.time()
        successful_files3 = runner3.run_all_batches()
        elapsed3 = time.time() - start_time
        
        n_cached3 = len(runner3.cached_batches)
        n_processed3 = len(successful_files3) - n_cached3
        
        print(f"\n   ✅ Third run complete:")
        print(f"      Time: {elapsed3:.1f}s")
        print(f"      Cached: {n_cached3}")
        print(f"      Processed: {n_processed3}")
        
        # Verify no batches were cached when force_rerun=True
        assert n_cached3 == 0, f"Expected 0 cached batches with force_rerun=True, got {n_cached3}"
        assert n_processed3 == n_batches, f"Expected {n_batches} processed batches with force_rerun=True, got {n_processed3}"
        print(f"\n   ✅ Assertion passed: Force rerun processed all batches")
        
        # ===== SUMMARY =====
        print(f"\n{'='*80}")
        print(f"✅ ALL TESTS PASSED")
        print(f"{'='*80}")
        print(f"\n   Test Summary:")
        print(f"   • First run:  {n_processed1}/{n_batches} batches processed ({elapsed1:.1f}s)")
        print(f"   • Second run: {n_cached2}/{n_batches} batches cached ({elapsed2:.1f}s)")
        print(f"   • Third run:  {n_processed3}/{n_batches} batches processed with --force-rerun ({elapsed3:.1f}s)")
        print(f"   • Speedup:    {elapsed1/elapsed2:.1f}x faster with cache")
        print(f"\n{'='*80}\n")
        
        return True
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        return False
        
    except Exception as e:
        print(f"\n❌ TEST ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


def cleanup_test_files():
    """Clean up test files"""
    print("\n🗑️  Cleaning up test files...")
    
    # Remove test data
    test_data_path = OUTPUT_DIR / "test_cache_batch_data.parquet"
    if test_data_path.exists():
        test_data_path.unlink()
        print(f"   ✅ Removed: {test_data_path}")
    
    # Remove batch results directory
    batch_results_dir = OUTPUT_DIR / "batch_results"
    if batch_results_dir.exists():
        shutil.rmtree(batch_results_dir)
        print(f"   ✅ Removed: {batch_results_dir}")
    
    print()


if __name__ == "__main__":
    try:
        success = test_cache_detection()
        
        # Optional: clean up test files
        import argparse
        parser = argparse.ArgumentParser()
        parser.add_argument("--no-cleanup", action="store_true", help="Keep test files")
        args = parser.parse_args()
        
        if not args.no_cleanup:
            cleanup_test_files()
        
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        sys.exit(1)
