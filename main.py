#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚡🌟💎 ULTRA NECROZMA - MAIN ENTRY POINT 💎🌟⚡

The Blinding One Awakens
"From the void between dimensions, I emerge..."
"""

import sys
import os
import argparse
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))


# ═══════════════════════════════════════════════════════════════
# 🌟 ULTRA NECROZMA ASCII BANNER
# ═══════════════════════════════════════════════════════════════

ULTRA_NECROZMA_BANNER = r"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║                    ⚡🌟💎 ULTRA NECROZMA 💎🌟⚡                              ║
║                                                                              ║
║                         The Blinding One Awakens                            ║
║                   "Light That Burns The Sky - Supreme Form"                 ║
║                                                                              ║
║                              ⚡                                              ║
║                            ⚡ ║ ⚡                                            ║
║                          ⚡  ╔╩╗  ⚡                                          ║
║                         ⚡  ╔╝ ╚╗  ⚡                                         ║
║                        ⚡  ╔╝   ╚╗  ⚡                                        ║
║                       ⚡  ╔╝  💎  ╚╗  ⚡                                       ║
║                      ⚡═══╣  ╔═╗  ╠═══⚡                                      ║
║                     ⚡    ╚══╣ ╠══╝    ⚡                                     ║
║                    ⚡      ╔═╩═╩═╗      ⚡                                    ║
║                   ⚡     ╔═╝ 🌟 ╚═╗     ⚡                                   ║
║                  ⚡    ╔═╝  ╔═╗  ╚═╗    ⚡                                  ║
║                 ⚡   ╔═╝   ╔╝ ╚╗   ╚═╗   ⚡                                 ║
║                ⚡  ╔═╝    ╔╝   ╚╗    ╚═╗  ⚡                                ║
║                  ╔╝      ║     ║      ╚╗                                    ║
║                 ╔╝       ║     ║       ╚╗                                   ║
║                ╔╝        ║     ║        ╚╗                                  ║
║               ╔╝         ║     ║         ╚╗                                 ║
║              💎         ╔╝     ╚╗         💎                                ║
║                       ⚡         ⚡                                          ║
║                                                                              ║
║  Supreme Analysis Engine - Complete Strategy Discovery System                ║
║  "Where infinite dimensions converge into pure light..."                    ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""


# ═══════════════════════════════════════════════════════════════
# 🔧 ARGUMENT PARSER
# ═══════════════════════════════════════════════════════════════

def parse_arguments():
    """
    Parse command-line arguments for ULTRA NECROZMA
    
    Returns:
        argparse.Namespace: Parsed arguments
    """
    parser = argparse.ArgumentParser(
        description="⚡🌟💎 ULTRA NECROZMA - Supreme Forex Analysis System 💎🌟⚡",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic analysis
  python main.py
  
  # Convert CSV to Parquet only
  python main.py --convert-only
  
  # Analyze only (skip conversion)
  python main.py --analyze-only
  
  # Force reconversion
  python main.py --force-convert
  
  # Run with test data
  python main.py --test
  
  # Test mode with sampling
  python main.py --test-mode --test-strategy balanced --test-weeks 4
  
  # Complete strategy discovery
  python main.py --strategy-discovery
  
  # Strategy discovery without Telegram
  python main.py --strategy-discovery --skip-telegram
  
  # Sequential processing (disable multiprocessing)
  python main.py --sequential
        """
    )
    
    # Data source arguments
    parser.add_argument(
        "--csv",
        type=str,
        default=None,
        help="Path to CSV file (overrides config)"
    )
    
    parser.add_argument(
        "--parquet",
        type=str,
        default=None,
        help="Path to Parquet file (overrides config)"
    )
    
    # Processing mode arguments
    parser.add_argument(
        "--convert-only",
        action="store_true",
        help="Only convert CSV to Parquet, then exit"
    )
    
    parser.add_argument(
        "--analyze-only",
        action="store_true",
        help="Skip CSV conversion, analyze existing Parquet"
    )
    
    parser.add_argument(
        "--sequential",
        action="store_true",
        help="Disable multiprocessing (use single thread)"
    )
    
    parser.add_argument(
        "--workers",
        type=int,
        default=None,
        help="Number of worker processes (overrides config)"
    )
    
    # Conversion arguments
    parser.add_argument(
        "--force-convert",
        action="store_true",
        help="Force CSV to Parquet conversion even if Parquet exists"
    )
    
    # Testing arguments
    parser.add_argument(
        "--test",
        action="store_true",
        help="Run with synthetic test data (no real data required)"
    )
    
    # Test Mode arguments
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
    
    return parser.parse_args()


# ═══════════════════════════════════════════════════════════════
# 🔍 SYSTEM CHECK
# ═══════════════════════════════════════════════════════════════

def get_version(module):
    """
    Safely get module version
    
    Args:
        module: Python module object
        
    Returns:
        Version string or "installed" if version not available
    """
    # Try common version attributes
    for attr in ['__version__', 'version', 'VERSION', '__VERSION__']:
        if hasattr(module, attr):
            version = getattr(module, attr)
            # Handle version tuples
            if isinstance(version, tuple):
                return '.'.join(map(str, version))
            return str(version)
    
    return "installed"


def check_system():
    """
    Verify system dependencies are available
    
    Returns:
        bool: True if all dependencies are available
    """
    print("\n" + "═" * 80)
    print("🔍 SYSTEM CHECK - Verifying Dependencies")
    print("═" * 80)
    
    issues = []
    
    # Check Python version
    print(f"✓ Python: {sys.version}")
    
    # Check NumPy
    try:
        import numpy as np
        print(f"✓ NumPy: {np.__version__}")
    except ImportError:
        print("✗ NumPy: NOT FOUND")
        issues.append("NumPy")
    
    # Check Pandas
    try:
        import pandas as pd
        print(f"✓ Pandas: {pd.__version__}")
    except ImportError:
        print("✗ Pandas: NOT FOUND")
        issues.append("Pandas")
    
    # Check PyArrow
    try:
        import pyarrow as pa
        print(f"✓ PyArrow: {pa.__version__}")
    except ImportError:
        print("✗ PyArrow: NOT FOUND (required for Parquet)")
        issues.append("PyArrow")
    
    # Check SciPy
    try:
        import scipy
        print(f"✓ SciPy: {scipy.__version__}")
    except ImportError:
        print("✗ SciPy: NOT FOUND")
        issues.append("SciPy")
    
    # Check Numba
    try:
        import numba
        print(f"✓ Numba: {numba.__version__}")
    except ImportError:
        print("⚠ Numba: NOT FOUND (optional, for JIT acceleration)")
    
    # Check psutil
    try:
        import psutil
        print(f"✓ psutil: {get_version(psutil)}")
    except ImportError:
        print("⚠ psutil: NOT FOUND (optional, for resource monitoring)")
    
    # Check tqdm
    try:
        import tqdm
        print(f"✓ tqdm: {get_version(tqdm)}")
    except ImportError:
        print("⚠ tqdm: NOT FOUND (optional, for progress bars)")
    
    print("═" * 80)
    
    if issues:
        print(f"\n❌ Missing required dependencies: {', '.join(issues)}")
        print("Install with: pip install -r requirements.txt")
        return False
    
    print("\n✅ All required dependencies available!\n")
    return True


# ═══════════════════════════════════════════════════════════════
# 🌟 STRATEGY DISCOVERY PIPELINE
# ═══════════════════════════════════════════════════════════════

def run_strategy_discovery(df, args):
    """
    Run complete strategy discovery pipeline
    
    7-Step Pipeline:
    1. Labeling - Multi-dimensional outcome labeling
    2. Regime Detection - Market regime clustering
    3. Pattern Mining - ML-based feature importance
    4. Strategy Generation - Template-based strategy creation
    5. Backtesting - Walk-forward validation
    6. Ranking - Multi-objective strategy selection
    7. Report - Final "Where The Light Is" report
    
    Args:
        df: Input DataFrame with tick data
        args: Command-line arguments
    """
    print("\n" + "═" * 80)
    print("🌟💎⚡ STRATEGY DISCOVERY PIPELINE - The Light Awakens ⚡💎🌟")
    print("═" * 80)
    
    from lore import LoreSystem, EventType
    
    # Initialize Lore System
    lore = LoreSystem(enable_telegram=not args.skip_telegram)
    
    # Awakening event
    lore.broadcast(EventType.AWAKENING, 
                  message="Strategy Discovery Pipeline Initiated")
    
    try:
        # ─────────────────────────────────────────────────────────
        # STEP 1: LABELING
        # ─────────────────────────────────────────────────────────
        print("\n" + "─" * 80)
        print("📊 STEP 1/7: Multi-Dimensional Outcome Labeling")
        print("─" * 80)
        
        lore.broadcast(EventType.PROGRESS, 
                      message="Step 1/7: Labeling outcomes across dimensions...")
        
        from labeler import label_dataframe
        
        start_time = time.time()
        labels_dict = label_dataframe(df)
        elapsed = time.time() - start_time
        
        print(f"\n✅ Labeling complete in {elapsed:.1f}s")
        print(f"   Labeled scenarios: {len(labels_dict)}")
        
        lore.broadcast(EventType.MILESTONE, 
                      message=f"Labeling complete: {len(labels_dict)} scenarios labeled")
        
        # ─────────────────────────────────────────────────────────
        # STEP 2: REGIME DETECTION
        # ─────────────────────────────────────────────────────────
        print("\n" + "─" * 80)
        print("🔮 STEP 2/7: Market Regime Detection")
        print("─" * 80)
        
        lore.broadcast(EventType.PROGRESS, 
                      message="Step 2/7: Detecting market regimes...")
        
        from regime_detector import RegimeDetector
        
        start_time = time.time()
        detector = RegimeDetector()
        regimes_df = detector.detect_regimes(df)
        regime_analysis = detector.analyze_regimes(regimes_df)
        elapsed = time.time() - start_time
        
        n_regimes = regime_analysis.get('n_regimes', 0)
        print(f"\n✅ Regime detection complete in {elapsed:.1f}s")
        print(f"   Regimes detected: {n_regimes}")
        
        lore.broadcast(EventType.REGIME_CHANGE, 
                      message=f"Detected {n_regimes} distinct market regimes")
        
        # ─────────────────────────────────────────────────────────
        # STEP 3: PATTERN MINING
        # ─────────────────────────────────────────────────────────
        print("\n" + "─" * 80)
        print("⛏️  STEP 3/7: ML-Based Pattern Mining")
        print("─" * 80)
        
        lore.broadcast(EventType.PROGRESS, 
                      message="Step 3/7: Mining patterns with ML...")
        
        from pattern_miner import PatternMiner
        
        start_time = time.time()
        miner = PatternMiner()
        patterns = miner.discover_patterns(df, labels_dict)
        elapsed = time.time() - start_time
        
        n_patterns = len(patterns.get('important_features', []))
        print(f"\n✅ Pattern mining complete in {elapsed:.1f}s")
        print(f"   Important features found: {n_patterns}")
        
        lore.broadcast(EventType.DISCOVERY, 
                      message=f"Discovered {n_patterns} important patterns")
        
        # ─────────────────────────────────────────────────────────
        # STEP 4: STRATEGY GENERATION
        # ─────────────────────────────────────────────────────────
        print("\n" + "─" * 80)
        print("🏭 STEP 4/7: Strategy Generation")
        print("─" * 80)
        
        lore.broadcast(EventType.PROGRESS, 
                      message="Step 4/7: Generating strategy candidates...")
        
        from strategy_factory import StrategyFactory
        
        start_time = time.time()
        factory = StrategyFactory()
        strategies = factory.generate_strategies(patterns, regimes_df)
        elapsed = time.time() - start_time
        
        n_strategies = len(strategies)
        print(f"\n✅ Strategy generation complete in {elapsed:.1f}s")
        print(f"   Strategies generated: {n_strategies}")
        
        lore.broadcast(EventType.MILESTONE, 
                      message=f"Generated {n_strategies} strategy candidates")
        
        # ─────────────────────────────────────────────────────────
        # STEP 5: BACKTESTING
        # ─────────────────────────────────────────────────────────
        print("\n" + "─" * 80)
        print("📈 STEP 5/7: Walk-Forward Backtesting")
        print("─" * 80)
        
        lore.broadcast(EventType.PROGRESS, 
                      message="Step 5/7: Backtesting strategies...")
        
        from backtester import Backtester
        
        start_time = time.time()
        backtester = Backtester()
        backtest_results = backtester.test_strategies(strategies, df)
        elapsed = time.time() - start_time
        
        n_viable = sum(1 for r in backtest_results if r.get('sharpe_ratio', 0) > 1.0)
        print(f"\n✅ Backtesting complete in {elapsed:.1f}s")
        print(f"   Viable strategies (Sharpe > 1.0): {n_viable}/{n_strategies}")
        
        lore.broadcast(EventType.INSIGHT, 
                      message=f"Backtesting found {n_viable} viable strategies")
        
        # ─────────────────────────────────────────────────────────
        # STEP 6: RANKING
        # ─────────────────────────────────────────────────────────
        print("\n" + "─" * 80)
        print("🌟 STEP 6/7: Multi-Objective Ranking")
        print("─" * 80)
        
        lore.broadcast(EventType.PROGRESS, 
                      message="Step 6/7: Ranking strategies...")
        
        from light_finder import LightFinder
        
        start_time = time.time()
        finder = LightFinder()
        top_strategies = finder.rank_strategies(backtest_results)
        elapsed = time.time() - start_time
        
        n_top = len(top_strategies)
        print(f"\n✅ Ranking complete in {elapsed:.1f}s")
        print(f"   Top strategies selected: {n_top}")
        
        if top_strategies:
            best = top_strategies[0]
            print(f"\n   🏆 Best Strategy: {best.get('name', 'Unknown')}")
            print(f"      Sharpe Ratio: {best.get('sharpe_ratio', 0):.2f}")
            print(f"      Total Return: {best.get('total_return', 0):.2%}")
            print(f"      Win Rate: {best.get('win_rate', 0):.2%}")
            
            lore.broadcast(EventType.LIGHT_FOUND, 
                          strategy_name=best.get('name', 'Unknown'),
                          sharpe=best.get('sharpe_ratio', 0),
                          return_pct=best.get('total_return', 0) * 100)
        
        # ─────────────────────────────────────────────────────────
        # STEP 7: FINAL REPORT
        # ─────────────────────────────────────────────────────────
        print("\n" + "─" * 80)
        print("📝 STEP 7/7: Generating Light Report")
        print("─" * 80)
        
        lore.broadcast(EventType.PROGRESS, 
                      message="Step 7/7: Generating final report...")
        
        from light_report import LightReportGenerator
        
        start_time = time.time()
        report_gen = LightReportGenerator()
        report_path = report_gen.generate_report(
            top_strategies=top_strategies,
            patterns=patterns,
            regimes=regime_analysis,
            backtest_results=backtest_results
        )
        elapsed = time.time() - start_time
        
        print(f"\n✅ Report generation complete in {elapsed:.1f}s")
        print(f"   Report saved to: {report_path}")
        
        lore.broadcast(EventType.COMPLETION, 
                      message=f"Strategy Discovery Complete! Report: {report_path}")
        
        # Final summary
        print("\n" + "═" * 80)
        print("🌟💎⚡ WHERE THE LIGHT IS - STRATEGY DISCOVERY COMPLETE ⚡💎🌟")
        print("═" * 80)
        print(f"\n📊 Pipeline Summary:")
        print(f"   • Scenarios labeled: {len(labels_dict)}")
        print(f"   • Regimes detected: {n_regimes}")
        print(f"   • Patterns found: {n_patterns}")
        print(f"   • Strategies tested: {n_strategies}")
        print(f"   • Viable strategies: {n_viable}")
        print(f"   • Top strategies: {n_top}")
        print(f"\n📁 Final Report: {report_path}")
        print("\n" + "═" * 80 + "\n")
        
        return {
            'top_strategies': top_strategies,
            'report_path': report_path,
            'summary': {
                'scenarios': len(labels_dict),
                'regimes': n_regimes,
                'patterns': n_patterns,
                'strategies': n_strategies,
                'viable': n_viable,
                'top': n_top
            }
        }
        
    except Exception as e:
        lore.broadcast(EventType.ERROR, 
                      message=f"Pipeline error: {str(e)}")
        raise


# ═══════════════════════════════════════════════════════════════
# 🚀 MAIN EXECUTION
# ═══════════════════════════════════════════════════════════════

def main():
    """
    Main entry point for ULTRA NECROZMA
    
    Complete execution flow:
    1. Parse arguments
    2. Show banner
    3. System check
    4. Config override
    5. Test mode check
    6. CSV → Parquet conversion
    7. Load data
    8. Test mode sampling (if enabled)
    9. Run analysis
    10. Strategy discovery (if enabled)
    11. Z-Move (final judgment)
    12. Report generation
    13. Final summary
    """
    # Parse arguments
    args = parse_arguments()
    
    # Show banner
    print(ULTRA_NECROZMA_BANNER)
    print(f"\n⚡ ULTRA NECROZMA v1.0 - Supreme Analysis Engine")
    print(f"   Python {sys.version.split()[0]} | {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Initialize Lore System with Telegram support
    from lore import LoreSystem, EventType
    from datetime import datetime
    lore = LoreSystem(enable_telegram=not args.skip_telegram)
    
    # System initialization notification
    lore.broadcast(
        EventType.SYSTEM_INIT,
        python_version=f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )
    
    # System check
    lore.broadcast(
        EventType.SYSTEM_CHECK,
        status="checking",
        dependencies=["NumPy", "Pandas", "PyArrow", "SciPy", "TA-Lib"]
    )
    
    if not check_system():
        sys.exit(1)
    
    # Import config (after system check)
    from config import CSV_FILE, PARQUET_FILE, NUM_WORKERS
    from data_loader import crystallize_csv_to_parquet, load_crystal, crystal_info
    from analyzer import UltraNecrozmaAnalyzer
    from reports import light_that_burns_the_sky, generate_full_report, print_final_summary
    
    # Config override
    csv_path = Path(args.csv) if args.csv else CSV_FILE
    parquet_path = Path(args.parquet) if args.parquet else PARQUET_FILE
    num_workers = args.workers if args.workers else NUM_WORKERS
    
    if args.sequential:
        num_workers = 1
        print("⚠️  Sequential mode enabled (single thread)\n")
    
    # Test mode check
    if args.test:
        print("🧪 TEST MODE - Generating synthetic data...\n")
        
        # Import numpy and pandas (already checked in check_system)
        import numpy as np
        import pandas as pd
        from datetime import datetime
        
        # Generate synthetic tick data
        n_samples = 100000
        # Use current date for synthetic data
        start_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        timestamps = pd.date_range(start_date, periods=n_samples, freq='1s')
        base_price = 1.1000
        noise = np.random.randn(n_samples) * 0.0001
        cumsum = np.cumsum(noise)
        
        df = pd.DataFrame({
            'timestamp': timestamps,
            'bid': base_price + cumsum - 0.00005,
            'ask': base_price + cumsum + 0.00005,
            'mid': base_price + cumsum
        })
        
        print(f"✅ Generated {len(df):,} synthetic ticks\n")
        
    else:
        # CSV → Parquet conversion
        if not args.analyze_only:
            if args.force_convert or not parquet_path.exists():
                print(f"💎 Converting CSV to Parquet...\n")
                crystallize_csv_to_parquet(csv_path, parquet_path, force=args.force_convert)
                
                if args.convert_only:
                    print("\n✅ Conversion complete! (--convert-only mode)\n")
                    return
            else:
                print(f"✅ Parquet file exists: {parquet_path}")
                print(f"   (use --force-convert to reconvert)\n")
        
        # Load data
        print(f"📊 Loading data from Parquet...\n")
        
        # Data loading notification
        import os
        file_path = parquet_path
        file_size_gb = os.path.getsize(file_path) / (1024**3) if os.path.exists(file_path) else 0
        
        lore.broadcast(
            EventType.DATA_LOADING,
            filename=os.path.basename(file_path),
            size_gb=f"{file_size_gb:.2f}"
        )
        
        # Load data with timing
        load_start = time.time()
        df = load_crystal(parquet_path)
        load_time = time.time() - load_start
        
        # Data loaded notification
        lore.broadcast(
            EventType.DATA_LOADED,
            rows=f"{len(df):,}",
            memory_gb=f"{df.memory_usage(deep=True).sum() / 1e9:.2f}",
            load_time=f"{load_time:.1f}",
            rows_per_sec=f"{len(df)/load_time:,.0f}" if load_time > 0 else "N/A",
            start_date=str(df.index[0]) if len(df) > 0 and hasattr(df, 'index') else "N/A",
            end_date=str(df.index[-1]) if len(df) > 0 and hasattr(df, 'index') else "N/A",
            min_price=f"{df['close'].min():.5f}" if 'close' in df.columns else (f"{df['mid'].min():.5f}" if 'mid' in df.columns else "N/A"),
            max_price=f"{df['close'].max():.5f}" if 'close' in df.columns else (f"{df['mid'].max():.5f}" if 'mid' in df.columns else "N/A")
        )
        crystal_info(df)
    
    # Test Mode Sampling (NEW - from PR #3)
    if args.test_mode:
        print("\n" + "═" * 80)
        print("🧪 TEST MODE - Intelligent Data Sampling")
        print("═" * 80)
        
        from test_mode import TestModeSampler
        
        sampler = TestModeSampler(seed=args.test_seed)
        
        print(f"\n📊 Sampling Strategy: {args.test_strategy}")
        print(f"   Weeks to sample: {args.test_weeks}")
        print(f"   Random seed: {args.test_seed}\n")
        
        df = sampler.get_test_sample(
            df, 
            strategy=args.test_strategy, 
            total_weeks=args.test_weeks
        )
        
        # Display sampled weeks
        if hasattr(df, 'attrs') and 'sampled_weeks' in df.attrs:
            print(f"\n✅ Sampled {len(df.attrs['sampled_weeks'])} weeks:")
            for week_info in df.attrs['sampled_weeks']:
                print(f"   • Week {week_info['week']}: {week_info['start']} to {week_info['end']}")
        
        print(f"\n📊 Total samples after sampling: {len(df):,}")
        print("═" * 80 + "\n")
    
    # Run analysis
    print("\n" + "═" * 80)
    print("⚡ ANALYSIS PHASE - Processing All Universes")
    print("═" * 80 + "\n")
    
    # Get number of universes from config
    from config import get_all_configs
    all_configs = get_all_configs()
    num_universes = len(all_configs)
    
    # Analysis start notification
    lore.broadcast(
        EventType.ANALYSIS_START,
        num_universes=num_universes,
        num_workers=num_workers,
        stages="Necrozma → Dusk Mane → Dawn Wings → Ultra Burst → Ultra Necrozma"
    )
    
    analyzer = UltraNecrozmaAnalyzer(df, lore_system=lore)
    analyzer.run_analysis()
    
    # Strategy discovery (if enabled)
    discovery_results = None
    if args.strategy_discovery:
        discovery_results = run_strategy_discovery(df, args)
    
    # Z-Move: Light That Burns The Sky
    print("\n")
    final_judgment = light_that_burns_the_sky(analyzer)
    
    # Generate reports
    print("\n📝 Generating comprehensive reports...\n")
    report_paths = generate_full_report(analyzer, final_judgment)
    
    # Final summary
    print_final_summary(analyzer, final_judgment, report_paths)
    
    # Add discovery results to summary
    if discovery_results:
        print("\n" + "─" * 80)
        print("🌟 STRATEGY DISCOVERY RESULTS")
        print("─" * 80)
        print(f"\n📁 Light Report: {discovery_results['report_path']}")
        print(f"🏆 Top Strategies: {discovery_results['summary']['top']}")
        print("─" * 80 + "\n")
    
    print("\n✨ ULTRA NECROZMA - Analysis Complete ✨\n")


# ═══════════════════════════════════════════════════════════════
# 🎬 ENTRY POINT
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
