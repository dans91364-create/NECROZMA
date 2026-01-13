#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚡🌟💎 ULTRA NECROZMA - FEATURE EXTRACTOR 💎🌟⚡

Extract pattern features from universe JSON files for backtesting
"Transform pattern features into tradable signals"
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional
import warnings

warnings.filterwarnings("ignore")


def extract_features_from_universe(universe_data: Dict) -> pd.DataFrame:
    """
    Extract features from universe JSON patterns
    
    The universe JSON contains patterns with features like:
    - ohlc_body_mean, ohlc_range_mean, ohlc_trend_efficiency
    - ohlc_volume_mean, ohlc_volume_trend, ohlc_spread_mean
    - ohlc_up_ratio, ohlc_down_ratio
    
    This function aggregates these features across all patterns to create
    a feature DataFrame that can be combined with OHLC data.
    
    Args:
        universe_data: Universe result dictionary from JSON file
        
    Returns:
        DataFrame with aggregated features (currently returns empty DataFrame
        as features will be aligned with timestamps during OHLC generation)
    """
    # Extract all features from patterns
    all_features = []
    
    try:
        # Navigate the universe structure
        results = universe_data.get("results", {})
        
        # Handle both list and dict results formats
        if isinstance(results, list) and len(results) > 0:
            results = results[0].get("results", {})
        
        # Iterate through levels (Pequeno, Médio, Grande, Muito Grande)
        for level_name, level_data in results.items():
            if not isinstance(level_data, dict):
                continue
                
            # Iterate through directions (up, down)
            for direction, direction_data in level_data.items():
                if not isinstance(direction_data, dict):
                    continue
                
                # Get patterns
                patterns = direction_data.get("patterns", {})
                
                # Extract features from each pattern
                for pattern_name, pattern_data in patterns.items():
                    if not isinstance(pattern_data, dict):
                        continue
                    
                    pattern_features = pattern_data.get("features", [])
                    
                    if isinstance(pattern_features, list):
                        all_features.extend(pattern_features)
    
    except Exception as e:
        print(f"      ⚠️  Warning: Failed to extract features from universe: {e}", flush=True)
        return pd.DataFrame()
    
    if not all_features:
        print(f"      ⚠️  Warning: No features found in universe data", flush=True)
        return pd.DataFrame()
    
    # Calculate aggregated feature statistics
    feature_stats = _aggregate_features(all_features)
    
    # Return as single-row DataFrame (will be broadcast to match OHLC timestamps)
    return pd.DataFrame([feature_stats])


def _aggregate_features(feature_list: List[Dict]) -> Dict:
    """
    Aggregate a list of feature dictionaries into mean statistics
    
    Args:
        feature_list: List of feature dictionaries
        
    Returns:
        Dictionary with aggregated feature statistics
    """
    if not feature_list:
        return {}
    
    # Collect all feature values
    feature_arrays = {}
    
    for features in feature_list:
        if not isinstance(features, dict):
            continue
            
        for key, value in features.items():
            if isinstance(value, (int, float)):
                if key not in feature_arrays:
                    feature_arrays[key] = []
                feature_arrays[key].append(value)
    
    # Calculate mean for each feature
    aggregated = {}
    
    for key, values in feature_arrays.items():
        if values:
            aggregated[key] = np.mean(values)
    
    # Derive additional features for strategies
    # These are the features that strategies look for
    
    # Body mean (from ohlc_body_mean)
    body_mean = aggregated.get("ohlc_body_mean", 0.0)
    aggregated["body_mean"] = body_mean
    
    # Range mean (from ohlc_range_mean)
    range_mean = aggregated.get("ohlc_range_mean", 0.0)
    aggregated["range_mean"] = range_mean
    
    # Trend efficiency (from ohlc_trend_efficiency)
    trend_efficiency = aggregated.get("ohlc_trend_efficiency", 0.0)
    aggregated["trend_efficiency"] = trend_efficiency
    
    # Volume mean (from ohlc_volume_mean)
    volume_mean = aggregated.get("ohlc_volume_mean", 0.0)
    aggregated["volume_mean"] = volume_mean
    
    # Volume trend (from ohlc_volume_trend)
    volume_trend = aggregated.get("ohlc_volume_trend", 1.0)
    aggregated["volume_trend"] = volume_trend
    
    # Spread mean (from ohlc_spread_mean)
    spread_mean = aggregated.get("ohlc_spread_mean", 0.0)
    aggregated["spread_mean"] = spread_mean
    
    # Up/down ratios
    up_ratio = aggregated.get("ohlc_up_ratio", 0.5)
    down_ratio = aggregated.get("ohlc_down_ratio", 0.5)
    aggregated["up_ratio"] = up_ratio
    aggregated["down_ratio"] = down_ratio
    
    # DERIVED FEATURES (what strategies actually look for)
    
    # Momentum = trend_efficiency * range_mean
    aggregated["momentum"] = trend_efficiency * range_mean
    
    # Trend = up_ratio - down_ratio
    aggregated["trend"] = up_ratio - down_ratio
    
    # Volatility = range_mean / body_mean (with div by zero protection)
    if abs(body_mean) > 1e-10:
        aggregated["volatility"] = range_mean / abs(body_mean)
    else:
        aggregated["volatility"] = range_mean
    
    # Trend strength (alias for trend_efficiency for compatibility)
    aggregated["trend_strength"] = trend_efficiency
    
    return aggregated


def combine_ohlc_with_features(
    ohlc_df: pd.DataFrame,
    features_df: pd.DataFrame
) -> pd.DataFrame:
    """
    Combine OHLC DataFrame with features DataFrame
    
    Since features are aggregated statistics (not time-series),
    we broadcast them to all OHLC rows.
    
    Args:
        ohlc_df: DataFrame with OHLC data (has timestamp index or column)
        features_df: DataFrame with aggregated features (single row)
        
    Returns:
        Combined DataFrame with OHLC + features
    """
    if features_df.empty:
        print(f"      ⚠️  Warning: No features to combine, returning OHLC only", flush=True)
        return ohlc_df
    
    # Make a copy to avoid modifying original
    combined = ohlc_df.copy()
    
    # Get feature values (first row since features are aggregated)
    feature_row = features_df.iloc[0]
    
    # Add each feature as a column (broadcast to all rows)
    for col in features_df.columns:
        if col not in combined.columns:  # Don't overwrite existing columns
            combined[col] = feature_row[col]
    
    return combined


def validate_dataframe_for_backtesting(df: pd.DataFrame) -> Dict:
    """
    Validate that DataFrame has required columns for backtesting
    
    Args:
        df: DataFrame to validate
        
    Returns:
        Dictionary with validation results:
        - valid: bool
        - missing_required: list of missing required columns
        - missing_optional: list of missing optional columns
        - warnings: list of warnings
    """
    # Required columns for basic backtesting
    required_columns = ["open", "high", "low", "close", "volume"]
    
    # Optional but recommended feature columns
    recommended_columns = ["momentum", "trend", "volatility", "trend_strength"]
    
    missing_required = [col for col in required_columns if col not in df.columns]
    missing_recommended = [col for col in recommended_columns if col not in df.columns]
    
    warnings_list = []
    
    # Check for NaN values in critical columns
    if not missing_required:
        for col in required_columns:
            nan_count = df[col].isna().sum()
            if nan_count > 0:
                warnings_list.append(f"Column '{col}' has {nan_count} NaN values")
    
    # Check data length
    if len(df) < 100:
        warnings_list.append(f"DataFrame has only {len(df)} rows (recommended: >100)")
    
    # Check price variation
    if "close" in df.columns:
        price_std = df["close"].std()
        if price_std < 1e-10:
            warnings_list.append("Price data has no variation (constant prices)")
    
    return {
        "valid": len(missing_required) == 0,
        "missing_required": missing_required,
        "missing_recommended": missing_recommended,
        "warnings": warnings_list,
    }


# ═══════════════════════════════════════════════════════════════
# 🧪 TESTING
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════════╗
║           🔮 FEATURE EXTRACTOR TEST 🔮                       ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    # Test with mock universe data
    print("📊 Testing feature extraction with mock data...")
    
    mock_universe = {
        "name": "test_universe",
        "config": {"interval": 5, "lookback": 5},
        "results": {
            "Pequeno": {
                "up": {
                    "patterns": {
                        "pattern_1": {
                            "count": 10,
                            "features": [
                                {
                                    "ohlc_body_mean": -1.02,
                                    "ohlc_range_mean": 2.46,
                                    "ohlc_trend_efficiency": 0.76,
                                    "ohlc_volume_mean": 81.8,
                                    "ohlc_volume_trend": 1.05,
                                    "ohlc_spread_mean": 0.5,
                                    "ohlc_up_ratio": 0.6,
                                    "ohlc_down_ratio": 0.4,
                                },
                                {
                                    "ohlc_body_mean": -0.98,
                                    "ohlc_range_mean": 2.50,
                                    "ohlc_trend_efficiency": 0.78,
                                    "ohlc_volume_mean": 85.2,
                                    "ohlc_volume_trend": 1.02,
                                    "ohlc_spread_mean": 0.48,
                                    "ohlc_up_ratio": 0.65,
                                    "ohlc_down_ratio": 0.35,
                                }
                            ]
                        }
                    }
                },
                "down": {
                    "patterns": {}
                }
            }
        }
    }
    
    # Extract features
    features_df = extract_features_from_universe(mock_universe)
    
    print(f"\n📊 Extracted features:")
    print(f"   Shape: {features_df.shape}")
    print(f"   Columns: {list(features_df.columns)}")
    
    if not features_df.empty:
        print(f"\n   Feature values:")
        for col in ["momentum", "trend", "volatility", "body_mean", "range_mean"]:
            if col in features_df.columns:
                print(f"      {col}: {features_df[col].iloc[0]:.4f}")
    
    # Test combining with mock OHLC data
    print(f"\n🔮 Testing combination with OHLC data...")
    
    mock_ohlc = pd.DataFrame({
        "timestamp": pd.date_range("2025-01-01", periods=5, freq="5min"),
        "open": [1.10, 1.101, 1.102, 1.103, 1.104],
        "high": [1.101, 1.102, 1.103, 1.104, 1.105],
        "low": [1.099, 1.100, 1.101, 1.102, 1.103],
        "close": [1.100, 1.101, 1.102, 1.103, 1.104],
        "volume": [100, 105, 98, 110, 95],
    })
    
    combined_df = combine_ohlc_with_features(mock_ohlc, features_df)
    
    print(f"\n   Combined DataFrame:")
    print(f"      Shape: {combined_df.shape}")
    print(f"      Columns: {list(combined_df.columns)}")
    print(f"      Sample row:")
    if not combined_df.empty:
        print(f"         OHLC: O={combined_df['open'].iloc[0]:.5f}, H={combined_df['high'].iloc[0]:.5f}, "
              f"L={combined_df['low'].iloc[0]:.5f}, C={combined_df['close'].iloc[0]:.5f}")
        if "momentum" in combined_df.columns:
            print(f"         Features: momentum={combined_df['momentum'].iloc[0]:.4f}, "
                  f"trend={combined_df['trend'].iloc[0]:.4f}, "
                  f"volatility={combined_df['volatility'].iloc[0]:.4f}")
    
    # Test validation
    print(f"\n✅ Testing DataFrame validation...")
    validation = validate_dataframe_for_backtesting(combined_df)
    
    print(f"   Valid: {validation['valid']}")
    print(f"   Missing required: {validation['missing_required']}")
    print(f"   Missing recommended: {validation['missing_recommended']}")
    print(f"   Warnings: {validation['warnings']}")
    
    print("\n✅ Feature extractor test complete!")
