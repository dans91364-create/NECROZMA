#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚡🌟💎 NECROZMA - MASS TESTING SYSTEM 💎🌟⚡

Testa todas as estratégias em múltiplos pares e anos
COM SISTEMA DE RESUME para rodar overnight sem perder progresso

Uso:
    python run_mass_test.py                    # Roda todos (resume automático)
    python run_mass_test.py --pair EURUSD      # Testa apenas EURUSD
    python run_mass_test.py --year 2024        # Testa apenas 2024
    python run_mass_test.py --status           # Mostra progresso
    python run_mass_test.py --fresh            # Reinicia do zero
    python run_mass_test.py --retry-failed     # Retenta apenas falhas
"""

import os
import sys
import argparse
import json
import time
import subprocess
import shutil
from pathlib import Path
from datetime import datetime
import pandas as pd

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))


# ═══════════════════════════════════════════════════════════════
# 🎯 CONFIGURATION
# ═══════════════════════════════════════════════════════════════

PARQUET_DIR = Path("data/parquet")
RESULTS_DIR = Path("results/mass_test")
PROGRESS_FILE = RESULTS_DIR / "progress.json"

# Pares disponíveis
PAIRS = [
    "AUDJPY", "AUDUSD", "EURGBP", "EURJPY", "EURUSD",
    "GBPJPY", "GBPUSD", "USDCAD", "USDCHF", "USDJPY"
]

# Anos disponíveis
YEARS = ["2023", "2024", "2025"]


# ═══════════════════════════════════════════════════════════════
# 💾 PROGRESS TRACKING
# ═══════════════════════════════════════════════════════════════

def load_progress():
    """Load progress from file"""
    if PROGRESS_FILE.exists():
        try:
            with open(PROGRESS_FILE, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"⚠️ Error loading progress file: {e}")
    return {
        "completed": [],
        "failed": [],
        "in_progress": None,
        "started_at": None,
        "last_update": None
    }


def save_progress(progress):
    """Save progress to file"""
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    progress["last_update"] = datetime.now().isoformat()
    with open(PROGRESS_FILE, 'w') as f:
        json.dump(progress, f, indent=2)


def mark_completed(progress, dataset_key, result):
    """Mark a dataset as completed"""
    if dataset_key not in progress["completed"]:
        progress["completed"].append(dataset_key)
    if dataset_key in progress["failed"]:
        progress["failed"].remove(dataset_key)
    progress["in_progress"] = None
    progress["results"] = progress.get("results", {})
    progress["results"][dataset_key] = result
    save_progress(progress)


def mark_failed(progress, dataset_key, error):
    """Mark a dataset as failed"""
    if dataset_key not in progress["failed"]:
        progress["failed"].append(dataset_key)
    progress["in_progress"] = None
    progress["errors"] = progress.get("errors", {})
    progress["errors"][dataset_key] = str(error)
    save_progress(progress)


def mark_in_progress(progress, dataset_key):
    """Mark a dataset as in progress"""
    progress["in_progress"] = dataset_key
    if progress["started_at"] is None:
        progress["started_at"] = datetime.now().isoformat()
    save_progress(progress)


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
        name = parquet_file.stem
        parts = name.split("_")
        
        if len(parts) >= 2:
            pair = parts[0]
            year = parts[1]
            datasets.append({
                "pair": pair,
                "year": year,
                "file": parquet_file,
                "name": name,
                "key": f"{pair}_{year}"
            })
    
    return sorted(datasets, key=lambda x: (x["pair"], x["year"]))


def run_single_backtest(dataset: dict) -> dict:
    """Run backtest for a single pair/year using subprocess (NO TIMEOUT)"""
    
    pair = dataset["pair"]
    year = dataset["year"]
    parquet_file = dataset["file"]
    
    print(f"\n{'='*70}")
    print(f"🚀 Testing {pair} {year}")
    print(f"   File: {parquet_file}")
    print(f"   Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*70}")
    
    start_time = time.time()
    
    try:
        cmd = [
            sys.executable,
            "main.py",
            "--strategy-discovery",
            "--batch-mode",
            "--parquet", str(parquet_file)
        ]
        
        print(f"   Command: {' '.join(cmd)}")
        print(f"   Running... (NO TIMEOUT - will complete fully)")
        
        # Run WITHOUT timeout - let it complete naturally
        # Note: We don't capture output to allow real-time display
        result = subprocess.run(cmd, check=False)
        
        # Check if subprocess succeeded
        if result.returncode != 0:
            elapsed = time.time() - start_time
            print(f"   ❌ Subprocess failed with exit code {result.returncode}")
            return {
                "pair": pair, "year": year,
                "status": "error",
                "elapsed_time": elapsed,
                "error": f"Subprocess exited with code {result.returncode}"
            }
        
        elapsed = time.time() - start_time
        elapsed_str = f"{elapsed/3600:.1f}h" if elapsed > 3600 else f"{elapsed/60:.1f}m"
        
        print(f"   ✅ Completed in {elapsed_str}")
        
        # Clean up labels directory to free space
        labels_dir = Path("labels")
        if labels_dir.exists():
            try:
                shutil.rmtree(labels_dir, ignore_errors=True)
                print(f"   🗑️  Labels cleaned for next dataset")
            except Exception as e:
                print(f"   ⚠️  Could not clean labels: {e}")
        
        # Find the report file
        reports_dir = Path("ultra_necrozma_results/reports")
        if reports_dir.exists():
            # Try multiple patterns
            patterns = [
                f"{pair}_{year}_*LIGHT_REPORT*.json",
                f"{pair}_{year}_LIGHT_REPORT_*.json",
                f"*{pair}*{year}*LIGHT*.json"
            ]
            
            report_files = []
            for pattern in patterns:
                report_files.extend(list(reports_dir.glob(pattern)))
            
            if report_files:
                report_file = max(report_files, key=lambda p: p.stat().st_mtime)
                print(f"   📄 Report: {report_file.name}")
                
                with open(report_file, 'r') as f:
                    report = json.load(f)
                
                best = report.get("executive_summary", {}).get("best_strategy", {})
                
                return {
                    "pair": pair,
                    "year": year,
                    "status": "success",
                    "elapsed_time": elapsed,
                    "elapsed_str": elapsed_str,
                    "total_strategies": report.get("executive_summary", {}).get("viable_strategies_found", 0),
                    "best_strategy": best.get("name", "N/A"),
                    "best_sharpe": best.get("sharpe_ratio", 0),
                    "avg_sharpe": report.get("executive_summary", {}).get("avg_sharpe", 0),
                    "report_file": str(report_file)
                }
        
        return {
            "pair": pair, "year": year,
            "status": "no_report",
            "elapsed_time": elapsed,
            "elapsed_str": elapsed_str,
            "error": "Report file not found"
        }
        
    except KeyboardInterrupt:
        print(f"\n   ⚠️ Interrupted by user")
        raise
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"   ❌ Error: {e}")
        return {
            "pair": pair, "year": year,
            "status": "error",
            "elapsed_time": elapsed,
            "error": str(e)
        }


def show_status():
    """Show current progress status"""
    progress = load_progress()
    datasets = get_available_datasets()
    
    total = len(datasets)
    completed = len(progress.get("completed", []))
    failed = len(progress.get("failed", []))
    remaining = total - completed
    
    print("\n" + "="*70)
    print("📊 MASS TEST PROGRESS STATUS")
    print("="*70)
    
    print(f"\n📈 Overall Progress:")
    print(f"   Total datasets:    {total}")
    print(f"   ✅ Completed:      {completed}" + (f" ({completed/total*100:.1f}%)" if total > 0 else ""))
    print(f"   ❌ Failed:         {failed}")
    print(f"   ⏳ Remaining:      {remaining}")
    
    if progress.get("started_at"):
        print(f"\n⏱️  Started: {progress['started_at']}")
    if progress.get("last_update"):
        print(f"   Last update: {progress['last_update']}")
    if progress.get("in_progress"):
        print(f"   🔄 In progress: {progress['in_progress']}")
    
    if progress.get("completed"):
        print(f"\n✅ Completed ({len(progress['completed'])}):")
        for key in progress["completed"]:
            result = progress.get("results", {}).get(key, {})
            sharpe = result.get("best_sharpe", "?")
            elapsed = result.get("elapsed_str", "?")
            print(f"   • {key}: Sharpe {sharpe}, Time {elapsed}")
    
    if progress.get("failed"):
        print(f"\n❌ Failed ({len(progress['failed'])}):")
        for key in progress["failed"]:
            error = progress.get("errors", {}).get(key, "Unknown")
            print(f"   • {key}: {error[:50]}")
    
    remaining_datasets = [d for d in datasets if d["key"] not in progress.get("completed", [])]
    if remaining_datasets and remaining_datasets[:5]:
        print(f"\n⏳ Next up:")
        for d in remaining_datasets[:5]:
            print(f"   • {d['key']}")


def run_mass_test(pairs=None, years=None, fresh=False, retry_failed=False):
    """Run mass testing with resume support"""
    
    print("\n" + "="*70)
    print("⚡🌟💎 NECROZMA MASS TESTING SYSTEM 💎🌟⚡")
    print("        WITH RESUME SUPPORT (NO TIMEOUT)")
    print("="*70)
    
    # Load or initialize progress
    if fresh:
        print("\n🔄 Fresh start - clearing previous progress...")
        progress = {
            "completed": [],
            "failed": [],
            "in_progress": None,
            "started_at": datetime.now().isoformat(),
            "last_update": None
        }
        save_progress(progress)
    else:
        progress = load_progress()
    
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
    
    # Filter based on progress
    if retry_failed:
        # Only retry failed ones
        failed_keys = progress.get("failed", [])
        datasets = [d for d in datasets if d["key"] in failed_keys]
        print(f"\n🔄 Retrying {len(datasets)} failed datasets...")
    else:
        # Skip completed ones
        completed_keys = progress.get("completed", [])
        skipped = [d for d in datasets if d["key"] in completed_keys]
        datasets = [d for d in datasets if d["key"] not in completed_keys]
        
        if skipped:
            print(f"\n⏭️  Skipping {len(skipped)} already completed datasets")
    
    if not datasets:
        print("\n✅ All datasets already completed!")
        show_status()
        return
    
    print(f"\n📊 Datasets to process: {len(datasets)}")
    for d in datasets:
        print(f"   • {d['pair']} {d['year']}: {d['file']}")
    
    # Create results directory
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    
    # Run tests sequentially with resume
    total = len(datasets)
    
    print(f"\n🚀 Starting mass test ({total} datasets)...")
    print(f"   Press Ctrl+C to pause (progress is saved automatically)")
    
    for i, dataset in enumerate(datasets, 1):
        key = dataset["key"]
        
        print(f"\n{'─'*70}")
        print(f"📌 Progress: {i}/{total} ({i/total*100:.1f}%)")
        print(f"{'─'*70}")
        
        # Mark as in progress
        mark_in_progress(progress, key)
        
        try:
            result = run_single_backtest(dataset)
            
            if result["status"] == "success":
                mark_completed(progress, key, result)
                print(f"   ✅ {key}: Best Sharpe = {result.get('best_sharpe', 'N/A')}")
            else:
                mark_failed(progress, key, result.get("error", "Unknown"))
                print(f"   ❌ {key}: {result.get('error', 'Unknown error')}")
                
        except KeyboardInterrupt:
            print(f"\n\n⚠️ Interrupted! Progress saved.")
            print(f"   Run again to resume from {key}")
            save_progress(progress)
            return
        except Exception as e:
            mark_failed(progress, key, str(e))
            print(f"   ❌ {key}: {e}")
            continue  # Continue with next dataset
    
    # Generate final report
    print("\n" + "="*70)
    print("🏁 MASS TEST COMPLETE!")
    print("="*70)
    
    generate_final_report(progress)


def generate_final_report(progress):
    """Generate final consolidated report"""
    
    results = progress.get("results", {})
    
    if not results:
        print("No results to report.")
        return
    
    print(f"\n📊 FINAL RESULTS ({len(results)} datasets)")
    print("-"*70)
    
    # Sort by best sharpe (handle None values)
    sorted_results = sorted(
        results.items(),
        key=lambda x: x[1].get("best_sharpe") or 0,
        reverse=True
    )
    
    print("\n🏆 Top 10 by Sharpe Ratio:")
    for i, (key, r) in enumerate(sorted_results[:10], 1):
        print(f"   {i:2}. {key}: Sharpe {r.get('best_sharpe', 0):.2f} - {r.get('best_strategy', 'N/A')}")
    
    # Save CSV summary
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_file = RESULTS_DIR / f"mass_test_summary_{timestamp}.csv"
    
    rows = []
    for key, r in results.items():
        rows.append({
            "pair_year": key,
            "pair": r.get("pair"),
            "year": r.get("year"),
            "status": r.get("status"),
            "best_strategy": r.get("best_strategy"),
            "best_sharpe": r.get("best_sharpe"),
            "avg_sharpe": r.get("avg_sharpe"),
            "total_strategies": r.get("total_strategies"),
            "elapsed_time": r.get("elapsed_str")
        })
    
    df = pd.DataFrame(rows)
    df.to_csv(csv_file, index=False)
    print(f"\n💾 CSV saved: {csv_file}")
    
    # Save JSON report
    json_file = RESULTS_DIR / f"mass_test_report_{timestamp}.json"
    with open(json_file, 'w') as f:
        json.dump(progress, f, indent=2, default=str)
    print(f"💾 JSON saved: {json_file}")


# ═══════════════════════════════════════════════════════════════
# 🎯 MAIN
# ═══════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="NECROZMA Mass Testing System with Resume Support",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python run_mass_test.py                    # Run all (auto-resume)
    python run_mass_test.py --status           # Show progress
    python run_mass_test.py --fresh            # Start from zero
    python run_mass_test.py --retry-failed     # Retry only failed
    python run_mass_test.py --pair EURUSD      # Test only EURUSD
    python run_mass_test.py --year 2024        # Test only 2024
        """
    )
    
    parser.add_argument("--pair", "-p", nargs="+", choices=PAIRS, help="Pairs to test")
    parser.add_argument("--year", "-y", nargs="+", choices=YEARS, help="Years to test")
    parser.add_argument("--status", "-s", action="store_true", help="Show progress status")
    parser.add_argument("--fresh", "-f", action="store_true", help="Start fresh (ignore progress)")
    parser.add_argument("--retry-failed", "-r", action="store_true", help="Retry only failed datasets")
    parser.add_argument("--list", "-l", action="store_true", help="List available datasets")
    
    args = parser.parse_args()
    
    if args.list:
        datasets = get_available_datasets()
        print(f"\n📁 Available datasets ({len(datasets)}):")
        for d in datasets:
            print(f"   • {d['pair']} {d['year']}: {d['file']}")
        return
    
    if args.status:
        show_status()
        return
    
    run_mass_test(
        pairs=args.pair,
        years=args.year,
        fresh=args.fresh,
        retry_failed=args.retry_failed
    )


if __name__ == "__main__":
    main()
