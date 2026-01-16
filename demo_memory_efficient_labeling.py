#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚡🌟💎 NECROZMA - MEMORY-EFFICIENT LABELING DEMO 💎🌟⚡

This script demonstrates the new memory-efficient labeling system that:
- Saves each config immediately to disk (no RAM overflow!)
- Supports resume after crashes
- Processes 210 configs with only ~5-10GB RAM (vs ~500GB before)
"""

import numpy as np
import pandas as pd
from pathlib import Path
from labeler import label_dataframe, load_label_results, load_all_label_results

def demo_memory_efficient_labeling():
    """Demonstrate memory-efficient labeling"""
    
    print("""
╔══════════════════════════════════════════════════════════════╗
║     ⚡ MEMORY-EFFICIENT LABELING DEMONSTRATION ⚡            ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    # Generate sample data
    print("📊 Generating sample data (500 candles)...")
    np.random.seed(42)
    n_candles = 500
    timestamps = pd.date_range("2025-01-01", periods=n_candles, freq="1min")
    prices = 1.10 + np.cumsum(np.random.randn(n_candles) * 0.0001)
    
    df = pd.DataFrame({
        "timestamp": timestamps,
        "mid_price": prices,
    })
    print(f"   ✅ Generated {len(df):,} candles\n")
    
    # Label with small subset (to keep demo fast)
    print("🏷️  Labeling with 4 configurations (small subset for demo)...")
    print("   Targets: [10, 20]")
    print("   Stops: [5]")
    print("   Horizons: [30, 60]\n")
    
    # Run memory-efficient labeling
    saved_files = label_dataframe(
        df,
        target_pips=[10, 20],
        stop_pips=[5],
        horizons=[30, 60],
        use_cache=False,
        return_dict=False  # ← Memory-efficient mode!
    )
    
    print(f"\n✅ Labeling complete!")
    print(f"   💾 Saved {len(saved_files)} parquet files to labels/\n")
    
    # Demonstrate loading specific config
    print("📂 Loading specific config (T10_S5_H30)...")
    result_df = load_label_results("T10_S5_H30")
    print(f"   ✅ Loaded {len(result_df):,} rows")
    print(f"   📊 Columns: {list(result_df.columns[:5])}...\n")
    
    # Show resume capability
    print("🔄 Demonstrating RESUME capability...")
    print("   Running labeling again with MORE configs...")
    saved_files_2 = label_dataframe(
        df,
        target_pips=[10, 20, 30],  # Added 30!
        stop_pips=[5],
        horizons=[30, 60],
        use_cache=False,
        return_dict=False
    )
    
    print(f"\n   ⏭️  Notice: Skipped existing files and only processed new ones!")
    print(f"   💾 Total files: {len(saved_files_2)}\n")
    
    # List all saved files
    print("📋 All saved label files:")
    for f in sorted(Path("labels").glob("*.parquet")):
        size_kb = f.stat().st_size / 1024
        print(f"   • {f.name} ({size_kb:.1f} KB)")
    
    print("""
╔══════════════════════════════════════════════════════════════╗
║                    KEY BENEFITS                              ║
╠══════════════════════════════════════════════════════════════╣
║  ✅ Low Memory: Only ~5-10GB RAM (vs ~500GB before!)        ║
║  ✅ Resume Support: Restart after crash without data loss   ║
║  ✅ 210 Files: Each config saved individually               ║
║  ✅ Fast Loading: Load only configs you need                ║
╚══════════════════════════════════════════════════════════════╝

💡 TIP: Use load_label_results(config_key) to load specific configs
⚠️  WARNING: load_all_label_results() loads everything (memory-intensive!)

🔧 BACKWARD COMPATIBILITY:
   Use return_dict=True to get old behavior (loads all into RAM)
    """)
    
    # Cleanup
    print("\n🧹 Cleaning up demo files...")
    import shutil
    if Path("labels").exists():
        shutil.rmtree("labels")
    print("   ✅ Done!\n")

if __name__ == "__main__":
    demo_memory_efficient_labeling()
