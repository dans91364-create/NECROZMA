#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚡🌟💎 ULTRA NECROZMA - Sequential Backtesting Runner 💎🌟⚡

Loads processed universe results and runs backtesting sequentially
with CPU management and cooling breaks.

"Light that illuminates the path to profit"
"""

import sys
import json
import time
import gc
import argparse
import traceback
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import pandas as pd
import numpy as np

# Ensure correct imports
sys.path.insert(0, str(Path(__file__).parent))

from backtester import Backtester, BacktestResults
from strategy_factory import StrategyFactory
from light_finder import LightFinder
from light_report import LightReportGenerator
from lore import LoreSystem, EventType
from config import RANDOM_SEED, PARQUET_FILE
from ohlc_generator import generate_ohlc_bars, validate_ohlc_data
from feature_extractor import (
    extract_features_from_universe,
    combine_ohlc_with_features,
    validate_dataframe_for_backtesting
)

# Import psutil for monitoring (optional)
try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False
    print("⚠️  Warning: psutil not available - CPU monitoring will use fallback mode")


# ═══════════════════════════════════════════════════════════════
# 🔧 CONFIGURATION
# ═══════════════════════════════════════════════════════════════

DEFAULT_CPU_THRESHOLD = 85  # Target CPU percentage
DEFAULT_COOLING_DURATION = 120  # Seconds
COOLING_INTERVAL = 5  # Check every N universes
INITIAL_CAPITAL = 10000  # Starting capital for backtests


# ═══════════════════════════════════════════════════════════════
# 💾 DATA LOADING
# ═══════════════════════════════════════════════════════════════

def load_universe_results(results_dir: Path, universe_ids: Optional[List[int]] = None) -> List[Dict]:
    """
    Load universe results from JSON files
    
    Args:
        results_dir: Directory containing universe result files
        universe_ids: Optional list of specific universe IDs to load
        
    Returns:
        List of universe result dictionaries
    """
    print(f"\n📂 Loading universe results from {results_dir}...", flush=True)
    
    if not results_dir.exists():
        print(f"❌ Error: Directory not found: {results_dir}", flush=True)
        return []
    
    # Find all universe JSON files
    universe_files = sorted(results_dir.glob("universe_*.json"))
    
    if not universe_files:
        print(f"❌ No universe files found in {results_dir}", flush=True)
        return []
    
    print(f"   Found {len(universe_files)} universe files", flush=True)
    
    # Filter by universe IDs if specified
    if universe_ids:
        filtered_files = []
        for f in universe_files:
            # Extract universe number from filename (e.g., universe_001_5min_5lb.json)
            try:
                parts = f.stem.split('_')
                if len(parts) >= 2:
                    universe_num = int(parts[1])
                    if universe_num in universe_ids:
                        filtered_files.append(f)
            except (ValueError, IndexError):
                continue
        universe_files = filtered_files
        print(f"   Filtered to {len(universe_files)} universes based on selection", flush=True)
    
    # Load each universe file
    universes = []
    for filepath in universe_files:
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
                data['_filepath'] = str(filepath)  # Store filepath for reference
                universes.append(data)
        except Exception as e:
            print(f"⚠️  Failed to load {filepath.name}: {e}", flush=True)
            continue
    
    print(f"   ✅ Loaded {len(universes)} universes successfully", flush=True)
    return universes


def parse_universe_selection(selection: str) -> List[int]:
    """
    Parse universe selection string into list of IDs
    
    Examples:
        "1,5,10-15,25" -> [1, 5, 10, 11, 12, 13, 14, 15, 25]
        "1-3" -> [1, 2, 3]
        
    Args:
        selection: Selection string
        
    Returns:
        List of universe IDs
    """
    ids = []
    parts = selection.split(',')
    
    for part in parts:
        part = part.strip()
        if '-' in part:
            # Range (e.g., "10-15")
            try:
                start, end = part.split('-')
                ids.extend(range(int(start), int(end) + 1))
            except ValueError:
                print(f"⚠️  Invalid range: {part}", flush=True)
        else:
            # Single ID
            try:
                ids.append(int(part))
            except ValueError:
                print(f"⚠️  Invalid ID: {part}", flush=True)
    
    return sorted(set(ids))  # Remove duplicates and sort


# ═══════════════════════════════════════════════════════════════
# ❄️ COOLING & CPU MANAGEMENT
# ═══════════════════════════════════════════════════════════════

def get_system_stats() -> Dict:
    """Get current system statistics"""
    if not HAS_PSUTIL:
        return {"cpu_percent": 0.0, "ram_gb": 0.0}
    
    return {
        "cpu_percent": psutil.cpu_percent(interval=1),
        "ram_gb": psutil.virtual_memory().used / 1e9
    }


def cooling_break(duration: int, cpu_threshold: float):
    """
    Pause execution with cooling break
    
    Args:
        duration: Duration in seconds
        cpu_threshold: CPU threshold percentage
    """
    if not HAS_PSUTIL:
        print(f"\n❄️  COOLING BREAK - Waiting {duration}s...", flush=True)
        time.sleep(duration)
        print("   ✅ Resumed\n", flush=True)
        return
    
    current_cpu = psutil.cpu_percent(interval=2)
    
    if current_cpu > cpu_threshold:
        print(f"\n❄️  COOLING BREAK - CPU too high ({current_cpu:.1f}%)", flush=True)
        print(f"   Waiting {duration}s...", flush=True)
        
        # Display countdown with stats
        remaining = duration
        while remaining > 0:
            cpu = psutil.cpu_percent(interval=1)
            mem_gb = psutil.virtual_memory().used / 1e9
            print(f"   {remaining:3d}s | CPU: {cpu:5.1f}% | RAM: {mem_gb:5.1f}GB", flush=True)
            
            wait_time = min(10, remaining)
            time.sleep(wait_time)
            remaining -= wait_time
        
        print("   ✅ Resumed\n", flush=True)
    else:
        print(f"\n   💤 Quick pause ({duration}s, CPU OK at {current_cpu:.1f}%)...", flush=True)
        time.sleep(duration)
        print("   ✅ Resumed\n", flush=True)


# ═══════════════════════════════════════════════════════════════
# 🏭 STRATEGY GENERATION
# ═══════════════════════════════════════════════════════════════

def generate_strategies_for_universe(universe_data: Dict, max_strategies: int = 100) -> List:
    """
    Generate strategies for a universe based on its features
    
    Args:
        universe_data: Universe result dictionary
        max_strategies: Maximum strategies to generate
        
    Returns:
        List of Strategy objects
    """
    factory = StrategyFactory()
    
    # Generate default strategies
    strategies = factory.generate_strategies(max_strategies=max_strategies)
    
    return strategies


# ═══════════════════════════════════════════════════════════════
# 📊 BACKTESTING
# ═══════════════════════════════════════════════════════════════

def load_ohlc_for_universe(universe_data: Dict, parquet_path: Path = None, verbose: bool = False) -> pd.DataFrame:
    """
    Load OHLC data for a universe from Parquet file and combine with pattern features
    
    This function:
    1. Generates OHLC bars from tick data
    2. Extracts features from universe JSON patterns
    3. Combines OHLC + features into a single DataFrame
    
    Args:
        universe_data: Universe result dictionary
        parquet_path: Path to parquet file (default: from config)
        verbose: Whether to print detailed output
        
    Returns:
        DataFrame with OHLC price data + pattern features ready for backtesting
    """
    # Extract universe parameters
    lookback = universe_data.get('lookback', 20)
    interval = universe_data.get('interval', 5)
    
    if parquet_path is None:
        parquet_path = PARQUET_FILE
    
    if verbose:
        print(f"      📂 Loading OHLC data (interval={interval}min, lookback={lookback})...", flush=True)
    
    # Generate OHLC bars from tick data
    try:
        ohlc_df = generate_ohlc_bars(
            parquet_path=parquet_path,
            interval_minutes=interval,
            lookback=lookback
        )
        
        # Validate the data
        validation = validate_ohlc_data(ohlc_df)
        
        if not validation["valid"]:
            raise ValueError(f"OHLC validation failed: {validation['errors']}")
        
        if verbose and validation["warnings"]:
            for warning in validation["warnings"]:
                print(f"      ⚠️  {warning}", flush=True)
        
        # ✅ NEW: Extract features from universe JSON patterns
        if verbose:
            print(f"      🔮 Extracting features from universe patterns...", flush=True)
        
        features_df = extract_features_from_universe(universe_data)
        
        if verbose:
            if not features_df.empty:
                print(f"      ✅ Extracted {len(features_df.columns)} features", flush=True)
            else:
                print(f"      ⚠️  No features extracted, using OHLC only", flush=True)
        
        # ✅ NEW: Combine OHLC + features
        combined_df = combine_ohlc_with_features(ohlc_df, features_df)
        
        # Fill NaN values (may occur from feature broadcast or OHLC calculations)
        combined_df = combined_df.bfill().fillna(0)
        
        if verbose:
            print(f"      ✅ Combined DataFrame: {combined_df.shape}", flush=True)
            print(f"      📊 Columns: {list(combined_df.columns)[:10]}...", flush=True)
            
            # Show sample feature values
            if "momentum" in combined_df.columns:
                momentum_stats = combined_df["momentum"].describe()
                print(f"      📊 Sample momentum: mean={momentum_stats['mean']:.4f}, "
                      f"std={momentum_stats['std']:.4f}", flush=True)
        
        # ✅ NEW: Validate DataFrame before returning
        validation_result = validate_dataframe_for_backtesting(combined_df)
        
        if not validation_result["valid"]:
            missing = validation_result["missing_required"]
            raise ValueError(f"DataFrame missing required columns: {missing}")
        
        if verbose and validation_result["missing_recommended"]:
            print(f"      ⚠️  Missing recommended features: {validation_result['missing_recommended']}", 
                  flush=True)
        
        return combined_df
        
    except FileNotFoundError:
        print(f"      ⚠️  Parquet file not found: {parquet_path}", flush=True)
        print(f"      ⚠️  Falling back to synthetic data for testing...", flush=True)
        return create_mock_dataframe_fallback(universe_data, interval, lookback)
    except Exception as e:
        print(f"      ⚠️  Error loading OHLC data: {e}", flush=True)
        print(f"      ⚠️  Falling back to synthetic data for testing...", flush=True)
        return create_mock_dataframe_fallback(universe_data, interval, lookback)


def create_mock_dataframe_fallback(universe_data: Dict, interval: int = 5, lookback: int = 20) -> pd.DataFrame:
    """
    Fallback: Create synthetic OHLC data for testing when real data is unavailable
    
    This is used only when the Parquet file is not found.
    
    Args:
        universe_data: Universe result dictionary
        interval: Interval in minutes
        lookback: Lookback period
        
    Returns:
        DataFrame with synthetic OHLC data + extracted features
    """
    np.random.seed(RANDOM_SEED)
    
    # Generate more realistic number of bars (1 year of 5min data = ~105k bars)
    # For testing, use a smaller but reasonable amount
    n_bars = 10000
    
    # Start from a base price
    base_price = 1.10
    
    # Generate random walk with realistic volatility
    returns = np.random.randn(n_bars) * 0.0001
    close_prices = base_price + np.cumsum(returns)
    
    # Generate OHLC from close prices
    opens = np.roll(close_prices, 1)
    opens[0] = base_price
    
    # High and low with some randomness
    highs = np.maximum(opens, close_prices) + np.abs(np.random.randn(n_bars)) * 0.00005
    lows = np.minimum(opens, close_prices) - np.abs(np.random.randn(n_bars)) * 0.00005
    
    # Create OHLC dataframe
    ohlc_df = pd.DataFrame({
        'open': opens,
        'high': highs,
        'low': lows,
        'close': close_prices,
        'mid_price': close_prices,
        'volume': np.random.randint(50, 500, n_bars),
    })
    
    # ✅ Extract features from universe JSON patterns
    features_df = extract_features_from_universe(universe_data)
    
    # ✅ Combine OHLC + features
    combined_df = combine_ohlc_with_features(ohlc_df, features_df)
    
    # Fill NaN values
    combined_df = combined_df.bfill().fillna(0)
    
    return combined_df


def backtest_universe(universe_data: Dict, strategies: List, parquet_path: Path = None, 
                      verbose: bool = False) -> Tuple[List[BacktestResults], Dict]:
    """
    Backtest all strategies for a universe
    
    Args:
        universe_data: Universe result dictionary
        strategies: List of Strategy objects
        parquet_path: Path to parquet file (default: from config)
        verbose: Whether to print detailed output
        
    Returns:
        Tuple of (list of BacktestResults, stats dict)
    """
    backtester = Backtester()
    
    # Load OHLC data for this universe
    # This now uses REAL price data from Parquet instead of mock data
    df = load_ohlc_for_universe(universe_data, parquet_path, verbose)
    
    # Validate data before backtesting
    if len(df) == 0:
        raise ValueError("❌ No data loaded for backtesting!")
    
    if "close" not in df.columns and "mid_price" not in df.columns:
        raise ValueError("❌ Price data missing (need 'close' or 'mid_price' column)!")
    
    # Check price variation
    price_col = "mid_price" if "mid_price" in df.columns else "close"
    price_std = df[price_col].std()
    if price_std == 0:
        raise ValueError("❌ Price data is constant (no variation)!")
    
    if verbose:
        print(f"      📊 Data loaded: {len(df):,} bars", flush=True)
        print(f"      📈 Price range: {df[price_col].min():.5f} - {df[price_col].max():.5f}", flush=True)
    
    results = []
    failed = 0
    
    for i, strategy in enumerate(strategies):
        try:
            if verbose and i % 10 == 0:
                print(f"      Backtesting strategy {i+1}/{len(strategies)}...", flush=True)
            
            result = backtester.backtest(strategy, df, initial_capital=INITIAL_CAPITAL)
            results.append(result)
            
        except Exception as e:
            if verbose:
                print(f"      ⚠️  Strategy {strategy.name} failed: {e}", flush=True)
            failed += 1
            continue
    
    stats = {
        "total_strategies": len(strategies),
        "successful": len(results),
        "failed": failed,
    }
    
    return results, stats


# ═══════════════════════════════════════════════════════════════
# 💾 RESULTS SAVING
# ═══════════════════════════════════════════════════════════════

def save_universe_backtest_results(universe_data: Dict, results: List[BacktestResults], 
                                   stats: Dict, output_dir: Path):
    """
    Save backtest results for a universe
    
    Args:
        universe_data: Universe result dictionary
        results: List of BacktestResults
        stats: Statistics dictionary
        output_dir: Output directory
    """
    # Extract universe identifier
    filepath = Path(universe_data.get('_filepath', ''))
    universe_name = filepath.stem if filepath.stem else 'unknown'
    
    # Prepare output
    output = {
        "universe_name": universe_name,
        "universe_metadata": {
            "interval": universe_data.get('interval'),
            "lookback": universe_data.get('lookback'),
            "total_patterns": universe_data.get('total_patterns', 0),
        },
        "backtest_timestamp": datetime.now().isoformat(),
        "statistics": stats,
        "results": [r.to_dict() for r in results],
    }
    
    # Save to file
    output_file = output_dir / f"{universe_name}_backtest.json"
    with open(output_file, 'w') as f:
        json.dump(output, f, indent=2)
    
    return output_file


def save_consolidated_results(all_universe_results: List[Dict], output_dir: Path):
    """
    Save consolidated results from all universes
    
    Args:
        all_universe_results: List of universe backtest result dicts
        output_dir: Output directory
    """
    # Consolidate all results
    consolidated = {
        "backtest_timestamp": datetime.now().isoformat(),
        "total_universes": len(all_universe_results),
        "universes": all_universe_results,
    }
    
    output_file = output_dir / "consolidated_backtest_results.json"
    with open(output_file, 'w') as f:
        json.dump(consolidated, f, indent=2)
    
    print(f"\n💾 Consolidated results saved to: {output_file}", flush=True)
    return output_file


# ═══════════════════════════════════════════════════════════════
# 🎯 MAIN EXECUTION
# ═══════════════════════════════════════════════════════════════

def print_banner():
    """Print startup banner"""
    print("""
═══════════════════════════════════════════════════════════
🌟 ULTRA NECROZMA - Sequential Backtesting
═══════════════════════════════════════════════════════════
    """, flush=True)


def print_summary(summary_stats: Dict):
    """Print final summary"""
    print("""
═══════════════════════════════════════════════════════════
🎉 BACKTESTING COMPLETE!
═══════════════════════════════════════════════════════════
    """, flush=True)
    
    print(f"\n📊 Summary:", flush=True)
    print(f"   Total Universes: {summary_stats['total_universes']}", flush=True)
    print(f"   Total Strategies Tested: {summary_stats['total_strategies']}", flush=True)
    print(f"   Viable Strategies (Sharpe > 1.0): {summary_stats['viable_strategies']}", flush=True)
    print(f"   Best Overall Sharpe: {summary_stats['best_sharpe']:.2f}", flush=True)
    print(f"   Total Time: {summary_stats['total_time']:.1f}s ({summary_stats['total_time']/3600:.2f} hours)", flush=True)
    
    if summary_stats.get('top_strategies'):
        print(f"\n🏆 Top {len(summary_stats['top_strategies'])} Strategies:", flush=True)
        for i, strat in enumerate(summary_stats['top_strategies'][:5], 1):
            print(f"   #{i} {strat['name']} (Sharpe: {strat['sharpe']:.2f}, Return: {strat['return']:.1%})", flush=True)
    
    print(f"\n💾 Results saved to:", flush=True)
    print(f"   📄 {summary_stats['consolidated_file']}", flush=True)
    print(f"   📄 {summary_stats['ranked_file']}", flush=True)
    print(f"   📄 {summary_stats['report_file']}", flush=True)


def main():
    """Main sequential backtesting runner"""
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description='Sequential Backtesting for ULTRA NECROZMA')
    parser.add_argument('--universes', type=str, help='Universe selection (e.g., "1,5,10-15,25")')
    parser.add_argument('--cpu-threshold', type=float, default=DEFAULT_CPU_THRESHOLD,
                       help=f'CPU threshold percentage (default: {DEFAULT_CPU_THRESHOLD})')
    parser.add_argument('--cooling-duration', type=int, default=DEFAULT_COOLING_DURATION,
                       help=f'Cooling break duration in seconds (default: {DEFAULT_COOLING_DURATION})')
    parser.add_argument('--skip-telegram', action='store_true',
                       help='Skip Telegram notifications')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Verbose output')
    parser.add_argument('--results-dir', type=str, default='ultra_necrozma_results',
                       help='Directory containing universe results (default: ultra_necrozma_results)')
    parser.add_argument('--max-strategies', type=int, default=50,
                       help='Maximum strategies to generate per universe (default: 50)')
    
    args = parser.parse_args()
    
    # Setup
    print_banner()
    
    # Initialize lore system
    lore = LoreSystem(enabled=True, enable_telegram=not args.skip_telegram)
    lore.broadcast(EventType.AWAKENING, "Sequential backtesting initiated...")
    
    # Parse universe selection
    universe_ids = None
    if args.universes:
        universe_ids = parse_universe_selection(args.universes)
        print(f"\n📌 Selected universes: {universe_ids}", flush=True)
    
    # Load universe results
    results_dir = Path(args.results_dir)
    universes = load_universe_results(results_dir, universe_ids)
    
    if not universes:
        print("\n❌ No universes loaded. Exiting.", flush=True)
        return 1
    
    # Setup output directory
    output_dir = results_dir / "backtest_results"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"\n💾 Output directory: {output_dir}", flush=True)
    print(f"⚙️  CPU threshold: {args.cpu_threshold}%", flush=True)
    print(f"❄️  Cooling duration: {args.cooling_duration}s", flush=True)
    print(f"📊 Max strategies per universe: {args.max_strategies}", flush=True)
    
    # Track overall statistics
    start_time = time.time()
    all_results = []
    all_backtest_results = {}  # (universe_name, strategy_name) -> BacktestResults for unique key
    all_backtest_results_list = []  # List of all BacktestResults for ranking
    total_strategies_tested = 0
    
    # Process each universe sequentially
    for idx, universe_data in enumerate(universes, 1):
        universe_name = Path(universe_data.get('_filepath', '')).stem
        
        print(f"\n{'─'*63}", flush=True)
        print(f"📊 Universe {idx}/{len(universes)}: {universe_name}", flush=True)
        print(f"{'─'*63}", flush=True)
        
        try:
            # Check CPU before starting
            stats = get_system_stats()
            cpu_str = f"{stats['cpu_percent']:.1f}%" if HAS_PSUTIL else "N/A"
            
            # Generate strategies
            print(f"   🏭 Generating strategies...", flush=True)
            strategies = generate_strategies_for_universe(universe_data, args.max_strategies)
            print(f"   📈 Generated {len(strategies)} strategies", flush=True)
            
            # Backtest
            print(f"   📊 Backtesting... (CPU: {cpu_str})", flush=True)
            backtest_start = time.time()
            results, backtest_stats = backtest_universe(universe_data, strategies, PARQUET_FILE, args.verbose)
            backtest_time = time.time() - backtest_start
            
            # Find best strategy for this universe
            best_sharpe = 0.0
            best_result = None
            for result in results:
                if result.sharpe_ratio > best_sharpe:
                    best_sharpe = result.sharpe_ratio
                    best_result = result
                # Store in global dict with unique key (universe_name, strategy_name)
                all_backtest_results[(universe_name, result.strategy_name)] = result
                # Also add to list for ranking
                all_backtest_results_list.append(result)
            
            print(f"   ✅ Complete! Best Sharpe: {best_sharpe:.2f}", flush=True)
            
            # Save individual universe results
            output_file = save_universe_backtest_results(
                universe_data, results, backtest_stats, output_dir
            )
            print(f"   💾 Saved: {output_file.name}", flush=True)
            print(f"   ⏱️  Time: {backtest_time:.1f}s", flush=True)
            
            # Track stats
            all_results.append({
                "universe_name": universe_name,
                "strategies_tested": len(strategies),
                "successful": len(results),
                "best_sharpe": best_sharpe,
                "processing_time": backtest_time,
            })
            total_strategies_tested += len(strategies)
            
            # Garbage collection
            del strategies, results
            gc.collect()
            
            # Cooling break every N universes
            if idx % COOLING_INTERVAL == 0 and idx < len(universes):
                cooling_break(args.cooling_duration, args.cpu_threshold)
            
        except Exception as e:
            print(f"   ❌ Error processing universe: {e}", flush=True)
            if args.verbose:
                traceback.print_exc()
            continue
    
    total_time = time.time() - start_time
    
    # Rank all strategies using LightFinder
    print(f"\n{'═'*63}", flush=True)
    print(f"🌟 Ranking strategies...", flush=True)
    print(f"{'═'*63}", flush=True)
    
    if all_backtest_results_list:
        finder = LightFinder()
        ranked_strategies = finder.rank_strategies(all_backtest_results_list, top_n=20)
        
        # Save ranked strategies
        ranked_file = output_dir / "top_strategies_ranked.json"
        ranked_data = {
            "timestamp": datetime.now().isoformat(),
            "total_strategies": len(all_backtest_results_list),
            "top_strategies": ranked_strategies.to_dict('records')
        }
        with open(ranked_file, 'w') as f:
            json.dump(ranked_data, f, indent=2)
        print(f"\n💾 Ranked strategies saved to: {ranked_file}", flush=True)
    else:
        ranked_strategies = pd.DataFrame()
        ranked_file = None
    
    # Generate final Light Report
    print(f"\n📝 Generating final Light Report...", flush=True)
    
    # Convert backtest results list to dict for report (use last occurrence of each strategy name)
    backtest_results_dict = {}
    for result in all_backtest_results_list:
        backtest_results_dict[result.strategy_name] = result
    
    report_generator = LightReportGenerator(output_dir=output_dir)
    report = report_generator.generate_report(
        top_strategies=ranked_strategies,
        all_backtest_results=backtest_results_dict,
        total_strategies=total_strategies_tested
    )
    
    report_file = report_generator.save_report(report)
    report_generator.print_summary(report)
    
    # Save consolidated results
    consolidated_file = save_consolidated_results(all_results, output_dir)
    
    # Calculate summary statistics
    viable_count = sum(1 for r in all_backtest_results_list if r.sharpe_ratio > 1.0)
    best_sharpe = max((r.sharpe_ratio for r in all_backtest_results_list), default=0.0)
    
    top_strategies_list = []
    if len(ranked_strategies) > 0:
        for _, row in ranked_strategies.head(5).iterrows():
            top_strategies_list.append({
                'name': row['strategy_name'],
                'sharpe': row['sharpe_ratio'],
                'return': row['total_return'],
            })
    
    summary_stats = {
        'total_universes': len(universes),
        'total_strategies': total_strategies_tested,
        'viable_strategies': viable_count,
        'best_sharpe': best_sharpe,
        'total_time': total_time,
        'top_strategies': top_strategies_list,
        'consolidated_file': consolidated_file,
        'ranked_file': ranked_file,
        'report_file': report_file,
    }
    
    # Print final summary
    print_summary(summary_stats)
    
    # Broadcast completion
    lore.broadcast(EventType.COMPLETION, "Sequential backtesting complete!")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
