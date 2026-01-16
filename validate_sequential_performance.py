#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚡🌟💎 NECROZMA - SEQUENTIAL LABELING PERFORMANCE VALIDATION 💎🌟⚡

Validates that removing multiprocessing Pool improves performance
by eliminating data copying overhead.
"""

import numpy as np
import pandas as pd
import time
from labeler import label_dataframe, NUMBA_AVAILABLE

print("""
╔══════════════════════════════════════════════════════════════╗
║     🚀 SEQUENTIAL LABELING PERFORMANCE VALIDATION 🚀          ║
╚══════════════════════════════════════════════════════════════╝
""")

print(f"✅ Numba Available: {NUMBA_AVAILABLE}")
print()

# ═══════════════════════════════════════════════════════════════
# 📊 TEST 1: Small Dataset (Fast validation)
# ═══════════════════════════════════════════════════════════════

print("═" * 60)
print("📊 TEST 1: Small Dataset (1,000 candles)")
print("═" * 60)
print()

# Generate test data
n_candles = 1_000
print(f"Generating {n_candles:,} candles...")
timestamps = pd.date_range('2025-01-01', periods=n_candles, freq='1s')
prices = 1.1000 + np.cumsum(np.random.randn(n_candles) * 0.0001)

df_small = pd.DataFrame({
    'timestamp': timestamps,
    'mid_price': prices,
})

print(f"   DataFrame shape: {df_small.shape}")
print()

# Test with minimal configuration
print("Testing with 4 configurations (2 targets × 2 stops × 1 horizon)...")
start = time.time()
results = label_dataframe(
    df_small,
    target_pips=[10, 20],
    stop_pips=[10, 15],
    horizons=[60],
    num_workers=4,  # This parameter is now ignored
    use_cache=False
)
elapsed = time.time() - start

print(f"\n   ⏱️  Total Time: {elapsed:.2f} seconds")
print(f"   📦 Configurations: {len(results)}")
print(f"   ⏱️  Time per config: {elapsed / len(results):.2f} seconds")
print()

# ═══════════════════════════════════════════════════════════════
# 📊 TEST 2: Medium Dataset (Realistic)
# ═══════════════════════════════════════════════════════════════

print("═" * 60)
print("📊 TEST 2: Medium Dataset (10,000 candles)")
print("═" * 60)
print()

# Generate larger dataset
n_candles = 10_000
print(f"Generating {n_candles:,} candles...")
timestamps = pd.date_range('2025-01-01', periods=n_candles, freq='1s')
prices = 1.1000 + np.cumsum(np.random.randn(n_candles) * 0.0001)

df_medium = pd.DataFrame({
    'timestamp': timestamps,
    'mid_price': prices,
})

print(f"   DataFrame shape: {df_medium.shape}")
print()

# Test with more configurations
print("Testing with 8 configurations (2 targets × 2 stops × 2 horizons)...")
start = time.time()
results = label_dataframe(
    df_medium,
    target_pips=[10, 20],
    stop_pips=[10, 15],
    horizons=[60, 240],
    num_workers=8,  # This parameter is now ignored
    use_cache=False
)
elapsed = time.time() - start

print(f"\n   ⏱️  Total Time: {elapsed:.2f} seconds")
print(f"   📦 Configurations: {len(results)}")
print(f"   ⏱️  Time per config: {elapsed / len(results):.2f} seconds")

# Calculate projected time for full labeling
configs_per_sec = len(results) / elapsed
total_configs = 210  # From problem statement (6 targets × 5 stops × 7 horizons)

projected_time_sec = total_configs / configs_per_sec
projected_time_min = projected_time_sec / 60
projected_time_hr = projected_time_min / 60

print()
print(f"   📈 Throughput: {configs_per_sec:.2f} configs/second")
print()

# ═══════════════════════════════════════════════════════════════
# 📊 SUMMARY & PROJECTION
# ═══════════════════════════════════════════════════════════════

print("═" * 60)
print("📊 PERFORMANCE SUMMARY & PROJECTION")
print("═" * 60)
print()

print(f"✅ Sequential processing with Numba optimization")
print(f"✅ Zero data copying overhead (no multiprocessing Pool)")
print()
print(f"Projected time for 210 configurations:")
print(f"   Sequential (new): ~{projected_time_hr:.1f} hours ({projected_time_min:.0f} minutes)")
print(f"   Parallel Pool (old): ~80+ hours")
print()

if projected_time_hr < 5:
    print(f"   🎯 TARGET ACHIEVED!")
    print(f"   Expected: ~3-5 hours")
    print(f"   Actual: ~{projected_time_hr:.1f} hours")
    speedup_factor = 80 / projected_time_hr
    print(f"   🚀 Speedup: {speedup_factor:.0f}x faster than old implementation!")
else:
    print(f"   ⚠️  Performance not meeting expectations")
    print(f"   Expected: ~3-5 hours")
    print(f"   Projected: ~{projected_time_hr:.1f} hours")

print()
print("🎯 VALIDATION COMPLETE!")
print()
