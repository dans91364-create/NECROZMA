#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚡🌟💎 ULTRA NECROZMA - OHLC GENERATOR 💎🌟⚡

Converts tick data to OHLC bars for backtesting
"Transform raw ticks into tradable candles"

Features:
- Load tick data from Parquet
- Generate OHLC bars with configurable intervals
- Calculate mid_price, volume, and other metrics
- Data validation and quality checks
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Optional, Dict
import warnings

warnings.filterwarnings("ignore")

from config import PARQUET_FILE
from data_loader import load_crystal, ensure_datetime_column


# ═══════════════════════════════════════════════════════════════
# 🔮 OHLC GENERATION
# ═══════════════════════════════════════════════════════════════

def generate_ohlc_bars(
    tick_data: Optional[pd.DataFrame] = None,
    parquet_path: Optional[Path] = None,
    interval_minutes: int = 5,
    lookback: Optional[int] = None
) -> pd.DataFrame:
    """
    Generate OHLC bars from tick data
    
    Args:
        tick_data: DataFrame with tick data (optional if parquet_path provided)
        parquet_path: Path to parquet file (optional if tick_data provided)
        interval_minutes: Candle interval in minutes (default: 5)
        lookback: Lookback period (currently not used, for metadata)
        
    Returns:
        DataFrame with OHLC bars containing:
        - timestamp: Bar timestamp
        - open: Opening price
        - high: Highest price
        - low: Lowest price
        - close: Closing price
        - mid_price: Alias for close (for compatibility)
        - volume: Tick count
        
    Raises:
        ValueError: If neither tick_data nor parquet_path is provided
        ValueError: If data is empty or missing required columns
    """
    # Load data if not provided
    if tick_data is None:
        if parquet_path is None:
            parquet_path = PARQUET_FILE
        
        print(f"📂 Loading tick data from {parquet_path}...", flush=True)
        tick_data = load_crystal(parquet_path)
    
    # Validate data
    if tick_data is None or len(tick_data) == 0:
        raise ValueError("❌ Tick data is empty!")
    
    # Check required columns
    if "timestamp" not in tick_data.columns:
        raise ValueError("❌ Data missing 'timestamp' column!")
    
    # Ensure we have price data
    has_mid_price = "mid_price" in tick_data.columns
    has_bid_ask = "bid" in tick_data.columns and "ask" in tick_data.columns
    has_close = "close" in tick_data.columns
    
    if not (has_mid_price or has_bid_ask or has_close):
        raise ValueError("❌ Data missing price columns (need mid_price, bid/ask, or close)!")
    
    print(f"   📊 Input: {len(tick_data):,} ticks", flush=True)
    print(f"   🕐 Generating {interval_minutes}min OHLC bars...", flush=True)
    
    # Ensure timestamp is datetime
    tick_data = ensure_datetime_column(tick_data, 'timestamp', utc=True)
    
    # Calculate mid_price if needed
    if not has_mid_price and has_bid_ask:
        tick_data = tick_data.copy()
        tick_data["mid_price"] = (tick_data["bid"] + tick_data["ask"]) / 2
    elif not has_mid_price and has_close:
        tick_data = tick_data.copy()
        tick_data["mid_price"] = tick_data["close"]
    
    # Set timestamp as index for resampling
    df_temp = tick_data.set_index("timestamp")
    
    # Resample to OHLC
    ohlc = df_temp["mid_price"].resample(f"{interval_minutes}min").agg({
        "open": "first",
        "high": "max",
        "low": "min",
        "close": "last"
    }).dropna()
    
    # Add volume (tick count)
    ohlc["volume"] = df_temp["mid_price"].resample(f"{interval_minutes}min").count()
    
    # Add mid_price as alias for close (for backtester compatibility)
    ohlc["mid_price"] = ohlc["close"]
    
    # Calculate additional useful metrics
    ohlc["body"] = ohlc["close"] - ohlc["open"]
    ohlc["body_pips"] = ohlc["body"] * 10000  # For EURUSD
    ohlc["range_pips"] = (ohlc["high"] - ohlc["low"]) * 10000
    
    # Add spread if available
    if "spread_pips" in df_temp.columns:
        ohlc["spread_avg"] = df_temp["spread_pips"].resample(f"{interval_minutes}min").mean()
    
    # Reset index to get timestamp as column
    ohlc = ohlc.reset_index()
    
    # Validate output
    if len(ohlc) == 0:
        raise ValueError("❌ OHLC generation produced no bars!")
    
    # Check for reasonable price variation
    price_std = ohlc["close"].std()
    if price_std == 0:
        raise ValueError("❌ Price data is constant (no variation)!")
    
    print(f"   ✅ Generated {len(ohlc):,} OHLC bars", flush=True)
    print(f"   📈 Price range: {ohlc['close'].min():.5f} - {ohlc['close'].max():.5f}", flush=True)
    print(f"   📊 Price std dev: {price_std:.6f}", flush=True)
    
    return ohlc


def load_parquet_for_backtest(
    parquet_path: Optional[Path] = None,
    interval_minutes: int = 5,
    lookback: Optional[int] = None
) -> pd.DataFrame:
    """
    Load Parquet data and generate OHLC bars for backtesting
    
    This is a convenience function that combines loading and OHLC generation.
    
    Args:
        parquet_path: Path to parquet file (default: from config)
        interval_minutes: Candle interval in minutes
        lookback: Lookback period (for metadata)
        
    Returns:
        DataFrame with OHLC bars ready for backtesting
    """
    return generate_ohlc_bars(
        parquet_path=parquet_path,
        interval_minutes=interval_minutes,
        lookback=lookback
    )


def validate_ohlc_data(ohlc: pd.DataFrame) -> Dict:
    """
    Validate OHLC data quality
    
    Args:
        ohlc: DataFrame with OHLC data
        
    Returns:
        Dictionary with validation results
    """
    results = {
        "valid": True,
        "errors": [],
        "warnings": [],
        "stats": {}
    }
    
    # Check minimum bars
    if len(ohlc) < 100:
        results["warnings"].append(f"Low bar count: {len(ohlc)} (recommended: >100)")
    
    results["stats"]["n_bars"] = len(ohlc)
    
    # Check required columns
    required_cols = ["timestamp", "open", "high", "low", "close"]
    missing_cols = [col for col in required_cols if col not in ohlc.columns]
    if missing_cols:
        results["valid"] = False
        results["errors"].append(f"Missing columns: {missing_cols}")
        return results
    
    # Check for nulls
    null_counts = ohlc[required_cols].isnull().sum()
    if null_counts.any():
        results["warnings"].append(f"Null values found: {null_counts[null_counts > 0].to_dict()}")
    
    # Check OHLC logic (high >= low, etc.)
    invalid_high_low = (ohlc["high"] < ohlc["low"]).sum()
    if invalid_high_low > 0:
        results["valid"] = False
        results["errors"].append(f"Invalid bars (high < low): {invalid_high_low}")
    
    invalid_high_open = (ohlc["high"] < ohlc["open"]).sum()
    if invalid_high_open > 0:
        results["warnings"].append(f"Bars with high < open: {invalid_high_open}")
    
    invalid_high_close = (ohlc["high"] < ohlc["close"]).sum()
    if invalid_high_close > 0:
        results["warnings"].append(f"Bars with high < close: {invalid_high_close}")
    
    invalid_low_open = (ohlc["low"] > ohlc["open"]).sum()
    if invalid_low_open > 0:
        results["warnings"].append(f"Bars with low > open: {invalid_low_open}")
    
    invalid_low_close = (ohlc["low"] > ohlc["close"]).sum()
    if invalid_low_close > 0:
        results["warnings"].append(f"Bars with low > close: {invalid_low_close}")
    
    # Price statistics
    results["stats"]["price_min"] = float(ohlc["close"].min())
    results["stats"]["price_max"] = float(ohlc["close"].max())
    results["stats"]["price_mean"] = float(ohlc["close"].mean())
    results["stats"]["price_std"] = float(ohlc["close"].std())
    
    # Check for constant price
    if results["stats"]["price_std"] < 1e-10:  # Near-zero threshold for floating point
        results["valid"] = False
        results["errors"].append("Price data is constant (std dev ≈ 0)")
    
    # Check for suspicious price values
    if results["stats"]["price_min"] <= 0:
        results["valid"] = False
        results["errors"].append(f"Invalid price: {results['stats']['price_min']} <= 0")
    
    return results


# ═══════════════════════════════════════════════════════════════
# 🧪 TESTING
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════════╗
║              🔮 OHLC GENERATOR TEST 🔮                       ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    # Test with synthetic data
    print("📊 Generating synthetic tick data...")
    np.random.seed(42)
    
    # Generate realistic tick data
    n_ticks = 10000
    base_time = pd.Timestamp("2025-01-01", tz="UTC")
    timestamps = pd.date_range(base_time, periods=n_ticks, freq="1s")
    
    # Random walk for prices
    base_price = 1.10
    price_changes = np.random.randn(n_ticks) * 0.00001
    mid_prices = base_price + np.cumsum(price_changes)
    
    # Create tick dataframe
    tick_df = pd.DataFrame({
        "timestamp": timestamps,
        "bid": mid_prices - 0.00002,
        "ask": mid_prices + 0.00002,
        "mid_price": mid_prices
    })
    
    print(f"   ✅ Generated {len(tick_df):,} ticks")
    print(f"   📅 Period: {tick_df['timestamp'].min()} to {tick_df['timestamp'].max()}")
    
    # Test OHLC generation
    print("\n🔮 Testing OHLC generation...")
    ohlc_5m = generate_ohlc_bars(tick_df, interval_minutes=5)
    
    print(f"\n📊 5-minute OHLC bars:")
    print(f"   Bars: {len(ohlc_5m):,}")
    print(f"   Columns: {list(ohlc_5m.columns)}")
    print(f"\n   Sample (first 3 bars):")
    print(ohlc_5m[["timestamp", "open", "high", "low", "close", "volume"]].head(3))
    
    # Test validation
    print("\n✅ Testing validation...")
    validation = validate_ohlc_data(ohlc_5m)
    print(f"   Valid: {validation['valid']}")
    print(f"   Errors: {validation['errors']}")
    print(f"   Warnings: {validation['warnings']}")
    print(f"   Stats: {validation['stats']}")
    
    # Test different intervals
    print("\n🔮 Testing different intervals...")
    for interval in [1, 5, 15, 60]:
        ohlc = generate_ohlc_bars(tick_df, interval_minutes=interval)
        print(f"   {interval:3d}min: {len(ohlc):4d} bars")
    
    print("\n✅ OHLC Generator test complete!")
