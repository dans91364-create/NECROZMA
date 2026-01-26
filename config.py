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
from datetime import datetime


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


# ═══════════════════════════════════════════════════════════════
# 🎯 PAIR PREFIX CONFIGURATION (File Identification)
# ═══════════════════════════════════════════════════════════════

def get_pair_info():
    """
    Extract pair name and year from PARQUET_FILE path
    
    Technical: Automatically derives pair and year from the parquet filename
    to prefix all output files and prevent overwriting when running multiple pairs.
    
    Returns:
        tuple: (pair_name, data_year)
        
    Example:
        PARQUET_FILE = "data/EURUSD_2025.parquet"
        Returns: ("EURUSD", "2025")
    """
    filename = PARQUET_FILE.stem  # e.g., "EURUSD_2025"
    parts = filename.split("_")
    
    # Extract pair (first part) and year (second part if exists)
    pair = parts[0] if parts else "UNKNOWN"
    year = parts[1] if len(parts) > 1 else str(datetime.now().year)
    
    return pair, year


# Extract pair name and year from PARQUET_FILE
PAIR_NAME, DATA_YEAR = get_pair_info()

# File prefix for all outputs: "EURUSD_2025_"
# This prevents overwriting when running multiple pairs
FILE_PREFIX = f"{PAIR_NAME}_{DATA_YEAR}_"


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
# NOTE: Set to 1 for sequential processing (low CPU mode)
NUM_WORKERS = _processing_config.get("num_workers", 1)  # Sequential mode by default

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
# NOTE: Increased to 50GB for sequential processing (can use more RAM)
MEMORY_WARNING_GB = _limits_config.get("memory_warning_gb", 50)

# Maximum memory usage in GB (soft limit for cleanup triggers)
MAX_MEMORY_GB = _limits_config.get("max_memory_gb", 50)

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
# 📱 TELEGRAM CONFIGURATION (Divine Messages)
# ═══════════════════════════════════════════════════════════════

# Telegram bot configuration
# Set via environment variables or telegram_config.json:
#   TELEGRAM_BOT_TOKEN - Your bot token from @BotFather
#   TELEGRAM_CHAT_ID - Your chat/channel ID
TELEGRAM_ENABLED = True  # Master switch for notifications
LORE_ENABLED = True      # Use deity personalities in messages


# ═══════════════════════════════════════════════════════════════
# 🏷️ LABELING CONFIGURATION (Outcome Targets)
# ═══════════════════════════════════════════════════════════════

# Target levels in pips (Profit Targets)
TARGET_PIPS = [5, 10, 15, 20, 30, 50]

# Stop loss levels in pips (Risk Limits)
STOP_PIPS = [5, 10, 15, 20, 30]

# Time horizons in minutes (Temporal Windows)
TIME_HORIZONS = [1, 5, 15, 30, 60, 240, 1440]  # 1m to 1d

# Metrics to calculate
LABELING_METRICS = {
    "direction": True,        # Direction of movement
    "magnitude": True,        # Size of movement
    "time_to_target": True,   # Time to reach target
    "time_to_stop": True,     # Time to hit stop
    "mfe": True,              # Maximum Favorable Excursion
    "mae": True,              # Maximum Adverse Excursion
    "r_multiple": True,       # Risk/Reward multiple
}


# ═══════════════════════════════════════════════════════════════
# 🤖 MACHINE LEARNING CONFIGURATION (Pattern Discovery)
# ═══════════════════════════════════════════════════════════════

# Regime detection
REGIME_CONFIG = {
    "methods": ["kmeans", "hdbscan"],  # Clustering methods to try
    "n_clusters_range": [2, 3, 4, 5, 6],  # Range for k-means
    "min_cluster_size": 100,  # Base minimum cluster size for HDBSCAN (auto-scaled dynamically based on dataset size)
    "min_cluster_size_absolute": 10000,  # Absolute minimum cluster size threshold (prevents over-segmentation)
    "min_cluster_size_pct": 0.01,  # Minimum cluster size as percentage of dataset (1%)
}

# Feature importance
FEATURE_IMPORTANCE_CONFIG = {
    "methods": ["xgboost", "lightgbm", "permutation"],
    "n_estimators": 100,
    "max_depth": 6,
    "learning_rate": 0.1,
}

# Association rules
ASSOCIATION_CONFIG = {
    "min_support": 0.01,     # Minimum support (1%)
    "min_confidence": 0.5,   # Minimum confidence (50%)
    "max_len": 3,            # Maximum rule length
}

# SHAP values
SHAP_CONFIG = {
    "enabled": True,
    "max_samples": 1000,     # Max samples for SHAP calculation
}


# ═══════════════════════════════════════════════════════════════
# 🎯 BACKTESTING CONFIGURATION (Strategy Validation)
# ═══════════════════════════════════════════════════════════════

# Walk-forward validation
BACKTEST_CONFIG = {
    "train_size": 0.6,           # 60% training
    "validation_size": 0.2,      # 20% validation
    "test_size": 0.2,            # 20% testing
    "n_splits": 5,               # Number of walk-forward splits
    "min_trades": 30,            # Minimum trades for valid strategy
}

# Monte Carlo simulation
MONTE_CARLO_CONFIG = {
    "enabled": True,
    "n_simulations": 1000,
    "confidence_level": 0.95,
}

# Performance metrics thresholds
METRIC_THRESHOLDS = {
    "min_sharpe": 1.0,
    "min_profit_factor": 1.2,
    "max_drawdown": 0.25,        # 25%
    "min_win_rate": 0.45,        # 45%
    "min_trades": 30,
}


# ═══════════════════════════════════════════════════════════════
# 🏭 STRATEGY FACTORY CONFIGURATION (Strategy Generation)
# ═══════════════════════════════════════════════════════════════

# Strategy templates to generate
STRATEGY_TEMPLATES = [
    'TrendFollower',
    'MeanReverter', 
    'MeanReverterV2',
    'MeanReverterV3',
    'MomentumBurst',
]

# Parameter ranges for strategy generation (Round 3: ~1000 combinations focused on FREQUENCY)
STRATEGY_PARAMS = {
    # ═══════════════════════════════════════════════════════════════
    # CAMADA 1: MeanReverter - Base sólida (poucos trades, alto Sharpe)
    # Mantido do Round 2 - funciona bem, não mexer muito
    # ═══════════════════════════════════════════════════════════════
    'MeanReverter': {
        'lookback_periods': [5],  # L=5 é o único que funciona
        'threshold_std': [1.5, 1.8, 2.0],
        'stop_loss_pips': [20, 30],
        'take_profit_pips': [40, 50],
    },
    # Total: 1 × 3 × 2 × 2 = 12 combinações
    
    # ═══════════════════════════════════════════════════════════════
    # CAMADA 2: MeanReverterV2 - Frequência média (10-20 trades/dia)
    # Foco: Sharpe > 0.8, mais trades que MeanReverter
    # ═══════════════════════════════════════════════════════════════
    'MeanReverterV2': {
        'lookback_periods': [20, 30],
        'threshold_std': [0.8, 1.0, 1.2, 1.5],  # Mais sensível!
        'stop_loss_pips': [15, 20, 25],
        'take_profit_pips': [30, 40, 50],
        'rsi_oversold': [30, 35],
        'rsi_overbought': [75, 80],
        'volume_filter': [1.5, 2.0],
    },
    # Total: 2 × 4 × 3 × 3 × 2 × 2 × 2 = 576 combinações
    
    # ═══════════════════════════════════════════════════════════════
    # CAMADA 2.5: MeanReverterV3 - Optimized from Round 3 results
    # Fixed lookback=5, adaptive threshold, optimal R:R ratio
    # Best performance: Sharpe 6.29, Return 59%, Win Rate 51.2%
    # ═══════════════════════════════════════════════════════════════
    'MeanReverterV3': {
        'threshold_std': [1.8, 2.0, 2.2],  # Narrow range around optimal
        'adaptive_threshold': [True, False],
        'stop_loss_pips': [25, 30, 35],
        'take_profit_pips': [45, 50, 55],
        'require_confirmation': [True, False],
        'use_session_filter': [True, False],
    },
    # Total: 3 × 2 × 3 × 3 × 2 × 2 = 216 combinations
    
    # ═══════════════════════════════════════════════════════════════
    # CAMADA 3: MomentumBurst - Alta frequência (30-60 trades/dia)
    # Foco: Volume de trades, Sharpe > 0.3
    # MUDANÇA PRINCIPAL: Cooldowns mais baixos! (CD30 removed - too many trades)
    # ═══════════════════════════════════════════════════════════════
    'MomentumBurst': {
        'lookback_periods': [5, 10, 15],
        'threshold_std': [0.5, 0.8, 1.0, 1.2, 1.5],  # Mais sensível!
        'stop_loss_pips': [10, 15, 20],
        'take_profit_pips': [20, 30, 40],
        'cooldown_minutes': [60, 90, 120, 180],  # Removed CD30 - causes overtrading even with max_trades_per_day fix
    },
    # Total: 3 × 5 × 3 × 3 × 4 = 540 combinações (reduced from 675 after removing CD30)
    
    # ═══════════════════════════════════════════════════════════════
    # CAMADA 4: TrendFollower - Capturar tendências (10-20 trades/dia)
    # Foco: Movimentos maiores, complementa reversão
    # ═══════════════════════════════════════════════════════════════
    'TrendFollower': {
        'lookback_periods': [10, 20, 30],
        'threshold_std': [0.5, 0.8, 1.0, 1.5],  # Mais sensível!
        'stop_loss_pips': [20, 30, 40],
        'take_profit_pips': [40, 60, 80],
    },
    # Total: 3 × 4 × 3 × 3 = 108 combinações
    
    # TOTAL ROUND 3+: 12 + 576 + 216 + 675 + 108 = 1587 combinations
}


# ═══════════════════════════════════════════════════════════════
# 🔗 CORRELATION CONFIGURATION (Multi-Pair Analysis)
# ═══════════════════════════════════════════════════════════════

CORRELATION_CONFIG = {
    "pairs": [
        "EURUSD", "GBPUSD", "USDJPY", "USDCHF", "AUDUSD",
        "USDCAD", "EURGBP", "GBPJPY", "EURJPY", "AUDJPY"
    ],
    "rolling_windows": [20, 50, 100],
    "divergence_threshold": 2.0,
    "min_correlation": 0.7,
}


# ═══════════════════════════════════════════════════════════════
# 📊 TRADE ANALYSIS CONFIGURATION
# ═══════════════════════════════════════════════════════════════

TRADE_ANALYSIS_CONFIG = {
    "top_n_for_detailed": 10,  # Trade log and Monte Carlo only for top 10
    "monte_carlo_simulations": 1000,
    "sessions": {
        "london": {"start": 8, "end": 16},
        "new_york": {"start": 13, "end": 21},
        "tokyo": {"start": 0, "end": 8},
    }
}


# ═══════════════════════════════════════════════════════════════
# 🌟 RANKING CONFIGURATION (Light Finder)
# ═══════════════════════════════════════════════════════════════

# Multi-objective weights
RANKING_WEIGHTS = {
    "return": 0.30,          # 30% weight on returns
    "risk": 0.25,            # 25% weight on risk metrics
    "consistency": 0.25,     # 25% weight on consistency
    "robustness": 0.20,      # 20% weight on robustness
}

# Top strategies to report
TOP_N_STRATEGIES = 300

# Overfitting detection
OVERFITTING_CONFIG = {
    "max_is_oos_ratio": 2.0,     # Max in-sample / out-of-sample ratio
    "min_stability_score": 0.7,   # Min parameter stability score
}


# ═══════════════════════════════════════════════════════════════
# 🧪 TEST MODE CONFIGURATION
# ═══════════════════════════════════════════════════════════════

# Test Mode Configuration
TEST_MODE_CONFIG = {
    'strategies': {
        'minimal': {
            'weeks': 1,
            'method': 'random',
            'estimated_time_minutes': 10,
            'description': 'Smoke test - just check if it runs'
        },
        'quick': {
            'weeks': 2,
            'method': 'random',
            'estimated_time_minutes': 20,
            'description': 'Quick validation'
        },
        'balanced': {
            'weeks': 4,
            'method': 'stratified',  # 1 week per quarter
            'estimated_time_minutes': 45,
            'description': 'Balanced test with all quarters represented'
        },
        'thorough': {
            'weeks': 8,
            'method': 'diverse',  # Mix of volatility regimes
            'estimated_time_minutes': 90,
            'description': 'Thorough test before full analysis'
        }
    },
    'avoid_holidays': True,
    'default_seed': 42,
    'min_ticks_per_week': 100_000,  # Minimum ticks to consider valid week
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


# ═══════════════════════════════════════════════════════════════
# 💾 STORAGE CONFIGURATION (Parquet Migration)
# ═══════════════════════════════════════════════════════════════

# Storage format configuration
STORAGE_CONFIG = {
    "format": "parquet",           # "parquet" or "json" - default format for new files
    "compression": "snappy",        # "snappy", "gzip", "brotli" - compression algorithm
    "partition_by": None,           # Can partition by "pair", "date", etc. (None = no partitioning)
    "enable_metadata_sidecar": True,  # Save metadata in separate JSON file alongside Parquet
    "auto_detect_format": True,     # Automatically detect and load from available format (Parquet preferred)
}


# ═══════════════════════════════════════════════════════════════
# ⚡ MULTI-WORKER CONFIGURATION (Parallel Processing)
# ═══════════════════════════════════════════════════════════════

# Multi-worker processing configuration
WORKER_CONFIG = {
    "default_workers": 1,           # Default number of workers (1 = sequential)
    "max_workers": 16,              # Maximum allowed workers
    "cpu_limit": 80,                # Maximum CPU usage percentage (adaptive throttling)
    "cooldown_seconds": 5,          # Pause between batches (seconds)
    "nice_priority": False,         # Run with low priority (nice)
    "adaptive_throttling": True,    # Dynamically adjust workers based on CPU
    "cpu_check_interval": 5,        # Check CPU every N completed tasks
}


# ═══════════════════════════════════════════════════════════════
# 📊 MIGRATION CONFIGURATION
# ═══════════════════════════════════════════════════════════════

# Migration settings for JSON to Parquet conversion
MIGRATION_CONFIG = {
    "auto_migrate": False,          # Automatically migrate JSON to Parquet on load
    "delete_json_after_migration": False,  # Delete JSON files after successful migration
    "backup_before_delete": True,   # Create backup before deleting JSON files
}


# ═══════════════════════════════════════════════════════════════
# 💾 CACHE CONFIGURATION (Performance Optimization)
# ═══════════════════════════════════════════════════════════════

# Cache and resume configuration
CACHE_CONFIG = {
    "enabled": True,                    # Master switch for caching
    "skip_existing_universes": True,    # Skip universes that already exist
    "cache_labeling": True,             # Cache labeling results
    "cache_regimes": True,              # Cache regime detection (future)
    "checkpoint_interval": 10,          # Save progress every N items
    "cache_dir": OUTPUT_DIR / "cache",  # Cache directory path
}