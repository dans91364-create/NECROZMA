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
- Parallel processing for all 32 threads
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from multiprocessing import Pool, cpu_count
from functools import partial
import warnings

warnings.filterwarnings("ignore")

from config import TARGET_PIPS, STOP_PIPS, TIME_HORIZONS, NUM_WORKERS, LABELING_METRICS


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
        
        hit_target = False
        hit_stop = False
        target_time = None
        stop_time = None
        target_idx = None
        stop_idx = None
        
        max_favorable = 0.0  # MFE
        max_adverse = 0.0    # MAE
        
        # Scan forward within horizon
        for i in range(candle_idx + 1, horizon_idx):
            price = prices[i]
            
            if direction == "up":
                # Track MFE and MAE
                excursion = (price - entry_price) / pip_value
                max_favorable = max(max_favorable, excursion)
                max_adverse = min(max_adverse, excursion)
                
                # Check target
                if not hit_target and price >= target_price:
                    hit_target = True
                    target_time = timestamps[i]
                    target_idx = i
                
                # Check stop
                if not hit_stop and price <= stop_price:
                    hit_stop = True
                    stop_time = timestamps[i]
                    stop_idx = i
                    
            else:  # down
                # Track MFE and MAE
                excursion = (entry_price - price) / pip_value
                max_favorable = max(max_favorable, excursion)
                max_adverse = min(max_adverse, excursion)
                
                # Check target
                if not hit_target and price <= target_price:
                    hit_target = True
                    target_time = timestamps[i]
                    target_idx = i
                
                # Check stop
                if not hit_stop and price >= stop_price:
                    hit_stop = True
                    stop_time = timestamps[i]
                    stop_idx = i
            
            # Exit if both hit
            if hit_target and hit_stop:
                break
        
        # Calculate time to target/stop
        time_to_target = None
        time_to_stop = None
        
        if hit_target and target_time:
            # Handle both numpy.timedelta64 and pandas Timedelta
            time_diff = target_time - entry_time
            if hasattr(time_diff, 'total_seconds'):
                time_to_target = time_diff.total_seconds() / 60.0
            else:
                # numpy.timedelta64 - convert to float (nanoseconds)
                time_to_target = float(time_diff) / 1e9 / 60.0
        
        if hit_stop and stop_time:
            # Handle both numpy.timedelta64 and pandas Timedelta
            time_diff = stop_time - entry_time
            if hasattr(time_diff, 'total_seconds'):
                time_to_stop = time_diff.total_seconds() / 60.0
            else:
                # numpy.timedelta64 - convert to float (nanoseconds)
                time_to_stop = float(time_diff) / 1e9 / 60.0
        
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


def label_chunk(
    chunk_indices: List[int],
    prices: np.ndarray,
    timestamps: np.ndarray,
    target_pip: float,
    stop_pip: float,
    horizon_minutes: int,
    pip_value: float = 0.0001
) -> List[Dict]:
    """
    Label a chunk of candles (for parallel processing)
    
    Args:
        chunk_indices: List of candle indices to process
        prices: Array of mid prices
        timestamps: Array of timestamps
        target_pip: Target in pips
        stop_pip: Stop loss in pips
        horizon_minutes: Time horizon in minutes
        pip_value: Value of 1 pip
        
    Returns:
        List of labeling results
    """
    results = []
    for idx in chunk_indices:
        result = label_single_candle(
            idx, prices, timestamps,
            target_pip, stop_pip, horizon_minutes, pip_value
        )
        if result:
            results.append(result)
    return results


# ═══════════════════════════════════════════════════════════════
# 🚀 PARALLEL LABELING
# ═══════════════════════════════════════════════════════════════

def label_dataframe(
    df: pd.DataFrame,
    target_pips: List[float] = None,
    stop_pips: List[float] = None,
    horizons: List[int] = None,
    num_workers: int = None,
    pip_value: float = 0.0001,
    progress_callback = None
) -> Dict[str, pd.DataFrame]:
    """
    Label entire dataframe with multiple targets/stops/horizons
    
    Args:
        df: DataFrame with at least 'mid_price' and 'timestamp' columns
        target_pips: List of target levels in pips
        stop_pips: List of stop levels in pips
        horizons: List of time horizons in minutes
        num_workers: Number of parallel workers
        pip_value: Value of 1 pip
        progress_callback: Optional callback(current, total, desc) for progress
        
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
    if num_workers is None:
        num_workers = min(NUM_WORKERS, cpu_count())
    
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
    
    print(f"🏷️  Labeling {len(df):,} candles with {total_configs} configurations...")
    print(f"   Targets: {target_pips}")
    print(f"   Stops: {stop_pips}")
    print(f"   Horizons: {horizons}")
    print(f"   Workers: {num_workers}")
    print()
    
    # Process each configuration
    for config_idx, config in enumerate(configs):
        target = config["target"]
        stop = config["stop"]
        horizon = config["horizon"]
        
        config_key = f"T{target}_S{stop}_H{horizon}"
        
        if progress_callback:
            progress_callback(config_idx, total_configs, f"Labeling {config_key}")
        else:
            print(f"   [{config_idx+1}/{total_configs}] Processing {config_key}...")
        
        # Split indices into chunks for parallel processing
        indices = list(range(len(df) - 1))
        chunk_size = max(1, len(indices) // (num_workers * 4))
        chunks = [indices[i:i+chunk_size] for i in range(0, len(indices), chunk_size)]
        
        # Create partial function with fixed parameters
        label_func = partial(
            label_chunk,
            prices=prices,
            timestamps=timestamps,
            target_pip=target,
            stop_pip=stop,
            horizon_minutes=horizon,
            pip_value=pip_value
        )
        
        # Process in parallel
        with Pool(num_workers) as pool:
            chunk_results = pool.map(label_func, chunks)
        
        # Flatten results
        all_results = []
        for chunk_result in chunk_results:
            all_results.extend(chunk_result)
        
        # Convert to DataFrame
        if all_results:
            results_df = pd.DataFrame(all_results)
            results_dict[config_key] = results_df
    
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
