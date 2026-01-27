#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚡🌟💎 NECROZMA - MASS TESTING SYSTEM 💎🌟⚡

Testa todas as estratégias em múltiplos pares e anos
"Light That Burns The Sky - Across All Dimensions"

Uso:
    python run_mass_test.py                    # Testa todos os pares/anos
    python run_mass_test.py --pair EURUSD      # Testa apenas EURUSD
    python run_mass_test.py --year 2024        # Testa apenas 2024
    python run_mass_test.py --parallel 4       # 4 processos paralelos
"""

import os
import sys
import argparse
import json
import time
from pathlib import Path
from datetime import datetime
from concurrent.futures import ProcessPoolExecutor, as_completed
import pandas as pd

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))


# ═══════════════════════════════════════════════════════════════
# 🎯 CONFIGURATION
# ═══════════════════════════════════════════════════════════════

PARQUET_DIR = Path("data/parquet")
RESULTS_DIR = Path("results/mass_test")

# Pares disponíveis
PAIRS = [
    "AUDJPY", "AUDUSD", "EURGBP", "EURJPY", "EURUSD",
    "GBPJPY", "GBPUSD", "USDCAD", "USDCHF", "USDJPY"
]

# Anos disponíveis
YEARS = ["2023", "2024", "2025"]


# ═══════════════════════════════════════════════════════════════
# 🔧 HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════

def get_available_datasets():
    """Scan parquet directory for available datasets"""
    datasets = []
    
    if not PARQUET_DIR.exists():
        print(f"⚠️ Parquet directory not found: {PARQUET_DIR}")
        return datasets
    
    for parquet_file in PARQUET_DIR.glob("*.parquet"):
        # Parse filename: PAIR_YEAR.parquet
        name = parquet_file.stem
        parts = name.split("_")
        
        if len(parts) >= 2:
            pair = parts[0]
            year = parts[1]
            datasets.append({
                "pair": pair,
                "year": year,
                "file": parquet_file,
                "name": name
            })
    
    return datasets


def run_single_backtest(dataset: dict) -> dict:
    """
    Run backtest for a single pair/year combination
    
    Args:
        dataset: Dict with pair, year, file info
        
    Returns:
        Dict with results
    """
    pair = dataset["pair"]
    year = dataset["year"]
    parquet_file = dataset["file"]
    
    print(f"\n{'='*70}")
    print(f"🚀 Testing {pair} {year}")
    print(f"{'='*70}")
    
    start_time = time.time()
    
    try:
        # Import after path setup
        import config
        
        # Update config to use this parquet file
        original_parquet = config.PARQUET_FILE
        config.PARQUET_FILE = parquet_file
        
        # Set FILE_PREFIX for this test
        original_prefix = config.FILE_PREFIX
        config.FILE_PREFIX = f"{pair}_{year}_"
        
        # Import main after config is set
        from main import main as run_necrozma
        
        # Run the backtest
        run_necrozma()
        
        # Restore original config
        config.PARQUET_FILE = original_parquet
        config.FILE_PREFIX = original_prefix
        
        elapsed = time.time() - start_time
        
        # Find the most recent light report for this pair/year
        reports_dir = Path("ultra_necrozma_results/reports")
        if reports_dir.exists():
            # Look for reports with this prefix
            pattern = f"{pair}_{year}_LIGHT_REPORT_*.json"
            report_files = list(reports_dir.glob(pattern))
            
            if report_files:
                # Get the most recent one
                report_file = max(report_files, key=lambda p: p.stat().st_mtime)
                
                with open(report_file, 'r') as f:
                    report = json.load(f)
                
                return {
                    "pair": pair,
                    "year": year,
                    "status": "success",
                    "elapsed_time": elapsed,
                    "total_strategies": report.get("executive_summary", {}).get("viable_strategies_found", 0),
                    "best_strategy": report.get("executive_summary", {}).get("best_strategy", {}),
                    "avg_sharpe": report.get("executive_summary", {}).get("avg_sharpe", 0),
                    "top_strategies": report.get("top_strategies", [])[:10]
                }
        
        # No report found
        return {
            "pair": pair,
            "year": year,
            "status": "no_report",
            "elapsed_time": elapsed,
            "error": "Report file not found"
        }
            
    except Exception as e:
        elapsed = time.time() - start_time
        return {
            "pair": pair,
            "year": year,
            "status": "error",
            "elapsed_time": elapsed,
            "error": str(e)
        }


def run_mass_test(pairs=None, years=None, parallel=1):
    """
    Run mass testing across multiple pairs and years
    
    Args:
        pairs: List of pairs to test (None = all)
        years: List of years to test (None = all)
        parallel: Number of parallel processes
    """
    print("\n" + "="*70)
    print("⚡🌟💎 NECROZMA MASS TESTING SYSTEM 💎🌟⚡")
    print("="*70)
    
    # Get available datasets
    datasets = get_available_datasets()
    
    if not datasets:
        print("❌ No datasets found!")
        return
    
    # Filter by pairs/years if specified
    if pairs:
        datasets = [d for d in datasets if d["pair"] in pairs]
    if years:
        datasets = [d for d in datasets if d["year"] in years]
    
    print(f"\n📊 Found {len(datasets)} datasets to test:")
    for d in datasets:
        print(f"   • {d['pair']} {d['year']}: {d['file']}")
    
    # Create results directory
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    
    # Run tests
    all_results = []
    start_time = time.time()
    
    if parallel > 1:
        # Parallel execution
        print(f"\n🚀 Running {len(datasets)} tests with {parallel} parallel processes...")
        
        with ProcessPoolExecutor(max_workers=parallel) as executor:
            futures = {executor.submit(run_single_backtest, d): d for d in datasets}
            
            for future in as_completed(futures):
                result = future.result()
                all_results.append(result)
                
                if result["status"] == "success":
                    print(f"✅ {result['pair']} {result['year']}: "
                          f"Sharpe {result.get('avg_sharpe', 0):.2f}, "
                          f"{result.get('total_strategies', 0)} strategies")
                else:
                    print(f"❌ {result['pair']} {result['year']}: {result.get('error', 'Unknown error')}")
    else:
        # Sequential execution
        print(f"\n🚀 Running {len(datasets)} tests sequentially...")
        
        for dataset in datasets:
            result = run_single_backtest(dataset)
            all_results.append(result)
            
            if result["status"] == "success":
                print(f"✅ {result['pair']} {result['year']}: "
                      f"Sharpe {result.get('avg_sharpe', 0):.2f}, "
                      f"{result.get('total_strategies', 0)} strategies")
            else:
                print(f"❌ {result['pair']} {result['year']}: {result.get('error', 'Unknown error')}")
    
    total_time = time.time() - start_time
    
    # Generate summary report
    generate_summary_report(all_results, total_time)
    
    return all_results


def generate_summary_report(results: list, total_time: float):
    """Generate consolidated summary report"""
    
    print("\n" + "="*70)
    print("📊 MASS TEST SUMMARY REPORT")
    print("="*70)
    
    # Basic stats
    successful = [r for r in results if r["status"] == "success"]
    failed = [r for r in results if r["status"] != "success"]
    
    print(f"\n📈 Overall Statistics:")
    print(f"   Total tests: {len(results)}")
    print(f"   Successful: {len(successful)}")
    print(f"   Failed: {len(failed)}")
    print(f"   Total time: {total_time:.1f}s ({total_time/60:.1f}m)")
    
    if successful:
        # Best performers by pair
        print(f"\n🏆 Best Strategy by Pair:")
        print("-" * 70)
        
        pair_best = {}
        for r in successful:
            pair = r["pair"]
            best = r.get("best_strategy", {})
            sharpe = best.get("sharpe_ratio", 0)
            
            if pair not in pair_best or sharpe > pair_best[pair]["sharpe"]:
                pair_best[pair] = {
                    "year": r["year"],
                    "strategy": best.get("name", "N/A"),
                    "sharpe": sharpe,
                    "win_rate": best.get("win_rate", 0)
                }
        
        for pair in sorted(pair_best.keys()):
            info = pair_best[pair]
            print(f"   {pair} ({info['year']}): {info['strategy']}")
            print(f"      Sharpe: {info['sharpe']:.2f}, Win Rate: {info['win_rate']*100:.1f}%")
        
        # Global top 10
        print(f"\n🌟 Global Top 10 Strategies (All Pairs/Years):")
        print("-" * 70)
        
        all_strategies = []
        for r in successful:
            for s in r.get("top_strategies", []):
                all_strategies.append({
                    "pair": r["pair"],
                    "year": r["year"],
                    "name": s.get("name", "N/A"),
                    "sharpe": s.get("performance", {}).get("sharpe_ratio", 0),
                    "trades": s.get("trading_stats", {}).get("total_trades", 0),
                    "win_rate": s.get("performance", {}).get("win_rate", 0)
                })
        
        # Sort by Sharpe
        all_strategies.sort(key=lambda x: x["sharpe"], reverse=True)
        
        for i, s in enumerate(all_strategies[:10], 1):
            print(f"   {i}. {s['pair']} {s['year']}: {s['name']}")
            print(f"      Sharpe: {s['sharpe']:.2f}, Trades: {s['trades']}, Win: {s['win_rate']*100:.1f}%")
        
        # Consistency analysis
        print(f"\n📊 Strategy Consistency Across Pairs/Years:")
        print("-" * 70)
        
        strategy_counts = {}
        for s in all_strategies:
            name_base = s["name"].split("_")[0]  # e.g., "MeanReverter"
            if name_base not in strategy_counts:
                strategy_counts[name_base] = {"count": 0, "sharpes": []}
            strategy_counts[name_base]["count"] += 1
            strategy_counts[name_base]["sharpes"].append(s["sharpe"])
        
        for name, data in sorted(strategy_counts.items(), key=lambda x: sum(x[1]["sharpes"])/len(x[1]["sharpes"]) if x[1]["sharpes"] else 0, reverse=True):
            avg_sharpe = sum(data["sharpes"]) / len(data["sharpes"]) if data["sharpes"] else 0
            print(f"   {name}: {data['count']} appearances, Avg Sharpe: {avg_sharpe:.2f}")
    
    # Save detailed report
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = RESULTS_DIR / f"mass_test_report_{timestamp}.json"
    
    report = {
        "timestamp": timestamp,
        "total_tests": len(results),
        "successful": len(successful),
        "failed": len(failed),
        "total_time_seconds": total_time,
        "results": results
    }
    
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2, default=str)
    
    print(f"\n💾 Detailed report saved to: {report_file}")
    
    # Save CSV summary
    if successful:
        csv_file = RESULTS_DIR / f"mass_test_summary_{timestamp}.csv"
        
        rows = []
        for r in successful:
            best = r.get("best_strategy", {})
            rows.append({
                "pair": r["pair"],
                "year": r["year"],
                "best_strategy": best.get("name", "N/A"),
                "sharpe_ratio": best.get("sharpe_ratio", 0),
                "total_return": best.get("total_return", 0),
                "win_rate": best.get("win_rate", 0),
                "max_drawdown": best.get("max_drawdown", 0),
                "total_strategies": r.get("total_strategies", 0),
                "elapsed_time": r.get("elapsed_time", 0)
            })
        
        df = pd.DataFrame(rows)
        df.to_csv(csv_file, index=False)
        print(f"💾 CSV summary saved to: {csv_file}")


# ═══════════════════════════════════════════════════════════════
# 🎯 MAIN
# ═══════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="NECROZMA Mass Testing System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python run_mass_test.py                    # Test all pairs/years
    python run_mass_test.py --pair EURUSD      # Test only EURUSD
    python run_mass_test.py --year 2024        # Test only 2024
    python run_mass_test.py --pair EURUSD GBPUSD --year 2024 2025
    python run_mass_test.py --parallel 4       # Use 4 parallel processes
        """
    )
    
    parser.add_argument(
        "--pair", "-p",
        nargs="+",
        choices=PAIRS,
        help="Pairs to test (default: all)"
    )
    
    parser.add_argument(
        "--year", "-y",
        nargs="+",
        choices=YEARS,
        help="Years to test (default: all)"
    )
    
    parser.add_argument(
        "--parallel", "-j",
        type=int,
        default=1,
        help="Number of parallel processes (default: 1)"
    )
    
    parser.add_argument(
        "--list", "-l",
        action="store_true",
        help="List available datasets and exit"
    )
    
    args = parser.parse_args()
    
    if args.list:
        datasets = get_available_datasets()
        print(f"\n📁 Available datasets ({len(datasets)}):")
        for d in sorted(datasets, key=lambda x: (x["pair"], x["year"])):
            print(f"   • {d['pair']} {d['year']}: {d['file']}")
        return
    
    # Run mass test
    run_mass_test(
        pairs=args.pair,
        years=args.year,
        parallel=args.parallel
    )


if __name__ == "__main__":
    main()
