#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚡🌟💎 ULTRA NECROZMA - ANALYZER ENGINE 💎🌟⚡

The Supreme Analysis Engine:  Where Light Becomes Knowledge
"Processing infinite dimensions at the speed of light"

Technical: Main analysis engine with multiprocessing support
- OHLC resampling and movement classification
- Feature extraction orchestration
- Parallel universe processing
- Pattern aggregation and ranking
"""

import numpy as np
import pandas as pd
from pathlib import Path
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor, as_completed
import multiprocessing as mp
import time
import json
import gc
import warnings

warnings.filterwarnings("ignore")

# Local imports
from config import (
    INTERVALS, LOOKBACKS, MOVEMENT_LEVELS, DIRECTIONS,
    NUM_WORKERS, MIN_SAMPLES, FEATURE_GROUPS,
    CONFIDENCE_THRESHOLDS, TOP_PATTERNS_PER_LEVEL,
    get_all_configs, get_output_dirs, THEME, MAX_MEMORY_GB
)
from data_loader import resample_to_ohlc
from features_core import extract_core_features
from features_advanced import extract_advanced_features


# ═══════════════════════════════════════════════════════════════
# 🌟 MOVEMENT CLASSIFICATION (Energy Levels)
# ═══════════════════════════════════════════════════════════════

def classify_movement(pips_change):
    """
    Classify price movement by magnitude (Energy Level Detection)
    Technical: Categorize pip movement into predefined levels
    
    Args:
        pips_change: Movement in pips
        
    Returns:
        tuple: (level_name, direction)
    """
    direction = "up" if pips_change > 0 else "down"
    abs_pips = abs(pips_change)
    
    for level_name, level_config in MOVEMENT_LEVELS.items():
        if level_config["min"] <= abs_pips < level_config["max"]: 
            return level_name, direction
    
    return "Muito Grande", direction


def get_movement_targets(ohlc_df, lookback):
    """
    Find all movement targets in OHLC data (Target Acquisition)
    Technical: Identify price movements and their preceding patterns
    
    Args:
        ohlc_df:  OHLC DataFrame
        lookback: Number of candles to look back
        
    Returns: 
        dict:  Targets organized by level and direction
    """
    targets = {level: {"up": [], "down": []} for level in MOVEMENT_LEVELS. keys()}
    
    if len(ohlc_df) < lookback + 2:
        return targets
    
    for i in range(lookback, len(ohlc_df) - 1):
        # Current candle movement
        current_pips = ohlc_df.iloc[i]["body_pips"]
        
        if abs(current_pips) < 1:   # Ignore tiny movements
            continue
        
        level, direction = classify_movement(current_pips)
        
        # Get lookback window
        window_start = i - lookback
        window_end = i
        
        window_data = ohlc_df.iloc[window_start:window_end]. copy()
        
        if len(window_data) >= MIN_SAMPLES:
            targets[level][direction].append({
                "index": i,
                "timestamp": ohlc_df.iloc[i]["timestamp"],
                "movement_pips": float(current_pips),
                "window_data": window_data
            })
    
    return targets


# ═══════════════════════════════════════════════════════════════
# 💎 PATTERN EXTRACTION (Crystal Formation)
# ═══════════════════════════════════════════════════════════════

def extract_window_features(window_data):
    """
    Extract features from a lookback window (Crystal Analysis)
    Technical: Apply all feature extractors to price window
    
    Args:
        window_data: DataFrame with OHLC data for window
        
    Returns:
        dict: All extracted features
    """
    features = {}
    
    try:
        # Get price series
        prices = window_data["close"].values
        
        # Calculate pips
        pips = np.diff(prices) * 10000
        
        if len(prices) < MIN_SAMPLES:
            return features
        
        # Core features
        if FEATURE_GROUPS. get("statistical", True):
            features.update(extract_core_features(prices, pips))
        
        # Advanced features
        if any([
            FEATURE_GROUPS. get("quantum", True),
            FEATURE_GROUPS.get("multifractal", True),
            FEATURE_GROUPS.get("recurrence", True),
            FEATURE_GROUPS.get("patterns", True),
            FEATURE_GROUPS.get("ultra", True)
        ]):
            features.update(extract_advanced_features(prices, pips))
        
        # Add OHLC-specific features
        features.update(extract_ohlc_features(window_data))
        
    except Exception as e:
        pass
    
    return features


def extract_ohlc_features(window_data):
    """
    Extract OHLC-specific features (Candle Crystal Analysis)
    Technical: Features derived from candlestick patterns
    """
    features = {}
    
    try:
        # Body statistics
        bodies = window_data["body_pips"].values
        features["ohlc_body_mean"] = float(np.mean(bodies))
        features["ohlc_body_std"] = float(np.std(bodies))
        features["ohlc_body_sum"] = float(np.sum(bodies))
        
        # Range statistics
        ranges = window_data["range_pips"].values
        features["ohlc_range_mean"] = float(np.mean(ranges))
        features["ohlc_range_std"] = float(np.std(ranges))
        features["ohlc_range_max"] = float(np.max(ranges))
        
        # Direction statistics
        up_candles = np.sum(bodies > 0)
        down_candles = np.sum(bodies < 0)
        total_candles = len(bodies)
        
        features["ohlc_up_ratio"] = float(up_candles / total_candles) if total_candles > 0 else 0.5
        features["ohlc_down_ratio"] = float(down_candles / total_candles) if total_candles > 0 else 0.5
        
        # Wick analysis
        if "upper_wick" in window_data.columns and "lower_wick" in window_data.columns:
            upper_wicks = window_data["upper_wick"].values * 10000
            lower_wicks = window_data["lower_wick"].values * 10000
            
            features["ohlc_upper_wick_mean"] = float(np.mean(upper_wicks))
            features["ohlc_lower_wick_mean"] = float(np.mean(lower_wicks))
            features["ohlc_wick_ratio"] = float(
                np.mean(upper_wicks) / (np.mean(lower_wicks) + 1e-10)
            )
        
        # Trend strength
        closes = window_data["close"].values
        if len(closes) > 1:
            net_change = (closes[-1] - closes[0]) * 10000
            total_change = np.sum(np.abs(np.diff(closes))) * 10000
            features["ohlc_trend_efficiency"] = float(
                abs(net_change) / (total_change + 1e-10)
            )
        
        # Volume (tick count) if available
        if "tick_volume" in window_data.columns:
            volumes = window_data["tick_volume"].values
            features["ohlc_volume_mean"] = float(np. mean(volumes))
            features["ohlc_volume_trend"] = float(
                np. mean(volumes[-3:]) / (np.mean(volumes[:-3]) + 1e-10)
            ) if len(volumes) > 3 else 1.0
        
        # Spread if available
        if "spread_avg" in window_data.columns:
            spreads = window_data["spread_avg"].values
            features["ohlc_spread_mean"] = float(np.mean(spreads))
            features["ohlc_spread_std"] = float(np.std(spreads))
        
    except Exception: 
        pass
    
    return features


def create_pattern_signature(features, n_bins=5):
    """
    Create a pattern signature from features (Crystal Signature)
    Technical: Discretize features into a pattern string
    
    Args:
        features: Feature dictionary
        n_bins: Number of bins for discretization
        
    Returns:
        str: Pattern signature
    """
    if not features:
        return "UNKNOWN"
    
    # Key features for signature
    key_features = [
        "dfa_alpha", "hurst", "d1_mean", "stat_trend_slope",
        "ohlc_up_ratio", "photon_efficiency"
    ]
    
    signature_parts = []
    
    for feat in key_features:
        if feat in features:
            val = features[feat]
            # Simple binning
            if val < -0.5:
                sig = "VL"  # Very Low
            elif val < -0.1:
                sig = "L"   # Low
            elif val < 0.1:
                sig = "N"   # Neutral
            elif val < 0.5:
                sig = "H"   # High
            else:
                sig = "VH"  # Very High
            signature_parts.append(f"{feat[: 3]}:{sig}")
    
    return "|".join(signature_parts) if signature_parts else "UNKNOWN"


# ═══════════════════════════════════════════════════════════════
# 🌌 UNIVERSE PROCESSING (Dimensional Analysis)
# ═══════════════════════════════════════════════════════════════

def process_universe(df, interval, lookback, universe_name):
    """
    Process a single universe (Dimensional Creation)
    Technical: Complete analysis for one interval/lookback configuration
    
    Args:
        df: Full tick DataFrame
        interval: Candle interval in minutes
        lookback:  Lookback period in candles
        universe_name: Name for this universe
        
    Returns: 
        dict: Universe analysis results
    """
    universe_start = time.time()
    
    results = {
        level: {direction: {
            "total_occurrences": 0,
            "patterns": defaultdict(lambda: {"count": 0, "features": []}),
            "all_features": [],
            "feature_stats": {},
            "debug_stats": {"targets_found": 0, "features_extracted": 0, "features_failed": 0}
        } for direction in DIRECTIONS}
        for level in MOVEMENT_LEVELS.keys()
    }
    
    try:
        # Resample to OHLC
        ohlc = resample_to_ohlc(df, interval)
        
        if len(ohlc) < lookback + 10:
            return None
        
        # Find targets
        targets = get_movement_targets(ohlc, lookback)
        
        # Process each level and direction
        for level in MOVEMENT_LEVELS.keys():
            for direction in DIRECTIONS: 
                target_list = targets[level][direction]
                
                if not target_list:
                    continue
                
                results[level][direction]["total_occurrences"] = len(target_list)
                results[level][direction]["debug_stats"]["targets_found"] = len(target_list)
                
                # Extract features for each target
                for target in target_list:
                    features = extract_window_features(target["window_data"])
                    
                    if features:
                        # Store features
                        results[level][direction]["all_features"].append(features)
                        results[level][direction]["debug_stats"]["features_extracted"] += 1
                        
                        # Create pattern signature
                        signature = create_pattern_signature(features)
                        results[level][direction]["patterns"][signature]["count"] += 1
                        results[level][direction]["patterns"][signature]["features"].append(features)
                    else:
                        results[level][direction]["debug_stats"]["features_failed"] += 1
        
        # Calculate feature statistics
        for level in MOVEMENT_LEVELS.keys():
            for direction in DIRECTIONS:
                all_feats = results[level][direction]["all_features"]
                
                if all_feats: 
                    results[level][direction]["feature_stats"] = calculate_feature_stats(all_feats)
        
        # Convert defaultdicts to regular dicts
        for level in results: 
            for direction in results[level]:
                results[level][direction]["patterns"] = dict(results[level][direction]["patterns"])
        
    except Exception as e:
        print(f"   ❌ Error in universe {universe_name}: {e}")
        return None
    
    universe_time = time.time() - universe_start

    # Extract metadata from OHLC
    ohlc_dict = ohlc.to_dict("records") if len(ohlc) > 0 else []
    start_date = str(ohlc_dict[0]["timestamp"]) if len(ohlc_dict) > 0 else ""
    end_date = str(ohlc_dict[-1]["timestamp"]) if len(ohlc_dict) > 0 else ""
    total_candles = len(ohlc_dict)

    
    return {
        "name": universe_name,
        "config": {"interval": interval, "lookback":  lookback},
        "results":  results,
        "processing_time": universe_time,
        "total_patterns": sum(
            results[l][d]["total_occurrences"]
            for l in results for d in results[l]
        ),
        "ohlc_data":  ohlc_dict,
        "metadata": {
            "start_date": start_date,
            "end_date":   end_date,
            "total_candles": total_candles,
            "interval_minutes": interval,
            "lookback_candles": lookback
        },
    }


def calculate_feature_stats(feature_list):
    """
    Calculate statistics for a list of feature dictionaries
    Technical: Aggregate feature statistics across multiple samples
    """
    if not feature_list:
        return {}
    
    stats = {}
    
    # Get all feature names
    all_keys = set()
    for f in feature_list:
        all_keys.update(f.keys())
    
    for key in all_keys:
        values = [f[key] for f in feature_list if key in f and isinstance(f[key], (int, float))]
        
        if values:
            stats[f"{key}_mean"] = float(np.mean(values))
            stats[f"{key}_std"] = float(np.std(values))
            stats[f"{key}_min"] = float(np.min(values))
            stats[f"{key}_max"] = float(np.max(values))
    
    return stats


# ═══════════════════════════════════════════════════════════════
# ⚡ PARALLEL PROCESSING (Photon Burst Mode)
# ═══════════════════════════════════════════════════════════════

def process_universe_wrapper(args):
    """
    Wrapper for multiprocessing (Photon Clone)
    Technical:  Unpack arguments for process_universe
    """
    df, interval, lookback, universe_name = args
    return process_universe(df, interval, lookback, universe_name)


class UltraNecrozmaAnalyzer:
    """
    Main Analysis Engine (Ultra Necrozma Core)
    Technical: Orchestrates parallel universe processing
    """
    
    def __init__(self, df, output_dir=None, lore_system=None):
        """
        Initialize analyzer with data
        
        Args:
            df:  Tick DataFrame (from data_loader)
            output_dir: Output directory path
            lore_system: Optional LoreSystem for notifications
        """
        self.df = df
        self.output_dirs = get_output_dirs()
        self.output_dir = output_dir or self.output_dirs["root"]
        self.lore_system = lore_system
        
        self.configs = get_all_configs()
        self.results = {}
        
        self.start_time = time.time()
        self.universes_processed = 0
        self. total_patterns = 0
        
        # Evolution tracking (Pokemon theme)
        self.evolution_stage = "Necrozma"
        self.light_power = 0.0
        self.prismatic_cores = []
        
        print(f"""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║       ⚡🌟💎 ULTRA NECROZMA ANALYZER INITIALIZED 💎🌟⚡      ║
║                                                              ║
║   "The light that will analyze all dimensions..."            ║
║                                                              ║
╠══════════════════════════════════════════════════════════════╣
║   📊 Data Points:      {len(df):>15,}                         ║
║   🌌 Universes:       {len(self.configs):>15}                         ║
║   ⚡ Workers:         {NUM_WORKERS: >15}                         ║
║   📂 Output:           {str(self.output_dir):<25}   ║
╚══════════════════════════════════════════════════════════════╝
        """)
    
    def evolve(self):
        """Update evolution stage based on patterns found (uses new lore system)"""
        from lore import evolution_status, show_prismatic_progress
        
        # Get evolution based on total patterns
        evo = evolution_status(self.total_patterns)
        
        self.evolution_stage = evo["name"]
        self.light_power = evo["power_percent"]
        
        # Show prismatic progress if significant milestone
        if self.total_patterns > 0 and self.total_patterns % 50000 == 0:
            print(f"\n   💎 Necrozma absorbs light from {self.total_patterns:,} patterns...")
            show_prismatic_progress(evo["cores"], 7, evo["power_percent"])
            print(f"   🌟 Evolution: {evo['name']}")
            print()
    
    def collect_prismatic_core(self, color):
        """Collect a prismatic core (progress tracking)"""
        if color not in self.prismatic_cores:
            self.prismatic_cores.append(color)
            print(f"   💎 Prismatic Core collected: {color} ({len(self.prismatic_cores)}/7)")
    
    def _universe_exists(self, universe_name):
        """
        Check if a universe already exists (Cache Detection)
        Technical: Check for parquet or json file existence
        
        Args:
            universe_name: Name of the universe to check
            
        Returns:
            bool: True if universe exists
        """
        from config import CACHE_CONFIG
        
        # Don't skip if cache is disabled
        if not CACHE_CONFIG.get("enabled", True):
            return False
        if not CACHE_CONFIG.get("skip_existing_universes", True):
            return False
        
        parquet_path = self.output_dirs["universes"] / f"{universe_name}.parquet"
        json_path = self.output_dirs["universes"] / f"{universe_name}.json"
        
        return parquet_path.exists() or json_path.exists()
    
    def _load_universe_metadata(self, universe_name):
        """
        Load metadata from existing universe (Cache Retrieval)
        Technical: Load universe metadata for progress tracking
        
        Args:
            universe_name: Name of the universe
            
        Returns:
            dict: Universe metadata or None
        """
        metadata_path = self.output_dirs["universes"] / f"{universe_name}_metadata.json"
        
        if metadata_path.exists():
            try:
                with open(metadata_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"   ⚠️ Failed to load metadata for {universe_name}: {e}")
                return None
        
        # Try to extract from json file if no metadata sidecar
        json_path = self.output_dirs["universes"] / f"{universe_name}.json"
        if json_path.exists():
            try:
                with open(json_path, 'r') as f:
                    data = json.load(f)
                    return {
                        "name": data.get("name", universe_name),
                        "total_patterns": data.get("total_patterns", 0),
                        "processing_time": data.get("processing_time", 0),
                        "config": data.get("config", {}),
                        "metadata": data.get("metadata", {})
                    }
            except Exception as e:
                print(f"   ⚠️ Failed to load JSON for {universe_name}: {e}")
                return None
        
        return None
    
    def run_analysis(self, parallel=False):
        """
        Run the complete analysis (Light That Burns The Sky)
        Technical: Process all universes with optional parallelization
        
        Args:
            parallel: Use multiprocessing if True (DEFAULT: False for low CPU usage)
            
        Returns: 
            dict: All analysis results
        """
        print(f"""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║          🌟 INITIATING SUPREME ANALYSIS 🌟                   ║
║                                                              ║
║   "From the void between dimensions, I emerge..."            ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
        """)
        
        analysis_start = time.time()
        
        if parallel and NUM_WORKERS > 1:
            print("⚠️  WARNING: Parallel mode may cause high CPU usage!")
            print("   Recommended: Use sequential mode for VMs and low CPU systems\n")
            self._run_parallel()
        else:
            if parallel and NUM_WORKERS == 1:
                print("ℹ️  Parallel mode requested but NUM_WORKERS=1, using sequential\n")
            self._run_sequential()
        
        analysis_time = time.time() - analysis_start
        
        # Final evolution
        self.evolve()
        
        # Collect final cores based on results
        if self.total_patterns > 1000:
            self.collect_prismatic_core("Red")
        if self.total_patterns > 5000:
            self.collect_prismatic_core("Blue")
        if len(self.results) >= len(self.configs):
            self.collect_prismatic_core("Yellow")
        
        # Show final evolution status
        from lore import evolution_status, show_prismatic_progress, print_legendary_banner
        
        evo = evolution_status(self.total_patterns)
        
        # If we've reached Ultra Necrozma, show the banner
        if evo["cores"] >= 5:
            print_legendary_banner('ultra_necrozma', count=self.total_patterns, universes=len(self.configs))
        
        print(f"""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║          ⚡💎 ANALYSIS COMPLETE 💎⚡                         ║
║                                                              ║
╠══════════════════════════════════════════════════════════════╣
║   🌌 Universes Processed:  {self.universes_processed:>10}                    ║
║   🎯 Total Patterns:       {self.total_patterns:>10,}                    ║
║   ⏱️  Time:                 {analysis_time: >10.1f}s                   ║
║   ⚡ Evolution:            {self.evolution_stage:>10}                    ║
║   💎 Light Power:         {self.light_power:>10.1f}%                   ║
║   🌈 Prismatic Cores:     {len(self.prismatic_cores):>10}/7                    ║
╚══════════════════════════════════════════════════════════════╝
        """)
        
        # Show prismatic progress
        print()
        show_prismatic_progress(evo["cores"], 7, self.light_power)
        print(f"🌟 Final Evolution: {evo['emoji']} {evo['name']}")
        print()
        
        return self.results
    
    def _run_sequential(self):
        """Run analysis sequentially (Single Thread Mode)"""
        print(f"🔄 Running SEQUENTIAL analysis ({len(self.configs)} universes)...")
        print(f"   Mode: LOW CPU (1 process, < 85% target)")
        print(f"   RAM: Can use up to 50GB")
        print("─" * 60)
        
        # Import psutil for monitoring
        try:
            import psutil
            has_psutil = True
        except ImportError:
            has_psutil = False
            print("⚠️  psutil not available - CPU/RAM monitoring disabled")
        
        for i, config in enumerate(self.configs, 1):
            universe_name = config['name']
            print(f"\n🌌 [{i}/{len(self.configs)}] Processing {universe_name}...", flush=True)
            
            # Check if universe already exists
            if self._universe_exists(universe_name):
                print(f"   ✅ {universe_name} already exists, loading from cache...", flush=True)
                
                # Load metadata for tracking
                metadata = self._load_universe_metadata(universe_name)
                if metadata:
                    # Track the cached universe
                    self.universes_processed += 1
                    total_patterns = metadata.get("total_patterns", 0)
                    self.total_patterns += total_patterns
                    
                    print(f"   💾 Loaded from cache: {total_patterns:,} patterns "
                          f"(saved {metadata.get('processing_time', 0):.1f}s)", flush=True)
                    
                    # Store minimal result reference for later use
                    self.results[universe_name] = {
                        "cached": True,
                        "name": universe_name,
                        "total_patterns": total_patterns,
                        "config": metadata.get("config", {}),
                        "metadata": metadata.get("metadata", {})
                    }
                else:
                    print(f"   ⚠️ Cache exists but metadata unavailable, continuing...", flush=True)
                
                continue
            
            # Universe doesn't exist, process it
            result = process_universe(
                self.df,
                config["interval"],
                config["lookback"],
                universe_name
            )
            
            if result:
                self.results[config["name"]] = result
                self.universes_processed += 1
                self.total_patterns += result["total_patterns"]
                
                # Get CPU and RAM stats
                if has_psutil:
                    cpu = psutil.cpu_percent(interval=0.5)
                    mem_gb = psutil.virtual_memory().used / 1e9
                    print(f"   ✅ {result['total_patterns']:,} patterns found "
                          f"({result['processing_time']:.1f}s) | "
                          f"CPU: {cpu:.1f}% | RAM: {mem_gb:.1f}GB", flush=True)
                else:
                    print(f"   ✅ {result['total_patterns']:,} patterns found "
                          f"({result['processing_time']:.1f}s)", flush=True)
            else:
                print(f"   ⚠️ No results for {config['name']}", flush=True)
            
            self.evolve()
            
            # Checkpoint every 5 universes or on the last one
            if i % 5 == 0 or i == len(self.configs):
                progress = i / len(self.configs) * 100
                
                # Send Telegram notification
                if self.lore_system:
                    try:
                        from lore import EventType
                        self.lore_system.broadcast(
                            EventType.UNIVERSE_PROGRESS,
                            percentage=f"{progress:.0f}",
                            completed=i,
                            total=len(self.configs),
                            total_patterns=f"{self.total_patterns:,}",
                            current_evolution=self.evolution_stage,
                            power=f"{self.light_power:.1f}"
                        )
                    except Exception as e:
                        # Don't crash if notification fails
                        pass
                
                self._save_checkpoint(i)
                
                # Cleanup if RAM > MAX_MEMORY_GB
                if has_psutil:
                    mem_gb = psutil.virtual_memory().used / 1e9
                    if mem_gb > MAX_MEMORY_GB:
                        print(f"\n   💾 RAM usage high ({mem_gb:.1f}GB), running cleanup...", flush=True)
                        gc.collect()
                        mem_after = psutil.virtual_memory().used / 1e9
                        print(f"   💾 RAM after cleanup: {mem_after:.1f}GB\n", flush=True)
                    else:
                        gc.collect()
    
    def _run_parallel(self):
        """Run analysis in parallel (Photon Burst Mode)"""
        print(f"⚡ Running parallel analysis ({len(self.configs)} universes, {NUM_WORKERS} workers)...")
        print("─" * 60)
        
        # First, check for existing universes
        configs_to_process = []
        skipped_count = 0
        
        for config in self.configs:
            universe_name = config["name"]
            
            if self._universe_exists(universe_name):
                print(f"   ✅ {universe_name} already exists, loading from cache...")
                
                # Load metadata for tracking
                metadata = self._load_universe_metadata(universe_name)
                if metadata:
                    self.universes_processed += 1
                    total_patterns = metadata.get("total_patterns", 0)
                    self.total_patterns += total_patterns
                    
                    print(f"   💾 Loaded from cache: {total_patterns:,} patterns "
                          f"(saved {metadata.get('processing_time', 0):.1f}s)")
                    
                    # Store minimal result reference
                    self.results[universe_name] = {
                        "cached": True,
                        "name": universe_name,
                        "total_patterns": total_patterns,
                        "config": metadata.get("config", {}),
                        "metadata": metadata.get("metadata", {})
                    }
                    skipped_count += 1
            else:
                configs_to_process.append(config)
        
        if skipped_count > 0:
            print(f"\n   💾 Skipped {skipped_count} existing universes from cache")
            print(f"   🔄 Processing {len(configs_to_process)} new universes\n")
        
        if not configs_to_process:
            print("\n   ✅ All universes already exist in cache!")
            return
        
        # Prepare arguments for universes that need processing
        args_list = [
            (self.df, config["interval"], config["lookback"], config["name"])
            for config in configs_to_process
        ]
        
        completed = 0
        
        # Use ProcessPoolExecutor for parallel processing
        with ProcessPoolExecutor(max_workers=NUM_WORKERS) as executor:
            # Submit all tasks
            future_to_config = {
                executor.submit(process_universe_wrapper, args): args[3]
                for args in args_list
            }
            
            # Process completed tasks
            for future in as_completed(future_to_config):
                universe_name = future_to_config[future]
                completed += 1
                
                try:
                    result = future. result()
                    
                    if result:
                        self.results[universe_name] = result
                        self.universes_processed += 1
                        self.total_patterns += result["total_patterns"]
                        
                        print(f"   ✅ [{completed}/{len(configs_to_process)}] {universe_name}:  "
                              f"{result['total_patterns']} patterns ({result['processing_time']:.1f}s)")
                    else:
                        print(f"   ⚠️ [{completed}/{len(configs_to_process)}] {universe_name}: No results")
                    
                except Exception as e: 
                    print(f"   ❌ [{completed}/{len(configs_to_process)}] {universe_name}: Error - {e}")
                
                self.evolve()
                
                # Progress update and checkpoint
                if completed % 5 == 0 or completed == len(self.configs):
                    progress = completed / len(self.configs) * 100
                    print(f"\n   📊 Progress: {progress:.1f}% | "
                          f"Evolution: {self.evolution_stage} | "
                          f"Power: {self.light_power:.1f}%\n")
                    
                    # Send Telegram notification
                    if self.lore_system:
                        try:
                            from lore import EventType
                            self.lore_system.broadcast(
                                EventType.UNIVERSE_PROGRESS,
                                percentage=f"{progress:.0f}",
                                completed=completed,
                                total=len(self.configs),
                                total_patterns=f"{self.total_patterns:,}",
                                current_evolution=self.evolution_stage,
                                power=f"{self.light_power:.1f}"
                            )
                        except Exception as e:
                            # Don't crash if notification fails
                            pass
                    
                    self._save_checkpoint(completed)
                    gc.collect()
    
    def _save_checkpoint(self, step):
        """Save checkpoint (Dimensional Anchor)"""
        checkpoint_file = self.output_dirs["checkpoints"] / f"checkpoint_{step}.json"
        
        checkpoint_data = {
            "step": step,
            "universes_processed": self.universes_processed,
            "total_patterns": self.total_patterns,
            "evolution_stage": self. evolution_stage,
            "light_power": self.light_power,
            "prismatic_cores": self.prismatic_cores,
            "elapsed_time": time.time() - self.start_time,
            "completed_universes": list(self.results.keys())
        }
        
        with open(checkpoint_file, "w") as f:
            json.dump(checkpoint_data, f, indent=2, default=str)
    
    def get_rankings(self):
        """
        Get universe rankings (Arceus Judgment)
        Technical: Rank configurations by pattern count and quality
        
        Returns:
            list:  Ranked universes
        """
        rankings = []
        
        for name, result in self.results.items():
            if not result:
                continue
            
            # Calculate score
            total_patterns = result["total_patterns"]
            
            # Count high-confidence patterns
            high_conf_patterns = 0
            total_features = 0
            
            for level in result["results"]:
                for direction in result["results"][level]: 
                    level_data = result["results"][level][direction]
                    total_features += len(level_data. get("all_features", []))
                    
                    # Count patterns with multiple occurrences
                    for pattern, data in level_data. get("patterns", {}).items():
                        if data["count"] >= 3:
                            high_conf_patterns += 1
            
            # Calculate DFA mean if available
            dfa_mean = 0.5
            for level in result["results"]:
                for direction in result["results"][level]:
                    stats = result["results"][level][direction]. get("feature_stats", {})
                    if "dfa_alpha_mean" in stats:
                        dfa_mean = stats["dfa_alpha_mean"]
                        break
            
            # Score calculation
            score = (
                total_patterns * 1.0 +
                high_conf_patterns * 10.0 +
                (1 - abs(dfa_mean - 0.6)) * 50  # Optimal DFA around 0.6
            )
            
            rankings.append({
                "name": name,
                "interval": result["config"]["interval"],
                "lookback": result["config"]["lookback"],
                "total_patterns":  total_patterns,
                "high_conf_patterns": high_conf_patterns,
                "dfa_mean": dfa_mean,
                "score": score,
                "processing_time": result["processing_time"]
            })
        
        # Sort by score
        rankings.sort(key=lambda x: x["score"], reverse=True)
        
        return rankings
    
    def get_pattern_summary(self):
        """
        Get pattern summary across all universes (Crystal Formation Report)
        Technical: Aggregate patterns by level and direction
        
        Returns: 
            dict: Pattern summary
        """
        summary = {
            level: {direction: {
                "total_occurrences": 0,
                "unique_patterns": 0,
                "top_patterns": [],
                "feature_stats": {}
            } for direction in DIRECTIONS}
            for level in MOVEMENT_LEVELS. keys()
        }
        
        # Aggregate across universes
        for name, result in self.results.items():
            if not result:
                continue
            
            for level in result["results"]: 
                for direction in result["results"][level]:
                    level_data = result["results"][level][direction]
                    
                    summary[level][direction]["total_occurrences"] += level_data["total_occurrences"]
                    summary[level][direction]["unique_patterns"] += len(level_data.get("patterns", {}))
        
        return summary
    
    def save_results(self):
        """
        Save all results to files (Crystal Preservation)
        Technical: Serialize results to Parquet (preferred) or JSON (backward compatible)
        """
        from config import STORAGE_CONFIG
        
        print("\n💾 Saving results...")
        
        storage_format = STORAGE_CONFIG.get("format", "json")
        use_parquet = (storage_format == "parquet")
        
        # Save each universe
        for name, result in self.results.items():
            if result:
                # Simplify for serialization
                result_simplified = self._simplify_result(result)
                
                if use_parquet:
                    # Save as Parquet
                    self._save_universe_parquet(name, result_simplified)
                else:
                    # Save as JSON (legacy)
                    universe_file = self.output_dirs["universes"] / f"{name}.json"
                    with open(universe_file, "w") as f:
                        json.dump(result_simplified, f, indent=2, default=str)
        
        print(f"   ✅ Saved {len(self.results)} universe files ({storage_format})")
        
        # Save rankings
        rankings = self.get_rankings()
        rankings_file = self.output_dirs["reports"] / "rankings.json"
        with open(rankings_file, "w") as f:
            json.dump(rankings, f, indent=2, default=str)
        
        print(f"   ✅ Saved rankings")
        
        # Save summary
        summary = self.get_pattern_summary()
        summary_file = self.output_dirs["reports"] / "pattern_summary.json"
        with open(summary_file, "w") as f:
            json.dump(summary, f, indent=2, default=str)
        
        print(f"   ✅ Saved pattern summary")
        
        return {
            "universes_saved": len(self.results),
            "rankings_file": str(rankings_file),
            "summary_file": str(summary_file)
        }
    
    def _save_universe_parquet(self, name: str, result_simplified: dict):
        """
        Save universe result as Parquet with metadata sidecar
        
        Args:
            name: Universe name
            result_simplified: Simplified result dictionary
        """
        from config import STORAGE_CONFIG
        
        # Convert results to DataFrame
        rows = []
        for level in result_simplified["results"]:
            for direction in result_simplified["results"][level]:
                level_data = result_simplified["results"][level][direction]
                
                # Get feature_stats
                feature_stats = level_data.get("feature_stats", {})
                
                # Create row
                row = {
                    'level': level,
                    'direction': direction,
                }
                
                # Add all feature stats
                for key, value in feature_stats.items():
                    if isinstance(value, (int, float, str, bool)):
                        row[key] = value
                
                # Add pattern_count if available
                if 'pattern_count' in level_data:
                    row['pattern_count'] = level_data['pattern_count']
                
                rows.append(row)
        
        if rows:
            df = pd.DataFrame(rows)
            
            # Save as Parquet
            compression = STORAGE_CONFIG.get("compression", "snappy")
            parquet_file = self.output_dirs["universes"] / f"{name}.parquet"
            df.to_parquet(parquet_file, compression=compression, index=False)
            
            # Save metadata separately if enabled
            if STORAGE_CONFIG.get("enable_metadata_sidecar", True):
                metadata = {
                    "name": result_simplified.get("name", ""),
                    "config": result_simplified.get("config", {}),
                    "processing_time": result_simplified.get("processing_time", 0),
                    "total_patterns": result_simplified.get("total_patterns", 0),
                    "metadata": result_simplified.get("metadata", {})
                }
                metadata_file = self.output_dirs["universes"] / f"{name}_metadata.json"
                with open(metadata_file, "w") as f:
                    json.dump(metadata, f, indent=2, default=str)
    
    def _simplify_result(self, result):
        """Simplify result for JSON serialization"""
        simplified = {
            "name": result["name"],
            "config": result["config"],
            "processing_time": result["processing_time"],
            "total_patterns":  result["total_patterns"],
            "results": {},
            "ohlc_data":  result.get("ohlc_data", []),
            "metadata": result.get("metadata", {}),
        }
        
        for level in result["results"]: 
            simplified["results"][level] = {}
            
            for direction in result["results"][level]:
                level_data = result["results"][level][direction]
                
                # Get top patterns
                patterns = level_data.get("patterns", {})
                top_patterns = sorted(
                    patterns.items(),
                    key=lambda x: x[1]["count"],
                    reverse=True
                )[:TOP_PATTERNS_PER_LEVEL]
                
                simplified["results"][level][direction] = {
                    "total_occurrences": level_data["total_occurrences"],
                    "unique_patterns": len(patterns),
                    "top_patterns": [
                        {"signature": sig, "count": data["count"]}
                        for sig, data in top_patterns
                    ],
                    "feature_stats": level_data.get("feature_stats", {})
                }
        
        return simplified


# ═══════════════════════════════════════════════════════════════
# 🎮 TEST
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║         ⚡ ULTRA NECROZMA ANALYZER TEST ⚡                   ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    # Generate test data
    print("📊 Generating test data...")
    np.random.seed(42)
    
    n_ticks = 100000  # 100k ticks for testing
    timestamps = pd.date_range("2025-01-01", periods=n_ticks, freq="1s")
    prices = 1.10 + np.cumsum(np.random.randn(n_ticks) * 0.00005)
    
    df = pd.DataFrame({
        "timestamp": timestamps,
        "bid": prices - 0.00005,
        "ask": prices + 0.00005,
        "mid_price": prices,
        "spread_pips": 1.0,
        "pips_change": np.concatenate([[0], np.diff(prices) * 10000])
    })
    
    print(f"   ✅ Generated {len(df):,} ticks")
    print()
    
    # Test single universe
    print("🌌 Testing single universe processing...")
    print("─" * 50)
    
    result = process_universe(df, interval=5, lookback=10, universe_name="test_5m_10lb")
    
    if result: 
        print(f"   ✅ Universe created: {result['name']}")
        print(f"   📊 Total patterns: {result['total_patterns']}")
        print(f"   ⏱️  Time: {result['processing_time']:.2f}s")
        
        # Show level breakdown
        print(f"\n   Level breakdown:")
        for level in result["results"]:
            for direction in result["results"][level]: 
                count = result["results"][level][direction]["total_occurrences"]
                if count > 0:
                    print(f"      {level}/{direction}: {count}")
    
    print()
    print("✅ Analyzer test complete!")