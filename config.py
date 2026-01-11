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