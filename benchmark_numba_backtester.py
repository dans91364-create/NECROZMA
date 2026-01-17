#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚡🌟💎 NECROZMA - NUMBA BACKTESTER BENCHMARK 💎🌟⚡

Benchmark script to validate performance improvements from Numba optimization
"""

import numpy as np
import pandas as pd
import time
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from backtester import Backtester, BacktestProgress, NUMBA_AVAILABLE


# ═══════════════════════════════════════════════════════════════
# 🧪 TEST STRATEGY
# ═══════════════════════════════════════════════════════════════

class BenchmarkStrategy:
    """Simple test strategy for benchmarking"""
    
    def __init__(self, name="BenchmarkStrategy"):
        self.name = name
        self.params = {
            "stop_loss_pips": 20,
            "take_profit_pips": 40
        }
    
    def generate_signals(self, df):
        """Generate signals based on momentum"""
        signals = pd.Series(0, index=df.index)
        
        # Generate signals every 100 ticks
        for i in range(0, len(signals), 100):
            if i < len(signals):
                # Alternate between buy and sell
                signals.iloc[i] = 1 if (i // 100) % 2 == 0 else -1
        
        return signals


# ═══════════════════════════════════════════════════════════════
# 📊 BENCHMARK FUNCTIONS
# ═══════════════════════════════════════════════════════════════

def generate_test_data(n_ticks: int) -> pd.DataFrame:
    """Generate realistic tick data for benchmarking"""
    np.random.seed(42)
    
    # Simulate EUR/USD price movement
    base_price = 1.0500
    price_changes = np.random.randn(n_ticks) * 0.00005
    mid_prices = base_price + np.cumsum(price_changes)
    
    # Add spread (1 pip = 0.0001)
    spread = 0.00010
    bid_prices = mid_prices - spread / 2
    ask_prices = mid_prices + spread / 2
    
    df = pd.DataFrame({
        'bid': bid_prices,
        'ask': ask_prices,
        'mid_price': mid_prices,
        'momentum': np.random.randn(n_ticks) * 0.1,
        'volatility': np.abs(np.random.randn(n_ticks) * 0.01)
    })
    
    return df


def benchmark_single_backtest(n_ticks: int = 100_000):
    """Benchmark a single backtest with various data sizes"""
    print(f"\n{'='*80}")
    print(f"📊 BENCHMARK: Single Backtest Performance")
    print(f"{'='*80}\n")
    
    config = {
        'capital': {
            'initial_capital': 10000,
            'default_lot_size': 0.1,
            'pip_value_per_lot': 10,
            'pip_decimal_places': 4
        },
        'backtester': {
            'lot_sizes': [0.1],
            'commission_per_lot': 0.05
        }
    }
    
    print(f"Generating {n_ticks:,} ticks of test data...")
    df = generate_test_data(n_ticks)
    print(f"   ✅ Generated {len(df):,} ticks")
    print(f"   Price range: {df['mid_price'].min():.5f} - {df['mid_price'].max():.5f}\n")
    
    strategy = BenchmarkStrategy()
    backtester = Backtester(config=config)
    
    print("Running backtest...")
    start_time = time.time()
    results = backtester.backtest(strategy, df, multi_lot=False)
    elapsed = time.time() - start_time
    
    print(f"\n   ⏱️  Time: {elapsed:.3f} seconds")
    print(f"   📊 Trades: {results.n_trades}")
    print(f"   💰 Win Rate: {results.win_rate:.2%}")
    print(f"   📈 Total Return: {results.total_return:.2%}")
    print(f"   ⚡ Throughput: {n_ticks/elapsed:,.0f} ticks/sec")
    
    # Estimate for full dataset
    print(f"\n   Estimated time for 14.6M ticks: {(14_600_000 / n_ticks) * elapsed:.1f} seconds")
    
    return elapsed, results


def benchmark_multi_lot(n_ticks: int = 100_000):
    """Benchmark multi-lot backtesting"""
    print(f"\n{'='*80}")
    print(f"📊 BENCHMARK: Multi-Lot Backtest Performance")
    print(f"{'='*80}\n")
    
    config = {
        'capital': {
            'initial_capital': 10000,
            'default_lot_size': 0.1,
            'pip_value_per_lot': 10,
            'pip_decimal_places': 4
        },
        'backtester': {
            'lot_sizes': [0.01, 0.1, 1.0],
            'commission_per_lot': 0.05
        }
    }
    
    print(f"Generating {n_ticks:,} ticks of test data...")
    df = generate_test_data(n_ticks)
    
    strategy = BenchmarkStrategy()
    backtester = Backtester(config=config)
    
    print("Running multi-lot backtest (3 lot sizes)...")
    start_time = time.time()
    results_dict = backtester.backtest(strategy, df, multi_lot=True)
    elapsed = time.time() - start_time
    
    print(f"\n   ⏱️  Total Time: {elapsed:.3f} seconds")
    print(f"   ⏱️  Time per lot size: {elapsed/3:.3f} seconds")
    
    for lot_size, results in results_dict.items():
        print(f"\n   Lot {lot_size}:")
        print(f"      Trades: {results.n_trades}")
        print(f"      Return: {results.total_return:.2%}")
    
    return elapsed


def benchmark_multiple_strategies(n_strategies: int = 100, n_ticks: int = 10_000):
    """Benchmark multiple strategy backtests"""
    print(f"\n{'='*80}")
    print(f"📊 BENCHMARK: Multiple Strategies ({n_strategies} strategies)")
    print(f"{'='*80}\n")
    
    config = {
        'capital': {
            'initial_capital': 10000,
            'default_lot_size': 0.1,
            'pip_value_per_lot': 10,
            'pip_decimal_places': 4
        },
        'backtester': {
            'lot_sizes': [0.01, 0.1, 1.0],
            'commission_per_lot': 0.05
        }
    }
    
    print(f"Generating {n_ticks:,} ticks of test data...")
    df = generate_test_data(n_ticks)
    
    # Create strategies
    strategies = [BenchmarkStrategy(f"Strategy_{i}") for i in range(n_strategies)]
    
    backtester = Backtester(config=config)
    
    print(f"Running {n_strategies} backtests with progress tracking...")
    start_time = time.time()
    results = backtester.test_strategies(strategies, df, verbose=True, show_progress_bar=True)
    elapsed = time.time() - start_time
    
    total_backtests = n_strategies * 3  # 3 lot sizes
    avg_time = elapsed / total_backtests
    
    print(f"\n   📊 Summary:")
    print(f"      Total time: {elapsed:.2f} seconds")
    print(f"      Average per backtest: {avg_time:.3f} seconds")
    print(f"      Total backtests: {total_backtests}")
    
    # Estimate for full pipeline (4,620 strategies × 3 lots = 13,860 backtests)
    full_pipeline_time = 13_860 * avg_time
    print(f"\n   🔮 Projection for 13,860 backtests:")
    print(f"      Estimated time: {full_pipeline_time/3600:.2f} hours")
    print(f"      vs. Old estimate: ~696 hours (29 days)")
    print(f"      Speedup: {696 / (full_pipeline_time/3600):.0f}x faster")
    
    return elapsed


def benchmark_compilation_overhead():
    """Measure Numba JIT compilation overhead"""
    print(f"\n{'='*80}")
    print(f"📊 BENCHMARK: Numba JIT Compilation Overhead")
    print(f"{'='*80}\n")
    
    config = {
        'capital': {
            'initial_capital': 10000,
            'default_lot_size': 0.1,
            'pip_value_per_lot': 10,
            'pip_decimal_places': 4
        },
        'backtester': {
            'lot_sizes': [0.1],
            'commission_per_lot': 0.05
        }
    }
    
    # Small dataset for quick tests
    df = generate_test_data(1000)
    strategy = BenchmarkStrategy()
    
    # First run (with JIT compilation)
    print("First run (includes JIT compilation)...")
    backtester1 = Backtester(config=config)
    start = time.time()
    results1 = backtester1.backtest(strategy, df, multi_lot=False)
    first_run_time = time.time() - start
    print(f"   Time: {first_run_time:.3f} seconds")
    
    # Second run (JIT compiled, cached)
    print("\nSecond run (JIT compiled)...")
    backtester2 = Backtester(config=config)
    start = time.time()
    results2 = backtester2.backtest(strategy, df, multi_lot=False)
    second_run_time = time.time() - start
    print(f"   Time: {second_run_time:.3f} seconds")
    
    # Third run
    print("\nThird run (cached)...")
    backtester3 = Backtester(config=config)
    start = time.time()
    results3 = backtester3.backtest(strategy, df, multi_lot=False)
    third_run_time = time.time() - start
    print(f"   Time: {third_run_time:.3f} seconds")
    
    print(f"\n   Compilation overhead: {first_run_time - second_run_time:.3f} seconds")
    print(f"   Speedup after compilation: {first_run_time/second_run_time:.1f}x")


# ═══════════════════════════════════════════════════════════════
# 🚀 MAIN BENCHMARK
# ═══════════════════════════════════════════════════════════════

def main():
    """Run all benchmarks"""
    print("""
╔══════════════════════════════════════════════════════════════╗
║         ⚡ NUMBA BACKTESTER PERFORMANCE BENCHMARK ⚡         ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    print(f"✅ Numba Available: {NUMBA_AVAILABLE}")
    
    if not NUMBA_AVAILABLE:
        print("❌ Numba not available! Install with: pip install numba>=0.57.0")
        return
    
    # Benchmark 1: Single backtest with realistic data size
    benchmark_single_backtest(n_ticks=100_000)
    
    # Benchmark 2: Multi-lot backtest
    benchmark_multi_lot(n_ticks=100_000)
    
    # Benchmark 3: Multiple strategies (simulates real workflow)
    benchmark_multiple_strategies(n_strategies=50, n_ticks=10_000)
    
    # Benchmark 4: JIT compilation overhead
    benchmark_compilation_overhead()
    
    print(f"\n{'='*80}")
    print("✅ BENCHMARK COMPLETE!")
    print(f"{'='*80}\n")


if __name__ == "__main__":
    main()
