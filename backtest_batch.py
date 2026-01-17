#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚡🌟💎 NECROZMA - BATCH BACKTEST WORKER 💎🌟⚡

Worker script for batch processing of strategy backtests
Runs in isolated subprocess to prevent memory accumulation

Usage:
    python backtest_batch.py --start 0 --end 200 --output results_batch_0.parquet
"""

import sys
import argparse
import time
from pathlib import Path
import pandas as pd
import psutil

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from data_loader import load_crystal
from strategy_factory import StrategyFactory
from backtester import Backtester
from config import PARQUET_FILE, STRATEGY_TEMPLATES, STRATEGY_PARAMS
from batch_utils import prepare_features


def parse_arguments():
    """Parse command-line arguments"""
    parser = argparse.ArgumentParser(
        description="Batch backtest worker for strategy testing"
    )
    
    parser.add_argument(
        "--start",
        type=int,
        required=True,
        help="Start index (inclusive)"
    )
    
    parser.add_argument(
        "--end",
        type=int,
        required=True,
        help="End index (exclusive)"
    )
    
    parser.add_argument(
        "--output",
        type=str,
        required=True,
        help="Output parquet file path"
    )
    
    parser.add_argument(
        "--parquet",
        type=str,
        default=None,
        help="Path to input parquet data file (overrides config)"
    )
    
    return parser.parse_args()


def main():
    """Main worker execution"""
    args = parse_arguments()
    
    start_idx = args.start
    end_idx = args.end
    output_path = Path(args.output)
    
    # Get data file path
    parquet_path = Path(args.parquet) if args.parquet else PARQUET_FILE
    
    print(f"\n{'='*80}")
    print(f"⚡ BATCH WORKER: Strategies {start_idx}-{end_idx}")
    print(f"{'='*80}")
    
    # Track memory at start
    process = psutil.Process()
    mem_start = process.memory_info().rss / (1024 ** 3)  # GB
    
    try:
        # Step 1: Load data
        print(f"\n📊 Loading data from: {parquet_path}")
        load_start = time.time()
        df = load_crystal(parquet_path)
        load_time = time.time() - load_start
        print(f"   ✅ Loaded {len(df):,} rows in {load_time:.1f}s")
        
        # Step 2: Add required features if missing
        print(f"\n🔧 Preparing features...")
        df = prepare_features(df)
        print(f"   ✅ Features ready")
        
        # Step 3: Generate all strategies
        print(f"\n🏭 Generating strategies...")
        factory = StrategyFactory(
            templates=STRATEGY_TEMPLATES,
            params=STRATEGY_PARAMS
        )
        all_strategies = factory.generate_strategies()
        total_strategies = len(all_strategies)
        print(f"   ✅ Generated {total_strategies:,} total strategies")
        
        # Step 4: Select batch subset
        batch_strategies = all_strategies[start_idx:end_idx]
        batch_size = len(batch_strategies)
        print(f"\n📦 Batch subset: {batch_size} strategies ({start_idx} to {end_idx})")
        
        if batch_size == 0:
            print(f"   ⚠️  No strategies in this batch range!")
            # Create empty results file
            empty_df = pd.DataFrame()
            empty_df.to_parquet(output_path, compression='snappy')
            return
        
        # Step 5: Backtest batch
        print(f"\n🚀 Backtesting {batch_size} strategies...")
        bt_start = time.time()
        
        backtester = Backtester()
        results = backtester.test_strategies(
            batch_strategies, 
            df,
            verbose=True,
            show_progress_bar=True
        )
        
        bt_time = time.time() - bt_start
        avg_time = bt_time / batch_size if batch_size > 0 else 0
        
        print(f"\n   ✅ Backtesting complete in {bt_time:.1f}s")
        print(f"      Average: {avg_time:.3f}s per strategy")
        
        # Step 6: Convert results to DataFrame
        print(f"\n💾 Preparing results...")
        results_data = []
        
        for strategy_name, lot_results in results.items():
            for lot_size, backtest_result in lot_results.items():
                # Extract metrics from BacktestResults object
                result_dict = {
                    'strategy_name': strategy_name,
                    'lot_size': lot_size,
                    'sharpe_ratio': backtest_result.sharpe_ratio,
                    'sortino_ratio': backtest_result.sortino_ratio,
                    'calmar_ratio': backtest_result.calmar_ratio,
                    'total_return': backtest_result.total_return,
                    'max_drawdown': backtest_result.max_drawdown,
                    'win_rate': backtest_result.win_rate,
                    'n_trades': backtest_result.n_trades,
                    'profit_factor': backtest_result.profit_factor,
                    'avg_win': backtest_result.avg_win,
                    'avg_loss': backtest_result.avg_loss,
                    'expectancy': backtest_result.expectancy,
                    'gross_pnl': backtest_result.gross_pnl,
                    'net_pnl': backtest_result.net_pnl,
                    'total_commission': backtest_result.total_commission,
                }
                results_data.append(result_dict)
        
        results_df = pd.DataFrame(results_data)
        print(f"   ✅ Converted {len(results_df)} results")
        
        # Step 7: Save to parquet
        print(f"\n💾 Saving results to: {output_path}")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        results_df.to_parquet(output_path, compression='snappy')
        
        file_size_mb = output_path.stat().st_size / (1024 ** 2)
        print(f"   ✅ Saved {file_size_mb:.2f} MB")
        
        # Step 8: Final stats
        mem_end = process.memory_info().rss / (1024 ** 3)  # GB
        mem_peak = mem_end
        
        print(f"\n{'='*80}")
        print(f"✅ BATCH COMPLETE")
        print(f"{'='*80}")
        print(f"   Strategies: {batch_size}")
        print(f"   Time: {bt_time:.1f}s")
        print(f"   Memory: {mem_start:.2f}GB → {mem_end:.2f}GB (Δ{mem_end-mem_start:+.2f}GB)")
        print(f"   Output: {output_path}")
        print(f"{'='*80}\n")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
