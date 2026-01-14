#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Quick test for universe file creation
"""

import sys
from pathlib import Path
import tempfile
import shutil
import json
import numpy as np
import pandas as pd

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from analyzer import UltraNecrozmaAnalyzer, process_universe


def generate_sample_data():
    """Generate sample tick data"""
    np.random.seed(42)
    
    n_ticks = 10000
    timestamps = pd.date_range("2025-01-01", periods=n_ticks, freq="1s")
    base_price = 1.10
    noise = np.random.randn(n_ticks) * 0.0001
    cumsum = np.cumsum(noise)
    
    df = pd.DataFrame({
        'timestamp': timestamps,
        'bid': base_price + cumsum - 0.00005,
        'ask': base_price + cumsum + 0.00005,
        'mid_price': base_price + cumsum,
        'spread_pips': 1.0,
        'pips_change': np.concatenate([[0], np.diff(cumsum) * 10000])
    })
    
    return df


def test_process_universe():
    """Test that process_universe includes required fields"""
    print("\n" + "="*60)
    print("TEST 1: process_universe includes OHLC data")
    print("="*60)
    
    df = generate_sample_data()
    result = process_universe(df, interval=5, lookback=10, universe_name="test_5m_10lb")
    
    # Check required fields
    checks = {
        "name": "name" in result,
        "config": "config" in result,
        "total_patterns": "total_patterns" in result,
        "ohlc_data": "ohlc_data" in result,
        "metadata": "metadata" in result,
    }
    
    for field, present in checks.items():
        status = "✅" if present else "❌"
        print(f"{status} {field}: {present}")
    
    if "ohlc_data" in result:
        print(f"   OHLC candles: {len(result['ohlc_data'])}")
        if len(result["ohlc_data"]) > 0:
            first_candle = result["ohlc_data"][0]
            ohlc_fields = ["open", "high", "low", "close", "timestamp"]
            print(f"   OHLC fields: {', '.join([f for f in ohlc_fields if f in first_candle])}")
    
    if "metadata" in result:
        metadata = result["metadata"]
        print(f"   Metadata: interval={metadata.get('interval_minutes')}, " +
              f"lookback={metadata.get('lookback_periods')}, " +
              f"candles={metadata.get('total_candles')}")
    
    print(f"   Total patterns: {result.get('total_patterns', 0)}")
    
    all_passed = all(checks.values())
    print(f"\nResult: {'✅ PASSED' if all_passed else '❌ FAILED'}")
    return all_passed


def test_analyzer_save_files():
    """Test that analyzer.save_results() creates files"""
    print("\n" + "="*60)
    print("TEST 2: analyzer.save_results() creates universe files")
    print("="*60)
    
    # Create temp directory
    temp_dir = Path(tempfile.mkdtemp())
    
    try:
        df = generate_sample_data()
        
        # Initialize analyzer with temp output dir
        print(f"Output dir: {temp_dir}")
        analyzer = UltraNecrozmaAnalyzer(df, output_dir=temp_dir)
        
        # Run analysis (sequential mode, limited configs)
        print("Running analysis (this may take a moment)...")
        # Temporarily reduce configs for faster testing
        analyzer.configs = analyzer.configs[:2]  # Only test first 2 configs
        analyzer._run_sequential()
        
        # Save results
        print("Saving results...")
        save_stats = analyzer.save_results()
        
        print(f"✅ Saved {save_stats['universes_saved']} universe files")
        
        # Check files
        universes_dir = temp_dir / "universes"
        universe_files = list(universes_dir.glob("universe_*.json"))
        
        print(f"✅ Found {len(universe_files)} universe files:")
        for f in universe_files:
            size_kb = f.stat().st_size / 1024
            print(f"   - {f.name} ({size_kb:.2f} KB)")
        
        # Verify first file structure
        if universe_files:
            with open(universe_files[0], 'r') as f:
                universe_data = json.load(f)
            
            required_fields = ["name", "interval", "lookback", "total_patterns", 
                              "ohlc_data", "metadata", "_filepath"]
            
            print(f"\n✅ Checking structure of {universe_files[0].name}:")
            for field in required_fields:
                present = field in universe_data
                status = "✅" if present else "❌"
                print(f"   {status} {field}: {present}")
            
            print(f"\n   OHLC candles: {len(universe_data.get('ohlc_data', []))}")
            print(f"   Total patterns: {universe_data.get('total_patterns', 0)}")
            
            all_present = all(field in universe_data for field in required_fields)
            has_ohlc = len(universe_data.get('ohlc_data', [])) > 0
            
            success = all_present and has_ohlc
            print(f"\nResult: {'✅ PASSED' if success else '❌ FAILED'}")
            return success
        else:
            print("\n❌ FAILED: No universe files created")
            return False
            
    finally:
        # Cleanup
        if temp_dir.exists():
            shutil.rmtree(temp_dir)


if __name__ == "__main__":
    print("\n🌟 ULTRA NECROZMA - Universe File Creation Tests 🌟\n")
    
    test1_passed = test_process_universe()
    test2_passed = test_analyzer_save_files()
    
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"Test 1 (process_universe): {'✅ PASSED' if test1_passed else '❌ FAILED'}")
    print(f"Test 2 (save_results): {'✅ PASSED' if test2_passed else '❌ FAILED'}")
    
    all_passed = test1_passed and test2_passed
    print(f"\nOverall: {'✅ ALL TESTS PASSED' if all_passed else '❌ SOME TESTS FAILED'}")
    print("="*60 + "\n")
    
    sys.exit(0 if all_passed else 1)
