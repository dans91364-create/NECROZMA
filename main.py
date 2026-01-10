#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚡🌟💎 ULTRA NECROZMA - MAIN ENTRY POINT 💎🌟⚡

The Blinding One Awakens
"From the void between dimensions, I emerge..."

Technical: Main execution script for Forex analysis
- CSV to Parquet conversion
- Full analysis pipeline
- Report generation

Usage: 
    python main.py                    # Full analysis
    python main.py --convert-only     # Only convert CSV to Parquet
    python main.py --analyze-only     # Only analyze (Parquet must exist)
    python main.py --sequential       # Run without parallelization
    python main.py --help             # Show help
"""

import sys
import os
import argparse
import time
from pathlib import Path

# Add current directory to path
sys.path. insert(0, str(Path(__file__).parent))

# ═══════════════════════════════════════════════════════════════
# 🌟 BANNER
# ═══════════════════════════════════════════════════════════════

BANNER = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║     ⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡     ║
║     ⚡                                                                    ⚡     ║
║     ⚡    🌟💎  ULTRA NECROZMA - THE BLINDING ONE  💎🌟                  ⚡     ║
║     ⚡                                                                    ⚡     ║
║     ⚡         "Light That Burns The Sky"                                ⚡     ║
║     ⚡                                                                    ⚡     ║
║     ⚡    ██╗   ██╗██╗  ████████╗██████╗  █████╗                         ⚡     ║
║     ⚡    ██║   ██║██║  ╚══██╔══╝██╔══██╗██╔══██╗                        ⚡     ║
║     ⚡    ██║   ██║██║     ██║   ██████╔╝███████║                        ⚡     ║
║     ⚡    ██║   ██║██║     ██║   ██╔══██╗██╔══██║                        ⚡     ║
║     ⚡    ╚██████╔╝███████╗██║   ██║  ██║██║  ██║                        ⚡     ║
║     ⚡     ╚═════╝ ╚══════╝╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝                        ⚡     ║
║     ⚡                                                                    ⚡     ║
║     ⚡    ███╗   ██╗███████╗ ██████╗██████╗  ██████╗ ███████╗███╗   ███╗ ⚡     ║
║     ⚡    ████╗  ██║██╔════╝██╔════╝██╔══██╗██╔═══██╗╚══███╔╝████╗ ████║ ⚡     ║
║     ⚡    ██╔██╗ ██║█████╗  ██║     ██████╔╝██║   ██║  ███╔╝ ██╔████╔██║ ⚡     ║
║     ⚡    ██║╚██╗██║██╔══╝  ██║     ██╔══██╗██║   ██║ ███╔╝  ██║╚██╔╝██║ ⚡     ║
║     ⚡    ██║ ╚████║███████╗╚██████╗██║  ██║╚██████╔╝███████╗██║ ╚═╝ ██║ ⚡     ║
║     ⚡    ╚═╝  ╚═══╝╚══════╝ ╚═════╝╚═╝  ╚═╝ ╚═════╝ ╚══════╝╚═╝     ╚═╝ ⚡     ║
║     ⚡                                                                    ⚡     ║
║     ⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡     ║
║                                                                              ║
║     Forex Analysis System with 500+ Features                                 ║
║     Powered by:  NumPy, Numba, PyArrow, Multiprocessing                       ║
║                                                                              ║
║     Evolution Chain:                                                          ║
║     🔥 Monster → 🦎 Charmander → 🔥 Charmeleon → 🐉 Charizard                ║
║     → ⚡ Arceus → 🌟 Ultra Necrozma                                          ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""


# ═══════════════════════════════════════════════════════════════
# 🔧 ARGUMENT PARSER
# ═══════════════════════════════════════════════════════════════

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse. ArgumentParser(
        description="⚡ Ultra Necrozma - Forex Analysis System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                     # Full analysis (convert + analyze)
  python main.py --convert-only      # Only convert CSV to Parquet
  python main.py --analyze-only      # Only analyze existing Parquet
  python main. py --sequential        # Disable parallel processing
  python main.py --workers 8         # Use 8 parallel workers
  python main.py --csv /path/to. csv  # Specify custom CSV path
        """
    )
    
    parser.add_argument(
        "--csv",
        type=str,
        help="Path to input CSV file (overrides config)"
    )
    
    parser.add_argument(
        "--parquet",
        type=str,
        help="Path to Parquet file (overrides config)"
    )
    
    parser.add_argument(
        "--convert-only",
        action="store_true",
        help="Only convert CSV to Parquet, skip analysis"
    )
    
    parser.add_argument(
        "--analyze-only",
        action="store_true",
        help="Only run analysis (Parquet must exist)"
    )
    
    parser.add_argument(
        "--sequential",
        action="store_true",
        help="Run analysis sequentially (no parallelization)"
    )
    
    parser.add_argument(
        "--workers",
        type=int,
        help="Number of parallel workers (overrides config)"
    )
    
    parser.add_argument(
        "--force-convert",
        action="store_true",
        help="Force re-conversion even if Parquet exists"
    )
    
    parser.add_argument(
        "--test",
        action="store_true",
        help="Run with test data (small sample)"
    )
    
    return parser.parse_args()


# ═══════════════════════════════════════════════════════════════
# 🔍 SYSTEM CHECK
# ═══════════════════════════════════════════════════════════════

def check_system():
    """Check system requirements and display info"""
    print("""
╔══════════════════════════════════════════════════════════════╗
║                 🔍 SYSTEM CHECK                              ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    issues = []
    
    # Python version
    py_version = sys.version_info
    print(f"   🐍 Python:  {py_version.major}.{py_version.minor}.{py_version.micro}", end="")
    if py_version.major >= 3 and py_version.minor >= 8:
        print(" ✅")
    else:
        print(" ⚠️ (3.8+ recommended)")
        issues.append("Python 3.8+ recommended")
    
    # NumPy
    try:
        import numpy as np
        print(f"   📊 NumPy: {np.__version__} ✅")
    except ImportError:
        print(f"   📊 NumPy: NOT FOUND ❌")
        issues.append("NumPy not installed")
    
    # Pandas
    try:
        import pandas as pd
        print(f"   🐼 Pandas: {pd.__version__} ✅")
    except ImportError:
        print(f"   🐼 Pandas: NOT FOUND ❌")
        issues.append("Pandas not installed")
    
    # PyArrow
    try:
        import pyarrow as pa
        print(f"   🏹 PyArrow: {pa.__version__} ✅")
    except ImportError:
        print(f"   🏹 PyArrow: NOT FOUND ❌")
        issues.append("PyArrow not installed (pip install pyarrow)")
    
    # SciPy
    try: 
        import scipy
        print(f"   🔬 SciPy: {scipy.__version__} ✅")
    except ImportError:
        print(f"   🔬 SciPy: NOT FOUND ❌")
        issues.append("SciPy not installed")
    
    # Numba
    try:
        import numba
        print(f"   ⚡ Numba:  {numba.__version__} ✅ (JIT enabled)")
    except ImportError: 
        print(f"   ⚡ Numba: NOT FOUND ⚠️ (optional, for speed)")
    
    # psutil
    try:
        import psutil
        mem = psutil.virtual_memory()
        mem_gb = mem.total / (1024**3)
        print(f"   💾 RAM: {mem_gb:.1f} GB", end="")
        if mem_gb >= 16:
            print(" ✅")
        else:
            print(" ⚠️ (16GB+ recommended)")
        
        cpu_count = psutil.cpu_count()
        print(f"   🖥️  CPUs: {cpu_count} ✅")
    except ImportError:
        print(f"   💾 psutil: NOT FOUND ⚠️")
    
    # tqdm
    try:
        import tqdm
        print(f"   📊 tqdm: {tqdm.__version__} ✅")
    except ImportError:
        print(f"   📊 tqdm: NOT FOUND ⚠️ (optional)")
    
    print()
    
    if issues:
        print("   ⚠️  Issues found:")
        for issue in issues:
            print(f"      • {issue}")
        print()
        print("   Install missing packages:  pip install -r requirements.txt")
        return False
    
    print("   ✅ All systems ready!")
    return True


# ═══════════════════════════════════════════════════════════════
# 🎮 MAIN EXECUTION
# ═══════════════════════════════════════════════════════════════

def main():
    """Main execution function"""
    
    # Parse arguments
    args = parse_arguments()
    
    # Show banner
    print(BANNER)
    
    # System check
    if not check_system():
        print("\n❌ System check failed.  Please install required packages.")
        print("   Run: pip install -r requirements.txt")
        sys.exit(1)
    
    # Import modules after system check
    from config import CSV_FILE, PARQUET_FILE, NUM_WORKERS, get_output_dirs
    from data_loader import crystallize_csv_to_parquet, load_crystal, crystal_info
    from analyzer import UltraNecrozmaAnalyzer
    from reports import light_that_burns_the_sky, generate_full_report, print_final_summary
    
    # Override config with arguments
    csv_path = Path(args.csv) if args.csv else CSV_FILE
    parquet_path = Path(args.parquet) if args.parquet else PARQUET_FILE
    num_workers = args.workers if args.workers else NUM_WORKERS
    parallel = not args.sequential
    
    # Create output directories
    output_dirs = get_output_dirs()
    
    # Track total time
    total_start = time.time()
    
    print(f"""
╔══════════════════════════════════════════════════════════════╗
║                 ⚙️  CONFIGURATION                             ║
╠══════════════════════════════════════════════════════════════╣
║   📂 CSV:       {str(csv_path): <43} ║
║   💎 Parquet:  {str(parquet_path):<43} ║
║   ⚡ Workers:  {num_workers: <43} ║
║   🔄 Parallel:  {str(parallel):<43} ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    # ═══════════════════════════════════════════════════════════
    # TEST MODE
    # ═══════════════════════════════════════���═══════════════════
    
    if args.test:
        print("""
╔══════════════════════════════════════════════════════════════╗
║                 🧪 TEST MODE                                  ║
╚══════════════════════════════════════════════════════════════╝
        """)
        
        import numpy as np
        import pandas as pd
        
        print("📊 Generating test data (100,000 ticks)...")
        
        np.random.seed(42)
        n_ticks = 100_000
        
        timestamps = pd.date_range("2025-01-01", periods=n_ticks, freq="1s")
        prices = 1. 10 + np.cumsum(np.random.randn(n_ticks) * 0.00005)
        
        df = pd.DataFrame({
            "timestamp": timestamps,
            "bid": prices - 0.00005,
            "ask": prices + 0.00005,
            "mid_price": prices,
            "spread_pips": 1. 0,
            "pips_change": np.concatenate([[0], np.diff(prices) * 10000])
        })
        
        print(f"   ✅ Generated {len(df):,} test ticks")
        
        # Run analysis with test data
        print("\n🌌 Running analysis on test data...")
        
        analyzer = UltraNecrozmaAnalyzer(df)
        results = analyzer.run_analysis(parallel=parallel)
        
        # Generate reports
        final_judgment = light_that_burns_the_sky(analyzer)
        
        if final_judgment: 
            report_paths = generate_full_report(analyzer, final_judgment)
            print_final_summary(analyzer, final_judgment, report_paths)
        
        total_time = time.time() - total_start
        print(f"\n⏱️  Total test time: {total_time:.1f}s")
        print("\n✅ Test complete!")
        
        return
    
    # ═══════════════════════════════════════════════════════════
    # STEP 1: CSV TO PARQUET CONVERSION
    # ═══════════════════════════════════════════════════════════
    
    if not args.analyze_only:
        print("""
╔══════════════════════════════════════════════════════════════╗
║          💎 STEP 1: CRYSTALLIZATION (CSV → Parquet)          ║
╚══════════════════════════════════════════════════════════════╝
        """)
        
        # Check if CSV exists
        if not csv_path.exists():
            print(f"""
   ❌ CSV file not found: {csv_path}
   
   Please either:
   1. Update CSV_FILE in config.py
   2. Use --csv /path/to/your/file.csv
   3. Use --test for test mode
            """)
            sys.exit(1)
        
        # Check if conversion needed
        if parquet_path.exists() and not args.force_convert:
            print(f"   💎 Parquet already exists: {parquet_path}")
            print(f"   Use --force-convert to re-convert")
            print()
        else:
            try:
                crystallize_csv_to_parquet(csv_path, parquet_path, force=args.force_convert)
            except Exception as e:
                print(f"\n   ❌ Crystallization failed: {e}")
                sys.exit(1)
    
    # Exit if convert-only
    if args.convert_only:
        print("\n✅ Conversion complete (--convert-only mode)")
        return
    
    # ═══════════════════════════════════════════════════════════
    # STEP 2: LOAD DATA
    # ═══════════════════════���═══════════════════════════════════
    
    print("""
╔══════════════════════════════════════════════════════════════╗
║              ⚡ STEP 2: LOADING CRYSTAL DATA                  ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    # Check if Parquet exists
    if not parquet_path.exists():
        print(f"""
   ❌ Parquet file not found: {parquet_path}
   
   Please run without --analyze-only first to convert CSV. 
        """)
        sys.exit(1)
    
    try:
        df = load_crystal(parquet_path)
        crystal_info(df)
    except Exception as e:
        print(f"\n   ❌ Failed to load crystal:  {e}")
        sys.exit(1)
    
    # ═══════════════════════════════════════════════════════════
    # STEP 3: ANALYSIS
    # ═══════════════════════════════════════════════════════════
    
    print("""
╔══════════════════════════════════════════════════════════════╗
║            🌌 STEP 3: DIMENSIONAL ANALYSIS                    ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    # Confirmation for large datasets
    if len(df) > 1_000_000:
        print(f"""
   ⚠️  Large dataset detected: {len(df):,} rows
   
   Estimated time:  2-5 hours
   
   Press ENTER to continue or Ctrl+C to cancel... 
        """)
        try:
            input()
        except KeyboardInterrupt:
            print("\n\n   ⚠️ Cancelled by user")
            sys.exit(0)
    
    try:
        # Initialize analyzer
        analyzer = UltraNecrozmaAnalyzer(df, output_dir=output_dirs["root"])
        
        # Run analysis
        results = analyzer.run_analysis(parallel=parallel)
        
        # Save intermediate results
        analyzer.save_results()
        
    except KeyboardInterrupt:
        print("\n\n   ⚠️ Analysis interrupted by user")
        print("   💾 Progress saved in checkpoints")
        sys.exit(0)
    except Exception as e:
        print(f"\n   ❌ Analysis failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    # ═══════════════════════════════════════════════════════════
    # STEP 4: FINAL JUDGMENT (Z-MOVE)
    # ═════════════════════════════════���═════════════════════════
    
    print("""
╔══════════════════════════════════════════════════════════════╗
║          ⚡💎🌟 STEP 4: Z-MOVE ACTIVATION 🌟💎⚡              ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    try:
        final_judgment = light_that_burns_the_sky(analyzer)
    except Exception as e:
        print(f"\n   ❌ Z-Move failed: {e}")
        final_judgment = None
    
    # ═══════════════════════════════════════════════════════════
    # STEP 5: REPORT GENERATION
    # ═══════════════════════════════════════════════════════════
    
    print("""
╔══════════════════════════════════════════════════════════════╗
║              💾 STEP 5: CRYSTAL ARCHIVE                       ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    report_paths = {}
    
    if final_judgment:
        try:
            report_paths = generate_full_report(analyzer, final_judgment)
        except Exception as e:
            print(f"\n   ❌ Report generation failed: {e}")
    
    # ═══════════════════════════════════════════════════════════
    # FINAL SUMMARY
    # ═══════════════════════════════════════════════════════════
    
    total_time = time.time() - total_start
    
    if final_judgment and report_paths:
        print_final_summary(analyzer, final_judgment, report_paths)
    
    print(f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║                    ⚡🌟💎 MISSION COMPLETE 💎🌟⚡                            ║
║                                                                              ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║   ⏱️  Total Time:         {total_time: >10.1f} seconds                                  ║
║                          {total_time/60:>10.1f} minutes                                   ║
║                          {total_time/3600:>10.2f} hours                                     ║
║                                                                              ║
║   📂 Results saved in:   {str(output_dirs['root']):<50} ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝

   "The light has revealed all patterns.  Use this knowledge wisely."
   
                        - Ultra Necrozma, The Blinding One
    """)


# ═══════════════════════════════════════════════════════════════
# 🚀 ENTRY POINT
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__": 
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ Interrupted by user")
        sys.exit(0)
    except Exception as e: 
        print(f"\n\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)