#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚡🌟💎 ULTRA NECROZMA - DATA LOADER 💎🌟⚡

Photon Storage System:  CSV → Parquet Crystallization
"Light compressed into eternal crystals"

Technical: Data ingestion and Parquet conversion module
"""

import pandas as pd
import numpy as np
from pathlib import Path
import time
import gc

try:
    import pyarrow as pa
    import pyarrow.parquet as pq
    PYARROW_AVAILABLE = True
except ImportError:
    PYARROW_AVAILABLE = False

from config import (
    CSV_FILE, PARQUET_FILE, CSV_COLUMNS, 
    PARQUET_COMPRESSION, CSV_CHUNK_SIZE, THEME
)


# ═══════════════════════════════════════════════════════════════
# 🛠️ UTILITY FUNCTIONS
# ═══════════════════════════════════════════════════════════════

def ensure_datetime_column(df, column='timestamp', utc=True):
    """
    Ensure a column is datetime type
    
    Args:
        df: DataFrame
        column: Column name to convert
        utc: Whether to localize to UTC
        
    Returns:
        DataFrame with converted column
        
    Note:
        This function creates a copy of the DataFrame when conversion is needed
        to avoid modifying the original data. For large DataFrames, consider
        converting timestamps before loading into the main pipeline.
    """
    if column not in df.columns:
        return df
    
    if df[column].dtype == 'object' or pd.api.types.is_string_dtype(df[column]):
        # Copy to avoid modifying original DataFrame
        df = df.copy()
        df[column] = pd.to_datetime(df[column], utc=utc, errors='coerce')
    elif df[column].dtype.name.startswith('datetime') and utc:
        # Ensure UTC if not already
        if df[column].dt.tz is None:
            df[column] = df[column].dt.tz_localize('UTC')
        elif str(df[column].dt.tz) != 'UTC':
            df[column] = df[column].dt.tz_convert('UTC')
    
    return df


# ═══════════════════════════════════════════════════════════════
# 🌟 PRISM FORM:  CSV → PARQUET CRYSTALLIZATION
# ═══════════════════════════════════════════════════════════════

def crystallize_csv_to_parquet(csv_path=None, parquet_path=None, force=False):
    """
    Convert CSV tick data to Parquet format (Crystallization)
    Technical: CSV ingestion with chunked reading, Parquet serialization
    
    Args: 
        csv_path:  Path to input CSV (default: from config)
        parquet_path: Path to output Parquet (default: from config)
        force:  Overwrite existing Parquet if True
        
    Returns:
        Path:  Path to created Parquet file
    """
    csv_path = Path(csv_path or CSV_FILE)
    parquet_path = Path(parquet_path or PARQUET_FILE)
    
    print("""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║        💎 NECROZMA PRISM FORM - CRYSTALLIZATION 💎           ║
║                                                              ║
║    "Raw light transforms into eternal crystal..."            ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    # Check if already crystallized
    if parquet_path.exists() and not force:
        print(f"💎 Crystal already exists:  {parquet_path}")
        print(f"   Use force=True to re-crystallize")
        return parquet_path
    
    # Validate CSV
    if not csv_path.exists():
        raise FileNotFoundError(f"❌ Source light not found: {csv_path}")
    
    csv_size_gb = csv_path.stat().st_size / (1024**3)
    print(f"📂 Source:  {csv_path}")
    print(f"💾 Size: {csv_size_gb:.2f} GB")
    print(f"🎯 Target: {parquet_path}")
    print()
    
    # Create output directory
    parquet_path. parent.mkdir(parents=True, exist_ok=True)
    
    # ═══ PHASE 1: ABSORB LIGHT (Read CSV) ═══
    print("🌟 Phase 1: ABSORBING LIGHT (Reading CSV)")
    print("─" * 60)
    
    start_time = time.time()
    chunks = []
    total_rows = 0
    
    for i, chunk in enumerate(pd.read_csv(csv_path, chunksize=CSV_CHUNK_SIZE)):
        chunks.append(chunk)
        total_rows += len(chunk)
        
        if (i + 1) % 5 == 0:
            elapsed = time.time() - start_time
            speed = total_rows / elapsed
            print(f"   💫 Chunk {i+1}:  {total_rows:,} rows absorbed "
                  f"({speed: ,.0f} rows/sec)")
    
    # Concatenate
    print(f"\n   ⚡ Fusing {len(chunks)} light fragments...")
    df = pd.concat(chunks, ignore_index=True)
    del chunks
    gc.collect()
    
    read_time = time.time() - start_time
    print(f"   ✅ {len(df):,} rows absorbed in {read_time:.1f}s")
    
    # ═══ PHASE 2: REFRACT LIGHT (Process Data) ═══
    print(f"\n🔮 Phase 2: REFRACTING LIGHT (Processing)")
    print("─" * 60)
    
    process_start = time.time()
    
    # Rename columns if needed
    col_map = {v: k for k, v in CSV_COLUMNS.items() if v in df.columns}
    if col_map:
        df = df.rename(columns=col_map)
    
    # Parse timestamp
    print("   ⏰ Parsing temporal coordinates...")
    ts_col = CSV_COLUMNS.get("timestamp", "Timestamp")
    if ts_col in df.columns:
        df["timestamp"] = pd.to_datetime(df[ts_col], utc=True)
    elif "timestamp" not in df.columns:
        # Try to find timestamp column
        for col in df.columns:
            if "time" in col.lower():
                df["timestamp"] = pd.to_datetime(df[col], utc=True)
                break
    
    # Standardize column names
    df.columns = df.columns.str.lower().str.strip()
    
    # Calculate derived fields
    print("   💎 Crystallizing derived fields...")
    
    # Mid price
    if "bid" in df.columns and "ask" in df.columns:
        df["mid_price"] = (df["bid"] + df["ask"]) / 2
        
        # Spread in pips (for EURUSD: 1 pip = 0.0001)
        df["spread_pips"] = (df["ask"] - df["bid"]) * 10000
        
        # Price change in pips
        df["pips_change"] = df["mid_price"]. diff() * 10000
    
    # Sort by timestamp
    print("   🌀 Aligning temporal dimension...")
    df = df.sort_values("timestamp").reset_index(drop=True)
    
    # Select final columns
    final_columns = ["timestamp", "bid", "ask", "mid_price", "spread_pips", "pips_change"]
    final_columns = [c for c in final_columns if c in df.columns]
    df = df[final_columns]
    
    # Optimize dtypes
    print("   ⚡ Optimizing crystal structure...")
    df["bid"] = df["bid"].astype("float64")
    df["ask"] = df["ask"].astype("float64")
    df["mid_price"] = df["mid_price"].astype("float64")
    df["spread_pips"] = df["spread_pips"].astype("float32")
    df["pips_change"] = df["pips_change"].astype("float32")
    
    process_time = time.time() - process_start
    print(f"   ✅ Refraction complete in {process_time:.1f}s")
    
    # ═══ PHASE 3: CRYSTALLIZE (Save Parquet) ═══
    print(f"\n💎 Phase 3: CRYSTALLIZING (Saving Parquet)")
    print("─" * 60)
    
    crystal_start = time.time()
    
    # Memory usage before
    mem_before = df.memory_usage(deep=True).sum() / (1024**3)
    print(f"   📊 DataFrame memory:  {mem_before:.2f} GB")
    
    # Save to Parquet
    print(f"   💎 Compressing with {PARQUET_COMPRESSION}...")
    df.to_parquet(
        parquet_path,
        engine="pyarrow",
        compression=PARQUET_COMPRESSION,
        index=False
    )
    
    crystal_time = time.time() - crystal_start
    parquet_size_gb = parquet_path.stat().st_size / (1024**3)
    compression_ratio = csv_size_gb / parquet_size_gb
    
    print(f"   ✅ Crystal formed in {crystal_time:.1f}s")
    print(f"   💾 Crystal size: {parquet_size_gb:.2f} GB")
    print(f"   📉 Compression ratio: {compression_ratio:.1f}x")
    
    # ═══ SUMMARY ═══
    total_time = time.time() - start_time
    
    print(f"""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║           💎 CRYSTALLIZATION COMPLETE 💎                     ║
║                                                              ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║   📊 Rows:         {len(df):>15,}                            ║
║   📂 CSV Size:    {csv_size_gb: >15.2f} GB                        ║
║   💎 Parquet:      {parquet_size_gb: >15.2f} GB                        ║
║   📉 Compression: {compression_ratio: >15.1f}x                         ║
║   ⏱️  Time:        {total_time: >15.1f}s                         ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    return parquet_path


# ═══════════════════════════════════════════════════════════════
# 🌟 ULTRA BURST: LOAD PARQUET
# ═══════════════════════════════════════════════════════════════

def load_crystal(parquet_path=None):
    """
    Load Parquet data at light speed (Ultra Burst)
    Technical: Parquet deserialization with PyArrow
    
    Args: 
        parquet_path: Path to Parquet file (default:  from config)
        
    Returns:
        pd.DataFrame: Loaded tick data
    """
    parquet_path = Path(parquet_path or PARQUET_FILE)
    
    print("""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║          ⚡ ULTRA BURST - CRYSTAL LOADING ⚡                 ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    if not parquet_path.exists():
        raise FileNotFoundError(f"❌ Crystal not found: {parquet_path}")
    
    parquet_size = parquet_path.stat().st_size / (1024**3)
    print(f"💎 Loading crystal:  {parquet_path}")
    print(f"💾 Crystal size: {parquet_size:.2f} GB")
    print()
    
    start_time = time.time()
    
    # Load with PyArrow (faster)
    print("⚡ Initiating Ultra Burst...")
    df = pd.read_parquet(parquet_path, engine="pyarrow")
    
    # BUGFIX: Ensure timestamp is datetime after loading
    if "timestamp" in df.columns:
        if df['timestamp'].dtype == 'object' or pd.api.types.is_string_dtype(df['timestamp']):
            df['timestamp'] = pd.to_datetime(df['timestamp'], utc=True, errors='coerce')
    
    load_time = time.time() - start_time
    mem_usage = df.memory_usage(deep=True).sum() / (1024**3)
    speed = len(df) / load_time
    
    print(f"""
✅ Crystal loaded! 
   📊 Rows:     {len(df):,}
   💾 Memory:   {mem_usage:.2f} GB
   ⏱️  Time:     {load_time:.2f}s
   ⚡ Speed:    {speed: ,.0f} rows/sec
    """)
    
    return df


# ═══════════════════════════════════════════════════════════════
# 🔮 TEMPORAL RESAMPLING (OHLC Aggregation)
# ═══════════════════════════════════════════════════════════════

def resample_to_ohlc(df, interval_minutes):
    """
    Resample tick data to OHLC candles (Temporal Compression)
    Technical: Time-based resampling with OHLC aggregation
    
    Args:
        df: DataFrame with tick data
        interval_minutes:  Candle interval in minutes
        
    Returns:
        pd.DataFrame: OHLC data
    """
    from lore import print_legendary_banner
    
    # Show Dialga banner for temporal transformation
    if interval_minutes >= 5:  # Only show for major timeframes
        print_legendary_banner('dialga', count=len(df))
    
    print(f"   🕐 Resampling to {interval_minutes}min candles (Dialga Temporal Shift)...")
    print(f"   ⏰ Time itself bends to reveal market cycles...")
    
    # BUGFIX: Ensure timestamp column is datetime type
    if "timestamp" in df.columns:
        if df['timestamp'].dtype == 'object' or pd.api.types.is_string_dtype(df['timestamp']):
            df = df.copy()
            df['timestamp'] = pd.to_datetime(df['timestamp'], utc=True, errors='coerce')
    
    # Set timestamp as index
    df_temp = df.set_index("timestamp")
    
    # Resample
    ohlc = df_temp["mid_price"].resample(f"{interval_minutes}min").agg({
        "open": "first",
        "high": "max",
        "low": "min",
        "close": "last"
    }).dropna()
    
    # Add additional columns
    if "spread_pips" in df_temp.columns:
        spread = df_temp["spread_pips"].resample(f"{interval_minutes}min").mean()
        ohlc["spread_avg"] = spread
    
    # Volume (tick count)
    ohlc["tick_volume"] = df_temp["mid_price"].resample(f"{interval_minutes}min").count()
    
    # Calculate candle metrics
    ohlc["body"] = ohlc["close"] - ohlc["open"]
    ohlc["body_pips"] = ohlc["body"] * 10000
    ohlc["range_pips"] = (ohlc["high"] - ohlc["low"]) * 10000
    ohlc["upper_wick"] = ohlc["high"] - ohlc[["open", "close"]].max(axis=1)
    ohlc["lower_wick"] = ohlc[["open", "close"]].min(axis=1) - ohlc["low"]
    
    # Direction
    ohlc["direction"] = np.where(ohlc["body"] > 0, "up", "down")
    
    ohlc = ohlc.reset_index()
    
    print(f"   ✅ {len(ohlc):,} candles created (Temporal signatures detected)")
    
    return ohlc


# ═══════════════════════════════════════════════════════════════
# 📊 DATA INFO
# ═══════════════════════════════════════════════════════════════

def crystal_info(df):
    """
    Display crystal information (Data Summary)
    Technical: DataFrame statistics and info
    """
    print("""
╔══════════════════════════════════════════════════════════════╗
║                 💎 CRYSTAL INFORMATION 💎                    ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    print(f"📊 Shape: {df.shape[0]: ,} rows × {df.shape[1]} columns")
    print(f"💾 Memory:  {df.memory_usage(deep=True).sum() / (1024**3):.2f} GB")
    print()
    
    if "timestamp" in df.columns:
        # BUGFIX: Ensure timestamp is datetime type before arithmetic operations
        ts_col = df['timestamp']
        if ts_col.dtype == 'object' or pd.api.types.is_string_dtype(ts_col):
            ts_col = pd.to_datetime(ts_col, utc=True, errors='coerce')
        
        print(f"📅 Period:")
        print(f"   Start: {ts_col.min()}")
        print(f"   End:    {ts_col.max()}")
        
        # Safe duration calculation
        try:
            duration = ts_col.max() - ts_col.min()
            print(f"   Duration: {duration}")
        except Exception as e:
            print(f"   Duration: Unable to calculate ({type(e).__name__}: {str(e)})")
    print()
    
    if "mid_price" in df.columns:
        print(f"💰 Price Range:")
        print(f"   Min:   {df['mid_price']. min():.5f}")
        print(f"   Max:  {df['mid_price'].max():.5f}")
        print(f"   Mean: {df['mid_price'].mean():.5f}")
    print()
    
    if "spread_pips" in df. columns:
        print(f"📈 Spread (pips):")
        print(f"   Min:  {df['spread_pips'].min():.2f}")
        print(f"   Max:  {df['spread_pips'].max():.2f}")
        print(f"   Mean: {df['spread_pips'].mean():.2f}")
    print()
    
    print("📋 Columns:")
    for col in df.columns:
        dtype = df[col].dtype
        nulls = df[col].isnull().sum()
        print(f"   {col}: {dtype}" + (f" ({nulls:,} nulls)" if nulls > 0 else ""))


# ═══════════════════════════════════════════════════════════════
# 🎮 MAIN (Testing)
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__": 
    print(f"\n⚡ Ultra Necrozma Data Loader")
    print(f"💎 PyArrow available: {PYARROW_AVAILABLE}")
    print()
    
    # Test crystallization
    if CSV_FILE.exists():
        print("📂 CSV found, testing crystallization...")
        parquet_path = crystallize_csv_to_parquet(force=False)
        
        # Test loading
        df = load_crystal(parquet_path)
        crystal_info(df)
        
        # Test resampling
        print("\n🔮 Testing resampling...")
        ohlc_5m = resample_to_ohlc(df, 5)
        print(f"   5min candles: {len(ohlc_5m):,}")
        
    else:
        print(f"⚠️  CSV not found: {CSV_FILE}")
        print(f"   Configure CSV_FILE in config.py")