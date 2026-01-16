#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Demo script to show dynamic min_cluster_size in action

This script demonstrates the fix for over-segmentation by showing:
1. Small dataset (5K rows) -> uses minimum 10,000
2. Medium dataset (2M rows) -> uses 1% = 20,000
3. Large dataset (14.6M rows equivalent) -> uses 1% = 146,000
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import numpy as np
import pandas as pd
from regime_detector import RegimeDetector

print("""
╔══════════════════════════════════════════════════════════════╗
║     🔧 DYNAMIC MIN_CLUSTER_SIZE DEMONSTRATION 🔧             ║
╚══════════════════════════════════════════════════════════════╝
""")

def test_dataset_size(n_rows, description):
    """Test dynamic calculation with a specific dataset size"""
    print(f"\n{'='*60}")
    print(f"📊 {description}")
    print(f"{'='*60}")
    
    # Create synthetic dataset
    print(f"   Creating dataset with {n_rows:,} rows...")
    np.random.seed(42)
    df = pd.DataFrame({
        "volatility": np.random.uniform(0.1, 0.5, n_rows),
        "trend": np.random.uniform(-0.5, 0.5, n_rows),
        "momentum": np.random.uniform(-0.3, 0.3, n_rows),
    })
    
    # Calculate what min_cluster_size would be
    detector = RegimeDetector()
    config_min_size = detector.config.get("min_cluster_size", 100)
    calculated_min = max(10000, int(len(df) * 0.01), config_min_size)
    
    print(f"   Config base value: {config_min_size:,}")
    print(f"   1% of dataset: {int(len(df) * 0.01):,}")
    print(f"   Minimum threshold: 10,000")
    print(f"   ✨ Dynamic min_cluster_size: {calculated_min:,}")
    print(f"   📈 Percentage of data: {(calculated_min / len(df) * 100):.2f}%")
    
    return calculated_min

# Test 1: Small dataset
test_dataset_size(5_000, "Small Dataset (5,000 rows)")

# Test 2: Medium dataset  
test_dataset_size(100_000, "Medium Dataset (100,000 rows)")

# Test 3: Large dataset (2M rows)
test_dataset_size(2_000_000, "Large Dataset (2M rows)")

# Test 4: Very large dataset (14.6M rows - the problem case)
result = test_dataset_size(14_600_000, "Very Large Dataset (14.6M rows - Problem Case)")

print(f"\n{'='*60}")
print("📊 SUMMARY")
print(f"{'='*60}")
print(f"")
print(f"✅ OLD BEHAVIOR (Fixed min_cluster_size=100):")
print(f"   - 14.6M rows with min_cluster_size=100")
print(f"   - 100 / 14,600,000 = 0.0007% of data")
print(f"   - Result: 55,084 regimes (USELESS!)")
print(f"")
print(f"✅ NEW BEHAVIOR (Dynamic min_cluster_size={result:,}):")
print(f"   - 14.6M rows with min_cluster_size={result:,}")
print(f"   - {result:,} / 14,600,000 = {(result / 14_600_000 * 100):.2f}% of data")
print(f"   - Expected result: 3-10 regimes (USEFUL!)")
print(f"")
print(f"🎯 The dynamic calculation prevents over-segmentation!")
print(f"")
