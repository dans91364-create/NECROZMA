#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚡🌟💎 NECROZMA - CORRELATION ANALYZER 💎🌟⚡

Pre-calculate correlations between forex pairs before backtesting
Saves correlation features to universe JSON files

Features:
- Rolling correlation (20, 50, 100 periods)
- Z-score of correlation vs historical mean
- Divergence detection between correlated pairs
- Lead/Lag indicators
- Risk sentiment score
- USD strength index
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
import json
from pathlib import Path
from scipy import stats

# Constants
EPSILON = 1e-8  # Small value to prevent division by zero

# 10 Forex Pairs
PAIRS = [
    "EURUSD", "GBPUSD", "USDJPY", "USDCHF", "AUDUSD",
    "USDCAD", "EURGBP", "GBPJPY", "EURJPY", "AUDJPY"
]

# Correlation windows
CORRELATION_WINDOWS = [20, 50, 100]


# ═══════════════════════════════════════════════════════════════
# 📊 CORRELATION CALCULATION
# ═══════════════════════════════════════════════════════════════

def calculate_rolling_correlation(
    series1: pd.Series,
    series2: pd.Series,
    window: int
) -> pd.Series:
    """
    Calculate rolling correlation between two series
    
    Args:
        series1: First time series
        series2: Second time series
        window: Rolling window size
        
    Returns:
        Series with rolling correlation values
    """
    return series1.rolling(window).corr(series2)


def calculate_correlation_zscore(
    current_corr: float,
    historical_corr: pd.Series
) -> float:
    """
    Calculate Z-score of current correlation vs historical mean
    
    Args:
        current_corr: Current correlation value
        historical_corr: Historical correlation series
        
    Returns:
        Z-score value
    """
    mean = historical_corr.mean()
    std = historical_corr.std()
    
    if std == 0:
        return 0.0
    
    return (current_corr - mean) / std


def detect_divergence(
    series1: pd.Series,
    series2: pd.Series,
    lookback: int = 20
) -> pd.Series:
    """
    Detect divergence between two correlated pairs
    
    Args:
        series1: First time series
        series2: Second time series
        lookback: Lookback period
        
    Returns:
        Series with divergence scores
    """
    # Calculate returns
    returns1 = series1.pct_change()
    returns2 = series2.pct_change()
    
    # Calculate cumulative returns over lookback
    cum_ret1 = returns1.rolling(lookback).sum()
    cum_ret2 = returns2.rolling(lookback).sum()
    
    # Divergence is the difference in cumulative returns
    divergence = cum_ret1 - cum_ret2
    
    return divergence


def calculate_lead_lag(
    series1: pd.Series,
    series2: pd.Series,
    max_lag: int = 5
) -> Tuple[int, float]:
    """
    Calculate lead/lag relationship between two series
    
    Args:
        series1: Potential leading series
        series2: Potential lagging series
        max_lag: Maximum lag to test
        
    Returns:
        Tuple of (optimal_lag, correlation_at_lag)
    """
    # Ensure we have enough data for lag calculation
    if len(series1) < max_lag * 2 or len(series2) < max_lag * 2:
        return 0, 0.0
    
    best_lag = 0
    best_corr = 0.0
    
    for lag in range(-max_lag, max_lag + 1):
        try:
            if lag < 0:
                # series1 leads
                if len(series1[:lag]) < 2 or len(series2[-lag:]) < 2:
                    continue
                corr = series1.iloc[:lag].corr(series2.iloc[-lag:])
            elif lag > 0:
                # series2 leads
                if len(series1[lag:]) < 2 or len(series2[:-lag]) < 2:
                    continue
                corr = series1.iloc[lag:].corr(series2.iloc[:-lag])
            else:
                # No lag
                corr = series1.corr(series2)
            
            if pd.notna(corr) and abs(corr) > abs(best_corr):
                best_corr = corr
                best_lag = lag
        except (ValueError, IndexError):
            continue
    
    return best_lag, best_corr


# ═══════════════════════════════════════════════════════════════
# 💹 USD STRENGTH INDEX
# ═══════════════════════════════════════════════════════════════

def calculate_usd_strength(pairs_data: Dict[str, pd.Series]) -> pd.Series:
    """
    Calculate USD strength index from multiple pairs
    
    Args:
        pairs_data: Dictionary of pair_name -> price_series
        
    Returns:
        Series with USD strength index (0 to 1)
    """
    # USD pairs where USD is quote currency (inverse for strength)
    usd_quote_pairs = ["EURUSD", "GBPUSD", "AUDUSD"]
    
    # USD pairs where USD is base currency
    usd_base_pairs = ["USDJPY", "USDCHF", "USDCAD"]
    
    strength_components = []
    
    # For USD quote pairs, falling = USD strength
    for pair in usd_quote_pairs:
        if pair in pairs_data:
            returns = pairs_data[pair].pct_change()
            strength_components.append(-returns)  # Inverse
    
    # For USD base pairs, rising = USD strength
    for pair in usd_base_pairs:
        if pair in pairs_data:
            returns = pairs_data[pair].pct_change()
            strength_components.append(returns)
    
    if not strength_components:
        return pd.Series(0.5)
    
    # Average and normalize to 0-1
    avg_strength = pd.concat(strength_components, axis=1).mean(axis=1)
    
    # Normalize using rolling z-score, then map to 0-1
    rolling_mean = avg_strength.rolling(100).mean()
    rolling_std = avg_strength.rolling(100).std()
    
    z_score = (avg_strength - rolling_mean) / (rolling_std + EPSILON)
    
    # Map z-score to 0-1 using sigmoid
    strength_index = 1 / (1 + np.exp(-z_score))
    
    return strength_index


# ═══════════════════════════════════════════════════════════════
# 🎭 RISK SENTIMENT SCORE
# ═══════════════════════════════════════════════════════════════

def calculate_risk_sentiment(pairs_data: Dict[str, pd.Series]) -> pd.Series:
    """
    Calculate risk sentiment score (risk-on vs risk-off)
    
    Risk ON: AUD, NZD up / JPY, CHF down
    Risk OFF: AUD, NZD down / JPY, CHF up
    
    Args:
        pairs_data: Dictionary of pair_name -> price_series
        
    Returns:
        Series with risk sentiment score (0=risk-off, 1=risk-on)
    """
    # Risk-on currencies (when strong = risk-on)
    risk_on_pairs = ["AUDUSD", "AUDJPY"]  # AUD strength
    
    # Risk-off currencies (when strong = risk-off)
    risk_off_pairs = ["USDJPY", "USDCHF"]  # JPY/CHF strength (inverse)
    
    sentiment_components = []
    
    # Risk-on pairs: rising = risk-on
    for pair in risk_on_pairs:
        if pair in pairs_data:
            returns = pairs_data[pair].pct_change()
            sentiment_components.append(returns)
    
    # Risk-off pairs: falling = risk-on
    for pair in risk_off_pairs:
        if pair in pairs_data:
            returns = pairs_data[pair].pct_change()
            sentiment_components.append(-returns)  # Inverse
    
    if not sentiment_components:
        return pd.Series(0.5)
    
    # Average and normalize to 0-1
    avg_sentiment = pd.concat(sentiment_components, axis=1).mean(axis=1)
    
    # Normalize using rolling z-score, then map to 0-1
    rolling_mean = avg_sentiment.rolling(100).mean()
    rolling_std = avg_sentiment.rolling(100).std()
    
    z_score = (avg_sentiment - rolling_mean) / (rolling_std + EPSILON)
    
    # Map z-score to 0-1 using sigmoid
    sentiment_score = 1 / (1 + np.exp(-z_score))
    
    return sentiment_score


# ═══════════════════════════════════════════════════════════════
# 🔧 MAIN CORRELATION FEATURE EXTRACTION
# ═══════════════════════════════════════════════════════════════

def calculate_pair_correlations(pairs_data: Dict[str, pd.Series]) -> Dict:
    """
    Calculate comprehensive correlation features for all pairs
    
    Args:
        pairs_data: Dictionary of pair_name -> price_series
        
    Returns:
        Dictionary with correlation features
    """
    correlation_features = {}
    
    # Calculate pairwise correlations
    pair_names = list(pairs_data.keys())
    
    for i, pair1 in enumerate(pair_names):
        for j, pair2 in enumerate(pair_names):
            if i >= j:  # Skip duplicates and self-correlation
                continue
            
            series1 = pairs_data[pair1]
            series2 = pairs_data[pair2]
            
            # Rolling correlations
            for window in CORRELATION_WINDOWS:
                corr = calculate_rolling_correlation(series1, series2, window)
                
                # Store last value
                key = f"{pair1}_{pair2}_corr_{window}"
                correlation_features[key] = corr.iloc[-1] if len(corr) > 0 else 0.0
                
                # Z-score
                if len(corr) > window:
                    zscore = calculate_correlation_zscore(corr.iloc[-1], corr)
                    key_z = f"{pair1}_{pair2}_corr_zscore_{window}"
                    correlation_features[key_z] = zscore
            
            # Divergence
            div = detect_divergence(series1, series2)
            key_div = f"{pair1}_{pair2}_divergence"
            correlation_features[key_div] = div.iloc[-1] if len(div) > 0 else 0.0
            
            # Lead/Lag
            lag, lag_corr = calculate_lead_lag(series1, series2)
            key_lag = f"{pair1}_{pair2}_lead_lag"
            key_lag_corr = f"{pair1}_{pair2}_lead_lag_corr"
            correlation_features[key_lag] = lag
            correlation_features[key_lag_corr] = lag_corr
    
    # USD strength index
    usd_strength = calculate_usd_strength(pairs_data)
    correlation_features["USD_strength_index"] = usd_strength.iloc[-1] if len(usd_strength) > 0 else 0.5
    
    # Risk sentiment score
    risk_sentiment = calculate_risk_sentiment(pairs_data)
    correlation_features["risk_sentiment_score"] = risk_sentiment.iloc[-1] if len(risk_sentiment) > 0 else 0.5
    
    return correlation_features


def save_correlation_features(universe_path: str, correlation_data: Dict):
    """
    Add correlation_features to universe JSON
    
    Args:
        universe_path: Path to universe JSON file
        correlation_data: Dictionary with correlation features
    """
    universe_path = Path(universe_path)
    
    if not universe_path.exists():
        print(f"⚠️  Universe file not found: {universe_path}")
        return
    
    # Load universe
    with open(universe_path, 'r') as f:
        universe = json.load(f)
    
    # Add correlation features
    universe["correlation_features"] = correlation_data
    
    # Save back
    with open(universe_path, 'w') as f:
        json.dump(universe, f, indent=2)
    
    print(f"✅ Saved {len(correlation_data)} correlation features to {universe_path.name}")


# ═══════════════════════════════════════════════════════════════
# 🧪 TESTING
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════════╗
║           🔗 CORRELATION ANALYZER TEST 🔗                    ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    # Generate dummy data for testing
    np.random.seed(42)
    dates = pd.date_range("2025-01-01", periods=200, freq="1H")
    
    # Simulate correlated pairs
    pairs_data = {}
    
    # EUR/USD (base)
    eurusd = pd.Series(
        1.10 + np.cumsum(np.random.randn(200) * 0.001),
        index=dates,
        name="EURUSD"
    )
    pairs_data["EURUSD"] = eurusd
    
    # GBP/USD (correlated with EUR/USD)
    gbpusd = eurusd * 1.25 + np.random.randn(200) * 0.01
    pairs_data["GBPUSD"] = gbpusd
    
    # USD/JPY (inverse correlation)
    usdjpy = pd.Series(
        110 - (eurusd - 1.10) * 100 + np.random.randn(200) * 0.5,
        index=dates,
        name="USDJPY"
    )
    pairs_data["USDJPY"] = usdjpy
    
    # Add more pairs
    pairs_data["USDCHF"] = pd.Series(0.92 + np.random.randn(200) * 0.001, index=dates)
    pairs_data["AUDUSD"] = pd.Series(0.67 + np.random.randn(200) * 0.001, index=dates)
    pairs_data["USDCAD"] = pd.Series(1.35 + np.random.randn(200) * 0.001, index=dates)
    
    print("📊 Calculating correlation features...")
    correlation_features = calculate_pair_correlations(pairs_data)
    
    print(f"\n✅ Generated {len(correlation_features)} correlation features")
    
    # Display some key features
    print("\n🔍 Sample Features:")
    sample_keys = [
        "EURUSD_GBPUSD_corr_20",
        "EURUSD_GBPUSD_corr_50",
        "EURUSD_GBPUSD_divergence",
        "EURUSD_USDJPY_corr_20",
        "USD_strength_index",
        "risk_sentiment_score",
    ]
    
    for key in sample_keys:
        if key in correlation_features:
            value = correlation_features[key]
            print(f"   {key}: {value:.4f}")
    
    print("\n✅ Correlation analyzer test complete!")
