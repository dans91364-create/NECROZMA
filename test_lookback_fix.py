#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script to verify lookback periods < 30 now generate patterns
"""

import numpy as np
import pandas as pd
import sys
from datetime import datetime

# Import analyzer components
from config import MIN_SAMPLES, LOOKBACKS, INTERVALS
from analyzer import process_universe

print("=" * 80)
print("🧪 TESTING LOOKBACK FIX - Verify All Lookback Periods Generate Patterns")
print("=" * 80)

print(f"\n📋 Configuration:")
print(f"   MIN_SAMPLES = {MIN_SAMPLES}")
print(f"   LOOKBACKS = {LOOKBACKS}")
print(f"   INTERVALS = {INTERVALS}")

# Generate synthetic tick data
print(f"\n📊 Generating synthetic tick data...")
np.random.seed(42)

n_ticks = 200000  # 200k ticks for robust testing
timestamps = pd.date_range("2025-01-01", periods=n_ticks, freq="1s")

# Create price movements with clear patterns
base_price = 1.10
trend = np.linspace(0, 0.01, n_ticks)  # Upward trend
noise = np.random.randn(n_ticks) * 0.0001
cycles = 0.002 * np.sin(np.linspace(0, 50 * np.pi, n_ticks))  # Cyclical component

prices = base_price + trend + noise + cycles

df = pd.DataFrame({
    "timestamp": timestamps,
    "bid": prices - 0.00005,
    "ask": prices + 0.00005,
    "mid_price": prices,
    "spread_pips": 1.0,
    "pips_change": np.concatenate([[0], np.diff(prices) * 10000])
})

print(f"   ✅ Generated {len(df):,} ticks")

# Test each lookback period with a small subset of intervals
print(f"\n🌌 Testing Pattern Generation for Each Lookback:")
print("─" * 80)

test_interval = 5  # Use 5-minute interval for all tests
results = {}

for lookback in LOOKBACKS:
    universe_name = f"test_{test_interval}m_{lookback}lb"
    
    print(f"\n   Testing lookback={lookback:2d} ({universe_name})...")
    
    result = process_universe(df, test_interval, lookback, universe_name)
    
    if result:
        total_patterns = result["total_patterns"]
        results[lookback] = total_patterns
        
        # Show debug stats if available
        debug_info = []
        for level in result["results"]:
            for direction in result["results"][level]:
                level_data = result["results"][level][direction]
                if "debug_stats" in level_data:
                    stats = level_data["debug_stats"]
                    if stats["targets_found"] > 0:
                        debug_info.append(
                            f"{level}/{direction}: "
                            f"{stats['targets_found']} targets, "
                            f"{stats['features_extracted']} extracted, "
                            f"{stats['features_failed']} failed"
                        )
        
        if total_patterns > 0:
            print(f"      ✅ {total_patterns} patterns generated ({result['processing_time']:.2f}s)")
            if debug_info:
                for info in debug_info[:3]:  # Show first 3
                    print(f"         • {info}")
        else:
            print(f"      ❌ 0 patterns generated ({result['processing_time']:.2f}s)")
            print(f"         This indicates the bug is NOT fixed!")
    else:
        print(f"      ❌ No result returned")
        results[lookback] = 0

# Summary
print("\n" + "=" * 80)
print("📊 SUMMARY - Pattern Counts by Lookback Period:")
print("=" * 80)

all_working = True
for lookback in LOOKBACKS:
    count = results.get(lookback, 0)
    status = "✅" if count > 0 else "❌"
    print(f"   {status} Lookback {lookback:2d}: {count:>7,} patterns")
    if count == 0:
        all_working = False

print("=" * 80)

if all_working:
    print("\n✅ SUCCESS! All lookback periods generate patterns!")
    print("   The bug has been FIXED! 🎉")
    sys.exit(0)
else:
    print("\n❌ FAILURE! Some lookback periods still generate 0 patterns")
    print("   The bug is NOT fully fixed")
    sys.exit(1)
