#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚡🌟💎 NECROZMA - EDGE ANALYZER 💎🌟⚡

The missing piece: Cross Regime × Label to find real edge

"In which regime does which config actually work?"

Usage:
    python edge_analyzer.py
    python edge_analyzer.py --min-trades 500 --min-win-rate 0.55
"""

import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from scipy import stats
import json
from datetime import datetime

from config import OUTPUT_DIR, FILE_PREFIX


# ═══════════════════════════════════════════════════════════════
# 🔧 CONFIGURATION
# ═══════════════════════════════════════════════════════════════

EDGE_CONFIG = {
    "min_trades": 100,           # Minimum trades per regime×config
    "min_win_rate": 0.52,        # Minimum win rate to consider
    "max_p_value": 0.05,         # Statistical significance threshold
    "min_profit_factor": 1.3,    # Minimum profit factor
    "oos_split": 0.2,            # 20% out-of-sample validation
}


# ═══════════════════════════════════════════════════════════════
# 📊 STATISTICAL FUNCTIONS
# ═══════════════════════════════════════════════════════════════

def calculate_p_value(wins: int, total: int, null_hypothesis: float = 0.5) -> float:
    """
    Calculate p-value for win rate being better than random (50%)
    
    Uses binomial test: is observed win rate significantly > 50%?
    
    Args:
        wins: Number of winning trades
        total: Total number of trades
        null_hypothesis: Expected win rate under null (default 0.5 = random)
        
    Returns:
        p-value (lower = more significant)
    """
    if total == 0:
        return 1.0
    
    # One-tailed binomial test (is win rate > null_hypothesis?)
    # Use binomtest for scipy >= 1.7
    try:
        result = stats.binomtest(wins, total, null_hypothesis, alternative='greater')
        p_value = result.pvalue
    except AttributeError:
        # Fallback for older scipy versions
        p_value = stats.binom_test(wins, total, null_hypothesis, alternative='greater')
    return p_value


def calculate_bootstrap_ci(
    outcomes: np.ndarray, 
    n_iterations: int = 1000,
    confidence: float = 0.95
) -> Tuple[float, float, float]:
    """
    Bootstrap confidence interval for win rate
    
    Args:
        outcomes: Array of 1s (win) and 0s (loss)
        n_iterations: Number of bootstrap samples
        confidence: Confidence level (default 95%)
        
    Returns:
        (lower_bound, mean, upper_bound)
    """
    if len(outcomes) == 0:
        return (0.0, 0.0, 0.0)
    
    np.random.seed(42)
    bootstrap_means = []
    
    for _ in range(n_iterations):
        sample = np.random.choice(outcomes, size=len(outcomes), replace=True)
        bootstrap_means.append(sample.mean())
    
    bootstrap_means = np.array(bootstrap_means)
    
    alpha = 1 - confidence
    lower = np.percentile(bootstrap_means, alpha / 2 * 100)
    upper = np.percentile(bootstrap_means, (1 - alpha / 2) * 100)
    mean = bootstrap_means.mean()
    
    return (lower, mean, upper)


# ═══════════════════════════════════════════════════════════════
# 📁 DATA LOADING
# ═══════════════════════════════════════════════════════════════

def load_labels(labels_dir: Path = None, batch_mode: bool = False) -> Dict[str, pd.DataFrame]:
    """
    Load all label parquet files
    
    Args:
        labels_dir: Directory containing label parquets
        batch_mode: If True, returns file paths instead of loaded DataFrames (memory-efficient)
        
    Returns:
        Dictionary of config_key -> DataFrame (or Path if batch_mode=True)
    """
    if labels_dir is None:
        labels_dir = Path("labels")
    
    if not labels_dir.exists():
        raise FileNotFoundError(f"Labels directory not found: {labels_dir}")
    
    labels = {}
    parquet_files = list(labels_dir.glob("*.parquet"))
    
    if not parquet_files:
        # Try with FILE_PREFIX
        parquet_files = list(labels_dir.glob(f"{FILE_PREFIX}*.parquet"))
    
    print(f"📂 Loading {len(parquet_files)} label files...")
    
    if batch_mode:
        print(f"   🔄 Batch mode: returning file paths (not loading into memory)")
        for f in parquet_files:
            config_key = f.stem  # e.g., "T10_S5_H30" or "EURUSD_2025_T10_S5_H30"
            # Remove prefix if present
            if FILE_PREFIX and config_key.startswith(FILE_PREFIX):
                config_key = config_key[len(FILE_PREFIX):]
            labels[config_key] = f  # Store path instead of DataFrame
    else:
        for f in parquet_files:
            config_key = f.stem  # e.g., "T10_S5_H30" or "EURUSD_2025_T10_S5_H30"
            # Remove prefix if present
            if FILE_PREFIX and config_key.startswith(FILE_PREFIX):
                config_key = config_key[len(FILE_PREFIX):]
            
            try:
                labels[config_key] = pd.read_parquet(f)
            except Exception as e:
                print(f"   ⚠️ Failed to load {f.name}: {e}")
    
    print(f"   ✅ Loaded {len(labels)} label configs")
    return labels


def load_regimes(regimes_path: Path = None) -> pd.DataFrame:
    """
    Load regime data
    
    Args:
        regimes_path: Path to regimes parquet/csv
        
    Returns:
        DataFrame with 'regime' column and index matching labels
    """
    # Try common locations
    search_paths = [
        regimes_path,
        Path("regimes.parquet"),
        Path(f"{FILE_PREFIX}regimes.parquet"),
        OUTPUT_DIR / "regimes.parquet",
        OUTPUT_DIR / f"{FILE_PREFIX}regimes.parquet",
    ]
    
    for path in search_paths:
        if path and path.exists():
            print(f"📂 Loading regimes from {path}")
            if path.suffix == '.parquet':
                return pd.read_parquet(path)
            else:
                return pd.read_csv(path)
    
    raise FileNotFoundError("Regimes file not found. Run regime detection first.")


# ═══════════════════════════════════════════════════════════════
# 🎯 EDGE ANALYSIS
# ═══════════════════════════════════════════════════════════════

def parse_config_key(config_key: str) -> Optional[Tuple[float, float, int]]:
    """
    Parse configuration key to extract target, stop, and horizon values
    
    Args:
        config_key: Config string like "T10_S5_H30"
        
    Returns:
        Tuple of (target_pips, stop_pips, horizon_min) or None if parsing fails
    """
    parts = config_key.split("_")
    try:
        target_pips = float(parts[0][1:])  # T10 -> 10
        stop_pips = float(parts[1][1:])    # S5 -> 5
        horizon_min = int(parts[2][1:])    # H30 -> 30
        return (target_pips, stop_pips, horizon_min)
    except (IndexError, ValueError):
        return None


def analyze_regime_label_performance(
    labels: Dict[str, pd.DataFrame],
    regimes_df: pd.DataFrame,
    config: Dict = None,
    batch_mode: bool = True,
    sample_size: Optional[int] = None
) -> pd.DataFrame:
    """
    Cross Regime × Label to find which configs work in which regimes
    
    This is the CORE function - Phase 4 of the pipeline
    
    Memory-efficient implementation: processes one label at a time to avoid OOM
    
    Args:
        labels: Dictionary of config_key -> labeled DataFrame
        regimes_df: DataFrame with 'regime' column
        config: Analysis configuration
        batch_mode: If True, processes labels one at a time (memory-efficient)
        sample_size: If provided, randomly sample this many rows from regimes_df
        
    Returns:
        DataFrame with performance metrics per regime×config
    """
    if config is None:
        config = EDGE_CONFIG
    
    min_trades = config.get("min_trades", 100)
    
    print(f"\n🔬 Analyzing Regime × Label Performance...")
    print(f"   Configs: {len(labels)}")
    print(f"   Regimes: {regimes_df['regime'].nunique()}")
    print(f"   Rows: {len(regimes_df):,}")
    
    # Apply sampling if requested (for very large datasets)
    if sample_size and len(regimes_df) > sample_size:
        print(f"   📉 Sampling {sample_size:,} rows from {len(regimes_df):,} (to reduce memory usage)")
        regimes_df = regimes_df.sample(n=sample_size, random_state=42)
        print(f"   ✅ Sampled dataset has {len(regimes_df):,} rows")
    
    results = []
    
    # Get unique regimes (exclude noise = -1)
    unique_regimes = sorted([r for r in regimes_df['regime'].unique() if r != -1])
    
    # Process each label configuration individually to avoid loading all in memory
    if batch_mode:
        print(f"   🔄 Processing in batch mode (one label at a time)...")
        
        for idx, (config_key, labels_data) in enumerate(labels.items(), 1):
            print(f"   [{idx}/{len(labels)}] Processing {config_key}...", end=' ')
            
            # Load label data if it's a Path
            if isinstance(labels_data, Path):
                try:
                    labels_df = pd.read_parquet(labels_data)
                except Exception as e:
                    print(f"⚠️ Failed to load: {e}")
                    continue
            else:
                labels_df = labels_data
            
            # Parse config
            parsed = parse_config_key(config_key)
            if parsed is None:
                print(f"⚠️ Could not parse")
                continue
            
            target_pips, stop_pips, horizon_min = parsed
            
            # Merge with regimes (align by index or timestamp)
            if 'timestamp' in labels_df.columns and 'timestamp' in regimes_df.columns:
                merged = labels_df.merge(regimes_df[['timestamp', 'regime']], on='timestamp', how='left')
            else:
                # Assume same index
                merged = labels_df.copy()
                merged['regime'] = regimes_df['regime'].values[:len(labels_df)]
            
            # Analyze each regime
            regime_results = 0
            for regime_id in unique_regimes:
                regime_data = merged[merged['regime'] == regime_id]
                
                if len(regime_data) < min_trades:
                    continue
                
                # Calculate metrics for both directions
                for direction in ['up', 'down']:
                    outcome_col = f'{direction}_outcome'
                    
                    if outcome_col not in regime_data.columns:
                        continue
                    
                    # Count wins (target hit) and losses (stop hit)
                    outcomes = regime_data[outcome_col]
                    wins = (outcomes == 'target').sum()
                    losses = (outcomes == 'stop').sum()
                    total = wins + losses
                    
                    if total < min_trades:
                        continue
                    
                    win_rate = wins / total if total > 0 else 0
                    
                    # Calculate profit factor
                    # Win gives target_pips, loss gives -stop_pips
                    gross_profit = wins * target_pips
                    gross_loss = losses * stop_pips
                    profit_factor = gross_profit / gross_loss if gross_loss > 0 else 0
                    
                    # Calculate p-value
                    p_value = calculate_p_value(wins, total, null_hypothesis=0.5)
                    
                    # Calculate expectancy (in R-multiples)
                    # R = risk = stop_pips
                    # Win = target_pips / stop_pips R, Loss = -1 R
                    r_multiple = target_pips / stop_pips
                    expectancy_r = (win_rate * r_multiple) - ((1 - win_rate) * 1)
                    
                    # Bootstrap confidence interval
                    outcome_binary = np.where(outcomes == 'target', 1, 0)
                    outcome_binary = outcome_binary[~pd.isna(outcomes)]
                    ci_lower, ci_mean, ci_upper = calculate_bootstrap_ci(outcome_binary)
                    
                    results.append({
                        'regime': regime_id,
                        'config': config_key,
                        'direction': direction,
                        'target_pips': target_pips,
                        'stop_pips': stop_pips,
                        'horizon_min': horizon_min,
                        'risk_reward': r_multiple,
                        'n_trades': total,
                        'wins': wins,
                        'losses': losses,
                        'win_rate': win_rate,
                        'profit_factor': profit_factor,
                        'expectancy_r': expectancy_r,
                        'p_value': p_value,
                        'ci_lower': ci_lower,
                        'ci_upper': ci_upper,
                        'is_significant': p_value < config.get('max_p_value', 0.05),
                    })
                    regime_results += 1
            
            print(f"({regime_results} results)")
            
            # Free memory
            del merged
            
    else:
        # Original non-batch mode (loads all labels in memory)
        print(f"   ⚠️ Running in non-batch mode (higher memory usage)...")
        
        for config_key, labels_df in labels.items():
            # Parse config
            parsed = parse_config_key(config_key)
            if parsed is None:
                print(f"   ⚠️ Could not parse config: {config_key}")
                continue
            
            target_pips, stop_pips, horizon_min = parsed
            
            # Merge with regimes (align by index or timestamp)
            if 'timestamp' in labels_df.columns and 'timestamp' in regimes_df.columns:
                merged = labels_df.merge(regimes_df[['timestamp', 'regime']], on='timestamp', how='left')
            else:
                # Assume same index
                merged = labels_df.copy()
                merged['regime'] = regimes_df['regime'].values[:len(labels_df)]
            
            # Analyze each regime
            for regime_id in unique_regimes:
                regime_data = merged[merged['regime'] == regime_id]
                
                if len(regime_data) < min_trades:
                    continue
                
                # Calculate metrics for UP direction
                for direction in ['up', 'down']:
                    outcome_col = f'{direction}_outcome'
                    
                    if outcome_col not in regime_data.columns:
                        continue
                    
                    # Count wins (target hit) and losses (stop hit)
                    outcomes = regime_data[outcome_col]
                    wins = (outcomes == 'target').sum()
                    losses = (outcomes == 'stop').sum()
                    total = wins + losses
                    
                    if total < min_trades:
                        continue
                    
                    win_rate = wins / total if total > 0 else 0
                    
                    # Calculate profit factor
                    # Win gives target_pips, loss gives -stop_pips
                    gross_profit = wins * target_pips
                    gross_loss = losses * stop_pips
                    profit_factor = gross_profit / gross_loss if gross_loss > 0 else 0
                    
                    # Calculate p-value
                    p_value = calculate_p_value(wins, total, null_hypothesis=0.5)
                    
                    # Calculate expectancy (in R-multiples)
                    # R = risk = stop_pips
                    # Win = target_pips / stop_pips R, Loss = -1 R
                    r_multiple = target_pips / stop_pips
                    expectancy_r = (win_rate * r_multiple) - ((1 - win_rate) * 1)
                    
                    # Bootstrap confidence interval
                    outcome_binary = np.where(outcomes == 'target', 1, 0)
                    outcome_binary = outcome_binary[~pd.isna(outcomes)]
                    ci_lower, ci_mean, ci_upper = calculate_bootstrap_ci(outcome_binary)
                    
                    results.append({
                        'regime': regime_id,
                        'config': config_key,
                        'direction': direction,
                        'target_pips': target_pips,
                        'stop_pips': stop_pips,
                        'horizon_min': horizon_min,
                        'risk_reward': r_multiple,
                        'n_trades': total,
                        'wins': wins,
                        'losses': losses,
                        'win_rate': win_rate,
                        'profit_factor': profit_factor,
                        'expectancy_r': expectancy_r,
                        'p_value': p_value,
                        'ci_lower': ci_lower,
                        'ci_upper': ci_upper,
                        'is_significant': p_value < config.get('max_p_value', 0.05),
                    })
    
    results_df = pd.DataFrame(results)
    print(f"   ✅ Analyzed {len(results_df)} regime×config×direction combinations")
    
    return results_df


def filter_edge_candidates(
    results_df: pd.DataFrame,
    config: Dict = None
) -> pd.DataFrame:
    """
    Filter for statistically significant edge candidates
    
    Args:
        results_df: Results from analyze_regime_label_performance
        config: Filter configuration
        
    Returns:
        Filtered DataFrame with only significant edges
    """
    if config is None:
        config = EDGE_CONFIG
    
    min_win_rate = config.get('min_win_rate', 0.52)
    max_p_value = config.get('max_p_value', 0.05)
    min_profit_factor = config.get('min_profit_factor', 1.3)
    min_trades = config.get('min_trades', 100)
    
    print(f"\n🎯 Filtering Edge Candidates...")
    print(f"   Criteria:")
    print(f"      Win Rate ≥ {min_win_rate:.0%}")
    print(f"      p-value < {max_p_value}")
    print(f"      Profit Factor ≥ {min_profit_factor}")
    print(f"      Min Trades ≥ {min_trades}")
    
    filtered = results_df[
        (results_df['win_rate'] >= min_win_rate) &
        (results_df['p_value'] < max_p_value) &
        (results_df['profit_factor'] >= min_profit_factor) &
        (results_df['n_trades'] >= min_trades)
    ].copy()
    
    # Sort by expectancy
    filtered = filtered.sort_values('expectancy_r', ascending=False)
    
    print(f"   ✅ Found {len(filtered)} significant edge candidates")
    
    return filtered


def validate_out_of_sample(
    labels: Dict[str, pd.DataFrame],
    regimes_df: pd.DataFrame,
    edge_candidates: pd.DataFrame,
    oos_split: float = 0.2
) -> pd.DataFrame:
    """
    Validate edge candidates on out-of-sample data
    
    Args:
        labels: Dictionary of config_key -> labeled DataFrame
        regimes_df: DataFrame with 'regime' column
        edge_candidates: Filtered edge candidates
        oos_split: Fraction to use as out-of-sample (default 20%)
        
    Returns:
        DataFrame with in-sample and out-of-sample metrics
    """
    print(f"\n📊 Validating Out-of-Sample ({oos_split:.0%} holdout)...")
    
    validated_results = []
    
    for _, candidate in edge_candidates.iterrows():
        config_key = candidate['config']
        regime_id = candidate['regime']
        direction = candidate['direction']
        
        if config_key not in labels:
            continue
        
        labels_df = labels[config_key]
        
        # Merge with regimes
        if 'timestamp' in labels_df.columns and 'timestamp' in regimes_df.columns:
            merged = labels_df.merge(regimes_df[['timestamp', 'regime']], on='timestamp', how='left')
        else:
            merged = labels_df.copy()
            merged['regime'] = regimes_df['regime'].values[:len(labels_df)]
        
        # Filter by regime
        regime_data = merged[merged['regime'] == regime_id]
        
        if len(regime_data) < 50:
            continue
        
        # Split: first 80% = in-sample, last 20% = out-of-sample
        split_idx = int(len(regime_data) * (1 - oos_split))
        is_data = regime_data.iloc[:split_idx]
        oos_data = regime_data.iloc[split_idx:]
        
        outcome_col = f'{direction}_outcome'
        
        # In-sample metrics
        is_outcomes = is_data[outcome_col]
        is_wins = (is_outcomes == 'target').sum()
        is_total = is_wins + (is_outcomes == 'stop').sum()
        is_win_rate = is_wins / is_total if is_total > 0 else 0
        
        # Out-of-sample metrics
        oos_outcomes = oos_data[outcome_col]
        oos_wins = (oos_outcomes == 'target').sum()
        oos_total = oos_wins + (oos_outcomes == 'stop').sum()
        oos_win_rate = oos_wins / oos_total if oos_total > 0 else 0
        
        # Calculate degradation
        degradation = (is_win_rate - oos_win_rate) / is_win_rate if is_win_rate > 0 else 0
        
        validated_results.append({
            'regime': regime_id,
            'config': config_key,
            'direction': direction,
            'is_win_rate': is_win_rate,
            'is_trades': is_total,
            'oos_win_rate': oos_win_rate,
            'oos_trades': oos_total,
            'degradation': degradation,
            'survives_oos': degradation < 0.15,  # Less than 15% degradation
            'target_pips': candidate['target_pips'],
            'stop_pips': candidate['stop_pips'],
            'profit_factor': candidate['profit_factor'],
            'p_value': candidate['p_value'],
        })
    
    validated_df = pd.DataFrame(validated_results)
    
    if len(validated_df) > 0:
        surviving = validated_df['survives_oos'].sum()
        print(f"   ✅ {surviving}/{len(validated_df)} candidates survive OOS validation")
    
    return validated_df


# ═══════════════════════════════════════════════════════════════
# 📋 REPORTING
# ═══════════════════════════════════════════════════════════════

def print_edge_report(validated_df: pd.DataFrame, regimes_df: pd.DataFrame = None):
    """
    Print formatted edge report
    """
    print(f"""
╔══════════════════════════════════════════════════════════════╗
║           ⚡🌟💎 NECROZMA EDGE REPORT 💎🌟⚡                 ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    if len(validated_df) == 0:
        print("❌ No significant edges found.")
        print("\nPossible reasons:")
        print("   - Market is efficient in tested period")
        print("   - Need more data for statistical significance")
        print("   - Try different config ranges")
        return
    
    # Filter surviving edges
    surviving = validated_df[validated_df['survives_oos'] == True]
    
    print(f"🎯 VALIDATED EDGES: {len(surviving)}")
    print("─" * 60)
    
    for idx, row in surviving.head(20).iterrows():
        print(f"""
📊 Regime {row['regime']} + {row['config']} ({row['direction'].upper()})
   ├─ In-Sample:   {row['is_win_rate']:.1%} win rate ({row['is_trades']:,} trades)
   ├─ Out-Sample:  {row['oos_win_rate']:.1%} win rate ({row['oos_trades']:,} trades)
   ├─ Degradation: {row['degradation']:.1%}
   ├─ p-value:     {row['p_value']:.4f} {'✅' if row['p_value'] < 0.05 else '⚠️'}
   └─ Profit Factor: {row['profit_factor']:.2f}
        """)
    
    # Summary by regime
    print("\n📈 SUMMARY BY REGIME")
    print("─" * 60)
    
    for regime in surviving['regime'].unique():
        regime_edges = surviving[surviving['regime'] == regime]
        print(f"\nRegime {regime}: {len(regime_edges)} edges")
        for _, edge in regime_edges.iterrows():
            print(f"   • {edge['config']} {edge['direction']}: {edge['oos_win_rate']:.1%}")


def save_edge_report(validated_df: pd.DataFrame, output_dir: Path = None):
    """
    Save edge report to JSON and CSV
    """
    if output_dir is None:
        output_dir = OUTPUT_DIR / "edge_analysis"
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Save CSV
    csv_path = output_dir / f"{FILE_PREFIX}edge_candidates_{timestamp}.csv"
    validated_df.to_csv(csv_path, index=False)
    print(f"💾 Saved CSV: {csv_path}")
    
    # Save JSON summary
    summary = {
        "timestamp": timestamp,
        "total_candidates": len(validated_df),
        "surviving_oos": int(validated_df['survives_oos'].sum()) if 'survives_oos' in validated_df.columns else 0,
        "edges": validated_df.to_dict(orient='records')
    }
    
    json_path = output_dir / f"{FILE_PREFIX}edge_report_{timestamp}.json"
    with open(json_path, 'w') as f:
        json.dump(summary, f, indent=2, default=str)
    print(f"💾 Saved JSON: {json_path}")


# ═══════════════════════════════════════════════════════════════
# 🚀 MAIN
# ═══════════════════════════════════════════════════════════════

def find_edge(
    labels_dir: Path = None,
    regimes_path: Path = None,
    config: Dict = None
) -> pd.DataFrame:
    """
    Main function to find edge
    
    Args:
        labels_dir: Directory with label parquets
        regimes_path: Path to regimes file
        config: Analysis configuration
        
    Returns:
        DataFrame with validated edge candidates
    """
    print("""
╔══════════════════════════════════════════════════════════════╗
║           ⚡🌟💎 NECROZMA EDGE ANALYZER 💎🌟⚡               ║
║                                                              ║
║   "In which regime does which config actually work?"         ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    if config is None:
        config = EDGE_CONFIG
    
    # Load data
    labels = load_labels(labels_dir)
    regimes_df = load_regimes(regimes_path)
    
    # Analyze regime × label performance
    results_df = analyze_regime_label_performance(labels, regimes_df, config)
    
    if len(results_df) == 0:
        print("❌ No results to analyze")
        return pd.DataFrame()
    
    # Filter edge candidates
    edge_candidates = filter_edge_candidates(results_df, config)
    
    if len(edge_candidates) == 0:
        print("❌ No edge candidates found with current criteria")
        print("   Try lowering min_win_rate or min_profit_factor")
        return pd.DataFrame()
    
    # Validate out-of-sample
    validated = validate_out_of_sample(
        labels, regimes_df, edge_candidates, 
        oos_split=config.get('oos_split', 0.2)
    )
    
    # Print report
    print_edge_report(validated, regimes_df)
    
    # Save results
    save_edge_report(validated)
    
    return validated


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="NECROZMA Edge Analyzer")
    parser.add_argument("--labels-dir", type=Path, default=Path("labels"),
                        help="Directory with label parquet files")
    parser.add_argument("--regimes", type=Path, default=None,
                        help="Path to regimes parquet file")
    parser.add_argument("--min-trades", type=int, default=100,
                        help="Minimum trades per regime×config")
    parser.add_argument("--min-win-rate", type=float, default=0.52,
                        help="Minimum win rate to consider")
    parser.add_argument("--max-p-value", type=float, default=0.05,
                        help="Maximum p-value for significance")
    parser.add_argument("--min-pf", type=float, default=1.3,
                        help="Minimum profit factor")
    
    args = parser.parse_args()
    
    config = {
        "min_trades": args.min_trades,
        "min_win_rate": args.min_win_rate,
        "max_p_value": args.max_p_value,
        "min_profit_factor": args.min_pf,
        "oos_split": 0.2,
    }
    
    edges = find_edge(
        labels_dir=args.labels_dir,
        regimes_path=args.regimes,
        config=config
    )
    
    if len(edges) > 0:
        print(f"\n✅ Analysis complete! Found {len(edges)} potential edges.")
    else:
        print(f"\n⚠️ No significant edges found with current criteria.")
