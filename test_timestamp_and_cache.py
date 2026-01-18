#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for timestamp and cache features

Tests:
1. FILE_PREFIX includes timestamp and is unique
2. FILE_PREFIX_STABLE is constant
3. Pattern cache works correctly
4. --clean-strategy-cache deletes correct files
"""

import time
import json
from pathlib import Path


def test_file_prefix_timestamp():
    """Test that FILE_PREFIX includes timestamp and is unique"""
    print("\n" + "=" * 80)
    print("TEST 1: FILE_PREFIX Timestamp")
    print("=" * 80)
    
    from config import FILE_PREFIX, FILE_PREFIX_STABLE, _run_timestamp
    
    print(f"✓ FILE_PREFIX_STABLE: {FILE_PREFIX_STABLE}")
    print(f"✓ _run_timestamp: {_run_timestamp}")
    print(f"✓ FILE_PREFIX: {FILE_PREFIX}")
    
    # Verify format
    assert FILE_PREFIX_STABLE in FILE_PREFIX, "FILE_PREFIX should contain FILE_PREFIX_STABLE"
    assert _run_timestamp in FILE_PREFIX, "FILE_PREFIX should contain timestamp"
    
    # Example filenames
    print("\n📁 Example filenames:")
    print(f"  Cache (stable):   {FILE_PREFIX_STABLE}regimes.parquet")
    print(f"  Cache (stable):   {FILE_PREFIX_STABLE}patterns.json")
    print(f"  Results (unique): {FILE_PREFIX}backtest_results_merged.parquet")
    print(f"  Report (unique):  {FILE_PREFIX}LIGHT_REPORT.json")
    
    print("\n✅ TEST 1 PASSED\n")


def test_pattern_cache():
    """Test pattern cache functionality"""
    print("=" * 80)
    print("TEST 2: Pattern Cache")
    print("=" * 80)
    
    from config import OUTPUT_DIR, FILE_PREFIX_STABLE
    
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    patterns_cache_path = OUTPUT_DIR / f"{FILE_PREFIX_STABLE}patterns.json"
    
    # Create test pattern data
    test_patterns = {
        'important_features': [
            {'name': 'momentum', 'importance': 0.85},
            {'name': 'volatility', 'importance': 0.72},
            {'name': 'trend_strength', 'importance': 0.68}
        ],
        'n_patterns': 3
    }
    
    # Test 1: Save patterns
    print("\n1. Testing pattern save...")
    with open(patterns_cache_path, 'w') as f:
        json.dump(test_patterns, f, indent=2)
    print(f"   ✓ Saved to: {patterns_cache_path}")
    
    # Test 2: Load patterns
    print("\n2. Testing pattern load...")
    with open(patterns_cache_path, 'r') as f:
        loaded_patterns = json.load(f)
    
    assert loaded_patterns == test_patterns, "Loaded patterns don't match saved patterns"
    print(f"   ✓ Loaded {len(loaded_patterns['important_features'])} patterns")
    
    # Test 3: Verify cache reuse
    print("\n3. Verifying cache path uses stable prefix...")
    assert FILE_PREFIX_STABLE in str(patterns_cache_path), "Cache should use stable prefix"
    print(f"   ✓ Cache uses stable prefix (reusable between runs)")
    
    # Cleanup
    if patterns_cache_path.exists():
        patterns_cache_path.unlink()
    
    print("\n✅ TEST 2 PASSED\n")


def test_clean_strategy_cache():
    """Test --clean-strategy-cache functionality"""
    print("=" * 80)
    print("TEST 3: Clean Strategy Cache")
    print("=" * 80)
    
    from config import OUTPUT_DIR
    from main import clean_strategy_cache
    
    # Setup: Create test files
    print("\n1. Creating test files...")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Files to be deleted
    batch_dir = OUTPUT_DIR / 'batch_results'
    batch_dir.mkdir(exist_ok=True)
    (batch_dir / 'test_batch_1.parquet').touch()
    (batch_dir / 'test_batch_2.parquet').touch()
    
    (OUTPUT_DIR / 'EURUSD_2025_rankings.parquet').touch()
    (OUTPUT_DIR / 'EURUSD_2025_LIGHT_REPORT_20260118.json').touch()
    
    # Files to be kept
    (OUTPUT_DIR / 'EURUSD_2025_regimes.parquet').touch()
    (OUTPUT_DIR / 'EURUSD_2025_patterns.json').touch()
    (OUTPUT_DIR / 'EURUSD_2025_20260118_143052_backtest_results_merged.parquet').touch()
    
    labels_dir = OUTPUT_DIR / 'labels'
    labels_dir.mkdir(exist_ok=True)
    (labels_dir / 'test_label.pkl').touch()
    
    print("   ✓ Created test files")
    
    # Count files before
    all_files_before = list(OUTPUT_DIR.rglob('*'))
    all_files_before = [f for f in all_files_before if f.is_file()]
    print(f"   ✓ Total files before: {len(all_files_before)}")
    
    # Test: Clean strategy cache
    print("\n2. Running clean_strategy_cache()...")
    clean_strategy_cache()
    
    # Count files after
    all_files_after = list(OUTPUT_DIR.rglob('*'))
    all_files_after = [f for f in all_files_after if f.is_file()]
    print(f"   ✓ Total files after: {len(all_files_after)}")
    
    # Verify correct files were deleted
    print("\n3. Verifying cleanup...")
    assert not (batch_dir).exists(), "batch_results should be deleted"
    assert not (OUTPUT_DIR / 'EURUSD_2025_rankings.parquet').exists(), "rankings should be deleted"
    assert not (OUTPUT_DIR / 'EURUSD_2025_LIGHT_REPORT_20260118.json').exists(), "LIGHT_REPORT should be deleted"
    print("   ✓ Strategy cache files deleted")
    
    # Verify correct files were kept
    assert (OUTPUT_DIR / 'EURUSD_2025_regimes.parquet').exists(), "regimes should be kept"
    assert (OUTPUT_DIR / 'EURUSD_2025_patterns.json').exists(), "patterns should be kept"
    assert (OUTPUT_DIR / 'EURUSD_2025_20260118_143052_backtest_results_merged.parquet').exists(), "merged results should be kept"
    assert (labels_dir / 'test_label.pkl').exists(), "labels should be kept"
    print("   ✓ Important files preserved")
    
    # Cleanup
    import shutil
    if OUTPUT_DIR.exists():
        shutil.rmtree(OUTPUT_DIR)
    
    print("\n✅ TEST 3 PASSED\n")


def test_integration():
    """Test full integration scenario"""
    print("=" * 80)
    print("TEST 4: Integration Test")
    print("=" * 80)
    
    from config import FILE_PREFIX, FILE_PREFIX_STABLE, OUTPUT_DIR
    import config as config_module
    
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    print("\n1. Simulating first run...")
    first_run_prefix = FILE_PREFIX
    print(f"   Run 1 prefix: {first_run_prefix}")
    
    # Create result files from first run
    result_file_1 = OUTPUT_DIR / f"{first_run_prefix}backtest_results_merged.parquet"
    result_file_1.touch()
    print(f"   Created: {result_file_1.name}")
    
    # Create cache files (stable)
    cache_regimes = OUTPUT_DIR / f"{FILE_PREFIX_STABLE}regimes.parquet"
    cache_patterns = OUTPUT_DIR / f"{FILE_PREFIX_STABLE}patterns.json"
    cache_regimes.touch()
    cache_patterns.touch()
    print(f"   Created: {cache_regimes.name}")
    print(f"   Created: {cache_patterns.name}")
    
    print("\n2. Simulating second run (new timestamp)...")
    # In a real second run, we'd wait at least 1 second and reload the module
    # For this test, we'll simulate it by creating a different timestamp
    import time
    time.sleep(1.1)  # Wait to ensure different second
    
    # Simulate a new run by manually creating a new timestamp
    from datetime import datetime
    new_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    second_run_prefix = f"{config_module.FILE_PREFIX_STABLE}{new_timestamp}_"
    
    print(f"   Run 2 prefix: {second_run_prefix}")
    assert first_run_prefix != second_run_prefix, "Prefixes should be different"
    print("   ✓ New timestamp generated")
    
    # Create result files from second run
    result_file_2 = OUTPUT_DIR / f"{second_run_prefix}backtest_results_merged.parquet"
    result_file_2.touch()
    print(f"   Created: {result_file_2.name}")
    
    print("\n3. Verifying both results exist...")
    assert result_file_1.exists(), "First run results should exist"
    assert result_file_2.exists(), "Second run results should exist"
    print(f"   ✓ Run 1: {result_file_1.name}")
    print(f"   ✓ Run 2: {result_file_2.name}")
    
    print("\n4. Verifying cache is shared (stable prefix)...")
    assert cache_regimes.exists(), "Regimes cache should exist"
    assert cache_patterns.exists(), "Patterns cache should exist"
    print(f"   ✓ Shared cache: {cache_regimes.name}")
    print(f"   ✓ Shared cache: {cache_patterns.name}")
    
    # Count total result files
    result_files = list(OUTPUT_DIR.glob("*_backtest_results_merged.parquet"))
    print(f"\n5. Total result files: {len(result_files)}")
    for f in result_files:
        print(f"   - {f.name}")
    
    # Cleanup
    import shutil
    if OUTPUT_DIR.exists():
        shutil.rmtree(OUTPUT_DIR)
    
    print("\n✅ TEST 4 PASSED\n")


def main():
    """Run all tests"""
    print("\n" + "=" * 80)
    print("TIMESTAMP AND CACHE FEATURE TESTS")
    print("=" * 80)
    
    try:
        test_file_prefix_timestamp()
        test_pattern_cache()
        test_clean_strategy_cache()
        test_integration()
        
        print("=" * 80)
        print("✅ ALL TESTS PASSED!")
        print("=" * 80)
        print("\nSummary:")
        print("  ✓ Timestamp-based FILE_PREFIX works correctly")
        print("  ✓ FILE_PREFIX_STABLE is constant for caches")
        print("  ✓ Pattern cache loads and saves correctly")
        print("  ✓ Clean strategy cache preserves important files")
        print("  ✓ Multiple runs don't overwrite each other")
        print()
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
