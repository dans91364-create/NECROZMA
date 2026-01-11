#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚡🌟💎 ULTRA NECROZMA - MAIN SYSTEM 💎🌟⚡

The Supreme Analysis System - Complete Trading Strategy Discovery
"From raw light to eternal wisdom - the complete transformation"

Technical: Main entry point for NECROZMA system
- CSV to Parquet conversion
- Feature extraction across multiple dimensions
- Strategy discovery pipeline
- Backtesting and ranking
- Final report generation
"""

import sys
import os
import time
import argparse
import warnings
from pathlib import Path
from datetime import datetime
import multiprocessing as mp

warnings.filterwarnings("ignore")

# Local imports
from config import (
    CSV_FILE, PARQUET_FILE, OUTPUT_DIR, THEME,
    NUM_WORKERS, INTERVALS, LOOKBACKS,
    get_all_configs, get_output_dirs, set_random_seeds,
    TELEGRAM_ENABLED, TEST_MODE_CONFIG
)
from data_loader import crystallize_csv_to_parquet, load_parquet_data
from analyzer import UltraNecrozmaAnalyzer
from reports import light_that_burns_the_sky
from test_mode import TestModeSampler


# ═══════════════════════════════════════════════════════════════
# 🌟 BANNER
# ═══════════════════════════════════════════════════════════════

BANNER = """
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║      ⚡💎�� ULTRA NECROZMA - THE BLINDING ONE 🌟💎⚡        ║
║                                                              ║
║           "Light That Burns The Sky"                        ║
║                                                              ║
║   Complete Strategy Discovery System for Forex Trading      ║
║   From Raw Tick Data to Validated Trading Strategies        ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝

📊 Features:
   • 500+ mathematical features extracted per pattern
   • Multi-dimensional analysis (5 intervals × 5 lookbacks)
   • Parallel processing with 16 cores
   • Strategy discovery with ML-based ranking
   • Telegram notifications (optional)

🎮 Deities:
   ⚪ ARCEUS  - Genesis & Synthesis
   🔵 DIALGA  - Temporal Features
   🟣 PALKIA  - Spatial Features
   ⚫ GIRATINA - Chaos & Regimes
   🌟 NECROZMA - Final Strategy Synthesis

"""


# ═══════════════════════════════════════════════════════════════
# 🔍 SYSTEM CHECK
# ═══════════════════════════════════════════════════════════════

def check_system():
    """
    Verify system requirements and dependencies
    Technical: Check for required Python packages
    
    Returns:
        bool: True if all checks pass
    """
    print("🔍 SYSTEM CHECK")
    print("─" * 60)
    
    # Python version
    python_version = sys.version_info
    print(f"✅ Python: {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    # Required packages
    required = {
        "numpy": "NumPy",
        "pandas": "Pandas",
        "scipy": "SciPy",
    }
    
    optional = {
        "pyarrow": "PyArrow (for fast Parquet I/O)",
        "sklearn": "scikit-learn (for ML features)",
        "xgboost": "XGBoost (for strategy discovery)",
        "lightgbm": "LightGBM (for strategy discovery)",
        "hdbscan": "HDBSCAN (for regime detection)",
        "shap": "SHAP (for feature importance)",
    }
    
    missing_required = []
    missing_optional = []
    
    # Check required
    for module, name in required.items():
        try:
            __import__(module)
            print(f"✅ {name}")
        except ImportError:
            print(f"❌ {name} - REQUIRED")
            missing_required.append(name)
    
    # Check optional
    for module, name in optional.items():
        try:
            __import__(module)
            print(f"✅ {name}")
        except ImportError:
            print(f"⚠️  {name} - Optional (needed for strategy discovery)")
            missing_optional.append(name)
    
    print()
    
    if missing_required:
        print(f"❌ Missing required packages: {', '.join(missing_required)}")
        print("   Install with: pip install -r requirements.txt")
        return False
    
    if missing_optional:
        print(f"⚠️  Missing optional packages: {', '.join(missing_optional)}")
        print("   Some features may not work. Install with: pip install -r requirements.txt")
    
    # CPU cores
    cores = mp.cpu_count()
    print(f"✅ CPU Cores: {cores} (using {NUM_WORKERS} workers)")
    print()
    
    return True


# ═══════════════════════════════════════════════════════════════
# 🔮 STRATEGY DISCOVERY PIPELINE
# ═══════════════════════════════════════════════════════════════

def run_strategy_discovery(df, analyzer_results, skip_telegram=False):
    """
    Run complete strategy discovery pipeline
    Technical: Execute 7-step ML-based strategy discovery
    
    Args:
        df: DataFrame with tick data
        analyzer_results: Results from feature extraction
        skip_telegram: Disable Telegram notifications
        
    Returns:
        dict: Discovery results
    """
    print("""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║        🌟 STRATEGY DISCOVERY PIPELINE 🌟                     ║
║                                                              ║
║   "From patterns to profit - the ultimate synthesis"        ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    pipeline_start = time.time()
    
    # Initialize Telegram if enabled
    telegram = None
    if TELEGRAM_ENABLED and not skip_telegram:
        try:
            from telegram_notifier import TelegramNotifier
            telegram = TelegramNotifier()
            telegram.send_event("AWAKENING", "NECROZMA", {
                "message": "Strategy Discovery Pipeline Initiated",
                "steps": 7
            })
        except Exception as e:
            print(f"⚠️  Telegram disabled: {e}")
    
    results = {}
    
    # ═══ STEP 1: LABELING ═══
    print("\n🏷️  STEP 1/7: Multi-Dimensional Labeling")
    print("─" * 60)
    step_start = time.time()
    
    try:
        from labeler import label_outcomes
        
        print("   Labeling outcomes with multiple targets, stops, and horizons...")
        labels = label_outcomes(df)
        results["labels"] = labels
        
        step_time = time.time() - step_start
        print(f"   ✅ Labeling complete: {len(labels):,} candles labeled ({step_time:.1f}s)")
        
        if telegram:
            telegram.send_event("PROGRESS", "DIALGA", {
                "step": "Labeling",
                "candles_labeled": len(labels),
                "time_seconds": step_time
            })
    
    except Exception as e:
        print(f"   ⚠️  Labeling failed: {e}")
        results["labels"] = None
    
    # ═══ STEP 2: REGIME DETECTION ═══
    print("\n�� STEP 2/7: Regime Detection")
    print("─" * 60)
    step_start = time.time()
    
    try:
        from regime_detector import detect_regimes
        
        print("   Detecting market regimes using clustering...")
        regimes = detect_regimes(df)
        results["regimes"] = regimes
        
        n_regimes = len(regimes.get("regime_summary", {}))
        step_time = time.time() - step_start
        print(f"   ✅ Regime detection complete: {n_regimes} regimes found ({step_time:.1f}s)")
        
        if telegram:
            telegram.send_event("DISCOVERY", "GIRATINA", {
                "discovery": "Market Regimes",
                "n_regimes": n_regimes,
                "method": "Clustering"
            })
    
    except Exception as e:
        print(f"   ⚠️  Regime detection failed: {e}")
        results["regimes"] = None
    
    # ═══ STEP 3: PATTERN MINING ═══
    print("\n⛏️  STEP 3/7: Pattern Mining & Feature Importance")
    print("─" * 60)
    step_start = time.time()
    
    try:
        from pattern_miner import mine_patterns
        
        print("   Mining patterns with XGBoost, LightGBM, and SHAP...")
        patterns = mine_patterns(analyzer_results, results.get("labels"))
        results["patterns"] = patterns
        
        n_important = len(patterns.get("important_features", []))
        step_time = time.time() - step_start
        print(f"   ✅ Pattern mining complete: {n_important} important features ({step_time:.1f}s)")
        
        if telegram:
            telegram.send_event("INSIGHT", "PALKIA", {
                "insight": "Feature Importance",
                "n_important_features": n_important
            })
    
    except Exception as e:
        print(f"   ⚠️  Pattern mining failed: {e}")
        results["patterns"] = None
    
    # ═══ STEP 4: STRATEGY GENERATION ═══
    print("\n🏭 STEP 4/7: Strategy Generation")
    print("─" * 60)
    step_start = time.time()
    
    try:
        from strategy_factory import generate_strategies
        
        print("   Generating strategy candidates...")
        strategies = generate_strategies(results.get("patterns"))
        results["strategies"] = strategies
        
        n_strategies = len(strategies)
        step_time = time.time() - step_start
        print(f"   ✅ Strategy generation complete: {n_strategies} strategies ({step_time:.1f}s)")
        
        if telegram:
            telegram.send_event("PROGRESS", "ARCEUS", {
                "step": "Strategy Generation",
                "n_strategies": n_strategies
            })
    
    except Exception as e:
        print(f"   ⚠️  Strategy generation failed: {e}")
        results["strategies"] = []
    
    # ═══ STEP 5: BACKTESTING ═══
    print("\n📊 STEP 5/7: Backtesting")
    print("─" * 60)
    step_start = time.time()
    
    try:
        from backtester import Backtester
        
        print("   Backtesting strategies with walk-forward validation...")
        backtester = Backtester()
        backtest_results = []
        
        for i, strategy in enumerate(results.get("strategies", [])):
            if (i + 1) % 10 == 0:
                print(f"   Progress: {i+1}/{len(results['strategies'])} strategies tested")
            
            try:
                result = backtester.backtest(strategy, df)
                backtest_results.append(result)
            except Exception as e:
                print(f"   ⚠️  Strategy {strategy.name} failed: {e}")
        
        results["backtest_results"] = backtest_results
        
        step_time = time.time() - step_start
        print(f"   ✅ Backtesting complete: {len(backtest_results)} strategies tested ({step_time:.1f}s)")
        
        if telegram:
            telegram.send_event("MILESTONE", "DIALGA", {
                "milestone": "Backtesting Complete",
                "strategies_tested": len(backtest_results)
            })
    
    except Exception as e:
        print(f"   ⚠️  Backtesting failed: {e}")
        results["backtest_results"] = []
    
    # ═══ STEP 6: RANKING ═══
    print("\n🌟 STEP 6/7: Strategy Ranking")
    print("─" * 60)
    step_start = time.time()
    
    try:
        from light_finder import LightFinder
        
        print("   Ranking strategies with multi-objective optimization...")
        finder = LightFinder()
        rankings = finder.rank_strategies(results.get("backtest_results", []))
        results["rankings"] = rankings
        
        step_time = time.time() - step_start
        print(f"   ✅ Ranking complete: Top strategies identified ({step_time:.1f}s)")
        
        if rankings is not None and len(rankings) > 0:
            best = rankings.iloc[0]
            print(f"\n   💎 BEST STRATEGY: {best['strategy_name']}")
            print(f"      Score: {best['composite_score']:.3f}")
            print(f"      Return: {best['total_return']:.2%}")
            print(f"      Sharpe: {best['sharpe_ratio']:.2f}")
            print(f"      Win Rate: {best['win_rate']:.2%}")
            
            if telegram:
                telegram.send_event("LIGHT_FOUND", "NECROZMA", {
                    "strategy": best['strategy_name'],
                    "score": float(best['composite_score']),
                    "return": float(best['total_return']),
                    "sharpe": float(best['sharpe_ratio'])
                })
    
    except Exception as e:
        print(f"   ⚠️  Ranking failed: {e}")
        results["rankings"] = None
    
    # ═══ STEP 7: FINAL REPORT ═══
    print("\n📝 STEP 7/7: Final Report Generation")
    print("─" * 60)
    step_start = time.time()
    
    try:
        from light_report import LightReportGenerator
        
        print("   Generating 'Where The Light Is' report...")
        report_gen = LightReportGenerator()
        report = report_gen.generate_report(
            results.get("rankings"),
            results.get("patterns"),
            results.get("regimes"),
            results.get("backtest_results")
        )
        results["final_report"] = report
        
        # Save report
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = OUTPUT_DIR / "reports" / f"LIGHT_REPORT_{timestamp}.json"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(report_path, 'w') as f:
            import json
            json.dump(report, f, indent=2)
        
        step_time = time.time() - step_start
        print(f"   ✅ Report saved: {report_path} ({step_time:.1f}s)")
        
        if telegram:
            telegram.send_event("COMPLETION", "NECROZMA", {
                "report_path": str(report_path),
                "total_time_minutes": (time.time() - pipeline_start) / 60
            })
            
            # Send report file
            try:
                telegram.send_document(str(report_path), "Where The Light Is - Final Report")
            except:
                pass
    
    except Exception as e:
        print(f"   ⚠️  Report generation failed: {e}")
        results["final_report"] = None
    
    # Pipeline summary
    total_time = time.time() - pipeline_start
    print(f"""
╔══════════════════════════════════════════════════════════════╗
║               STRATEGY DISCOVERY COMPLETE                    ║
╚══════════════════════════════════════════════════════════════╝

⏱️  Total Time: {total_time / 60:.1f} minutes
�� Strategies Generated: {len(results.get('strategies', []))}
✅ Strategies Tested: {len(results.get('backtest_results', []))}
🌟 Viable Strategies: {len(results.get('rankings', [])) if results.get('rankings') is not None else 0}

"The light has been found. WHERE THE LIGHT IS, now you know."
    """)
    
    return results


# ═══════════════════════════════════════════════════════════════
# 🚀 MAIN EXECUTION FUNCTION
# ═══════════════════════════════════════════════════════════════

def main():
    """
    Main execution function
    Technical: Orchestrate complete analysis pipeline
    """
    # Parse arguments
    parser = argparse.ArgumentParser(
        description="⚡🌟💎 Ultra Necrozma - Complete Strategy Discovery System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Full analysis with strategy discovery
  python main.py --strategy-discovery
  
  # Test mode with minimal sampling
  python main.py --test-mode --test-strategy minimal
  
  # Test mode with strategy discovery
  python main.py --test-mode --test-strategy balanced --strategy-discovery
  
  # Convert CSV to Parquet only
  python main.py --convert-only
  
  # Analysis only (Parquet must exist)
  python main.py --analyze-only
        """
    )
    
    # Data options
    parser.add_argument(
        "--csv",
        type=str,
        help="Path to CSV file (overrides config)"
    )
    
    parser.add_argument(
        "--parquet",
        type=str,
        help="Path to Parquet file (overrides config)"
    )
    
    # Execution modes
    parser.add_argument(
        "--convert-only",
        action="store_true",
        help="Only convert CSV to Parquet, then exit"
    )
    
    parser.add_argument(
        "--analyze-only",
        action="store_true",
        help="Only run analysis (skip conversion)"
    )
    
    parser.add_argument(
        "--force-convert",
        action="store_true",
        help="Force re-conversion of Parquet even if it exists"
    )
    
    # Processing options
    parser.add_argument(
        "--sequential",
        action="store_true",
        help="Run analysis sequentially (no multiprocessing)"
    )
    
    parser.add_argument(
        "--workers",
        type=int,
        default=NUM_WORKERS,
        help=f"Number of parallel workers (default: {NUM_WORKERS})"
    )
    
    # Test Mode arguments (PR #3)
    parser.add_argument(
        "--test-mode",
        action="store_true",
        help="Run in test mode with sampled data"
    )
    
    parser.add_argument(
        "--test-strategy",
        type=str,
        default="balanced",
        choices=["minimal", "quick", "balanced", "thorough"],
        help="Test sampling strategy (default: balanced)"
    )
    
    parser.add_argument(
        "--test-weeks",
        type=int,
        default=4,
        help="Number of weeks to sample for testing (default: 4)"
    )
    
    parser.add_argument(
        "--test-seed",
        type=int,
        default=42,
        help="Random seed for reproducible test samples (default: 42)"
    )
    
    parser.add_argument(
        "--strategy-discovery",
        action="store_true",
        help="Run complete strategy discovery pipeline (labeling, regime detection, backtesting, ranking)"
    )
    
    parser.add_argument(
        "--skip-telegram",
        action="store_true",
        help="Disable Telegram notifications"
    )
    
    args = parser.parse_args()
    
    # Display banner
    print(BANNER)
    
    # System check
    if not check_system():
        print("❌ System check failed. Please install required dependencies.")
        sys.exit(1)
    
    # Set random seeds for reproducibility
    set_random_seeds()
    
    # Create output directories
    output_dirs = get_output_dirs()
    print(f"📂 Output Directory: {OUTPUT_DIR}")
    print()
    
    # Determine file paths
    csv_file = Path(args.csv) if args.csv else CSV_FILE
    parquet_file = Path(args.parquet) if args.parquet else PARQUET_FILE
    
    start_time = time.time()
    
    # ═══ STEP 1: CSV → PARQUET CONVERSION ═══
    if not args.analyze_only:
        print("💎 STEP 1: Data Crystallization (CSV → Parquet)")
        print("═" * 60)
        
        try:
            parquet_file = crystallize_csv_to_parquet(
                csv_path=csv_file,
                parquet_path=parquet_file,
                force=args.force_convert
            )
            print(f"✅ Parquet ready: {parquet_file}\n")
        except Exception as e:
            print(f"❌ Crystallization failed: {e}")
            if not parquet_file.exists():
                sys.exit(1)
            print(f"⚠️  Using existing Parquet: {parquet_file}\n")
        
        if args.convert_only:
            print("✅ Conversion complete. Exiting (--convert-only mode).")
            sys.exit(0)
    
    # ═══ STEP 2: LOAD DATA ═══
    print("⚡ STEP 2: Loading Parquet Data")
    print("═" * 60)
    
    try:
        df = load_parquet_data(parquet_file)
        print(f"✅ Data loaded: {len(df):,} ticks")
        print(f"   Timespan: {df['timestamp'].min()} to {df['timestamp'].max()}")
        print()
    except Exception as e:
        print(f"❌ Failed to load data: {e}")
        sys.exit(1)
    
    # ═══ STEP 3: TEST MODE SAMPLING (PR #3) ═══
    if args.test_mode:
        print("🧪 STEP 3: Test Mode - Data Sampling")
        print("═" * 60)
        
        try:
            sampler = TestModeSampler(seed=args.test_seed)
            df = sampler.get_test_sample(
                df,
                strategy=args.test_strategy,
                total_weeks=args.test_weeks
            )
            
            if len(df) == 0:
                print("❌ No data after sampling. Exiting.")
                sys.exit(1)
            
            print(f"✅ Test data ready: {len(df):,} ticks")
            print()
        except Exception as e:
            print(f"❌ Test mode sampling failed: {e}")
            sys.exit(1)
    
    # ═══ STEP 4: FEATURE EXTRACTION ═══
    print("🌌 STEP 4: Feature Extraction & Analysis")
    print("═" * 60)
    
    try:
        # Create analyzer
        analyzer = UltraNecrozmaAnalyzer(
            df=df,
            num_workers=1 if args.sequential else args.workers
        )
        
        # Get all configurations
        configs = get_all_configs()
        print(f"📊 Analysis Matrix: {len(INTERVALS)} intervals × {len(LOOKBACKS)} lookbacks = {len(configs)} universes")
        print()
        
        # Run analysis
        print("🚀 Starting parallel analysis...")
        print()
        
        analyzer.analyze_all_universes()
        
        print()
        print(f"✅ Feature extraction complete!")
        print()
    
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    # ═══ STEP 5: STRATEGY DISCOVERY (OPTIONAL) ═══
    if args.strategy_discovery:
        try:
            discovery_results = run_strategy_discovery(
                df=df,
                analyzer_results=analyzer.results,
                skip_telegram=args.skip_telegram
            )
        except Exception as e:
            print(f"❌ Strategy discovery failed: {e}")
            import traceback
            traceback.print_exc()
    
    # ═══ STEP 6: GENERATE REPORTS ═══
    print("📊 STEP 6: Generating Reports")
    print("═" * 60)
    
    try:
        final_judgment = light_that_burns_the_sky(analyzer)
        print("✅ Reports generated!")
        print()
    except Exception as e:
        print(f"⚠️  Report generation failed: {e}")
        print()
    
    # ═══ FINAL SUMMARY ═══
    total_time = time.time() - start_time
    
    print("""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║         ⚡💎🌟 ULTRA NECROZMA COMPLETE 🌟💎⚡              ║
║                                                              ║
║           "Light That Burns The Sky"                        ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    print(f"⏱️  Total Execution Time: {total_time / 60:.1f} minutes")
    print(f"📂 Results saved to: {OUTPUT_DIR}")
    
    if args.strategy_discovery:
        print(f"📝 Light Report: {OUTPUT_DIR / 'reports'}")
    
    print()
    print("🌟 The analysis is complete. The light has been found.")
    print()


# ═══════════════════════════════════════════════════════════════
# 🎮 ENTRY POINT
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user. Exiting gracefully...")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
