#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚡🌟💎 ULTRA NECROZMA - PROGRESS INDICATOR DEMO 💎🌟⚡

Demonstration of progress indicators in label processing
This script shows how the progress bars look during actual label processing.
"""

import numpy as np
import pandas as pd
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from labeler import label_dataframe

def main():
    """Demo the progress indicators"""
    
    print("=" * 80)
    print("⚡🌟💎 ULTRA NECROZMA - Progress Indicator Demo 💎🌟⚡")
    print("=" * 80)
    print()
    print("This demo shows the new progress indicators for label processing.")
    print("Watch the nested progress bars as they process multiple configurations!")
    print()
    
    # Create sample data
    print("📊 Creating sample data...")
    n_samples = 500
    timestamps = pd.date_range('2025-01-01', periods=n_samples, freq='1s')
    
    # Generate realistic price movements
    base_price = 1.1000
    np.random.seed(42)  # For reproducibility
    noise = np.random.randn(n_samples) * 0.0001
    cumsum = np.cumsum(noise)
    
    df = pd.DataFrame({
        'timestamp': timestamps,
        'mid_price': base_price + cumsum,
        'bid': base_price + cumsum - 0.00005,
        'ask': base_price + cumsum + 0.00005,
    })
    
    print(f"✅ Created {len(df):,} data points")
    print()
    
    # Configure labeling (small set for demo)
    print("🏷️  Labeling Configuration:")
    target_pips = [5, 10, 15]     # 3 targets
    stop_pips = [5, 10]            # 2 stops
    horizons = [2, 5, 10]          # 3 horizons
    # Total: 3 * 2 * 3 = 18 configurations
    
    print(f"   Targets: {target_pips} pips")
    print(f"   Stops: {stop_pips} pips")
    print(f"   Horizons: {horizons} minutes")
    print(f"   Total configurations: {len(target_pips) * len(stop_pips) * len(horizons)}")
    print()
    
    # Run labeling with progress bars
    print("🚀 Starting labeling with progress indicators...")
    print("-" * 80)
    print()
    
    results = label_dataframe(
        df,
        target_pips=target_pips,
        stop_pips=stop_pips,
        horizons=horizons,
        num_workers=4,
        use_cache=False
    )
    
    print()
    print("-" * 80)
    print("✅ Demo Complete!")
    print()
    print("Progress Indicators Demonstrated:")
    print("  ✅ Main progress bar showing % complete across all labels")
    print("  ✅ Current label being processed (e.g., T3_S5_H2)")
    print("  ✅ Time elapsed and time remaining estimates")
    print("  ✅ Processing rate (labels/second)")
    print("  ✅ Nested progress bar for chunk processing within each label")
    print()
    print(f"📊 Results: Generated {len(results)} labeled datasets")
    print()
    
    # Show sample results
    if results:
        sample_key = list(results.keys())[0]
        sample_df = results[sample_key]
        print(f"Sample result ({sample_key}):")
        print(f"  Labeled candles: {len(sample_df):,}")
        if len(sample_df) > 0:
            print(f"  Columns: {', '.join(sample_df.columns.tolist())}")
    
    print()
    print("=" * 80)


if __name__ == '__main__':
    main()
