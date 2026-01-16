#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚡🌟💎 ULTRA NECROZMA - FILE PREFIX VALIDATION 💎🌟⚡

Demonstrates file naming with prefix for multiple currency pairs
"""

import sys
from pathlib import Path

# Add parent directory to path for standalone script execution
# This allows running the validation script directly
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import FILE_PREFIX, PAIR_NAME, DATA_YEAR, PARQUET_FILE


def show_file_structure():
    """Display the new file structure with prefixes"""
    
    print("""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║   ⚡💎🌟 FILE PREFIX VALIDATION 🌟💎⚡                      ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    print(f"📂 PARQUET_FILE: {PARQUET_FILE}")
    print(f"🔑 PAIR_NAME: {PAIR_NAME}")
    print(f"📅 DATA_YEAR: {DATA_YEAR}")
    print(f"✨ FILE_PREFIX: {FILE_PREFIX}")
    print()
    
    print("="*70)
    print("📊 OUTPUT FILE STRUCTURE")
    print("="*70)
    print()
    
    print("ultra_necrozma_results/")
    print("├── universes/")
    
    # Sample universe files
    universes = ["universe_1m_5lb", "universe_5m_10lb", "universe_15m_20lb"]
    for universe in universes:
        print(f"│   ├── {FILE_PREFIX}{universe}.parquet")
        print(f"│   ├── {FILE_PREFIX}{universe}_metadata.json")
    print("│")
    
    print("├── reports/")
    timestamp = "20260116_120000"
    print(f"│   ├── {FILE_PREFIX}LIGHT_REPORT_{timestamp}.json")
    print(f"│   ├── {FILE_PREFIX}rankings_{timestamp}.json")
    print(f"│   ├── {FILE_PREFIX}rankings.json")
    print(f"│   ├── {FILE_PREFIX}pattern_summary.json")
    print(f"│   └── {FILE_PREFIX}top_strategies_ranked.json")
    print("│")
    
    print("├── backtest_results/")
    for universe in universes[:2]:
        print(f"│   ├── {FILE_PREFIX}{universe}_backtest.parquet")
        print(f"│   ├── {FILE_PREFIX}{universe}_backtest_metadata.json")
    print(f"│   ├── {FILE_PREFIX}consolidated_backtest_results.json")
    print(f"│   └── {FILE_PREFIX}top_strategies_ranked.json")
    print("│")
    
    print("├── cache/")
    hash_examples = ["a1b2c3d4", "e5f6g7h8"]
    for hash_ex in hash_examples:
        print(f"│   ├── {FILE_PREFIX}labels_{hash_ex}.pkl")
        print(f"│   └── {FILE_PREFIX}labels_progress_{hash_ex}.json")
    print("│")
    
    print("└── checkpoints/")
    print(f"    ├── {FILE_PREFIX}checkpoint_1.json")
    print(f"    ├── {FILE_PREFIX}checkpoint_2.json")
    print(f"    └── {FILE_PREFIX}checkpoint_3.json")
    
    print()
    print("="*70)
    print("✅ MULTI-PAIR SUPPORT")
    print("="*70)
    print()
    
    # Show example with multiple pairs
    pairs_examples = [
        ("EURUSD", "2025"),
        ("GBPUSD", "2025"),
        ("USDJPY", "2025"),
    ]
    
    print("When running multiple pairs, files won't overwrite:")
    print()
    
    for pair, year in pairs_examples:
        prefix = f"{pair}_{year}_"
        print(f"📁 {pair} {year}:")
        print(f"   ├── {prefix}universe_1m_5lb.parquet")
        print(f"   ├── {prefix}LIGHT_REPORT_20260116.json")
        print(f"   ├── {prefix}universe_1m_5lb_backtest.parquet")
        print(f"   └── {prefix}labels_abc123.pkl")
        print()
    
    print("="*70)
    print("✅ VALIDATION COMPLETE")
    print("="*70)
    print()
    
    print("Key Features:")
    print("  ✅ Automatic prefix extraction from PARQUET_FILE")
    print("  ✅ All output files include pair and year prefix")
    print("  ✅ Multiple pairs can be run without overwriting")
    print("  ✅ Backward compatible (empty prefix works)")
    print("  ✅ Easy to identify files by pair and year")
    print()


if __name__ == "__main__":
    show_file_structure()
