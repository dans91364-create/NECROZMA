#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚡🌟💎 ULTRA NECROZMA - RCMSE 💎🌟⚡

Refined Composite Multiscale Entropy
"Complexity across all time scales"

Technical: RCMSE Analysis
- Improved version of Multiscale Entropy
- Analyzes complexity at multiple scales
- Detects if market is simple at 1m but complex at 1h
- More stable than standard MSE
"""

import numpy as np

try:
    from numba import njit
    NUMBA_AVAILABLE = True
except ImportError:
    NUMBA_AVAILABLE = False
    def njit(*args, **kwargs):
        def decorator(func):
            return func
        if args and callable(args[0]):
            return args[0]
        return decorator


# ═══════════════════════════════════════════════════════════════
# 🌟 SAMPLE ENTROPY (Core function)
# ═══════════════════════════════════════════════════════════════

@njit(cache=True, fastmath=True)
def _sample_entropy_core(data, m, r):
    """
    Core Sample Entropy calculation (Numba-optimized)
    
    Args:
        data: Time series
        m: Pattern length
        r: Tolerance
        
    Returns:
        float: Sample entropy
    """
    n = len(data)
    
    if n < m + 10:
        return 0.0
    
    def count_matches(template_len):
        count = 0
        n_templates = n - template_len
        
        for i in range(n_templates - 1):
            for j in range(i + 1, n_templates):
                # Check if templates match
                match = True
                for k in range(template_len):
                    if abs(data[i + k] - data[j + k]) > r:
                        match = False
                        break
                if match:
                    count += 1
        
        return count
    
    B = count_matches(m)
    A = count_matches(m + 1)
    
    if B == 0 or A == 0:
        return 0.0
    
    return -np.log(A / B)


# ═══════════════════════════════════════════════════════════════
# 🌌 COARSE-GRAINING
# ═══════════════════════════════════════════════════════════════

def coarse_grain_standard(data, scale):
    """
    Standard coarse-graining for MSE
    
    Args:
        data: Time series
        scale: Scale factor
        
    Returns:
        array: Coarse-grained series
    """
    n = len(data)
    n_coarse = n // scale
    
    if n_coarse < 10:
        return np.array([])
    
    coarse = np.zeros(n_coarse)
    for i in range(n_coarse):
        coarse[i] = np.mean(data[i * scale:(i + 1) * scale])
    
    return coarse


def coarse_grain_refined(data, scale):
    """
    Refined coarse-graining for RCMSE
    
    Uses multiple starting points to reduce variance
    
    Args:
        data: Time series
        scale: Scale factor
        
    Returns:
        list: Multiple coarse-grained series
    """
    coarse_series = []
    
    for offset in range(scale):
        shifted_data = data[offset:]
        n = len(shifted_data)
        n_coarse = n // scale
        
        if n_coarse < 10:
            continue
        
        coarse = np.zeros(n_coarse)
        for i in range(n_coarse):
            start = i * scale
            end = (i + 1) * scale
            if end <= len(shifted_data):
                coarse[i] = np.mean(shifted_data[start:end])
        
        if len(coarse) >= 10:
            coarse_series.append(coarse)
    
    return coarse_series


# ═══════════════════════════════════════════════════════════════
# 📊 MULTISCALE ENTROPY
# ═══════════════════════════════════════════════════════════════

def multiscale_entropy(data, m=2, r=None, max_scale=20):
    """
    Standard Multiscale Entropy (MSE)
    
    Args:
        data: Time series
        m: Pattern length
        r: Tolerance (default: 0.15 * std)
        max_scale: Maximum scale factor
        
    Returns:
        dict: Entropy at each scale
    """
    data = np.asarray(data, dtype=np.float64)
    n = len(data)
    
    if r is None:
        r = 0.15 * np.std(data)
    
    # Adjust max_scale based on data length
    max_scale = min(max_scale, n // 20)
    
    if max_scale < 1:
        return {}
    
    mse_values = {}
    
    for scale in range(1, max_scale + 1):
        if scale == 1:
            coarse = data
        else:
            coarse = coarse_grain_standard(data, scale)
        
        if len(coarse) < m + 10:
            continue
        
        # Calculate tolerance for this scale
        r_scale = 0.15 * np.std(coarse)
        
        sampen = _sample_entropy_core(coarse, m, r_scale)
        mse_values[f"mse_scale_{scale}"] = float(sampen)
    
    return mse_values


def refined_composite_multiscale_entropy(data, m=2, r=None, max_scale=20):
    """
    Refined Composite Multiscale Entropy (RCMSE)
    
    More stable than MSE due to composite approach
    
    Args:
        data: Time series
        m: Pattern length
        r: Tolerance (default: 0.15 * std)
        max_scale: Maximum scale factor
        
    Returns:
        dict: RCMSE at each scale
    """
    data = np.asarray(data, dtype=np.float64)
    n = len(data)
    
    if r is None:
        r = 0.15 * np.std(data)
    
    # Adjust max_scale based on data length
    max_scale = min(max_scale, n // 20)
    
    if max_scale < 1:
        return {}
    
    rcmse_values = {}
    
    for scale in range(1, max_scale + 1):
        if scale == 1:
            # No coarse-graining at scale 1
            r_scale = 0.15 * np.std(data)
            sampen = _sample_entropy_core(data, m, r_scale)
            rcmse_values[f"rcmse_scale_{scale}"] = float(sampen)
        else:
            # Get multiple coarse-grained series
            coarse_series = coarse_grain_refined(data, scale)
            
            if not coarse_series:
                continue
            
            # Calculate entropy for each and average
            entropies = []
            for coarse in coarse_series:
                if len(coarse) >= m + 10:
                    r_scale = 0.15 * np.std(coarse)
                    sampen = _sample_entropy_core(coarse, m, r_scale)
                    if sampen > 0:
                        entropies.append(sampen)
            
            if entropies:
                rcmse_values[f"rcmse_scale_{scale}"] = float(np.mean(entropies))
    
    return rcmse_values


# ═══════════════════════════════════════════════════════════════
# 🎯 FEATURE EXTRACTION
# ═══════════════════════════════════════════════════════════════

def extract_rcmse_features(prices, m=2, max_scale=10):
    """
    Extract RCMSE features
    
    Args:
        prices: Price series
        m: Pattern length
        max_scale: Maximum scale
        
    Returns:
        dict: RCMSE features
    """
    features = {}
    prices = np.asarray(prices, dtype=np.float64)
    
    if len(prices) < 50:
        return features
    
    # Calculate RCMSE
    rcmse = refined_composite_multiscale_entropy(prices, m=m, max_scale=max_scale)
    
    # Add individual scale values
    features.update(rcmse)
    
    # Extract statistics
    if rcmse:
        values = list(rcmse.values())
        
        features["rcmse_mean"] = float(np.mean(values))
        features["rcmse_std"] = float(np.std(values))
        features["rcmse_min"] = float(np.min(values))
        features["rcmse_max"] = float(np.max(values))
        
        # Complexity Index (CI)
        # CI > 1: long-range correlations, complex
        # CI < 1: anti-correlated, simple
        # CI ~ 1: random, medium complexity
        if len(values) > 1:
            scale_1 = values[0] if values[0] > 0 else 0.001
            ci_values = [v / scale_1 for v in values[1:]]
            
            if ci_values:
                features["rcmse_complexity_index"] = float(np.mean(ci_values))
                features["rcmse_ci_slope"] = float(np.polyfit(range(len(ci_values)), ci_values, 1)[0])
        
        # Area under the curve
        features["rcmse_auc"] = float(np.trapz(values))
        
        # Slope of entropy across scales
        if len(values) >= 3:
            scales = np.arange(1, len(values) + 1)
            slope, intercept = np.polyfit(scales, values, 1)
            features["rcmse_slope"] = float(slope)
            features["rcmse_intercept"] = float(intercept)
    
    # Also calculate for returns
    if len(prices) > 1:
        returns = np.diff(prices)
        if len(returns) >= 50:
            rcmse_returns = refined_composite_multiscale_entropy(
                returns, m=m, max_scale=min(max_scale, len(returns) // 20)
            )
            
            if rcmse_returns:
                values_returns = list(rcmse_returns.values())
                features["rcmse_returns_mean"] = float(np.mean(values_returns))
                
                # Difference between price and return complexity
                if "rcmse_mean" in features:
                    features["rcmse_price_return_diff"] = float(
                        features["rcmse_mean"] - features["rcmse_returns_mean"]
                    )
    
    return features


def classify_complexity(rcmse_features):
    """
    Classify market complexity based on RCMSE
    
    Args:
        rcmse_features: RCMSE feature dictionary
        
    Returns:
        str: Complexity classification
    """
    if not rcmse_features or "rcmse_complexity_index" not in rcmse_features:
        return "UNKNOWN"
    
    ci = rcmse_features["rcmse_complexity_index"]
    
    if ci > 1.5:
        return "HIGHLY_COMPLEX"  # Long-range correlations
    elif ci > 1.1:
        return "COMPLEX"
    elif ci > 0.9:
        return "MEDIUM"  # Near random
    elif ci > 0.7:
        return "SIMPLE"
    else:
        return "VERY_SIMPLE"  # Anti-correlated
