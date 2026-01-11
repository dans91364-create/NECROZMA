#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚡🌟💎 ULTRA NECROZMA - CONFIGURATION CENTER 💎🌟⚡

Central de Configurações do Sistema
"The Prism that refracts all parameters into light"

Technical:  System Configuration Module
Enhanced with YAML support for PR #2
"""

from pathlib import Path
import yaml
import os


# ═══════════════════════════════════════════════════════════════
# 🔧 YAML CONFIGURATION LOADING (PR #2)
# ═══════════════════════════════════════════════════════════════

def load_yaml_config(config_path="config.yaml"):
    """
    Load configuration from YAML file
    
    Args:
        config_path: Path to config YAML file
        
    Returns:
        dict: Configuration dictionary
    """
    config_file = Path(config_path)
    
    if not config_file.exists():
        print(f"⚠️ Config file not found: {config_path}, using defaults")
        return {}
    
    try:
        with open(config_file, 'r') as f:
            config = yaml.safe_load(f)
        print(f"✅ Loaded configuration from {config_path}")
        return config
    except Exception as e:
        print(f"⚠️ Failed to load config: {e}, using defaults")
        return {}


# Load YAML config if available
_yaml_config = load_yaml_config()


# ═══════════════════════════════════════════════════════════════
# 🌟 PATH CONFIGURATION (Dimensional Gates)
# ═══════════════════════════════════════════════════════════════

# Load from YAML or use defaults
_paths = _yaml_config.get("paths", {})

# Input:  Raw tick data / Entrada de dados brutos
CSV_FILE = Path(_paths.get("csv_file", "/home/usuario/EURUSD_2025_COMPLETO.csv"))

# Parquet:  Crystallized data / Dados cristalizados
PARQUET_FILE = Path(_paths.get("parquet_file", "data/EURUSD_2025.parquet"))

# Output: Analysis results / Resultados das análises
OUTPUT_DIR = Path(_paths.get("output_dir", "ultra_necrozma_results"))

# Cache directory (PR #2)
CACHE_DIR = Path(_paths.get("cache_dir", "joblib_cache"))

# Log directory (PR #2)
LOG_DIR = Path(_paths.get("log_dir", "logs"))

# ═══════════════════════════════════════════════════════════════
# 💎 DATA CONFIGURATION (Crystal Structure)
# ═══════════════════════════════════════════════════════════════

_data_config = _yaml_config.get("data", {})

# CSV columns mapping / Mapeamento de colunas CSV
CSV_COLUMNS = {
    "timestamp": "Timestamp",
    "bid": "Bid",
    "ask": "Ask",
    "symbol": "Symbol",
    "source": "Exness"
}

# Parquet compression / Compressão do Parquet
PARQUET_COMPRESSION = _data_config.get("parquet_compression", "snappy")

# CSV chunk size
CSV_CHUNK_SIZE = _data_config.get("csv_chunk_size", 500_000)

# Minimum samples
MIN_SAMPLES = _data_config.get("min_samples", 30)

# ═══════════════════════════════════════════════════════════════
# ⚡ ANALYSIS CONFIGURATION (Z-Crystal Parameters)
# ═══════════════════════════════════════════════════════════════

_analysis_config = _yaml_config.get("analysis", {})

# Time intervals in minutes (Temporal Dimensions)
# Technical: Resampling intervals for OHLC aggregation
INTERVALS = _analysis_config.get("intervals", [1, 5, 15, 30, 60])

# Lookback periods (Dimensional Depth)
# Technical: Number of candles to analyze for patterns
LOOKBACKS = _analysis_config.get("lookbacks", [5, 10, 15, 20, 30])

# Movement levels in pips (Energy Thresholds)
# Technical: Price movement classification thresholds
_movement_levels_config = _analysis_config.get("movement_levels", {})
MOVEMENT_LEVELS = {}

# Build MOVEMENT_LEVELS from YAML or use defaults
if _movement_levels_config:
    for level_name, level_data in _movement_levels_config.items():
        MOVEMENT_LEVELS[level_name] = {
            "min": level_data.get("min", 1),
            "max": level_data.get("max", float("inf")),
            "technical": level_data.get("technical", "")
        }
else:
    MOVEMENT_LEVELS = {
        "Pequeno": {"min": 1, "max": 5, "technical": "Small (1-5 pips)"},
        "Médio": {"min": 5, "max": 15, "technical": "Medium (5-15 pips)"},
        "Grande": {"min": 15, "max": 30, "technical": "Large (15-30 pips)"},
        "Muito Grande": {"min":  30, "max": float("inf"), "technical": "Very Large (30+ pips)"}
    }

# Directions (Light Polarization)
DIRECTIONS = _analysis_config.get("directions", ["up", "down"])

# ═══════════════════════════════════════════════════════════════
# 🔥 PROCESSING CONFIGURATION (Photon Burst Settings)
# ═══════════════════════════════════════════════════════════════

_processing_config = _yaml_config.get("processing", {})

# Parallel workers (Light Clones)
# Technical: Number of parallel processes for multiprocessing
NUM_WORKERS = _processing_config.get("num_workers", 16)  # Ryzen 9: 16 cores available

# Caching enabled (PR #2)
ENABLE_CACHING = _processing_config.get("enable_caching", True)

# Checkpointing enabled (PR #2)
ENABLE_CHECKPOINTING = _processing_config.get("enable_checkpointing", True)

# Checkpoint interval
CHECKPOINT_INTERVAL = _processing_config.get("checkpoint_interval", 5)

# ═══════════════════════════════════════════════════════════════
# 🌌 FEATURE GROUPS (Prismatic Cores)
# ═══════════════════════════════════════════════════════════════

_features_config = _yaml_config.get("features", {})

# Enable/disable feature groups
# Technical: Feature extraction module toggles
FEATURE_GROUPS = {
    "derivatives": _features_config.get("derivatives", True),      # D1-D5 (Velocity, Acceleration, Jerk...)
    "spectral": _features_config.get("spectral", True),           # FFT, Wavelets (Frequency Domain)
    "chaos": _features_config.get("chaos", True),                 # Lyapunov, Fractal, DFA, Hurst
    "entropy": _features_config.get("entropy", True),             # Shannon, Sample, Approximate, Permutation
    "quantum": _features_config.get("quantum", True),             # Phase Space, Correlation Dimension
    "multifractal": _features_config.get("multifractal", True),   # Multifractal Spectrum (q-moments)
    "recurrence": _features_config.get("recurrence", True),       # RQA (Recurrence Quantification)
    "statistical": _features_config.get("statistical", True),     # Basic statistics
    "patterns": _features_config.get("patterns", True),           # Price patterns (crystals)
    "ultra": _features_config.get("ultra", True),                 # Photon features, Z-Crystal
    # PR #2 New Features
    "dispersion_entropy": _features_config.get("dispersion_entropy", True),
    "bubble_entropy": _features_config.get("bubble_entropy", True),
    "rcmse": _features_config.get("rcmse", True),
    "complexity_entropy": _features_config.get("complexity_entropy", True),
    "wavelet_leaders": _features_config.get("wavelet_leaders", True),
    "information_imbalance": _features_config.get("information_imbalance", False),
    "temporal_features": _features_config.get("temporal_features", True),
    "market_sessions": _features_config.get("market_sessions", True),
}

# ═══════════════════════════════════════════════════════════════
# 📊 OUTPUT CONFIGURATION (Light Crystal Formation)
# ═══════════════════════════════════════════════════════════════

_output_config = _yaml_config.get("output", {})

# Confidence thresholds (Energy Levels)
# Technical: Pattern confidence classification
_thresholds = _output_config.get("confidence_thresholds", {})
CONFIDENCE_THRESHOLDS = {
    "ultra_high": _thresholds.get("ultra_high", 80),   # 💎 Crystal Clear
    "high": _thresholds.get("high", 70),               # 🌟 Strong Signal
    "medium": _thresholds.get("medium", 60),           # ⚡ Moderate Signal
    "low": _thresholds.get("low", 50)                  # ✨ Weak Signal
}

# Top patterns to save per level (Crystal Collection)
TOP_PATTERNS_PER_LEVEL = _output_config.get("top_patterns_per_level", 50)

# ═══════════════════════════════════════════════════════════════
# 🛡️ SYSTEM LIMITS (Arceus Boundaries)
# ═══════════════════════════════════════════════════════════════

_limits_config = _yaml_config.get("limits", {})

# Memory warning threshold in GB
MEMORY_WARNING_GB = _limits_config.get("memory_warning_gb", 80)

# Maximum processing time per universe in seconds
MAX_UNIVERSE_TIME = _limits_config.get("max_universe_time", 600)  # 10 minutes

# ═══════════════════════════════════════════════════════════════
# 🧠 MACHINE LEARNING CONFIGURATION (PR #2)
# ═══════════════════════════════════════════════════════════════

ML_CONFIG = _yaml_config.get("ml", {})

# ═══════════════════════════════════════════════════════════════
# 📈 BACKTEST CONFIGURATION (PR #2)
# ═══════════════════════════════════════════════════════════════

BACKTEST_CONFIG = _yaml_config.get("backtest", {})

# ═══════════════════════════════════════════════════════════════
# 🛡️ RISK MANAGEMENT CONFIGURATION (PR #2)
# ═══════════════════════════════════════════════════════════════

RISK_CONFIG = _yaml_config.get("risk", {})

# ═══════════════════════════════════════════════════════════════
# ⚡ OPTIMIZATION CONFIGURATION (PR #2)
# ═══════════════════════════════════════════════════════════════

OPTIMIZATION_CONFIG = _yaml_config.get("optimization", {})

# ═══════════════════════════════════════════════════════════════
# 🔍 LOGGING CONFIGURATION (PR #2)
# ═══════════════════════════════════════════════════════════════

LOGGING_CONFIG = _yaml_config.get("logging", {})

# ═══════════════════════════════════════════════════════════════
# 🎲 REPRODUCIBILITY CONFIGURATION (PR #2)
# ═══════════════════════════════════════════════════════════════

REPRODUCIBILITY_CONFIG = _yaml_config.get("reproducibility", {})
RANDOM_SEED = REPRODUCIBILITY_CONFIG.get("random_seed", 42)
NUMPY_SEED = REPRODUCIBILITY_CONFIG.get("numpy_seed", 42)

# ═══════════════════════════════════════════════════════════════
# 📊 VISUALIZATION CONFIGURATION (PR #2)
# ═══════════════════════════════════════════════════════════════

VISUALIZATION_CONFIG = _yaml_config.get("visualization", {})

# ═══════════════════════════════════════════════════════════════
# 🎮 POKEMON THEME MAPPING (Ultra Necrozma Lore)
# ═══════════════════════════════════════════════════════════════

THEME = {
    "name": "Ultra Necrozma",
    "title": "The Blinding One",
    "z_move": "Light That Burns The Sky",
    "forms": {
        "loading": "Necrozma (Prism Form)",
        "processing": "Dusk Mane / Dawn Wings",
        "analyzing": "Ultra Burst",
        "complete": "Ultra Necrozma"
    },
    "powers": {
        "dialga": "Temporal Control (Time-based analysis)",
        "palkia": "Spatial Control (Memory optimization)",
        "giratina": "Antimatter (Anomaly detection)",
        "arceus": "Divine Judgment (Final ranking)"
    },
    "crystals": {
        "Red": "Trend Power",
        "Blue": "Stability",
        "Yellow": "Volatility",
        "Green": "Balance",
        "Orange": "Momentum",
        "Violet": "Transcendence",
        "Pink": "Reversal"
    }
}


# ═══════════════════════════════════════════════════════════════
# 🔧 HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════

def get_all_configs():
    """
    Generate all analysis configurations (Dimensional Matrix)
    Technical: Cartesian product of intervals × lookbacks
    
    Returns:
        list:  List of config dictionaries
    """
    configs = []
    for interval in INTERVALS:
        for lookback in LOOKBACKS: 
            configs.append({
                "interval": interval,
                "lookback": lookback,
                "name": f"universe_{interval}m_{lookback}lb",
                "technical": f"Interval={interval}min, Lookback={lookback}periods"
            })
    return configs


def get_output_dirs():
    """
    Create and return output directory structure (Crystal Chambers)
    Technical: Initialize output folder hierarchy
    
    Returns:
        dict:  Paths to output subdirectories
    """
    dirs = {
        "root": OUTPUT_DIR,
        "universes": OUTPUT_DIR / "universes",
        "crystals": OUTPUT_DIR / "crystals", 
        "reports": OUTPUT_DIR / "reports",
        "checkpoints": OUTPUT_DIR / "checkpoints",
        "cache": CACHE_DIR,
        "logs": LOG_DIR
    }
    
    for path in dirs.values():
        path.mkdir(parents=True, exist_ok=True)
    
    return dirs


def set_random_seeds():
    """
    Set random seeds for reproducibility (PR #2)
    """
    import random
    import numpy as np
    
    if RANDOM_SEED is not None:
        random.seed(RANDOM_SEED)
    
    if NUMPY_SEED is not None:
        np.random.seed(NUMPY_SEED)
    
    print(f"🎲 Random seeds set: Python={RANDOM_SEED}, NumPy={NUMPY_SEED}")


# ═══════════════════════════════════════════════════════════════
# 📋 CONFIGURATION SUMMARY
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__": 
    print("""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║      ⚡🌟💎 ULTRA NECROZMA CONFIGURATION 💎🌟⚡              ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    configs = get_all_configs()
    
    print(f"📂 CSV Input:      {CSV_FILE}")
    print(f"💎 Parquet:        {PARQUET_FILE}")
    print(f"📊 Output:        {OUTPUT_DIR}")
    print(f"")
    print(f"⚡ Intervals:     {INTERVALS}")
    print(f"🔮 Lookbacks:     {LOOKBACKS}")
    print(f"🌌 Total Configs: {len(configs)}")
    print(f"")
    print(f"🔥 Workers:       {NUM_WORKERS}")
    print(f"💾 Chunk Size:    {CSV_CHUNK_SIZE: ,}")
    print(f"")
    print(f"🎯 Feature Groups Enabled:")
    for group, enabled in FEATURE_GROUPS.items():
        status = "✅" if enabled else "❌"
        print(f"   {status} {group}")