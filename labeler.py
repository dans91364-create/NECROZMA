#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚡🌟💎 NECROZMA - LABELING SYSTEM 💎🌟⚡

Multi-Dimensional Outcome Labeling
"Mapping every possible future from every present moment"

Features:
- Multi-target labeling (5, 10, 15, 20, 30, 50 pips)
- Multi-horizon testing (1m to 1d)
- Multi-stop analysis (5, 10, 15, 20, 30 pips)
- Advanced metrics: MFE, MAE, R-Multiple
- Numba-optimized sequential processing (faster than parallel due to no data copying overhead)
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Union
import warnings
import hashlib
import pickle
import json
import gc
from pathlib import Path
from tqdm import tqdm

warnings.filterwarnings("ignore")

from config import TARGET_PIPS, STOP_PIPS, TIME_HORIZONS, LABELING_METRICS, CACHE_CONFIG, FILE_PREFIX


# ═══════════════════════════════════════════════════════════════
# ⚡ NUMBA JIT SETUP
# ═══════════════════════════════════════════════════════════════

try:
    from numba import njit
    NUMBA_AVAILABLE = True
    print("⚡ Numba JIT: ENABLED (Light Speed Mode - 50-100x faster labeling)")
except ImportError:
    NUMBA_AVAILABLE = False
    print("⚠️  Numba not available - using pure Python (install numba for 50-100x speedup)")
    # Dummy decorator if Numba not available
    def njit(*args, **kwargs):
        def decorator(func):
            return func
        if args and callable(args[0]):
            return args[0]
        return decorator


# ═══════════════════════════════════════════════════════════════
# 🚀 NUMBA-OPTIMIZED CORE FUNCTIONS
# ═══════════════════════════════════════════════════════════════

@njit(cache=True, fastmath=True)
def _scan_for_target_stop(
    prices: np.ndarray,
    candle_idx: int,
    horizon_idx: int,
    entry_price: float,
    target_price: float,
    stop_price: float,
    pip_value: float,
    direction_up: bool
) -> tuple:
    """
    Numba-optimized scan for target/stop hits
    
    This function replaces the pure Python loop in label_single_candle()
    providing 50-100x speedup through JIT compilation.
    
    Args:
        prices: Array of mid prices
        candle_idx: Starting candle index
        horizon_idx: End of horizon index
        entry_price: Entry price
        target_price: Target price level
        stop_price: Stop loss price level
        pip_value: Value of 1 pip (0.0001 for EUR/USD)
        direction_up: True for long, False for short
        
    Returns:
        Tuple: (hit_target, hit_stop, target_idx, stop_idx, max_favorable, max_adverse)
    """
    hit_target = False
    hit_stop = False
    target_idx = -1
    stop_idx = -1
    max_favorable = 0.0
    max_adverse = 0.0
    
    for i in range(candle_idx + 1, horizon_idx):
        price = prices[i]
        
        if direction_up:
            # Long position
            excursion = (price - entry_price) / pip_value
            if excursion > max_favorable:
                max_favorable = excursion
            if excursion < max_adverse:
                max_adverse = excursion
            
            if not hit_target and price >= target_price:
                hit_target = True
                target_idx = i
            
            if not hit_stop and price <= stop_price:
                hit_stop = True
                stop_idx = i
        else:
            # Short position
            excursion = (entry_price - price) / pip_value
            if excursion > max_favorable:
                max_favorable = excursion
            if excursion < max_adverse:
                max_adverse = excursion
            
            if not hit_target and price <= target_price:
                hit_target = True
                target_idx = i
            
            if not hit_stop and price >= stop_price:
                hit_stop = True
                stop_idx = i
        
        # Early exit if both hit
        if hit_target and hit_stop:
            break
    
    return (hit_target, hit_stop, target_idx, stop_idx, max_favorable, max_adverse)


# ═══════════════════════════════════════════════════════════════
# 🚀 VECTORIZED LABELING (1000x FASTER)
# ═══════════════════════════════════════════════════════════════

try:
    from numba import prange
except ImportError:
    # Fallback to regular range if prange not available
    prange = range


@njit(parallel=True, cache=True, fastmath=True)
def label_all_candles_vectorized(
    prices: np.ndarray,           # float64[:] - mid prices
    timestamps_ns: np.ndarray,    # int64[:] - timestamps as int64 nanoseconds
    target_pip: float,            # target in pips
    stop_pip: float,              # stop in pips
    horizon_ns: int,              # horizon in nanoseconds (int64)
    pip_value: float              # value of 1 pip (0.0001 for EUR/USD)
) -> tuple:
    """
    Label ALL candles in one Numba call - 1000x faster than Python loop
    
    This function processes all candles at once using Numba's parallel execution,
    eliminating Python loop overhead, pd.Timedelta creation, and dict operations.
    
    Args:
        prices: Array of mid prices (float64)
        timestamps_ns: Array of timestamps as int64 nanoseconds
        target_pip: Target level in pips
        stop_pip: Stop loss level in pips
        horizon_ns: Time horizon in nanoseconds (int64)
        pip_value: Value of 1 pip (default 0.0001 for EUR/USD)
        
    Returns:
        Tuple of 10 arrays (one for each metric):
        - outcomes_up: int8 array (0=none, 1=target, -1=stop)
        - outcomes_down: int8 array
        - max_favorable_up: float64 array (MFE in pips)
        - max_favorable_down: float64 array
        - max_adverse_up: float64 array (MAE in pips)
        - max_adverse_down: float64 array
        - time_to_target_up: float64 array (minutes, or -1 if not hit)
        - time_to_target_down: float64 array
        - time_to_stop_up: float64 array (minutes, or -1 if not hit)
        - time_to_stop_down: float64 array
    """
    n = len(prices)
    
    # Pre-allocate result arrays (Numba-friendly, no dicts!)
    outcomes_up = np.empty(n, dtype=np.int8)
    outcomes_down = np.empty(n, dtype=np.int8)
    max_favorable_up = np.empty(n, dtype=np.float64)
    max_favorable_down = np.empty(n, dtype=np.float64)
    max_adverse_up = np.empty(n, dtype=np.float64)
    max_adverse_down = np.empty(n, dtype=np.float64)
    time_to_target_up = np.empty(n, dtype=np.float64)
    time_to_target_down = np.empty(n, dtype=np.float64)
    time_to_stop_up = np.empty(n, dtype=np.float64)
    time_to_stop_down = np.empty(n, dtype=np.float64)
    
    # Process all candles in parallel using prange
    for i in prange(n - 1):  # prange = parallel range in Numba!
        entry_price = prices[i]
        entry_time_ns = timestamps_ns[i]
        
        # Calculate target/stop prices for both directions
        target_up = entry_price + (target_pip * pip_value)
        target_down = entry_price - (target_pip * pip_value)
        stop_up = entry_price - (stop_pip * pip_value)
        stop_down = entry_price + (stop_pip * pip_value)
        
        # Find horizon end index using timestamp arithmetic (all in int64)
        horizon_end_ns = entry_time_ns + horizon_ns
        horizon_idx = i + 1
        while horizon_idx < n and timestamps_ns[horizon_idx] <= horizon_end_ns:
            horizon_idx += 1
        
        # ===== UP DIRECTION (LONG) =====
        hit_target_up = False
        hit_stop_up = False
        target_idx_up = -1
        stop_idx_up = -1
        mfe_up = 0.0
        mae_up = 0.0
        
        for j in range(i + 1, horizon_idx):
            price = prices[j]
            
            # Calculate excursion
            excursion = (price - entry_price) / pip_value
            if excursion > mfe_up:
                mfe_up = excursion
            if excursion < mae_up:
                mae_up = excursion
            
            # Check for target hit
            if not hit_target_up and price >= target_up:
                hit_target_up = True
                target_idx_up = j
            
            # Check for stop hit
            if not hit_stop_up and price <= stop_up:
                hit_stop_up = True
                stop_idx_up = j
            
            # Early exit if both hit
            if hit_target_up and hit_stop_up:
                break
        
        # Calculate time to target/stop (in minutes)
        time_target_up = -1.0
        time_stop_up = -1.0
        
        if hit_target_up and target_idx_up >= 0:
            # Convert nanoseconds to minutes: ns / (60 * 1e9)
            time_diff_ns = timestamps_ns[target_idx_up] - entry_time_ns
            time_target_up = float(time_diff_ns) / 60_000_000_000.0
        
        if hit_stop_up and stop_idx_up >= 0:
            time_diff_ns = timestamps_ns[stop_idx_up] - entry_time_ns
            time_stop_up = float(time_diff_ns) / 60_000_000_000.0
        
        # Determine outcome for UP direction
        if hit_target_up and hit_stop_up:
            # Both hit - which came first?
            if target_idx_up < stop_idx_up:
                outcomes_up[i] = 1  # target
            else:
                outcomes_up[i] = -1  # stop
        elif hit_target_up:
            outcomes_up[i] = 1  # target
        elif hit_stop_up:
            outcomes_up[i] = -1  # stop
        else:
            outcomes_up[i] = 0  # none
        
        # Store UP results
        max_favorable_up[i] = mfe_up
        max_adverse_up[i] = mae_up
        time_to_target_up[i] = time_target_up
        time_to_stop_up[i] = time_stop_up
        
        # ===== DOWN DIRECTION (SHORT) =====
        hit_target_down = False
        hit_stop_down = False
        target_idx_down = -1
        stop_idx_down = -1
        mfe_down = 0.0
        mae_down = 0.0
        
        for j in range(i + 1, horizon_idx):
            price = prices[j]
            
            # Calculate excursion (inverted for short)
            excursion = (entry_price - price) / pip_value
            if excursion > mfe_down:
                mfe_down = excursion
            if excursion < mae_down:
                mae_down = excursion
            
            # Check for target hit
            if not hit_target_down and price <= target_down:
                hit_target_down = True
                target_idx_down = j
            
            # Check for stop hit
            if not hit_stop_down and price >= stop_down:
                hit_stop_down = True
                stop_idx_down = j
            
            # Early exit if both hit
            if hit_target_down and hit_stop_down:
                break
        
        # Calculate time to target/stop (in minutes)
        time_target_down = -1.0
        time_stop_down = -1.0
        
        if hit_target_down and target_idx_down >= 0:
            time_diff_ns = timestamps_ns[target_idx_down] - entry_time_ns
            time_target_down = float(time_diff_ns) / 60_000_000_000.0
        
        if hit_stop_down and stop_idx_down >= 0:
            time_diff_ns = timestamps_ns[stop_idx_down] - entry_time_ns
            time_stop_down = float(time_diff_ns) / 60_000_000_000.0
        
        # Determine outcome for DOWN direction
        if hit_target_down and hit_stop_down:
            # Both hit - which came first?
            if target_idx_down < stop_idx_down:
                outcomes_down[i] = 1  # target
            else:
                outcomes_down[i] = -1  # stop
        elif hit_target_down:
            outcomes_down[i] = 1  # target
        elif hit_stop_down:
            outcomes_down[i] = -1  # stop
        else:
            outcomes_down[i] = 0  # none
        
        # Store DOWN results
        max_favorable_down[i] = mfe_down
        max_adverse_down[i] = mae_down
        time_to_target_down[i] = time_target_down
        time_to_stop_down[i] = time_stop_down
    
    # Fill last candle with default values (can't be labeled)
    outcomes_up[n-1] = 0
    outcomes_down[n-1] = 0
    max_favorable_up[n-1] = 0.0
    max_favorable_down[n-1] = 0.0
    max_adverse_up[n-1] = 0.0
    max_adverse_down[n-1] = 0.0
    time_to_target_up[n-1] = -1.0
    time_to_target_down[n-1] = -1.0
    time_to_stop_up[n-1] = -1.0
    time_to_stop_down[n-1] = -1.0
    
    return (
        outcomes_up, outcomes_down,
        max_favorable_up, max_favorable_down,
        max_adverse_up, max_adverse_down,
        time_to_target_up, time_to_target_down,
        time_to_stop_up, time_to_stop_down
    )


# ═══════════════════════════════════════════════════════════════
# 💾 CACHE UTILITIES
# ═══════════════════════════════════════════════════════════════

def _get_cache_dir():
    """Get or create cache directory"""
    cache_dir = CACHE_CONFIG.get("cache_dir", Path("ultra_necrozma_results/cache"))
    cache_dir = Path(cache_dir)
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir


def _generate_data_hash(df: pd.DataFrame) -> str:
    """
    Generate a hash for data fingerprinting
    
    Args:
        df: DataFrame to hash
        
    Returns:
        str: Hash string
    """
    # Create hash from data shape and sample values
    hash_input = f"{len(df)}_{df['mid_price'].iloc[0] if len(df) > 0 else 0}_{df['mid_price'].iloc[-1] if len(df) > 0 else 0}"
    return hashlib.md5(hash_input.encode()).hexdigest()[:8]


def clear_label_cache():
    """
    Clear all labeling cache files
    Utility function for fresh starts
    
    Note: Glob patterns work for both prefixed and non-prefixed files:
    - 'labels_*.pkl' matches both 'labels_abc.pkl' and 'EURUSD_2025_labels_abc.pkl'
    - This ensures backward compatibility
    """
    cache_dir = _get_cache_dir()
    
    # Remove all cache files (glob matches both prefixed and non-prefixed)
    for cache_file in cache_dir.glob("*labels_*.pkl"):
        cache_file.unlink()
        print(f"   🗑️  Removed {cache_file.name}")
    
    for progress_file in cache_dir.glob("*labels_progress_*.json"):
        progress_file.unlink()
        print(f"   🗑️  Removed {progress_file.name}")
    
    print("   ✅ Label cache cleared!")


def _load_cache(cache_file: Path) -> Optional[Dict]:
    """Load labels from cache file"""
    try:
        with open(cache_file, 'rb') as f:
            return pickle.load(f)
    except Exception as e:
        print(f"   ⚠️ Failed to load cache: {e}")
        return None


def _save_cache(cache_file: Path, data: Dict):
    """Save labels to cache file"""
    try:
        with open(cache_file, 'wb') as f:
            pickle.dump(data, f)
    except Exception as e:
        print(f"   ⚠️ Failed to save cache: {e}")


def _load_progress(progress_file: Path) -> set:
    """Load progress from checkpoint file"""
    if not progress_file.exists():
        return set()
    
    try:
        with open(progress_file, 'r') as f:
            data = json.load(f)
            return set(data.get('completed', []))
    except Exception as e:
        print(f"   ⚠️ Failed to load progress: {e}")
        return set()


def _save_progress(progress_file: Path, completed: set):
    """Save progress to checkpoint file"""
    try:
        with open(progress_file, 'w') as f:
            json.dump({'completed': list(completed)}, f)
    except Exception as e:
        print(f"   ⚠️ Failed to save progress: {e}")


def _get_labels_dir():
    """
    Get or create labels directory for individual parquet files
    
    Returns:
        Path: Path to the labels/ directory
    """
    labels_dir = Path("labels")
    labels_dir.mkdir(exist_ok=True)
    return labels_dir


def load_label_results(config_key: str) -> pd.DataFrame:
    """
    Load a specific labeled dataset from disk
    
    Args:
        config_key: Configuration key (e.g., "T5_S5_H1")
        
    Returns:
        DataFrame with labeled results for that configuration
        
    Example:
        >>> df = load_label_results("T5_S5_H1")
        >>> print(f"Loaded {len(df):,} rows")
    """
    labels_dir = _get_labels_dir()
    file_path = labels_dir / f"{config_key}.parquet"
    
    if not file_path.exists():
        raise FileNotFoundError(f"Label file not found: {file_path}")
    
    return pd.read_parquet(file_path)


def load_all_label_results() -> Dict[str, pd.DataFrame]:
    """
    Load all labeled datasets from disk
    
    ⚠️  WARNING: This loads ALL results into memory at once!
    Only use this if you have enough RAM, or load specific configs with load_label_results()
    
    Returns:
        Dictionary mapping config_key -> DataFrame
        
    Example:
        >>> results = load_all_label_results()
        >>> print(f"Loaded {len(results)} configurations")
        >>> for config_key, df in results.items():
        ...     print(f"  {config_key}: {len(df):,} rows")
    """
    labels_dir = _get_labels_dir()
    results = {}
    
    parquet_files = list(labels_dir.glob("*.parquet"))
    
    if not parquet_files:
        print("   ⚠️  No label files found in labels/ directory")
        return results
    
    print(f"   📥 Loading {len(parquet_files)} label files from {labels_dir}/...")
    
    for file_path in parquet_files:
        config_key = file_path.stem
        results[config_key] = pd.read_parquet(file_path)
    
    print(f"   ✅ Loaded {len(results)} configurations into memory")
    
    return results


# ═══════════════════════════════════════════════════════════════
# 🎯 CORE LABELING FUNCTIONS
# ═══════════════════════════════════════════════════════════════

def label_single_candle(
    candle_idx: int,
    prices: np.ndarray,
    timestamps: np.ndarray,
    target_pip: float,
    stop_pip: float,
    horizon_minutes: int,
    pip_value: float = 0.0001
) -> Dict:
    """
    Label a single candle with target/stop outcomes
    
    Args:
        candle_idx: Index of candle to label
        prices: Array of mid prices
        timestamps: Array of timestamps
        target_pip: Target in pips
        stop_pip: Stop loss in pips
        horizon_minutes: Time horizon in minutes
        pip_value: Value of 1 pip (default 0.0001 for EUR/USD)
        
    Returns:
        Dictionary with labeling results
    """
    if candle_idx >= len(prices) - 1:
        return None
    
    entry_price = prices[candle_idx]
    entry_time = timestamps[candle_idx]
    
    # Calculate target and stop prices
    target_up = entry_price + (target_pip * pip_value)
    target_down = entry_price - (target_pip * pip_value)
    stop_up = entry_price - (stop_pip * pip_value)
    stop_down = entry_price + (stop_pip * pip_value)
    
    # Find horizon end index
    if horizon_minutes > 0:
        horizon_end_time = entry_time + pd.Timedelta(minutes=horizon_minutes)
        horizon_idx = candle_idx + 1
        while horizon_idx < len(timestamps) and timestamps[horizon_idx] <= horizon_end_time:
            horizon_idx += 1
        horizon_idx = min(horizon_idx, len(prices))
    else:
        horizon_idx = len(prices)
    
    # Initialize result
    result = {
        "candle_idx": candle_idx,
        "entry_price": entry_price,
        "target_pip": target_pip,
        "stop_pip": stop_pip,
        "horizon_minutes": horizon_minutes,
    }
    
    # Track outcomes for both directions
    for direction in ["up", "down"]:
        target_price = target_up if direction == "up" else target_down
        stop_price = stop_up if direction == "up" else stop_down
        direction_up = (direction == "up")
        
        # Use Numba-optimized scan function for performance
        (hit_target, hit_stop, target_idx, stop_idx, max_favorable, max_adverse) = _scan_for_target_stop(
            prices=prices,
            candle_idx=candle_idx,
            horizon_idx=horizon_idx,
            entry_price=entry_price,
            target_price=target_price,
            stop_price=stop_price,
            pip_value=pip_value,
            direction_up=direction_up
        )
        
        # Get timestamps for target/stop hits
        target_time = timestamps[target_idx] if hit_target and target_idx >= 0 else None
        stop_time = timestamps[stop_idx] if hit_stop and stop_idx >= 0 else None
        
        # Calculate time to target/stop
        time_to_target = None
        time_to_stop = None
        
        if hit_target and target_time:
            # Handle both numpy.timedelta64 and pandas Timedelta
            time_diff = target_time - entry_time
            if hasattr(time_diff, 'total_seconds'):
                time_to_target = time_diff.total_seconds() / 60.0
            else:
                # numpy.timedelta64 - convert to minutes using numpy division
                time_to_target = float(time_diff / np.timedelta64(1, 'm'))
        
        if hit_stop and stop_time:
            # Handle both numpy.timedelta64 and pandas Timedelta
            time_diff = stop_time - entry_time
            if hasattr(time_diff, 'total_seconds'):
                time_to_stop = time_diff.total_seconds() / 60.0
            else:
                # numpy.timedelta64 - convert to minutes using numpy division
                time_to_stop = float(time_diff / np.timedelta64(1, 'm'))
        
        # Determine outcome
        if hit_target and hit_stop:
            # Both hit - which came first?
            if target_idx < stop_idx:
                outcome = "target"
            else:
                outcome = "stop"
        elif hit_target:
            outcome = "target"
        elif hit_stop:
            outcome = "stop"
        else:
            outcome = "none"
        
        # Calculate R-Multiple
        r_multiple = None
        if outcome == "target":
            r_multiple = target_pip / stop_pip
        elif outcome == "stop":
            r_multiple = -1.0
        
        # Store direction-specific results
        prefix = f"{direction}_"
        result[f"{prefix}outcome"] = outcome
        result[f"{prefix}hit_target"] = hit_target
        result[f"{prefix}hit_stop"] = hit_stop
        result[f"{prefix}time_to_target"] = time_to_target
        result[f"{prefix}time_to_stop"] = time_to_stop
        result[f"{prefix}mfe"] = max_favorable
        result[f"{prefix}mae"] = max_adverse
        result[f"{prefix}r_multiple"] = r_multiple
    
    return result




# ═══════════════════════════════════════════════════════════════
# 🚀 SEQUENTIAL LABELING (Optimized with Numba)
# ═══════════════════════════════════════════════════════════════

def label_dataframe(
    df: pd.DataFrame,
    target_pips: List[float] = None,
    stop_pips: List[float] = None,
    horizons: List[int] = None,
    num_workers: int = None,
    pip_value: float = 0.0001,
    progress_callback = None,
    use_cache: bool = None,
    return_dict: bool = False
) -> Union[List[str], Dict[str, pd.DataFrame]]:
    """
    Label entire dataframe with multiple targets/stops/horizons
    
    MEMORY-EFFICIENT: Saves each config immediately to disk instead of accumulating in RAM!
    
    Args:
        df: DataFrame with at least 'mid_price' and 'timestamp' columns
        target_pips: List of target levels in pips
        stop_pips: List of stop levels in pips
        horizons: List of time horizons in minutes
        num_workers: Deprecated (kept for backward compatibility, ignored)
        pip_value: Value of 1 pip
        progress_callback: Optional callback(current, total, desc) for progress
        use_cache: Whether to use cache (default: from CACHE_CONFIG)
        return_dict: If True, returns Dict[str, pd.DataFrame] (backward compatibility, memory-intensive!)
                     If False (default), returns List[str] of saved file paths (memory-efficient)
        
    Returns:
        List[str]: List of saved file paths (if return_dict=False)
        Dict[str, pd.DataFrame]: Dict mapping config -> DataFrame (if return_dict=True, backward compatibility mode)
    """
    # Use config defaults if not provided
    if target_pips is None:
        target_pips = TARGET_PIPS
    if stop_pips is None:
        stop_pips = STOP_PIPS
    if horizons is None:
        horizons = TIME_HORIZONS
    # num_workers parameter is deprecated - kept for backward compatibility
    # Sequential processing with Numba is faster than parallel with data copying overhead
    if num_workers is not None:
        import warnings
        warnings.warn(
            "The 'num_workers' parameter is deprecated and will be ignored. "
            "Sequential processing with Numba optimization is now used for better performance.",
            DeprecationWarning,
            stacklevel=2
        )
    if use_cache is None:
        use_cache = CACHE_CONFIG.get("enabled", True) and CACHE_CONFIG.get("cache_labeling", True)
    
    # Create labels directory for individual parquet files
    labels_dir = _get_labels_dir()
    
    # Prepare data
    prices = df["mid_price"].values
    timestamps = pd.to_datetime(df["timestamp"]).values
    
    # Convert timestamps to int64 nanoseconds ONCE for vectorized processing
    timestamps_ns = timestamps.astype('datetime64[ns]').astype(np.int64)
    
    # Generate all configurations
    configs = []
    for target in target_pips:
        for stop in stop_pips:
            for horizon in horizons:
                configs.append({
                    "target": target,
                    "stop": stop,
                    "horizon": horizon,
                })
    
    total_configs = len(configs)
    saved_files = []
    
    # Helper function to format config key consistently
    def format_config_key(target, stop, horizon):
        target_str = str(int(target)) if target == int(target) else str(target)
        stop_str = str(int(stop)) if stop == int(stop) else str(stop)
        horizon_str = str(int(horizon)) if horizon == int(horizon) else str(horizon)
        return f"T{target_str}_S{stop_str}_H{horizon_str}"
    
    # Check which configs are already saved (resume support!)
    existing_files = set()
    for config in configs:
        config_key = format_config_key(config['target'], config['stop'], config['horizon'])
        cache_file = labels_dir / f"{config_key}.parquet"
        if cache_file.exists():
            existing_files.add(config_key)
            saved_files.append(str(cache_file))
    
    if existing_files:
        print(f"   ⏭️  Found {len(existing_files)}/{total_configs} already saved - resuming...")
    
    # Filter configs to process (skip already saved)
    configs_to_process = [
        (idx, config) for idx, config in enumerate(configs)
        if format_config_key(config['target'], config['stop'], config['horizon']) not in existing_files
    ]
    
    print(f"🏷️  Labeling {len(df):,} candles with {total_configs} configurations...")
    print(f"   Targets: {target_pips}")
    print(f"   Stops: {stop_pips}")
    print(f"   Horizons: {horizons}")
    print(f"   Processing: Vectorized Numba (1000x faster - parallel execution)")
    print(f"   Storage: Memory-efficient (save each config immediately to labels/)")
    print()
    
    # Process each configuration with progress bar
    with tqdm(
        total=total_configs,
        desc="🏷️  Labeling Progress",
        initial=len(existing_files),
        unit="config",
        ncols=100,
        bar_format="{desc}: {percentage:3.0f}%|{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]"
    ) as pbar:
        for config_idx, config in configs_to_process:
            target = config["target"]
            stop = config["stop"]
            horizon = config["horizon"]
            
            # Format config key with integers when possible (for consistency)
            config_key = format_config_key(target, stop, horizon)
            
            # Update progress bar description with current label
            pbar.set_description(f"🏷️  Label: {config_key}")
            
            if progress_callback:
                progress_callback(config_idx, total_configs, f"Labeling {config_key}")
            
            # Convert horizon from minutes to nanoseconds ONCE
            horizon_ns = int(horizon * 60 * 1_000_000_000)
            
            # Use vectorized Numba function - processes ALL candles at once (100x faster!)
            pbar.write(f"  🚀 Vectorized processing {len(df):,} candles...")
            
            (outcomes_up, outcomes_down,
             mfe_up, mfe_down,
             mae_up, mae_down,
             time_target_up, time_target_down,
             time_stop_up, time_stop_down) = label_all_candles_vectorized(
                prices=prices,
                timestamps_ns=timestamps_ns,
                target_pip=target,
                stop_pip=stop,
                horizon_ns=horizon_ns,
                pip_value=pip_value
            )
            
            # Convert result arrays to DataFrame (only ONCE at the end)
            n_candles = len(df) - 1  # Exclude last candle
            
            # Create results dictionary from arrays
            results_df = pd.DataFrame({
                'candle_idx': np.arange(n_candles),
                'entry_price': prices[:n_candles],
                'target_pip': target,
                'stop_pip': stop,
                'horizon_minutes': horizon,
                
                # UP direction
                'up_outcome': np.where(outcomes_up[:n_candles] == 1, 'target',
                                      np.where(outcomes_up[:n_candles] == -1, 'stop', 'none')),
                'up_hit_target': outcomes_up[:n_candles] == 1,
                'up_hit_stop': outcomes_up[:n_candles] == -1,
                'up_time_to_target': np.where(time_target_up[:n_candles] >= 0, time_target_up[:n_candles], None),
                'up_time_to_stop': np.where(time_stop_up[:n_candles] >= 0, time_stop_up[:n_candles], None),
                'up_mfe': mfe_up[:n_candles],
                'up_mae': mae_up[:n_candles],
                'up_r_multiple': np.where(outcomes_up[:n_candles] == 1, target / stop,
                                         np.where(outcomes_up[:n_candles] == -1, -1.0, None)),
                
                # DOWN direction
                'down_outcome': np.where(outcomes_down[:n_candles] == 1, 'target',
                                        np.where(outcomes_down[:n_candles] == -1, 'stop', 'none')),
                'down_hit_target': outcomes_down[:n_candles] == 1,
                'down_hit_stop': outcomes_down[:n_candles] == -1,
                'down_time_to_target': np.where(time_target_down[:n_candles] >= 0, time_target_down[:n_candles], None),
                'down_time_to_stop': np.where(time_stop_down[:n_candles] >= 0, time_stop_down[:n_candles], None),
                'down_mfe': mfe_down[:n_candles],
                'down_mae': mae_down[:n_candles],
                'down_r_multiple': np.where(outcomes_down[:n_candles] == 1, target / stop,
                                           np.where(outcomes_down[:n_candles] == -1, -1.0, None)),
            })
            
            # 💾 SAVE IMMEDIATELY to disk (memory-efficient!)
            cache_file = labels_dir / f"{config_key}.parquet"
            results_df.to_parquet(cache_file, index=False)
            saved_files.append(str(cache_file))
            pbar.write(f"  💾 Saved {config_key} ({len(results_df):,} rows) to {cache_file.name}")
            
            # 🗑️ CLEAR MEMORY immediately after saving!
            del results_df
            del outcomes_up, outcomes_down
            del mfe_up, mfe_down, mae_up, mae_down
            del time_target_up, time_target_down, time_stop_up, time_stop_down
            
            # Run garbage collection periodically (every 10 configs) to free memory
            # More frequent than this has diminishing returns and impacts performance
            if (config_idx + 1) % 10 == 0:
                gc.collect()
            
            # Update main progress bar
            pbar.update(1)
    
    print(f"\n✅ All {total_configs} configs saved to {labels_dir}/")
    print(f"   📊 Total files: {len(saved_files)}")
    print(f"   💾 Use load_label_results(config_key) to load specific configs")
    print(f"   ⚠️  Use load_all_label_results() to load all (memory-intensive!)")
    
    # Return based on mode
    if return_dict:
        print(f"\n   ⚠️  return_dict=True: Loading all results into memory (backward compatibility mode)")
        return load_all_label_results()
    else:
        return saved_files


# ═══════════════════════════════════════════════════════════════
# 📊 ANALYSIS FUNCTIONS
# ═══════════════════════════════════════════════════════════════

def analyze_labels(labels_df: pd.DataFrame, direction: str = "up") -> Dict:
    """
    Analyze labeling results for a specific direction
    
    Args:
        labels_df: Labeled DataFrame
        direction: "up" or "down"
        
    Returns:
        Dictionary with statistics
    """
    prefix = f"{direction}_"
    
    total = len(labels_df)
    hit_target = labels_df[f"{prefix}hit_target"].sum()
    hit_stop = labels_df[f"{prefix}hit_stop"].sum()
    
    outcomes = labels_df[f"{prefix}outcome"].value_counts()
    
    # Calculate success rate
    target_outcomes = outcomes.get("target", 0)
    stop_outcomes = outcomes.get("stop", 0)
    total_resolved = target_outcomes + stop_outcomes
    
    success_rate = target_outcomes / total_resolved if total_resolved > 0 else 0.0
    
    # Average times
    avg_time_to_target = labels_df[f"{prefix}time_to_target"].mean()
    avg_time_to_stop = labels_df[f"{prefix}time_to_stop"].mean()
    
    # Average MFE/MAE
    avg_mfe = labels_df[f"{prefix}mfe"].mean()
    avg_mae = labels_df[f"{prefix}mae"].mean()
    
    # Average R-Multiple
    r_multiples = labels_df[f"{prefix}r_multiple"].dropna()
    avg_r_multiple = r_multiples.mean() if len(r_multiples) > 0 else None
    
    return {
        "direction": direction,
        "total": total,
        "hit_target": hit_target,
        "hit_stop": hit_stop,
        "target_outcomes": target_outcomes,
        "stop_outcomes": stop_outcomes,
        "none_outcomes": outcomes.get("none", 0),
        "success_rate": success_rate,
        "avg_time_to_target": avg_time_to_target,
        "avg_time_to_stop": avg_time_to_stop,
        "avg_mfe": avg_mfe,
        "avg_mae": avg_mae,
        "avg_r_multiple": avg_r_multiple,
    }


def get_label_summary(results_dict: Dict[str, pd.DataFrame]) -> pd.DataFrame:
    """
    Create summary of all labeling configurations
    
    Args:
        results_dict: Dictionary of labeled DataFrames
        
    Returns:
        Summary DataFrame
    """
    summaries = []
    
    for config_key, labels_df in results_dict.items():
        # Parse config
        parts = config_key.split("_")
        target = float(parts[0][1:])
        stop = float(parts[1][1:])
        horizon = int(parts[2][1:])
        
        # Analyze both directions
        up_stats = analyze_labels(labels_df, "up")
        down_stats = analyze_labels(labels_df, "down")
        
        summaries.append({
            "config": config_key,
            "target_pips": target,
            "stop_pips": stop,
            "horizon_min": horizon,
            "risk_reward": target / stop,
            "up_success_rate": up_stats["success_rate"],
            "down_success_rate": down_stats["success_rate"],
            "up_avg_r": up_stats["avg_r_multiple"],
            "down_avg_r": down_stats["avg_r_multiple"],
            "up_avg_mfe": up_stats["avg_mfe"],
            "down_avg_mfe": down_stats["avg_mfe"],
        })
    
    return pd.DataFrame(summaries)


# ═══════════════════════════════════════════════════════════════
# 🧪 TESTING
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════════╗
║              🏷️  LABELING SYSTEM TEST 🏷️                     ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    # Generate test data
    print("📊 Generating test data...")
    np.random.seed(42)
    n_candles = 10000
    
    timestamps = pd.date_range("2025-01-01", periods=n_candles, freq="1min")
    prices = 1.10 + np.cumsum(np.random.randn(n_candles) * 0.0001)
    
    df = pd.DataFrame({
        "timestamp": timestamps,
        "mid_price": prices,
    })
    
    print(f"   Generated {len(df):,} candles")
    print()
    
    # Test labeling with small subset
    print("🏷️  Testing labeling...")
    results = label_dataframe(
        df,
        target_pips=[10, 20],
        stop_pips=[10, 15],
        horizons=[60, 240],
        num_workers=4,
        return_dict=True  # For backward compatibility in tests
    )
    
    print(f"\n📊 Results:")
    for config_key, labels_df in results.items():
        print(f"\n   {config_key}:")
        print(f"      Total labels: {len(labels_df)}")
        
        up_stats = analyze_labels(labels_df, "up")
        down_stats = analyze_labels(labels_df, "down")
        
        print(f"      UP   - Success: {up_stats['success_rate']:.1%}, R: {up_stats['avg_r_multiple']:.2f}")
        print(f"      DOWN - Success: {down_stats['success_rate']:.1%}, R: {down_stats['avg_r_multiple']:.2f}")
    
    # Summary
    print("\n📋 Summary:")
    summary_df = get_label_summary(results)
    print(summary_df.to_string(index=False))
    
    print("\n✅ Labeling test complete!")
