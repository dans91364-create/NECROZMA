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
import json
import shutil
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))


# ═══════════════════════════════════════════════════════════════
# 🔧 CONSTANTS
# ═══════════════════════════════════════════════════════════════

# Common version attribute names to check when getting module versions
VERSION_ATTRIBUTES = ['__version__', 'version', 'VERSION', '_version']

# Pip conversion factor (for EURUSD and most major pairs)
PIPS_MULTIPLIER = 10000

# Epsilon for numerical stability (avoid division by zero)
EPSILON = 1e-10


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
  
  # NEW: Split workflow for efficient strategy testing
  # Step 1: Generate base files (run once per pair)
  python main.py --parquet GBPUSD_2025.parquet --generate-base
  
  # Step 2: Test strategies (run multiple times with different configs)
  python main.py --parquet GBPUSD_2025.parquet --search-light
  python main.py --parquet GBPUSD_2025.parquet --search-light --force-rerun
  
  # Generate interactive dashboard
  python main.py --generate-dashboard
  
  # Generate and open dashboard automatically
  python main.py --open-dashboard
  
  # Sequential processing (disable multiprocessing)
  python main.py --sequential
  
  # Batch processing (prevents memory accumulation during backtesting)
  python main.py --strategy-discovery --batch-mode
  python main.py --strategy-discovery --batch-mode --batch-size 200
  
  # Force rerun backtesting (ignore cache)
  python main.py --strategy-discovery --batch-mode --force-rerun
  
  # Chunked processing examples
  python main.py --chunk-size monthly --strategy auto
  python main.py --chunk-size weekly --strategy universe
  python main.py --resume  # Resume from last checkpoint
  python main.py --fresh   # Start fresh, ignore checkpoints
  
  # VM-safe mode with cooling breaks
  python main.py --strategy universe --cooling-chunk-interval 3 --max-cpu 80
  
  # Process specific universes or chunks
  python main.py --universes "1,5,10-15" --chunks "1-6"
  
  # VAST MODE: High-performance parallel processing for cloud machines
  # Auto-detect and use all resources
  python main.py --vast-mode --input-dir data/parquet/ --generate-base
  
  # Specify parallelism manually
  python main.py --vast-mode --input-dir data/parquet/ --generate-base --parallel-pairs 30 --max-workers 4
  
  # Just search-light on existing bases
  python main.py --vast-mode --input-dir data/parquet/ --search-light
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
        help="Force sequential processing (recommended for VMs, low CPU mode, single thread)"
    )
    
    parser.add_argument(
        "--force-sequential",
        action="store_true",
        dest="sequential",
        help="Alias for --sequential (force single-threaded processing)"
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
        "--generate-base",
        action="store_true",
        help="Generate base files (universes + patterns + regimes), then stop. Run once per pair."
    )
    
    parser.add_argument(
        "--search-light",
        action="store_true",
        help="Run strategy generation + backtesting using existing base. Can run multiple times."
    )
    
    parser.add_argument(
        "--skip-telegram",
        action="store_true",
        help="Disable Telegram notifications"
    )
    
    parser.add_argument(
        "--generate-dashboard",
        action="store_true",
        help="Generate HTML dashboard after analysis"
    )
    
    parser.add_argument(
        "--open-dashboard",
        action="store_true",
        help="Auto-open dashboard in browser (implies --generate-dashboard)"
    )
    
    # Batch processing arguments
    parser.add_argument(
        "--batch-mode",
        action="store_true",
        help="Enable batch processing with subprocess isolation (prevents memory accumulation)"
    )
    
    parser.add_argument(
        "--batch-size",
        type=int,
        default=200,
        help="Number of strategies per batch (default: 200)"
    )
    
    parser.add_argument(
        "--force-rerun",
        action="store_true",
        help="Force rerun of backtesting even if cached results exist"
    )
    
    # Chunking arguments
    parser.add_argument(
        "--chunk-size",
        type=str,
        choices=["daily", "weekly", "monthly"],
        default="monthly",
        help="Temporal chunk size for processing (default: monthly)"
    )
    
    parser.add_argument(
        "--keep-chunks",
        action="store_true",
        help="Keep chunk files after processing"
    )
    
    # Strategy arguments
    parser.add_argument(
        "--strategy",
        type=str,
        choices=["chunked", "universe", "auto"],
        default="auto",
        help="Processing strategy: chunked (fast, more memory), universe (slow, less memory), auto (decide based on RAM)"
    )
    
    # Cooling arguments
    parser.add_argument(
        "--cooling-chunk-interval",
        type=int,
        default=3,
        help="Cooling break every N chunks (default: 3, 0 to disable)"
    )
    
    parser.add_argument(
        "--cooling-universe-interval",
        type=int,
        default=5,
        help="Cooling break every N universes (default: 5, 0 to disable)"
    )
    
    parser.add_argument(
        "--cooling-duration",
        type=int,
        default=120,
        help="Cooling break duration in seconds (default: 120)"
    )
    
    # CPU monitoring arguments
    parser.add_argument(
        "--max-cpu",
        type=int,
        default=85,
        help="Pause if CPU > this %% for 5+ minutes (default: 85)"
    )
    
    # Resume arguments
    parser.add_argument(
        "--resume",
        action="store_true",
        help="Resume from last checkpoint if available"
    )
    
    parser.add_argument(
        "--fresh",
        action="store_true",
        help="Ignore cache and checkpoints, recalculate everything from scratch"
    )
    
    parser.add_argument(
        "--skip-existing",
        action="store_true",
        default=True,
        help="Skip universes that already exist (default: True). Use --no-skip-existing to recalculate all."
    )
    
    parser.add_argument(
        "--no-skip-existing",
        action="store_false",
        dest="skip_existing",
        help="Recalculate all universes even if they exist"
    )
    
    # Specific processing arguments
    parser.add_argument(
        "--universes",
        type=str,
        default=None,
        help='Process specific universes (e.g., "1,5,10-15,20")'
    )
    
    parser.add_argument(
        "--chunks",
        type=str,
        default=None,
        help='Process specific chunks (e.g., "1-6,12")'
    )
    
    # VAST Mode arguments (high-performance parallel processing)
    parser.add_argument(
        "--vast-mode",
        action="store_true",
        help="Optimize for high-performance machines (auto-detects cores/RAM and maximizes utilization)"
    )
    
    parser.add_argument(
        "--input-dir",
        type=str,
        default=None,
        help="Directory containing multiple parquet files to process in parallel"
    )
    
    parser.add_argument(
        "--parallel-pairs",
        type=int,
        default=1,
        help="Number of currency pairs to process simultaneously (default: 1, auto in vast-mode)"
    )
    
    parser.add_argument(
        "--max-workers",
        type=int,
        default=None,
        help="Maximum workers per pair for parallel processing (default: auto-detect)"
    )
    
    return parser.parse_args()


# ═══════════════════════════════════════════════════════════════
# ⚡ VAST MODE FUNCTIONS
# ═══════════════════════════════════════════════════════════════

def detect_resources():
    """
    Detect available system resources
    
    Returns:
        dict: Dictionary containing:
            - cpu_cores: Number of CPU cores
            - ram_gb: Total RAM in GB
            - recommended_parallel_pairs: Recommended number of pairs to process in parallel
            - recommended_workers_per_pair: Recommended workers per pair
            - recommended_chunk_size: Recommended chunk size for memory operations (reserved for future use)
    """
    import psutil
    
    cpu_count = os.cpu_count() or 8
    ram_gb = psutil.virtual_memory().total / (1024**3)
    
    return {
        'cpu_cores': cpu_count,
        'ram_gb': ram_gb,
        'recommended_parallel_pairs': min(30, max(1, cpu_count // 4)),  # 4 cores per pair, minimum 1
        'recommended_workers_per_pair': 4,
        'recommended_chunk_size': int(ram_gb * 10_000_000)  # Reserved for future memory optimization
    }


def print_resources_banner(resources, num_parquet_files, parallel_pairs, workers_per_pair):
    """
    Print VAST mode banner with detected resources
    
    Args:
        resources: Dictionary from detect_resources()
        num_parquet_files: Number of parquet files to process
        parallel_pairs: Number of pairs to process in parallel
        workers_per_pair: Number of workers per pair
    """
    # Estimate time based on typical runtime (3-4 hours for 128 cores)
    # Scale based on actual resources
    base_time_hours = 3.5
    cpu_cores = max(1, resources['cpu_cores'])  # Prevent division by zero
    scaling_factor = 128 / cpu_cores
    estimated_hours = base_time_hours * scaling_factor
    
    print("\n")
    print("╔═══════════════════════════════════════════════════════════════════════════════╗")
    print("║                    ⚡ VAST MODE ACTIVATED ⚡                                   ║")
    print("╠═══════════════════════════════════════════════════════════════════════════════╣")
    print(f"║   🖥️  CPU Cores:     {resources['cpu_cores']:<55} ║")
    print(f"║   🧠 RAM:           {resources['ram_gb']:.0f} GB{' ' * (55 - len(f'{resources['ram_gb']:.0f} GB'))} ║")
    print(f"║   📁 Parquet Files: {num_parquet_files:<55} ║")
    print(f"║   ⚡ Parallel Pairs: {parallel_pairs:<55} ║")
    print(f"║   👷 Workers/Pair:  {workers_per_pair:<55} ║")
    print(f"║   📊 Est. Time:     ~{estimated_hours:.1f} hours{' ' * (55 - len(f'~{estimated_hours:.1f} hours'))} ║")
    print("╚═══════════════════════════════════════════════════════════════════════════════╝")
    print()


# ═══════════════════════════════════════════════════════════════
# 🧠 STRATEGY SELECTION
# ═══════════════════════════════════════════════════════════════

def select_strategy():
    """
    Auto-select best strategy based on environment
    
    Returns:
        str: Selected strategy ('chunked' or 'universe')
    """
    import psutil
    
    total_ram_gb = psutil.virtual_memory().total / 1e9
    
    # Check if VM (basic heuristic)
    is_vm = False
    try:
        # Check for common VM indicators
        product_name_file = Path('/sys/class/dmi/id/product_name')
        if product_name_file.exists():
            product_name = product_name_file.read_text().strip()
            is_vm = any(indicator in product_name.lower() for indicator in 
                       ['vmware', 'virtualbox', 'kvm', 'qemu', 'xen', 'hyperv'])
    except:
        pass
    
    # Decision logic
    if is_vm:
        print(f"   🖥️  VM detected - selecting 'universe' strategy (better checkpointing)")
        return 'universe'
    elif total_ram_gb < 32:
        print(f"   💾 RAM < 32GB ({total_ram_gb:.1f}GB) - selecting 'universe' strategy (memory constrained)")
        return 'universe'
    else:
        print(f"   ⚡ Bare metal + {total_ram_gb:.1f}GB RAM - selecting 'chunked' strategy (fast processing)")
        return 'chunked'


def parse_range_string(range_str: str) -> list:
    """
    Parse range string like "1,5,10-15,20" into list of integers
    
    Args:
        range_str: Range string
    
    Returns:
        list: List of integers
    """
    if not range_str:
        return []
    
    result = []
    parts = range_str.split(',')
    
    for part in parts:
        part = part.strip()
        if '-' in part:
            start, end = part.split('-')
            result.extend(range(int(start), int(end) + 1))
        else:
            result.append(int(part))
    
    return sorted(set(result))


# ═══════════════════════════════════════════════════════════════
# 🔍 SYSTEM CHECK
# ═══════════════════════════════════════════════════════════════

def get_version(module):
    """
    Safely get module version
    
    Args:
        module: Python module object
        
    Returns:
        str: Version string or "installed" if version not found
    """
    # Try common version attributes
    for attr in VERSION_ATTRIBUTES:
        if hasattr(module, attr):
            version = getattr(module, attr)
            # Handle version_info tuples
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
        print(f"✓ NumPy: {get_version(np)}")
    except ImportError:
        print("✗ NumPy: NOT FOUND")
        issues.append("NumPy")
    
    # Check Pandas
    try:
        import pandas as pd
        print(f"✓ Pandas: {get_version(pd)}")
    except ImportError:
        print("✗ Pandas: NOT FOUND")
        issues.append("Pandas")
    
    # Check PyArrow
    try:
        import pyarrow as pa
        print(f"✓ PyArrow: {get_version(pa)}")
    except ImportError:
        print("✗ PyArrow: NOT FOUND (required for Parquet)")
        issues.append("PyArrow")
    
    # Check SciPy
    try:
        import scipy
        print(f"✓ SciPy: {get_version(scipy)}")
    except ImportError:
        print("✗ SciPy: NOT FOUND")
        issues.append("SciPy")
    
    # Check Numba
    try:
        import numba
        print(f"✓ Numba: {get_version(numba)}")
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
# 💾 MEMORY MANAGEMENT
# ═══════════════════════════════════════════════════════════════

def cleanup_memory():
    """
    Aggressive memory cleanup between processing steps
    """
    import gc
    import psutil
    
    # Force garbage collection
    gc.collect()
    
    # Log memory usage
    mem = psutil.virtual_memory()
    print(f"💾 Memory: {mem.used/1e9:.1f}GB / {mem.total/1e9:.1f}GB ({mem.percent}%)")
    
    # Warn if high
    if mem.percent > 80:
        print("⚠️  Memory usage high - pausing for cooldown")
        time.sleep(30)
        gc.collect()
        
        mem = psutil.virtual_memory()
        print(f"💾 After cooldown: {mem.used/1e9:.1f}GB / {mem.total/1e9:.1f}GB ({mem.percent}%)")


def show_progress(
    universe_idx: int,
    total_universes: int,
    chunk_idx: int,
    total_chunks: int,
    elapsed_time: float,
    strategy: str,
    memory_gb: float,
    memory_total_gb: float,
    cpu_percent: float
):
    """
    Show detailed progress information
    
    Args:
        universe_idx: Current universe index
        total_universes: Total number of universes
        chunk_idx: Current chunk index
        total_chunks: Total number of chunks
        elapsed_time: Elapsed time in seconds
        strategy: Processing strategy
        memory_gb: Current memory usage in GB
        memory_total_gb: Total memory in GB
        cpu_percent: Current CPU percentage
    """
    # Calculate progress
    if strategy == "chunked":
        # Chunked: process all universes per chunk
        total_tasks = total_chunks
        completed_tasks = chunk_idx
        current_desc = f"Chunk {chunk_idx}/{total_chunks}"
    else:
        # Universe: process all chunks per universe
        total_tasks = total_universes
        completed_tasks = universe_idx
        current_desc = f"Universe {universe_idx}/{total_universes}"
    
    overall_progress = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
    
    # Calculate ETA
    if completed_tasks > 0 and elapsed_time > 0:
        avg_time_per_task = elapsed_time / completed_tasks
        remaining_tasks = total_tasks - completed_tasks
        eta_seconds = remaining_tasks * avg_time_per_task
        eta_hours = int(eta_seconds // 3600)
        eta_mins = int((eta_seconds % 3600) // 60)
        eta_str = f"{eta_hours}h {eta_mins}min"
    else:
        eta_str = "calculating..."
    
    # Display progress
    print(f"""
╔══════════════════════════════════════════════════════════════╗
║  🌟 ULTRA NECROZMA - Processing Progress                    ║
╚══════════════════════════════════════════════════════════════╝

📊 Configuration:
   Strategy:       {strategy}
   Total tasks:    {total_tasks}
   
🔄 Progress:
   Current:        {current_desc}
   Overall:        {completed_tasks}/{total_tasks} ({overall_progress:.1f}%)
   
⏱️  Timing:
   Elapsed:        {int(elapsed_time//3600)}h {int((elapsed_time%3600)//60)}min
   ETA:            {eta_str}
   
💾 Resources:
   Memory:         {memory_gb:.1f}GB / {memory_total_gb:.1f}GB ({memory_gb/memory_total_gb*100:.0f}%)
   CPU:            {cpu_percent:.1f}%
   
""")


# ═══════════════════════════════════════════════════════════════
# 🌟 STRATEGY DISCOVERY PIPELINE
# ═══════════════════════════════════════════════════════════════

def convert_df_to_backtest_results(results_df):
    """
    Convert DataFrame of backtest results to backtest_results format
    
    Args:
        results_df: DataFrame with columns: strategy_name, lot_size, metrics...
    
    Returns:
        dict: Backtest results in format {strategy_name: {lot_size: metrics_dict}}
    """
    backtest_results = {}
    for _, row in results_df.iterrows():
        strategy_name = row['strategy_name']
        lot_size = row['lot_size']
        
        if strategy_name not in backtest_results:
            backtest_results[strategy_name] = {}
        
        # Create a simple dict with metrics (compatible with ranking)
        backtest_results[strategy_name][lot_size] = {
            'sharpe_ratio': row.get('sharpe_ratio', 0),
            'sortino_ratio': row.get('sortino_ratio', 0),
            'calmar_ratio': row.get('calmar_ratio', 0),
            'total_return': row.get('total_return', 0),
            'max_drawdown': row.get('max_drawdown', 0),
            'win_rate': row.get('win_rate', 0),
            'n_trades': row.get('n_trades', 0),
            'profit_factor': row.get('profit_factor', 0),
            'avg_win': row.get('avg_win', 0),
            'avg_loss': row.get('avg_loss', 0),
            'expectancy': row.get('expectancy', 0),
            'gross_pnl': row.get('gross_pnl', 0),
            'net_pnl': row.get('net_pnl', 0),
            'total_commission': row.get('total_commission', 0),
        }
    
    return backtest_results


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
    from config import OUTPUT_DIR, FILE_PREFIX
    import pandas as pd
    
    # Initialize Lore System
    lore = LoreSystem(enable_telegram=not args.skip_telegram)
    
    # Awakening event
    lore.broadcast(EventType.AWAKENING, 
                  message="Strategy Discovery Pipeline Initiated")
    
    try:
        # Ensure output directory exists
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        
        # ─────────────────────────────────────────────────────────
        # STEP 1 & 3: CHECK FOR CACHED PATTERNS FIRST
        # ─────────────────────────────────────────────────────────
        patterns_path = OUTPUT_DIR / f"{FILE_PREFIX}patterns.json"
        
        if patterns_path.exists():
            print("\n" + "─" * 80)
            print("✅ PATTERNS FOUND IN CACHE - SKIPPING LABELING!")
            print("─" * 80)
            print(f"   Loading from: {patterns_path}")
            
            with open(patterns_path, 'r') as f:
                patterns = json.load(f)
            
            n_patterns = len(patterns.get('important_features', []))
            print(f"   Important features loaded: {n_patterns}")
            
            # Create empty labels_dict for compatibility
            labels_dict = {}
            
            lore.broadcast(EventType.MILESTONE, 
                          message="Patterns loaded from cache - Labeling skipped!")
        else:
            # ─────────────────────────────────────────────────────────
            # STEP 1: LABELING (only if patterns not cached)
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
            # STEP 3: PATTERN MINING (only if not cached)
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
            
            # SAVE PATTERNS for future use
            with open(patterns_path, 'w') as f:
                json.dump(patterns, f, indent=2, default=str)
            print(f"   💾 Patterns saved to: {patterns_path}")
            
            lore.broadcast(EventType.DISCOVERY, 
                          message=f"Discovered {n_patterns} important patterns")
            
            # ─────────────────────────────────────────────────────────
            # CLEANUP: Remove labels directory to free space (~56GB)
            # ─────────────────────────────────────────────────────────
            labels_dir = Path("labels")
            if labels_dir.exists():
                try:
                    # Calculate size before deletion
                    size_before = sum(f.stat().st_size for f in labels_dir.rglob('*') if f.is_file())
                    shutil.rmtree(labels_dir, ignore_errors=True)
                    size_gb = size_before / 1e9
                    print(f"   🗑️  Labels removed: {size_gb:.1f}GB freed!")
                except Exception as e:
                    print(f"   ⚠️  Could not remove labels directory: {e}")
        
        # ─────────────────────────────────────────────────────────
        # STEP 2: REGIME DETECTION
        # ─────────────────────────────────────────────────────────
        print("\n" + "─" * 80)
        print("🔮 STEP 2/7: Market Regime Detection")
        print("─" * 80)
        
        lore.broadcast(EventType.PROGRESS, 
                      message="Step 2/7: Detecting market regimes...")
        
        from regime_detector import RegimeDetector
        
        regimes_path = OUTPUT_DIR / f"{FILE_PREFIX}regimes.parquet"
        
        # Check if regimes already exist (cache)
        if regimes_path.exists():
            print("✅ Regimes found in cache, loading...")
            print(f"   Loading from: {regimes_path}")
            start_time = time.time()
            regimes_df = pd.read_parquet(regimes_path)
            elapsed = time.time() - start_time
            
            # Analyze cached regimes
            detector = RegimeDetector()
            regime_analysis = detector.analyze_regimes(regimes_df)
            n_regimes = regime_analysis.get('n_regimes', 0)
            
            print(f"   Loaded in {elapsed:.1f}s")
            print(f"   Regimes loaded: {n_regimes}")
            
            lore.broadcast(EventType.MILESTONE, 
                          message="Regimes loaded from cache")
        else:
            print("🔄 Running HDBSCAN clustering (this may take ~97 minutes)...")
            start_time = time.time()
            detector = RegimeDetector()
            regimes_df = detector.detect_regimes(df)
            regime_analysis = detector.analyze_regimes(regimes_df)
            elapsed = time.time() - start_time
            
            n_regimes = regime_analysis.get('n_regimes', 0)
            print(f"\n✅ Regime detection complete in {elapsed:.1f}s")
            print(f"   Regimes detected: {n_regimes}")
            
            # Save regimes to file
            regimes_df.to_parquet(regimes_path, compression='snappy')
            print(f"   💾 Regimes saved to: {regimes_path}")
        
        lore.broadcast(EventType.REGIME_CHANGE, 
                      message=f"Detected {n_regimes} distinct market regimes")
        
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
        strategies = factory.generate_strategies()
        elapsed = time.time() - start_time
        
        n_strategies = len(strategies)
        print(f"\n✅ Strategy generation complete in {elapsed:.1f}s")
        print(f"   Strategies generated: {n_strategies}")
        
        lore.broadcast(EventType.MILESTONE, 
                      message=f"Generated {n_strategies} strategy candidates")
        
        # ─────────────────────────────────────────────────────────
        # STEP 4.5: Add Tick-Level Features (if missing)
        # ─────────────────────────────────────────────────────────
        if 'momentum' not in df.columns:
            print("\n📊 Adding tick-level features...")
            
            # Momentum: sum of pips_change over last N ticks
            df['momentum'] = df['pips_change'].rolling(window=100, min_periods=1).sum()
            
            # Volatility: standard deviation of pips_change over last N ticks
            df['volatility'] = df['pips_change'].rolling(window=100, min_periods=1).std().fillna(0)
            
            # Trend strength: absolute normalized momentum
            df['trend_strength'] = df['momentum'].abs() / (df['volatility'] + EPSILON)
            
            # Close (alias for mid_price, needed by some strategies)
            df['close'] = df['mid_price']
            
            print(f"   ✅ Features added: momentum, volatility, trend_strength, close")
        
        # ─────────────────────────────────────────────────────────
        # STEP 5: BACKTESTING
        # ─────────────────────────────────────────────────────────
        print("\n" + "─" * 80)
        print("📈 STEP 5/7: Walk-Forward Backtesting")
        print("─" * 80)
        
        # Check for cached results
        merged_results_path = OUTPUT_DIR / f"{FILE_PREFIX}backtest_results_merged.parquet"
        force_rerun = getattr(args, 'force_rerun', False)
        
        if merged_results_path.exists() and not force_rerun:
            print(f"\n✅ Found cached backtest results!")
            print(f"   Loading from: {merged_results_path}")
            
            # Load cached results
            results_df = pd.read_parquet(merged_results_path)
            
            n_strategies = results_df['strategy_name'].nunique()
            n_rows = len(results_df)
            
            # Count viable strategies
            viable_df = results_df[results_df['sharpe_ratio'] > 1.0]
            n_viable = viable_df['strategy_name'].nunique()
            
            print(f"   Loaded {n_rows:,} results for {n_strategies:,} strategies")
            print(f"   Viable strategies (Sharpe > 1.0): {n_viable}/{n_strategies}")
            print(f"\n   💡 Use --force-rerun to reprocess")
            
            lore.broadcast(EventType.INSIGHT, 
                          message=f"Loaded cached results: {n_viable} viable strategies")
            
            # Keep as DataFrame - don't convert to dict
            backtest_results = results_df
        else:
            # Run backtesting (cache doesn't exist or force rerun requested)
            if force_rerun and merged_results_path.exists():
                print(f"\n🔄 Force rerun requested, reprocessing all batches...")
            
            lore.broadcast(EventType.PROGRESS, 
                          message="Step 5/7: Backtesting strategies...")
            
            # Check if batch mode is enabled
            use_batch_mode = getattr(args, 'batch_mode', False)
            
            start_time = time.time()
            
            if use_batch_mode:
                # Use batch processing with subprocess isolation
                print(f"\n🔄 Using batch mode (batch size: {args.batch_size})")
                
                from batch_runner import run_batch_processing
                from config import PARQUET_FILE
                import os
                
                # Save current dataframe to ensure batch workers use same data
                # Use process-specific filename to avoid conflicts
                temp_parquet = OUTPUT_DIR / f"temp_batch_data_{os.getpid()}_{int(time.time())}.parquet"
                print(f"   💾 Saving data for batch processing: {temp_parquet}")
                df.to_parquet(temp_parquet, compression='snappy')
                
                # Run batch processing
                merged_results_file = run_batch_processing(
                    batch_size=args.batch_size,
                    parquet_file=temp_parquet,
                    force_rerun=force_rerun
                )
                
                # Load merged results
                if merged_results_file and merged_results_file.exists():
                    print(f"\n   📊 Loading merged results from: {merged_results_file}")
                    results_df = pd.read_parquet(merged_results_file)
                    
                    # Keep as DataFrame - don't convert to dict
                    backtest_results = results_df
                    
                    # Clean up temp file
                    if temp_parquet.exists():
                        temp_parquet.unlink()
                        print(f"   🗑️  Cleaned up temp data file")
                else:
                    print(f"\n   ❌ Batch processing failed or no results!")
                    backtest_results = {}
            else:
                # Original in-process backtesting
                from backtester import Backtester
                
                backtester = Backtester()
                backtest_results = backtester.test_strategies(strategies, df)
            
            elapsed = time.time() - start_time
            
            # Count viable strategies (handle DataFrame, dict, and list formats)
            if isinstance(backtest_results, pd.DataFrame):
                # DataFrame format (from batch processing or cache)
                viable_df = backtest_results[backtest_results['sharpe_ratio'] > 1.0]
                n_viable = viable_df['strategy_name'].nunique()
                n_strategies = backtest_results['strategy_name'].nunique()
            elif isinstance(backtest_results, dict):
                # Dict format: {strategy_name: {lot_size: results}}
                n_viable = 0
                n_strategies = len(backtest_results)
                for strategy_name, lot_results in backtest_results.items():
                    for lot_size, result in lot_results.items():
                        sharpe = result.get('sharpe_ratio', 0) if isinstance(result, dict) else getattr(result, 'sharpe_ratio', 0)
                        if sharpe > 1.0:
                            n_viable += 1
                            break  # Count strategy once even if multiple lot sizes are viable
            else:
                # List format (legacy)
                n_strategies = len(backtest_results)
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
        
        if not top_strategies.empty:
            best = top_strategies.iloc[0]
            print(f"\n   🏆 Best Strategy: {best['strategy_name']}")
            print(f"      Sharpe Ratio: {best['sharpe_ratio']:.2f}")
            print(f"      Total Return: {best['total_return']:.2%}")
            print(f"      Win Rate: {best['win_rate']:.2%}")
            
            lore.broadcast(EventType.LIGHT_FOUND, 
                          strategy_name=best['strategy_name'],
                          sharpe=best['sharpe_ratio'],
                          return_pct=best['total_return'] * 100)
        
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
            feature_importance=patterns,
            regime_analysis=regime_analysis,
            all_backtest_results=backtest_results
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


def run_generate_base(df, args):
    """
    Generate base files (universes + patterns + regimes) for strategy testing
    
    Steps executed:
    1. Load parquet (tick data)
    2. analyzer.run_analysis() → Generate UNIVERSES
    3. analyzer.save_results() → Save universes/*.parquet
    4. Labeling (if not cached)
    5. Pattern Mining (if not cached) → Save patterns.json
    6. Regime Detection → Save regimes.parquet
    7. DELETE labels/ directory (~56GB freed!)
    8. STOP
    
    Args:
        df: Input DataFrame with tick data
        args: Command-line arguments
    """
    print("\n" + "═" * 80)
    print("🏗️  GENERATE BASE - Building Foundation For Strategy Testing")
    print("═" * 80)
    
    from lore import LoreSystem, EventType
    from config import OUTPUT_DIR, FILE_PREFIX
    import pandas as pd
    
    # Initialize Lore System
    lore = LoreSystem(enable_telegram=not args.skip_telegram)
    
    # Awakening event
    lore.broadcast(EventType.AWAKENING, 
                  message="Base Generation Pipeline Initiated")
    
    try:
        # Ensure output directory exists
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        
        # ─────────────────────────────────────────────────────────
        # STEP 1: CHECK FOR CACHED PATTERNS
        # ─────────────────────────────────────────────────────────
        patterns_path = OUTPUT_DIR / f"{FILE_PREFIX}patterns.json"
        
        if patterns_path.exists():
            print("\n" + "─" * 80)
            print("✅ PATTERNS FOUND IN CACHE - SKIPPING LABELING!")
            print("─" * 80)
            print(f"   Loading from: {patterns_path}")
            
            with open(patterns_path, 'r') as f:
                patterns = json.load(f)
            
            n_patterns = len(patterns.get('important_features', []))
            print(f"   Important features loaded: {n_patterns}")
            
            lore.broadcast(EventType.MILESTONE, 
                          message="Patterns loaded from cache - Labeling skipped!")
        else:
            # ─────────────────────────────────────────────────────────
            # STEP 1: LABELING
            # ─────────────────────────────────────────────────────────
            print("\n" + "─" * 80)
            print("📊 STEP 1: Multi-Dimensional Outcome Labeling")
            print("─" * 80)
            
            lore.broadcast(EventType.PROGRESS, 
                          message="Step 1: Labeling outcomes across dimensions...")
            
            from labeler import label_dataframe
            
            start_time = time.time()
            labels_dict = label_dataframe(df)
            elapsed = time.time() - start_time
            
            print(f"\n✅ Labeling complete in {elapsed:.1f}s")
            print(f"   Labeled scenarios: {len(labels_dict)}")
            
            lore.broadcast(EventType.MILESTONE, 
                          message=f"Labeling complete: {len(labels_dict)} scenarios labeled")
            
            # ─────────────────────────────────────────────────────────
            # STEP 2: PATTERN MINING
            # ─────────────────────────────────────────────────────────
            print("\n" + "─" * 80)
            print("⛏️  STEP 2: ML-Based Pattern Mining")
            print("─" * 80)
            
            lore.broadcast(EventType.PROGRESS, 
                          message="Step 2: Mining patterns with ML...")
            
            from pattern_miner import PatternMiner
            
            start_time = time.time()
            miner = PatternMiner()
            patterns = miner.discover_patterns(df, labels_dict)
            elapsed = time.time() - start_time
            
            n_patterns = len(patterns.get('important_features', []))
            print(f"\n✅ Pattern mining complete in {elapsed:.1f}s")
            print(f"   Important features found: {n_patterns}")
            
            # SAVE PATTERNS for future use
            with open(patterns_path, 'w') as f:
                json.dump(patterns, f, indent=2, default=str)
            print(f"   💾 Patterns saved to: {patterns_path}")
            
            lore.broadcast(EventType.DISCOVERY, 
                          message=f"Discovered {n_patterns} important patterns")
            
            # ─────────────────────────────────────────────────────────
            # CLEANUP: Remove labels directory to free space (~56GB)
            # ─────────────────────────────────────────────────────────
            labels_dir = Path("labels")
            if labels_dir.exists():
                try:
                    # Calculate size before deletion
                    size_before = sum(f.stat().st_size for f in labels_dir.rglob('*') if f.is_file())
                    shutil.rmtree(labels_dir, ignore_errors=True)
                    size_gb = size_before / 1e9
                    print(f"   🗑️  Labels removed: {size_gb:.1f}GB freed!")
                except Exception as e:
                    print(f"   ⚠️  Could not remove labels directory: {e}")
        
        # ─────────────────────────────────────────────────────────
        # STEP 3: REGIME DETECTION
        # ─────────────────────────────────────────────────────────
        print("\n" + "─" * 80)
        print("🔮 STEP 3: Market Regime Detection")
        print("─" * 80)
        
        lore.broadcast(EventType.PROGRESS, 
                      message="Step 3: Detecting market regimes...")
        
        from regime_detector import RegimeDetector
        
        regimes_path = OUTPUT_DIR / f"{FILE_PREFIX}regimes.parquet"
        
        # Check if regimes already exist (cache)
        if regimes_path.exists():
            print("✅ Regimes found in cache, loading...")
            print(f"   Loading from: {regimes_path}")
            start_time = time.time()
            regimes_df = pd.read_parquet(regimes_path)
            elapsed = time.time() - start_time
            
            # Analyze cached regimes
            detector = RegimeDetector()
            regime_analysis = detector.analyze_regimes(regimes_df)
            n_regimes = regime_analysis.get('n_regimes', 0)
            
            print(f"   Loaded in {elapsed:.1f}s")
            print(f"   Regimes loaded: {n_regimes}")
            
            lore.broadcast(EventType.MILESTONE, 
                          message="Regimes loaded from cache")
        else:
            print("🔄 Running HDBSCAN clustering (this may take ~97 minutes)...")
            start_time = time.time()
            detector = RegimeDetector()
            regimes_df = detector.detect_regimes(df)
            regime_analysis = detector.analyze_regimes(regimes_df)
            elapsed = time.time() - start_time
            
            n_regimes = regime_analysis.get('n_regimes', 0)
            print(f"\n✅ Regime detection complete in {elapsed:.1f}s")
            print(f"   Regimes detected: {n_regimes}")
            
            # Save regimes to file
            regimes_df.to_parquet(regimes_path, compression='snappy')
            print(f"   💾 Regimes saved to: {regimes_path}")
        
        lore.broadcast(EventType.REGIME_CHANGE, 
                      message=f"Detected {n_regimes} distinct market regimes")
        
        # Final summary
        print("\n" + "═" * 80)
        print("🏗️  BASE GENERATION COMPLETE - Ready For Strategy Testing!")
        print("═" * 80)
        print(f"\n📊 Base Files Generated:")
        print(f"   • Patterns: {patterns_path}")
        print(f"   • Regimes: {regimes_path}")
        print(f"   • Universes: universes/*.parquet (from analyzer)")
        print(f"\n💡 Next Step: Run --search-light to test strategies")
        print("\n" + "═" * 80 + "\n")
        
        lore.broadcast(EventType.COMPLETION, 
                      message="Base Generation Complete! Ready for strategy testing.")
        
        return {
            'patterns': patterns,
            'regimes': regimes_df,
            'regime_analysis': regime_analysis
        }
        
    except Exception as e:
        lore.broadcast(EventType.ERROR, 
                      message=f"Base generation error: {str(e)}")
        raise


def run_search_light(df, args):
    """
    Run strategy generation + backtesting using existing base files
    
    **Note**: This function modifies the input DataFrame `df` by adding columns
    (momentum, volatility, trend_strength, close) if they don't exist. These
    are required for strategy backtesting.
    
    Requires (from base):
    - parquet (tick data)
    - universes/*.parquet
    - patterns.json
    - regimes.parquet
    
    Steps executed:
    1. Load parquet (tick data)
    2. SKIP universes (already exist)
    3. LOAD patterns.json (from cache)
    4. LOAD regimes.parquet (from cache)
    5. Step 4: Strategy Generation
    6. Step 5: Backtesting (tick-level precision)
    7. SKIP Step 6: Ranking (not needed now)
    8. SKIP Step 7: Report (not needed now)
    
    Output:
    - backtest_results.parquet (raw results for analysis)
    
    Args:
        df: Input DataFrame with tick data
        args: Command-line arguments
    """
    print("\n" + "═" * 80)
    print("🔍 SEARCH LIGHT - Fast Strategy Testing")
    print("═" * 80)
    
    from lore import LoreSystem, EventType
    from config import OUTPUT_DIR, FILE_PREFIX
    import pandas as pd
    
    # Initialize Lore System
    lore = LoreSystem(enable_telegram=not args.skip_telegram)
    
    # Awakening event
    lore.broadcast(EventType.AWAKENING, 
                  message="Light Search Pipeline Initiated")
    
    try:
        # Ensure output directory exists
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        
        # ─────────────────────────────────────────────────────────
        # LOAD BASE FILES
        # ─────────────────────────────────────────────────────────
        print("\n" + "─" * 80)
        print("📂 Loading Base Files")
        print("─" * 80)
        
        patterns_path = OUTPUT_DIR / f"{FILE_PREFIX}patterns.json"
        regimes_path = OUTPUT_DIR / f"{FILE_PREFIX}regimes.parquet"
        
        # Check if base files exist
        if not patterns_path.exists():
            raise FileNotFoundError(
                f"❌ Patterns file not found: {patterns_path}\n"
                f"   Run --generate-base first to create base files!"
            )
        
        if not regimes_path.exists():
            raise FileNotFoundError(
                f"❌ Regimes file not found: {regimes_path}\n"
                f"   Run --generate-base first to create base files!"
            )
        
        # Load patterns
        print(f"   Loading patterns from: {patterns_path}")
        with open(patterns_path, 'r') as f:
            patterns = json.load(f)
        n_patterns = len(patterns.get('important_features', []))
        print(f"   ✅ Patterns loaded: {n_patterns} features")
        
        # Load regimes
        print(f"   Loading regimes from: {regimes_path}")
        regimes_df = pd.read_parquet(regimes_path)
        
        from regime_detector import RegimeDetector
        detector = RegimeDetector()
        regime_analysis = detector.analyze_regimes(regimes_df)
        n_regimes = regime_analysis.get('n_regimes', 0)
        print(f"   ✅ Regimes loaded: {n_regimes} regimes")
        
        lore.broadcast(EventType.MILESTONE, 
                      message="Base files loaded successfully")
        
        # ─────────────────────────────────────────────────────────
        # STEP 4: STRATEGY GENERATION
        # ─────────────────────────────────────────────────────────
        print("\n" + "─" * 80)
        print("🏭 STEP 4: Strategy Generation")
        print("─" * 80)
        
        lore.broadcast(EventType.PROGRESS, 
                      message="Step 4: Generating strategy candidates...")
        
        from strategy_factory import StrategyFactory
        
        start_time = time.time()
        factory = StrategyFactory()
        strategies = factory.generate_strategies()
        elapsed = time.time() - start_time
        
        n_strategies = len(strategies)
        print(f"\n✅ Strategy generation complete in {elapsed:.1f}s")
        print(f"   Strategies generated: {n_strategies}")
        
        lore.broadcast(EventType.MILESTONE, 
                      message=f"Generated {n_strategies} strategy candidates")
        
        # ─────────────────────────────────────────────────────────
        # STEP 4.5: Add Tick-Level Features (if missing)
        # ─────────────────────────────────────────────────────────
        if 'momentum' not in df.columns:
            print("\n📊 Adding tick-level features...")
            
            # Momentum: sum of pips_change over last N ticks
            df['momentum'] = df['pips_change'].rolling(window=100, min_periods=1).sum()
            
            # Volatility: standard deviation of pips_change over last N ticks
            df['volatility'] = df['pips_change'].rolling(window=100, min_periods=1).std().fillna(0)
            
            # Trend strength: absolute normalized momentum
            df['trend_strength'] = df['momentum'].abs() / (df['volatility'] + EPSILON)
            
            # Close (alias for mid_price, needed by some strategies)
            df['close'] = df['mid_price']
            
            print(f"   ✅ Features added: momentum, volatility, trend_strength, close")
        
        # ─────────────────────────────────────────────────────────
        # STEP 5: BACKTESTING
        # ─────────────────────────────────────────────────────────
        print("\n" + "─" * 80)
        print("📈 STEP 5: Walk-Forward Backtesting")
        print("─" * 80)
        
        # Check for cached results
        merged_results_path = OUTPUT_DIR / f"{FILE_PREFIX}backtest_results.parquet"
        force_rerun = getattr(args, 'force_rerun', False)
        
        if merged_results_path.exists() and not force_rerun:
            print(f"\n✅ Found cached backtest results!")
            print(f"   Loading from: {merged_results_path}")
            
            # Load cached results
            results_df = pd.read_parquet(merged_results_path)
            
            n_strategies_tested = results_df['strategy_name'].nunique()
            n_rows = len(results_df)
            
            # Count viable strategies
            viable_df = results_df[results_df['sharpe_ratio'] > 1.0]
            n_viable = viable_df['strategy_name'].nunique()
            
            print(f"   Loaded {n_rows:,} results for {n_strategies_tested:,} strategies")
            print(f"   Viable strategies (Sharpe > 1.0): {n_viable}/{n_strategies_tested}")
            print(f"\n   💡 Use --force-rerun to reprocess")
            
            lore.broadcast(EventType.INSIGHT, 
                          message=f"Loaded cached results: {n_viable} viable strategies")
            
            backtest_results = results_df
        else:
            # Run backtesting (cache doesn't exist or force rerun requested)
            if force_rerun and merged_results_path.exists():
                print(f"\n🔄 Force rerun requested, reprocessing all batches...")
            
            lore.broadcast(EventType.PROGRESS, 
                          message="Step 5: Backtesting strategies...")
            
            # Check if batch mode is enabled
            use_batch_mode = getattr(args, 'batch_mode', False)
            
            start_time = time.time()
            
            if use_batch_mode:
                # Use batch processing with subprocess isolation
                print(f"\n🔄 Using batch mode (batch size: {args.batch_size})")
                
                from batch_runner import run_batch_processing
                from config import PARQUET_FILE
                import os
                
                # Save current dataframe to ensure batch workers use same data
                # Use process-specific filename to avoid conflicts
                temp_parquet = OUTPUT_DIR / f"temp_batch_data_{os.getpid()}_{int(time.time())}.parquet"
                print(f"   💾 Saving data for batch processing: {temp_parquet}")
                df.to_parquet(temp_parquet, compression='snappy')
                
                # Run batch processing
                merged_results_file = run_batch_processing(
                    batch_size=args.batch_size,
                    parquet_file=temp_parquet,
                    force_rerun=force_rerun
                )
                
                # Load merged results
                if merged_results_file and merged_results_file.exists():
                    print(f"\n   📊 Loading merged results from: {merged_results_file}")
                    results_df = pd.read_parquet(merged_results_file)
                    
                    backtest_results = results_df
                    
                    # Clean up temp file
                    if temp_parquet.exists():
                        temp_parquet.unlink()
                        print(f"   🗑️  Cleaned up temp data file")
                else:
                    print(f"\n   ❌ Batch processing failed or no results!")
                    backtest_results = pd.DataFrame()
            else:
                # Original in-process backtesting
                from backtester import Backtester
                
                backtester = Backtester()
                backtest_results = backtester.test_strategies(strategies, df)
                
                # Convert to DataFrame if needed and save
                if isinstance(backtest_results, dict):
                    # Convert dict format to DataFrame
                    rows = []
                    for strategy_name, lot_results in backtest_results.items():
                        for lot_size, result in lot_results.items():
                            if isinstance(result, dict):
                                row = result.copy()
                                row['strategy_name'] = strategy_name
                                row['lot_size'] = lot_size
                                rows.append(row)
                    backtest_results = pd.DataFrame(rows)
                
                # Save results
                if not backtest_results.empty:
                    backtest_results.to_parquet(merged_results_path, compression='snappy')
                    print(f"   💾 Results saved to: {merged_results_path}")
            
            elapsed = time.time() - start_time
            
            # Count viable strategies
            if isinstance(backtest_results, pd.DataFrame) and not backtest_results.empty:
                viable_df = backtest_results[backtest_results['sharpe_ratio'] > 1.0]
                n_viable = viable_df['strategy_name'].nunique()
                n_strategies_tested = backtest_results['strategy_name'].nunique()
            else:
                n_viable = 0
                n_strategies_tested = 0
            
            print(f"\n✅ Backtesting complete in {elapsed:.1f}s")
            print(f"   Viable strategies (Sharpe > 1.0): {n_viable}/{n_strategies_tested}")
            
            lore.broadcast(EventType.INSIGHT, 
                          message=f"Backtesting found {n_viable} viable strategies")
        
        # Final summary
        print("\n" + "═" * 80)
        print("🔍 SEARCH LIGHT COMPLETE - Strategy Testing Done!")
        print("═" * 80)
        print(f"\n📊 Results Summary:")
        print(f"   • Strategies tested: {n_strategies}")
        print(f"   • Viable strategies: {n_viable}")
        print(f"   • Results saved to: {merged_results_path}")
        print(f"\n💡 Next Step: Run again with different config or analyze results")
        print("\n" + "═" * 80 + "\n")
        
        lore.broadcast(EventType.COMPLETION, 
                      message=f"Strategy Testing Complete! Found {n_viable} viable strategies.")
        
        return {
            'backtest_results': backtest_results,
            'summary': {
                'patterns': n_patterns,
                'regimes': n_regimes,
                'strategies': n_strategies,
                'viable': n_viable
            }
        }
        
    except Exception as e:
        lore.broadcast(EventType.ERROR, 
                      message=f"Light search error: {str(e)}")
        raise


# ═══════════════════════════════════════════════════════════════
# ⚡ VAST MODE - HIGH PERFORMANCE PARALLEL PROCESSING
# ═══════════════════════════════════════════════════════════════

def _setup_worker_environment(parquet_file, workers_per_pair, skip_telegram, mode='generate_base'):
    """
    Common setup for worker functions in vast mode
    
    **IMPORTANT**: Parquet files must follow the naming convention: PAIRNAME_YEAR.parquet
    Example: EURUSD_2025.parquet, GBPUSD_2024.parquet
    
    Args:
        parquet_file: Path to parquet file (must follow PAIRNAME_YEAR.parquet naming)
        workers_per_pair: Number of workers to use for this pair
        skip_telegram: Whether to skip Telegram notifications
        mode: 'generate_base' or 'search_light'
        
    Returns:
        tuple: (args, df, pair_name) where:
            - args: Configured arguments object
            - df: Loaded DataFrame
            - pair_name: Extracted pair name
    
    Note: This function runs in a separate process, so modifying config is process-safe.
    """
    # Create minimal args object
    class Args:
        pass
    
    args = Args()
    args.parquet = str(parquet_file)
    args.workers = workers_per_pair
    args.sequential = workers_per_pair == 1
    args.skip_telegram = skip_telegram
    args.test = False
    
    if mode == 'generate_base':
        args.generate_base = True
        args.search_light = False
        args.analyze_only = False
        args.force_convert = False
        args.convert_only = False
    else:  # search_light
        args.generate_base = False
        args.search_light = True
        args.batch_mode = False
        args.batch_size = 200
    
    # Load data
    from data_loader import load_crystal
    df = load_crystal(Path(parquet_file))
    
    # Set dynamic config for this pair
    # Note: This is safe in multiprocessing as each process has its own memory space
    parquet_filename = Path(parquet_file)
    filename = parquet_filename.stem
    parts = filename.split("_")
    
    if len(parts) >= 2:
        import config
        config.PAIR_NAME = parts[0]
        config.DATA_YEAR = parts[1]
        config.FILE_PREFIX = f"{parts[0]}_{parts[1]}_"
        if hasattr(config, 'FILE_PREFIX_STABLE'):
            config.FILE_PREFIX_STABLE = f"{parts[0]}_{parts[1]}_"
        pair_name = parts[0]
    else:
        pair_name = filename
    
    return args, df, pair_name


def run_generate_base_single(parquet_file, workers_per_pair, skip_telegram=False):
    """
    Run generate-base for a single parquet file (worker function for vast mode)
    
    **IMPORTANT**: Parquet files must follow the naming convention: PAIRNAME_YEAR.parquet
    Example: EURUSD_2025.parquet, GBPUSD_2024.parquet
    
    Args:
        parquet_file: Path to parquet file
        workers_per_pair: Number of workers to use for this pair
        skip_telegram: Whether to skip Telegram notifications
        
    Returns:
        dict: Results with file name, status, and pair name
    """
    try:
        # Setup environment
        args, df, pair_name = _setup_worker_environment(
            parquet_file, workers_per_pair, skip_telegram, 'generate_base'
        )
        
        # Run analysis first (generates universes)
        from analyzer import UltraNecrozmaAnalyzer
        from lore import LoreSystem
        
        lore = LoreSystem(enable_telegram=not skip_telegram)
        analyzer = UltraNecrozmaAnalyzer(df, lore_system=lore)
        use_parallel = workers_per_pair > 1
        analyzer.run_analysis(parallel=use_parallel)
        analyzer.save_results()
        
        # Run generate base (result not used, but function generates files)
        run_generate_base(df, args)
        
        return {
            'file': parquet_file.name,
            'status': 'success',
            'pair': pair_name
        }
        
    except Exception as e:
        return {
            'file': parquet_file.name,
            'status': 'failed',
            'error': str(e)
        }


def run_search_light_single(parquet_file, workers_per_pair, skip_telegram=False, force_rerun=False):
    """
    Run search-light for a single parquet file (worker function for vast mode)
    
    **IMPORTANT**: Parquet files must follow the naming convention: PAIRNAME_YEAR.parquet
    Example: EURUSD_2025.parquet, GBPUSD_2024.parquet
    
    Args:
        parquet_file: Path to parquet file
        workers_per_pair: Number of workers to use for this pair
        skip_telegram: Whether to skip Telegram notifications
        force_rerun: Whether to force rerun backtesting
        
    Returns:
        dict: Results with file name, status, pair name, and viable strategies count
    """
    try:
        # Setup environment
        args, df, pair_name = _setup_worker_environment(
            parquet_file, workers_per_pair, skip_telegram, 'search_light'
        )
        args.force_rerun = force_rerun
        
        # Run search light
        result = run_search_light(df, args)
        
        return {
            'file': parquet_file.name,
            'status': 'success',
            'pair': pair_name,
            'viable_strategies': result['summary']['viable']
        }
        
    except Exception as e:
        return {
            'file': parquet_file.name,
            'status': 'failed',
            'error': str(e)
        }


def run_vast_mode(args):
    """
    Run in VAST mode - process multiple pairs in parallel
    
    **IMPORTANT**: Parquet files must follow the naming convention: PAIRNAME_YEAR.parquet
    Examples: EURUSD_2025.parquet, GBPUSD_2024.parquet
    
    This function:
    1. Auto-detects system resources (CPU cores, RAM)
    2. Discovers all parquet files in input directory
    3. Calculates optimal parallelism settings
    4. Processes files in parallel using ProcessPoolExecutor
    5. Reports progress and results
    
    Args:
        args: Command-line arguments including:
            - input_dir: Directory containing parquet files
            - generate_base: Whether to run generate-base mode
            - search_light: Whether to run search-light mode
            - parallel_pairs: Number of pairs to process simultaneously (auto if not specified)
            - max_workers: Workers per pair (auto if not specified)
            - skip_telegram: Whether to skip Telegram notifications
    
    Exits:
        Prints summary and exits (does not return)
    """
    from concurrent.futures import ProcessPoolExecutor, as_completed
    
    # 1. Detect resources
    resources = detect_resources()
    
    # 2. Find all parquet files
    if not args.input_dir:
        print("❌ ERROR: --input-dir is required for VAST mode")
        print("   Example: python main.py --vast-mode --input-dir data/parquet/ --generate-base")
        sys.exit(1)
    
    input_dir = Path(args.input_dir)
    if not input_dir.exists():
        print(f"❌ ERROR: Input directory not found: {input_dir}")
        sys.exit(1)
    
    parquet_files = sorted(list(input_dir.glob("*.parquet")))
    
    if not parquet_files:
        print(f"❌ ERROR: No parquet files found in {input_dir}")
        sys.exit(1)
    
    # 3. Calculate optimal parallelism
    parallel_pairs = args.parallel_pairs if args.parallel_pairs > 1 else resources['recommended_parallel_pairs']
    workers_per_pair = args.max_workers if args.max_workers else resources['recommended_workers_per_pair']
    
    # 4. Print banner
    print_resources_banner(resources, len(parquet_files), parallel_pairs, workers_per_pair)
    
    # 5. Determine which mode to run
    if not args.generate_base and not args.search_light:
        print("❌ ERROR: Must specify either --generate-base or --search-light with --vast-mode")
        print("   Example: python main.py --vast-mode --input-dir data/parquet/ --generate-base")
        sys.exit(1)
    
    # 6. Process in parallel
    print(f"🐉 Processing {len(parquet_files)} pairs in parallel...")
    print()
    
    start_time = time.time()
    completed = 0
    failed = 0
    
    with ProcessPoolExecutor(max_workers=parallel_pairs) as executor:
        if args.generate_base:
            # Submit all generate-base tasks
            futures = {
                executor.submit(
                    run_generate_base_single, 
                    pf, 
                    workers_per_pair,
                    args.skip_telegram
                ): pf for pf in parquet_files
            }
        else:  # args.search_light
            # Submit all search-light tasks
            futures = {
                executor.submit(
                    run_search_light_single, 
                    pf, 
                    workers_per_pair,
                    args.skip_telegram,
                    args.force_rerun if hasattr(args, 'force_rerun') else False
                ): pf for pf in parquet_files
            }
        
        # Wait for all to complete with progress
        for future in as_completed(futures):
            result = future.result()
            completed += 1
            
            if result['status'] == 'success':
                elapsed = time.time() - start_time
                elapsed_str = f"{elapsed/3600:.1f}h" if elapsed > 3600 else f"{elapsed/60:.1f}m"
                
                if args.generate_base:
                    print(f"✅ [{completed}/{len(parquet_files)}] {result['pair']} - generate-base complete ({elapsed_str})")
                else:
                    viable = result.get('viable_strategies', 'N/A')
                    print(f"✅ [{completed}/{len(parquet_files)}] {result['pair']} - search-light complete (viable: {viable}, {elapsed_str})")
            else:
                failed += 1
                print(f"❌ [{completed}/{len(parquet_files)}] {result['file']} - FAILED: {result.get('error', 'Unknown error')}")
    
    # 7. Final summary
    total_time = time.time() - start_time
    total_time_str = f"{total_time/3600:.1f}h" if total_time > 3600 else f"{total_time/60:.1f}m"
    
    print()
    print("═" * 80)
    print("⚡ VAST MODE COMPLETE ⚡")
    print("═" * 80)
    print(f"   Total pairs: {len(parquet_files)}")
    print(f"   Successful: {completed - failed}")
    print(f"   Failed: {failed}")
    print(f"   Total time: {total_time_str}")
    print("═" * 80)
    print()


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
    
    # Display system resources with thermal status
    from utils.parallel import get_system_resources
    print("\n" + "═" * 80)
    print("🌡️ System Status")
    print("═" * 80)
    resources = get_system_resources()
    print(f"   CPU: {resources['cpu_count']} cores | {resources['cpu_percent']:.1f}% usage", end="")
    if resources.get('cpu_temperature'):
        thermal = resources['thermal_status']
        print(f" | {thermal['emoji']} {resources['cpu_temperature']:.0f}°C {thermal['status'].upper()}")
    else:
        print(" | 🌡️ Temperature monitoring unavailable")
    print(f"   RAM: {resources['memory_available_gb']:.1f} GB available | {resources['memory_percent']:.1f}% used")
    
    if resources.get('thermal_status') and resources['thermal_status']['action'] != 'continue':
        print(f"   ⚠️ Thermal Protection: ACTIVE")
    else:
        print(f"   ✅ Thermal Protection: Ready")
    print("═" * 80 + "\n")
    
    # Check if VAST mode is enabled
    if args.vast_mode:
        print("⚡ VAST MODE DETECTED - Switching to high-performance parallel processing\n")
        run_vast_mode(args)
        return  # Exit after vast mode completes
    
    # Import config (after system check)
    from config import CSV_FILE, PARQUET_FILE, NUM_WORKERS, CACHE_CONFIG
    from data_loader import crystallize_csv_to_parquet, load_crystal, crystal_info
    from analyzer import UltraNecrozmaAnalyzer
    from reports import light_that_burns_the_sky, generate_full_report, print_final_summary
    
    # Handle cache configuration based on command-line flags
    if args.fresh:
        print("🔥 FRESH MODE: Disabling all caching and recalculating everything...\n")
        CACHE_CONFIG["enabled"] = False
        CACHE_CONFIG["skip_existing_universes"] = False
        CACHE_CONFIG["cache_labeling"] = False
    elif not args.skip_existing:
        print("🔄 Recalculating all universes (skip-existing disabled)...\n")
        CACHE_CONFIG["skip_existing_universes"] = False
    
    # Config override
    csv_path = Path(args.csv) if args.csv else CSV_FILE
    parquet_path = Path(args.parquet) if args.parquet else PARQUET_FILE
    num_workers = args.workers if args.workers else NUM_WORKERS
    
    # ═══════════════════════════════════════════════════════════════
    # 📊 DYNAMIC FILE_PREFIX (Problem 2 Fix)
    # ═══════════════════════════════════════════════════════════════
    # When --parquet argument is provided, dynamically update config
    # to isolate cache per pair/year (prevents EURUSD cache being used for AUDJPY)
    if args.parquet:
        parquet_filename = Path(args.parquet)
        filename = parquet_filename.stem  # e.g., "AUDJPY_2023"
        parts = filename.split("_")
        if len(parts) >= 2:
            import config
            config.PAIR_NAME = parts[0]  # "AUDJPY"
            config.DATA_YEAR = parts[1]  # "2023"
            config.FILE_PREFIX = f"{parts[0]}_{parts[1]}_"
            # Also update FILE_PREFIX_STABLE if it exists
            if hasattr(config, 'FILE_PREFIX_STABLE'):
                config.FILE_PREFIX_STABLE = f"{parts[0]}_{parts[1]}_"
            print(f"📊 Dynamic config: PAIR={config.PAIR_NAME}, YEAR={config.DATA_YEAR}, PREFIX={config.FILE_PREFIX}")
    
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
            'mid_price': base_price + cumsum,
            'spread_pips': 1.0,
            'pips_change': np.concatenate([[0], np.diff(cumsum) * PIPS_MULTIPLIER])
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
    # Use parallel only if num_workers > 1 and not in sequential mode
    use_parallel = (num_workers > 1) and not args.sequential
    
    # Check for conflicting flags
    if args.generate_base and args.search_light:
        print("\n⚠️  WARNING: Both --generate-base and --search-light flags provided")
        print("   Only --generate-base will be executed (--search-light will be ignored)")
        print("   Run these commands separately for the intended workflow\n")
    
    # Check which workflow mode to use
    if args.generate_base:
        # Generate base mode - run analysis then generate base files
        analyzer.run_analysis(parallel=use_parallel)
        analyzer.save_results()  # Save universe files
        
        # Generate base files
        base_results = run_generate_base(df, args)
        
        # Exit early - no need for further processing
        print("\n✅ Base generation complete - exiting")
        print("   Next step: Run with --search-light to test strategies")
        sys.exit(0)
    elif args.search_light:
        # Search light mode - skip analysis, load base files
        print("\n🔍 Search Light mode - skipping universe analysis")
        print("   Loading existing base files...")
        
        # Don't run analyzer in search light mode
        # The base files already exist from --generate-base
        
        # Run search light
        search_results = run_search_light(df, args)
        
        # Exit early - no need for further processing
        print("\n✅ Strategy testing complete - exiting")
        print("   Results saved to backtest_results.parquet")
        sys.exit(0)
    else:
        # Normal mode - run full analysis
        analyzer.run_analysis(parallel=use_parallel)
        analyzer.save_results()  # Save universe files
    
    # Strategy discovery (if enabled)
    discovery_results = None
    if args.strategy_discovery:
        discovery_results = run_strategy_discovery(df, args)
    
    # Z-Move: Light That Burns The Sky
    print("\n")
    # Only call light_that_burns_the_sky if we have analyzer results
    # Strategy discovery has its own flow and doesn't populate analyzer.results
    if analyzer.results:
        final_judgment = light_that_burns_the_sky(analyzer)
        
        # Save final_judgment to JSON
        if final_judgment:
            import json
            from config import OUTPUT_DIR
            
            output_dir = Path(OUTPUT_DIR)
            output_dir.mkdir(parents=True, exist_ok=True)
            
            judgment_path = output_dir / "final_judgment.json"
            with open(judgment_path, 'w') as f:
                json.dump(final_judgment, f, indent=2, default=str)
            
            print(f"   💾 Saved regime analysis to {judgment_path}")
    else:
        # No results to analyze (strategy discovery mode without universe analysis)
        if args.strategy_discovery:
            print("⚡💎🌟 Z-MOVE: LIGHT THAT BURNS THE SKY 🌟💎⚡")
            print("   ⚠️ No universe results - using Strategy Discovery results")
            print("   ✅ Regime analysis skipped (run without --strategy-discovery for full analysis)")
        final_judgment = None
    
    # Generate reports
    print("\n📝 Generating comprehensive reports...\n")
    report_paths = generate_full_report(analyzer, final_judgment)
    
    # Generate dashboard (if enabled)
    dashboard_path = None
    if args.generate_dashboard or args.open_dashboard:
        print("\n🎨 Generating interactive HTML dashboard...\n")
        from dashboard_generator import DashboardGenerator
        
        generator = DashboardGenerator()
        dashboard_path = generator.generate_dashboard()
        
        if dashboard_path:
            report_paths["dashboard"] = dashboard_path
            
            # Open in browser if requested
            if args.open_dashboard:
                import webbrowser
                print("\n🌐 Opening dashboard in browser...")
                webbrowser.open(f'file://{os.path.abspath(dashboard_path)}')
    
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
