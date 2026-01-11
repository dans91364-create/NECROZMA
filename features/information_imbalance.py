#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚡🌟💎 ULTRA NECROZMA - INFORMATION IMBALANCE 💎🌟⚡

Information Imbalance
"Asymmetry between buyers and sellers"

Technical: Information Imbalance Metric
- Measures information asymmetry in microstructure
- Requires bid/ask or volume tick data
- Based on order flow imbalance
"""

import numpy as np


# ═══════════════════════════════════════════════════════════════
# 🌟 INFORMATION IMBALANCE
# ═══════════════════════════════════════════════════════════════

def information_imbalance(bid_volume, ask_volume):
    """
    Calculate information imbalance from bid/ask volumes
    
    Args:
        bid_volume: Array of bid volumes
        ask_volume: Array of ask volumes
        
    Returns:
        float: Information imbalance (-1 to 1)
    """
    bid_volume = np.asarray(bid_volume, dtype=np.float64)
    ask_volume = np.asarray(ask_volume, dtype=np.float64)
    
    total_volume = bid_volume + ask_volume
    
    # Avoid division by zero
    mask = total_volume > 0
    
    if not np.any(mask):
        return 0.0
    
    # Imbalance: (bid - ask) / (bid + ask)
    imbalance = (bid_volume[mask] - ask_volume[mask]) / total_volume[mask]
    
    # Average imbalance
    return float(np.mean(imbalance))


def rolling_information_imbalance(bid_volume, ask_volume, window=20):
    """
    Rolling information imbalance
    
    Args:
        bid_volume: Bid volumes
        ask_volume: Ask volumes
        window: Window size
        
    Returns:
        array: Rolling imbalance
    """
    n = len(bid_volume)
    if n < window:
        return np.array([])
    
    rolling_imb = []
    
    for i in range(window, n + 1):
        imb = information_imbalance(
            bid_volume[i - window:i],
            ask_volume[i - window:i]
        )
        rolling_imb.append(imb)
    
    return np.array(rolling_imb)


# ═══════════════════════════════════════════════════════════════
# 🎯 FEATURE EXTRACTION
# ═══════════════════════════════════════════════════════════════

def extract_information_imbalance_features(bid_volume=None, ask_volume=None, 
                                          prices=None, volumes=None):
    """
    Extract information imbalance features
    
    Note: Requires bid/ask volume data which may not always be available
    Falls back to price-based imbalance estimation if only prices available
    
    Args:
        bid_volume: Bid volumes (optional)
        ask_volume: Ask volumes (optional)
        prices: Prices (fallback if no bid/ask)
        volumes: Total volumes (fallback)
        
    Returns:
        dict: Information imbalance features
    """
    features = {}
    
    # If we have bid/ask volumes
    if bid_volume is not None and ask_volume is not None:
        # Overall imbalance
        imb = information_imbalance(bid_volume, ask_volume)
        features["info_imbalance"] = imb
        
        # Rolling statistics
        if len(bid_volume) >= 40:
            rolling_imb = rolling_information_imbalance(bid_volume, ask_volume, window=20)
            
            if len(rolling_imb) > 0:
                features["info_imbalance_mean"] = float(np.mean(rolling_imb))
                features["info_imbalance_std"] = float(np.std(rolling_imb))
                features["info_imbalance_min"] = float(np.min(rolling_imb))
                features["info_imbalance_max"] = float(np.max(rolling_imb))
    
    # Fallback: estimate from price movements if no bid/ask
    elif prices is not None and len(prices) > 1:
        # Estimate buy/sell pressure from price changes
        price_changes = np.diff(prices)
        
        # Positive changes = buy pressure, negative = sell pressure
        buy_pressure = np.sum(price_changes[price_changes > 0])
        sell_pressure = abs(np.sum(price_changes[price_changes < 0]))
        
        total_pressure = buy_pressure + sell_pressure
        
        if total_pressure > 0:
            imbalance = (buy_pressure - sell_pressure) / total_pressure
            features["info_imbalance_estimated"] = float(imbalance)
    
    return features
