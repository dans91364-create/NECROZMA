#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Demonstration script for timestamp and cache features

This script demonstrates:
1. How FILE_PREFIX and FILE_PREFIX_STABLE work
2. How pattern cache saves time
3. How --clean-strategy-cache preserves important files
"""

import time
import json
from pathlib import Path
from datetime import datetime


def demo_file_prefixes():
    """Demonstrate FILE_PREFIX and FILE_PREFIX_STABLE"""
    print("\n" + "=" * 80)
    print("DEMO 1: File Prefix System")
    print("=" * 80)
    
    from config import FILE_PREFIX, FILE_PREFIX_STABLE, PAIR_NAME, DATA_YEAR, _run_timestamp
    
    print(f"\n📌 Configuration:")
    print(f"   Pair: {PAIR_NAME}")
    print(f"   Year: {DATA_YEAR}")
    print(f"   Run timestamp: {_run_timestamp}")
    
    print(f"\n📂 File Prefixes:")
    print(f"   Stable (cache):  {FILE_PREFIX_STABLE}")
    print(f"   Unique (results): {FILE_PREFIX}")
    
    print(f"\n📁 Example Filenames:")
    print(f"\n   CACHE FILES (reusable between runs):")
    print(f"   ├─ {FILE_PREFIX_STABLE}regimes.parquet")
    print(f"   ├─ {FILE_PREFIX_STABLE}patterns.json")
    print(f"   └─ labels/")
    
    print(f"\n   RESULT FILES (unique per run):")
    print(f"   ├─ {FILE_PREFIX}backtest_results_merged.parquet")
    print(f"   ├─ {FILE_PREFIX}rankings.parquet")
    print(f"   └─ {FILE_PREFIX}LIGHT_REPORT.json")
    
    print(f"\n💡 Benefit: Multiple runs create different result files,")
    print(f"   but share the same cache files!")


def demo_pattern_cache():
    """Demonstrate pattern cache functionality"""
    print("\n" + "=" * 80)
    print("DEMO 2: Pattern Mining Cache")
    print("=" * 80)
    
    from config import OUTPUT_DIR, FILE_PREFIX_STABLE
    
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    patterns_cache_path = OUTPUT_DIR / f"{FILE_PREFIX_STABLE}patterns.json"
    
    # Simulate pattern mining (expensive operation)
    print("\n📊 First run (no cache):")
    print("   🔄 Running pattern mining...")
    
    # Create example pattern data
    patterns = {
        'important_features': [
            {'name': 'momentum', 'importance': 0.85},
            {'name': 'volatility', 'importance': 0.72},
            {'name': 'trend_strength', 'importance': 0.68}
        ],
        'n_patterns': 3,
        'timestamp': datetime.now().isoformat()
    }
    
    # Simulate processing time
    time.sleep(0.5)
    
    # Save to cache
    with open(patterns_cache_path, 'w') as f:
        json.dump(patterns, f, indent=2)
    
    print(f"   ✅ Pattern mining complete (0.5s)")
    print(f"   💾 Saved to: {patterns_cache_path.name}")
    
    # Simulate second run (with cache)
    print("\n📊 Second run (with cache):")
    print("   ✅ Loading saved patterns from cache...")
    
    start_time = time.time()
    with open(patterns_cache_path, 'r') as f:
        cached_patterns = json.load(f)
    elapsed = time.time() - start_time
    
    print(f"   ✅ Loaded in {elapsed:.3f}s")
    print(f"   💡 Time saved: ~0.5s (100x faster!)")
    
    # Cleanup
    if patterns_cache_path.exists():
        patterns_cache_path.unlink()


def demo_clean_strategy_cache():
    """Demonstrate --clean-strategy-cache functionality"""
    print("\n" + "=" * 80)
    print("DEMO 3: Clean Strategy Cache")
    print("=" * 80)
    
    from config import OUTPUT_DIR
    from main import clean_strategy_cache
    
    # Setup: Create example files
    print("\n📁 Creating example files...")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Files that will be deleted
    batch_dir = OUTPUT_DIR / 'batch_results'
    batch_dir.mkdir(exist_ok=True)
    (batch_dir / 'batch_1.parquet').touch()
    
    (OUTPUT_DIR / 'EURUSD_2025_rankings.parquet').touch()
    (OUTPUT_DIR / 'EURUSD_2025_LIGHT_REPORT_20260118.json').touch()
    
    # Files that will be preserved
    (OUTPUT_DIR / 'EURUSD_2025_regimes.parquet').touch()
    (OUTPUT_DIR / 'EURUSD_2025_patterns.json').touch()
    (OUTPUT_DIR / 'EURUSD_2025_20260118_143052_backtest_results_merged.parquet').touch()
    
    labels_dir = OUTPUT_DIR / 'labels'
    labels_dir.mkdir(exist_ok=True)
    (labels_dir / 'label_5_10.pkl').touch()
    
    print("   ✅ Created 7 files")
    
    # Show what will be deleted vs preserved
    print("\n🗑️  Will be DELETED:")
    print("   ├─ batch_results/")
    print("   ├─ *_rankings.parquet")
    print("   └─ *_LIGHT_REPORT_*.json")
    
    print("\n✅ Will be PRESERVED:")
    print("   ├─ *_regimes.parquet")
    print("   ├─ *_patterns.json")
    print("   ├─ *_backtest_results_merged.parquet")
    print("   └─ labels/")
    
    # Clean
    print("\n🧹 Running clean_strategy_cache()...")
    clean_strategy_cache()
    
    # Verify
    print("\n📊 Verification:")
    remaining = list(OUTPUT_DIR.rglob('*'))
    remaining = [f for f in remaining if f.is_file()]
    print(f"   Files remaining: {len(remaining)}")
    for f in sorted(remaining):
        print(f"   ✓ {f.relative_to(OUTPUT_DIR)}")
    
    # Cleanup
    import shutil
    if OUTPUT_DIR.exists():
        shutil.rmtree(OUTPUT_DIR)


def demo_multiple_runs():
    """Demonstrate multiple runs without overwriting"""
    print("\n" + "=" * 80)
    print("DEMO 4: Multiple Runs Without Overwriting")
    print("=" * 80)
    
    from config import OUTPUT_DIR, FILE_PREFIX, FILE_PREFIX_STABLE
    
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    print("\n📊 Simulating 3 backtest runs...")
    
    # Simulate 3 runs with different timestamps
    timestamps = [
        "20260118_143052",
        "20260118_145233",
        "20260118_151445"
    ]
    
    for i, ts in enumerate(timestamps, 1):
        result_file = OUTPUT_DIR / f"{FILE_PREFIX_STABLE}{ts}_backtest_results_merged.parquet"
        result_file.touch()
        print(f"   Run {i}: {result_file.name}")
        time.sleep(0.1)
    
    # Show all results exist
    print("\n📁 All result files in directory:")
    results = sorted(OUTPUT_DIR.glob("*_backtest_results_merged.parquet"))
    for f in results:
        print(f"   ✓ {f.name}")
    
    print(f"\n💡 All {len(results)} runs preserved!")
    print("   Each has a unique timestamp in the filename")
    print("   Perfect for comparing different parameter configurations")
    
    # Show how to identify latest
    if results:
        latest = max(results, key=lambda p: p.name)
        print(f"\n🏆 Latest run: {latest.name}")
    
    # Cleanup
    import shutil
    if OUTPUT_DIR.exists():
        shutil.rmtree(OUTPUT_DIR)


def main():
    """Run all demonstrations"""
    print("\n" + "=" * 80)
    print("🌟 TIMESTAMP AND CACHE FEATURES DEMONSTRATION 🌟")
    print("=" * 80)
    
    try:
        demo_file_prefixes()
        demo_pattern_cache()
        demo_clean_strategy_cache()
        demo_multiple_runs()
        
        print("\n" + "=" * 80)
        print("✅ ALL DEMONSTRATIONS COMPLETE")
        print("=" * 80)
        
        print("\n📚 Summary:")
        print("   1. FILE_PREFIX_STABLE - Constant prefix for reusable caches")
        print("   2. FILE_PREFIX - Unique prefix with timestamp for results")
        print("   3. Pattern cache - Saves computation time on reruns")
        print("   4. Clean command - Easy cache cleanup")
        print("   5. Multiple runs - No overwriting, all results preserved")
        
        print("\n🚀 Try it yourself:")
        print("   python main.py --clean-strategy-cache --strategy-discovery --batch-mode")
        print()
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
