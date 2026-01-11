#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚡🌟💎 ULTRA NECROZMA - WAVELET LEADERS MULTIFRACTAL 💎🌟⚡

Wavelet Leaders Multifractal Analysis
"Multifractal structure through wavelets"

Technical: Wavelet Leaders MF Analysis
- More robust than MF-DFA
- Better for series with jumps and discontinuities
- Uses wavelet decomposition
"""

import numpy as np

try:
    import pywt
    PYWT_AVAILABLE = True
except ImportError:
    PYWT_AVAILABLE = False


# ═══════════════════════════════════════════════════════════════
# 🌟 WAVELET LEADERS
# ═══════════════════════════════════════════════════════════════

def wavelet_leaders_multifractal(data, q_values=None, wavelet='db4', max_level=None):
    """
    Wavelet Leaders Multifractal Analysis
    
    Args:
        data: Time series
        q_values: List of q moments (default: [-5, -2, 0, 2, 5])
        wavelet: Wavelet type
        max_level: Maximum decomposition level
        
    Returns:
        dict: Multifractal features
    """
    if not PYWT_AVAILABLE:
        return {"wl_error": "PyWavelets not available"}
    
    if q_values is None:
        q_values = [-5, -2, 0, 2, 5]
    
    features = {}
    data = np.asarray(data, dtype=np.float64)
    
    if len(data) < 100:
        return features
    
    # Determine max level
    if max_level is None:
        max_level = min(8, int(np.log2(len(data))) - 2)
    
    try:
        # Wavelet decomposition
        coeffs = pywt.wavedec(data, wavelet, level=max_level)
        
        # Calculate wavelet leaders (supremum of wavelet coefficients)
        leaders = []
        for level_coeffs in coeffs[1:]:  # Skip approximation
            if len(level_coeffs) > 0:
                leaders.append(np.abs(level_coeffs))
        
        if not leaders:
            return features
        
        # Calculate structure functions for different q
        for q in q_values:
            S_q = []
            
            for leader in leaders:
                if len(leader) > 0:
                    if q == 0:
                        # Special case: log average
                        s = np.mean(np.log(leader + 1e-10))
                    else:
                        s = np.mean(np.power(leader + 1e-10, q))
                        if s > 0:
                            s = np.log(s) / q
                    S_q.append(s)
            
            if len(S_q) >= 3:
                # Linear fit to get scaling exponent
                scales = np.arange(1, len(S_q) + 1)
                slope = np.polyfit(np.log(scales), S_q, 1)[0]
                features[f"wl_h_q{int(q)}"] = float(slope)
        
        # Multifractal spectrum width
        if "wl_h_q-5" in features and "wl_h_q5" in features:
            features["wl_spectrum_width"] = float(
                abs(features["wl_h_q5"] - features["wl_h_q-5"])
            )
        
        # Asymmetry
        if "wl_h_q-2" in features and "wl_h_q2" in features and "wl_h_q0" in features:
            features["wl_asymmetry"] = float(
                (features["wl_h_q2"] - features["wl_h_q0"]) - 
                (features["wl_h_q0"] - features["wl_h_q-2"])
            )
        
    except Exception as e:
        features["wl_error"] = str(e)
    
    return features


# ═══════════════════════════════════════════════════════════════
# 🎯 FEATURE EXTRACTION
# ═══════════════════════════════════════════════════════════════

def extract_wavelet_leaders_features(prices):
    """
    Extract Wavelet Leaders multifractal features
    
    Args:
        prices: Price series
        
    Returns:
        dict: Wavelet Leaders features
    """
    features = {}
    
    if not PYWT_AVAILABLE:
        return features
    
    prices = np.asarray(prices, dtype=np.float64)
    
    if len(prices) < 100:
        return features
    
    # Calculate for prices
    wl_features = wavelet_leaders_multifractal(prices)
    features.update(wl_features)
    
    # Calculate for returns
    if len(prices) > 1:
        returns = np.diff(prices)
        if len(returns) >= 100:
            wl_returns = wavelet_leaders_multifractal(returns)
            for key, value in wl_returns.items():
                if not key.endswith("_error"):
                    features[f"{key}_returns"] = value
    
    return features
