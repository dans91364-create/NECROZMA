#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚡🌟💎 ULTRA NECROZMA - CONFIGURATION CENTER 💎🌟⚡

Central de Configurações do Sistema
"The Prism that refracts all parameters into light"

Technical:  System Configuration Module
"""

from pathlib import Path

# ═══════════════════════════════════════════════════════════════
# 🌟 PATH CONFIGURATION (Dimensional Gates)
# ═══════════════════════════════════════════════════════════════

# Input:  Raw tick data / Entrada de dados brutos
CSV_FILE = Path("/home/usuario/EURUSD_2025_COMPLETO.csv")

# Parquet:  Crystallized data / Dados cristalizados
PARQUET_FILE = Path("data/EURUSD_2025.parquet")

# Output: Analysis results / Resultados das análises
OUTPUT_DIR = Path("ultra_necrozma_results")

# ═══════════════════════════════════════════════════════════════
# 💎 DATA CONFIGURATION (Crystal Structure)
# ═══════════════════════════════════════════════════════════════

# CSV columns mapping / Mapeamento de colunas CSV
CSV_COLUMNS = {
    "timestamp": "Timestamp",
    "bid": "Bid",
    "ask": "Ask",
    "symbol": "Symbol",
    "source": "Exness"
}

# Parquet compression / Compressão do Parquet
PARQUET_COMPRESSION = "snappy"  # Fast read on HDD

# ═══════════════════════════════════════════════════════════════
# ⚡ ANALYSIS CONFIGURATION (Z-Crystal Parameters)
# ═══════════════════════════════════════════════════════════════

# Time intervals in minutes (Temporal Dimensions)
# Technical: Resampling intervals for OHLC aggregation
INTERVALS = [1, 5, 15, 30, 60]

# Lookback periods (Dimensional Depth)
# Technical: Number of candles to analyze for patterns
LOOKBACKS = [5, 10, 15, 20, 30]

# Movement levels in pips (Energy Thresholds)
# Technical: Price movement classification thresholds
MOVEMENT_LEVELS = {
    "Pequeno": {"min": 1, "max": 5, "technical": "Small (1-5 pips)"},
    "Médio": {"min": 5, "max": 15, "technical": "Medium (5-15 pips)"},
    "Grande": {"min": 15, "max": 30, "technical": "Large (15-30 pips)"},
    "Muito Grande": {"min":  30, "max": float("inf"), "technical": "Very Large (30+ pips)"}
}

# Directions (Light Polarization)
DIRECTIONS = ["up", "down"]

# ═══════════════════════════════════════════════════════════════
# 🔥 PROCESSING CONFIGURATION (Photon Burst Settings)
# ═══════════════════════════════════════════════════════════════

# Parallel workers (Light Clones)
# Technical: Number of parallel processes for multiprocessing
NUM_WORKERS = 16  # Ryzen 9: 16 cores available

# Chunk size for CSV reading (Photon Packets)
# Technical: Rows per chunk during CSV import
CSV_CHUNK_SIZE = 500_000

# Minimum samples for analysis (Critical Mass)
# Technical: Minimum data points required for feature calculation
MIN_SAMPLES = 30

# ═══════════════════════════════════════════════════════════════
# 🌌 FEATURE GROUPS (Prismatic Cores)
# ═══════════════════════════════════════════════════════════════

# Enable/disable feature groups
# Technical: Feature extraction module toggles
FEATURE_GROUPS = {
    "derivatives": True,      # D1-D5 (Velocity, Acceleration, Jerk...)
    "spectral":  True,         # FFT, Wavelets (Frequency Domain)
    "chaos": True,            # Lyapunov, Fractal, DFA, Hurst
    "entropy": True,          # Shannon, Sample, Approximate, Permutation
    "quantum": True,          # Phase Space, Correlation Dimension
    "multifractal": True,     # Multifractal Spectrum (q-moments)
    "recurrence": True,       # RQA (Recurrence Quantification)
    "statistical": True,      # Basic statistics
    "patterns": True,         # Price patterns (crystals)
    "ultra":  True             # Photon features, Z-Crystal
}

# ═══════════════════════════════════════════════════════════════
# 📊 OUTPUT CONFIGURATION (Light Crystal Formation)
# ═══════════════════════════════════════════════════════════════

# Confidence thresholds (Energy Levels)
# Technical: Pattern confidence classification
CONFIDENCE_THRESHOLDS = {
    "ultra_high": 80,   # 💎 Crystal Clear
    "high": 70,         # 🌟 Strong Signal
    "medium": 60,       # ⚡ Moderate Signal
    "low": 50           # ✨ Weak Signal
}

# Top patterns to save per level (Crystal Collection)
TOP_PATTERNS_PER_LEVEL = 50

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
# 🛡️ SYSTEM LIMITS (Arceus Boundaries)
# ═══════════════════════════════════════════════════════════════

# Memory warning threshold in GB
MEMORY_WARNING_GB = 80

# Maximum processing time per universe in seconds
MAX_UNIVERSE_TIME = 600  # 10 minutes

# Checkpoint interval (save progress every N universes)
CHECKPOINT_INTERVAL = 5


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
    "min_cluster_size": 100,  # Minimum cluster size for HDBSCAN
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
    "TrendFollower",
    "MeanReverter",
    "BreakoutTrader",
    "RegimeAdapter",
]

# Parameter ranges for strategy generation
STRATEGY_PARAMS = {
    "lookback_periods": [5, 10, 15, 20, 30],
    "thresholds": [0.5, 1.0, 1.5, 2.0, 2.5, 3.0],
    "stop_loss_pips": [10, 15, 20, 30],
    "take_profit_pips": [20, 30, 40, 50],
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
TOP_N_STRATEGIES = 20

# Overfitting detection
OVERFITTING_CONFIG = {
    "max_is_oos_ratio": 2.0,     # Max in-sample / out-of-sample ratio
    "min_stability_score": 0.7,   # Min parameter stability score
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
        "checkpoints": OUTPUT_DIR / "checkpoints"
    }
    
    for path in dirs.values():
        path.mkdir(parents=True, exist_ok=True)
    
    return dirs


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