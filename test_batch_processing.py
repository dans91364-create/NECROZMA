#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for batch processing functionality

This script tests:
1. Batch worker can process a small batch
2. Batch runner can orchestrate multiple batches
3. Results are correctly merged
"""

import sys
import time
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
    
    n_samples = 10000  # Small dataset for fast testing
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
    
    # Add required features using shared utility
    df = prepare_features(df)
    
    # Save to parquet
    test_data_path = OUTPUT_DIR / "test_batch_data.parquet"
    test_data_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(test_data_path, compression='snappy')
    
    print(f"   ✅ Created {len(df):,} rows")
    print(f"   💾 Saved to: {test_data_path}")
    
    return test_data_path


def test_batch_processing():
    """Test batch processing with small batches"""
    print("\n" + "="*80)
    print("🧪 TESTING BATCH PROCESSING")
    print("="*80)
    
    # Create test data
    test_data_path = create_test_data()
    
    # Test with very small batches (10 strategies per batch)
    batch_size = 10
    
    print(f"\n📦 Testing with batch size: {batch_size}")
    
    try:
        # Create batch runner
        runner = BatchRunner(batch_size=batch_size, parquet_file=test_data_path)
        
        # Run batch processing
        start_time = time.time()
        result_file = runner.run(merge=True)
        elapsed = time.time() - start_time
        
        print(f"\n{'='*80}")
        print(f"✅ TEST COMPLETE")
        print(f"{'='*80}")
        print(f"   Time: {elapsed:.1f}s")
        print(f"   Batches: {runner.num_batches}")
        print(f"   Total strategies: {runner.total_strategies}")
        print(f"   Failed batches: {len(runner.failed_batches)}")
        
        if result_file and result_file.exists():
            # Verify merged results
            results_df = pd.read_parquet(result_file)
            print(f"\n📊 Merged Results:")
            print(f"   Total rows: {len(results_df):,}")
            print(f"   Unique strategies: {results_df['strategy_name'].nunique()}")
            print(f"   Lot sizes: {sorted(results_df['lot_size'].unique())}")
            
            # Show sample
            print(f"\n   Sample results (first 5 rows):")
            print(results_df.head().to_string())
            
            print(f"\n   ✅ Results file: {result_file}")
            print(f"{'='*80}\n")
            
            return True
        else:
            print(f"\n   ❌ No merged results file generated!")
            print(f"{'='*80}\n")
            return False
            
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def cleanup_test_files():
    """Clean up test files"""
    print("\n🗑️  Cleaning up test files...")
    
    # Remove test data
    test_data_path = OUTPUT_DIR / "test_batch_data.parquet"
    if test_data_path.exists():
        test_data_path.unlink()
        print(f"   ✅ Removed: {test_data_path}")
    
    # Remove batch results directory
    batch_results_dir = OUTPUT_DIR / "batch_results"
    if batch_results_dir.exists():
        import shutil
        shutil.rmtree(batch_results_dir)
        print(f"   ✅ Removed: {batch_results_dir}")
    
    print()


if __name__ == "__main__":
    try:
        success = test_batch_processing()
        
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
