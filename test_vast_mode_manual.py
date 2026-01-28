#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Manual test script for VAST mode - creates sample parquet files and tests vast-mode
"""

import sys
import os
import tempfile
import shutil
from pathlib import Path
import pandas as pd
import numpy as np

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))


def create_sample_parquet_files(output_dir, num_files=3):
    """Create sample parquet files for testing"""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    pairs = ['EURUSD', 'GBPUSD', 'USDJPY'][:num_files]
    
    for i, pair in enumerate(pairs):
        # Generate minimal synthetic data
        n_samples = 10000
        timestamps = pd.date_range('2025-01-01', periods=n_samples, freq='1s')
        base_price = 1.1000 + (i * 0.05)  # Different base price for each pair
        
        # Add some random walk
        noise = np.random.randn(n_samples) * 0.0001
        cumsum = np.cumsum(noise)
        
        df = pd.DataFrame({
            'timestamp': timestamps,
            'bid': base_price + cumsum - 0.00005,
            'ask': base_price + cumsum + 0.00005,
            'mid': base_price + cumsum,
            'spread': 0.0001,
        })
        
        # Set timestamp as index
        df = df.set_index('timestamp')
        
        # Save as parquet
        filename = f"{pair}_2025.parquet"
        filepath = output_dir / filename
        df.to_parquet(filepath, engine='pyarrow')
        
        print(f"✅ Created {filename} with {len(df):,} rows")
    
    return output_dir


def test_vast_mode_help():
    """Test that vast mode help works"""
    print("\n" + "="*80)
    print("TEST 1: Check --help shows vast-mode options")
    print("="*80)
    
    result = os.system("python main.py --help | grep -q 'vast-mode'")
    
    if result == 0:
        print("✅ Help message includes vast-mode")
    else:
        print("❌ Help message missing vast-mode")
        sys.exit(1)


def test_vast_mode_validation():
    """Test that vast mode validates arguments correctly"""
    print("\n" + "="*80)
    print("TEST 2: Validate vast-mode requires input-dir")
    print("="*80)
    
    # We'll test the function directly since system check blocks CLI testing
    from main import run_vast_mode
    
    class MockArgs:
        vast_mode = True
        input_dir = None
        generate_base = True
        search_light = False
        skip_telegram = True
        parallel_pairs = 1
        max_workers = None
    
    args = MockArgs()
    
    # Test missing input-dir
    try:
        run_vast_mode(args)
        print("❌ Should have exited due to missing input-dir")
        sys.exit(1)
    except SystemExit:
        print("✅ Correctly requires input-dir")
    
    # Test missing mode flag
    args2 = MockArgs()
    args2.input_dir = "/tmp/test"
    args2.generate_base = False
    args2.search_light = False
    
    try:
        run_vast_mode(args2)
        print("❌ Should have exited due to missing mode flag")
        sys.exit(1)
    except SystemExit:
        print("✅ Correctly requires --generate-base or --search-light")


def test_vast_mode_banner():
    """Test that vast mode banner displays correctly"""
    print("\n" + "="*80)
    print("TEST 3: Test resource banner display")
    print("="*80)
    
    from main import detect_resources, print_resources_banner
    
    resources = detect_resources()
    print(f"\nDetected Resources:")
    print(f"  CPU Cores: {resources['cpu_cores']}")
    print(f"  RAM: {resources['ram_gb']:.1f} GB")
    print(f"  Recommended parallel pairs: {resources['recommended_parallel_pairs']}")
    print(f"  Recommended workers/pair: {resources['recommended_workers_per_pair']}")
    
    print("\nDisplaying banner:")
    print_resources_banner(resources, 3, 1, 4)
    
    print("✅ Banner displayed successfully")


def test_vast_mode_dry_run():
    """Test vast mode with sample data (dry run - won't actually process)"""
    print("\n" + "="*80)
    print("TEST 4: Test with sample parquet files (validation only)")
    print("="*80)
    
    # Create temporary directory with sample files
    temp_dir = Path('/tmp/necrozma_vast_test')
    
    # Clean up if exists
    if temp_dir.exists():
        shutil.rmtree(temp_dir)
    
    try:
        # Create sample files
        print("\nCreating sample parquet files...")
        create_sample_parquet_files(temp_dir, num_files=3)
        
        # Test file discovery (just check if it would work)
        parquet_files = list(temp_dir.glob("*.parquet"))
        
        if len(parquet_files) == 3:
            print(f"\n✅ Found {len(parquet_files)} parquet files:")
            for pf in parquet_files:
                print(f"   - {pf.name}")
        else:
            print(f"❌ Expected 3 files, found {len(parquet_files)}")
            sys.exit(1)
        
        print("\n✅ Dry run validation passed")
        print("   (Not running full vast-mode as it requires full environment)")
        
    finally:
        # Clean up
        if temp_dir.exists():
            shutil.rmtree(temp_dir)
            print(f"\n🗑️  Cleaned up test directory: {temp_dir}")


def main():
    """Run all manual tests"""
    print("\n" + "="*80)
    print("🧪 VAST MODE MANUAL TESTS")
    print("="*80)
    
    try:
        test_vast_mode_help()
        test_vast_mode_validation()
        test_vast_mode_banner()
        test_vast_mode_dry_run()
        
        print("\n" + "="*80)
        print("✅ ALL MANUAL TESTS PASSED")
        print("="*80)
        print("\nTo test full vast-mode functionality, run:")
        print("  python main.py --vast-mode --input-dir <your-parquet-dir> --generate-base")
        print("\n")
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
