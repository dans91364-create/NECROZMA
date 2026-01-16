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
from typing import Dict, List, Tuple, Optional
import warnings
import hashlib
import pickle
import json
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
    use_cache: bool = None
) -> Dict[str, pd.DataFrame]:
    """
    Label entire dataframe with multiple targets/stops/horizons
    
    Args:
        df: DataFrame with at least 'mid_price' and 'timestamp' columns
        target_pips: List of target levels in pips
        stop_pips: List of stop levels in pips
        horizons: List of time horizons in minutes
        num_workers: Deprecated (kept for backward compatibility, ignored)
        pip_value: Value of 1 pip
        progress_callback: Optional callback(current, total, desc) for progress
        use_cache: Whether to use cache (default: from CACHE_CONFIG)
        
    Returns:
        Dictionary mapping config -> labeled DataFrame
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
    if use_cache is None:
        use_cache = CACHE_CONFIG.get("enabled", True) and CACHE_CONFIG.get("cache_labeling", True)
    
    # Generate data hash for cache
    cache_dir = _get_cache_dir()
    data_hash = _generate_data_hash(df)
    cache_file = cache_dir / f"{FILE_PREFIX}labels_{data_hash}.pkl"
    progress_file = cache_dir / f"{FILE_PREFIX}labels_progress_{data_hash}.json"
    
    # Try to load from cache
    if use_cache and cache_file.exists():
        print(f"   ✅ Loading labels from cache ({cache_file.name})...")
        cached_data = _load_cache(cache_file)
        if cached_data is not None:
            print(f"   💾 Loaded {len(cached_data)} labeled datasets from cache!")
            return cached_data
    
    # Prepare data
    prices = df["mid_price"].values
    timestamps = pd.to_datetime(df["timestamp"]).values
    
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
    results_dict = {}
    
    # Load progress if exists (for resume)
    completed = _load_progress(progress_file) if use_cache else set()
    
    if completed:
        print(f"   📥 Resuming from checkpoint ({len(completed)}/{total_configs} already completed)...")
    
    print(f"🏷️  Labeling {len(df):,} candles with {total_configs} configurations...")
    print(f"   Targets: {target_pips}")
    print(f"   Stops: {stop_pips}")
    print(f"   Horizons: {horizons}")
    print(f"   Processing: Sequential (Numba-optimized)")
    if use_cache:
        print(f"   Cache: Enabled (checkpoint every {CACHE_CONFIG.get('checkpoint_interval', 10)} configs)")
    print()
    
    # Checkpoint interval
    checkpoint_interval = CACHE_CONFIG.get("checkpoint_interval", 10)
    
    # Filter configs to process (skip already completed)
    configs_to_process = [
        (idx, config) for idx, config in enumerate(configs)
        if f"T{config['target']}_S{config['stop']}_H{config['horizon']}" not in completed
    ]
    
    # Process each configuration with progress bar
    with tqdm(
        total=total_configs,
        desc="🏷️  Labeling Progress",
        initial=len(completed),
        unit="label",
        ncols=100,
        bar_format="{desc}: {percentage:3.0f}%|{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]"
    ) as pbar:
        for config_idx, config in configs_to_process:
            target = config["target"]
            stop = config["stop"]
            horizon = config["horizon"]
            
            config_key = f"T{target}_S{stop}_H{horizon}"
            
            # Update progress bar description with current label
            pbar.set_description(f"🏷️  Label: {config_key}")
            
            if progress_callback:
                progress_callback(config_idx, total_configs, f"Labeling {config_key}")
            
            # Process all candles sequentially (Numba is fast enough, no need for multiprocessing overhead)
            # The multiprocessing Pool was copying 14M+ floats to each worker, causing massive overhead
            # Numba JIT compilation makes sequential processing faster than parallel with data copying
            all_results = []
            for idx in tqdm(
                range(len(df) - 1),
                desc=f"  └─ Processing candles",
                leave=False,
                unit="candle",
                ncols=100,
                bar_format="  {desc}: {percentage:3.0f}%|{bar}| {n_fmt}/{total_fmt}"
            ):
                result = label_single_candle(
                    idx, prices, timestamps,
                    target, stop, horizon, pip_value
                )
                if result:
                    all_results.append(result)
            
            # Convert to DataFrame
            if all_results:
                results_df = pd.DataFrame(all_results)
                results_dict[config_key] = results_df
            
            # Mark as completed
            completed.add(config_key)
            
            # Update main progress bar
            pbar.update(1)
            
            # Save progress checkpoint
            if use_cache and len(completed) % checkpoint_interval == 0:
                _save_progress(progress_file, completed)
                pbar.write(f"   💾 Checkpoint saved ({len(completed)}/{total_configs} completed)")
    
    # Save final cache
    if use_cache:
        print(f"\n   💾 Saving complete cache...")
        _save_cache(cache_file, results_dict)
        # Clean up progress file
        if progress_file.exists():
            progress_file.unlink()
        print(f"   ✅ Cache saved to {cache_file.name}")
    
    print(f"\n✅ Labeling complete! Generated {len(results_dict)} labeled datasets.")
    
    return results_dict


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
        num_workers=4
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
