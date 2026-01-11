#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚡🌟💎 ULTRA NECROZMA - DISPERSION ENTROPY 💎🌟⚡

Dispersion Entropy - Faster alternative to Sample Entropy
"Patterns dispersed through chaos"

Technical: Dispersion Entropy Analysis
- Faster than Sample Entropy (no distance calculations)
- More robust to parameter selection
- Uses symbolic dynamics approach
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
# 🌟 DISPERSION ENTROPY
# ═══════════════════════════════════════════════════════════════

@njit(cache=True, fastmath=True)
def _map_to_classes(data, n_classes):
    """
    Map time series to discrete classes using NCDF
    
    Args:
        data: Time series array
        n_classes: Number of classes (typically 3-10)
        
    Returns:
        array: Mapped classes
    """
    n = len(data)
    mapped = np.zeros(n, dtype=np.int32)
    
    # Sort to get empirical CDF
    sorted_data = np.sort(data)
    
    for i in range(n):
        # Find rank
        rank = 0
        for j in range(n):
            if sorted_data[j] < data[i]:
                rank += 1
        
        # Map to class (1 to n_classes)
        class_idx = int((rank * n_classes) / n) + 1
        if class_idx > n_classes:
            class_idx = n_classes
        if class_idx < 1:
            class_idx = 1
        
        mapped[i] = class_idx
    
    return mapped


@njit(cache=True, fastmath=True)
def _dispersion_patterns(mapped_classes, m, delay):
    """
    Extract dispersion patterns
    
    Args:
        mapped_classes: Mapped class array
        m: Embedding dimension
        delay: Time delay
        
    Returns:
        array: Pattern indices
    """
    n = len(mapped_classes)
    n_patterns = n - (m - 1) * delay
    
    if n_patterns <= 0:
        return np.zeros(0, dtype=np.int32)
    
    patterns = np.zeros(n_patterns, dtype=np.int32)
    n_classes = int(np.max(mapped_classes))
    
    for i in range(n_patterns):
        pattern_idx = 0
        multiplier = 1
        
        for j in range(m):
            class_val = mapped_classes[i + j * delay] - 1  # 0-indexed
            pattern_idx += class_val * multiplier
            multiplier *= n_classes
        
        patterns[i] = pattern_idx
    
    return patterns


def dispersion_entropy(data, m=2, c=3, delay=1, normalize=True):
    """
    Calculate Dispersion Entropy
    
    Args:
        data: Time series (1D array)
        m: Embedding dimension (default: 2)
        c: Number of classes (default: 3)
        delay: Time delay (default: 1)
        normalize: Whether to normalize by maximum entropy
        
    Returns:
        float: Dispersion entropy value
    """
    data = np.asarray(data, dtype=np.float64)
    n = len(data)
    
    if n < m * delay + 10:
        return 0.0
    
    # Remove mean
    data = data - np.mean(data)
    
    # Map to classes
    mapped = _map_to_classes(data, c)
    
    # Extract patterns
    patterns = _dispersion_patterns(mapped, m, delay)
    
    if len(patterns) == 0:
        return 0.0
    
    # Count pattern occurrences
    max_patterns = c ** m
    pattern_counts = np.zeros(max_patterns)
    
    for pattern in patterns:
        if pattern < max_patterns:
            pattern_counts[pattern] += 1
    
    # Calculate entropy
    total = len(patterns)
    entropy = 0.0
    
    for count in pattern_counts:
        if count > 0:
            prob = count / total
            entropy -= prob * np.log(prob)
    
    # Normalize if requested
    if normalize:
        max_entropy = np.log(max_patterns)
        if max_entropy > 0:
            entropy = entropy / max_entropy
    
    return float(entropy)


def dispersion_entropy_multiscale(data, m=2, c=3, delay=1, scales=None):
    """
    Multiscale Dispersion Entropy
    
    Args:
        data: Time series
        m: Embedding dimension
        c: Number of classes
        delay: Time delay
        scales: List of scales (default: [1, 2, 3, 4, 5])
        
    Returns:
        dict: Dispersion entropy at each scale
    """
    if scales is None:
        scales = [1, 2, 3, 4, 5]
    
    results = {}
    data = np.asarray(data, dtype=np.float64)
    
    for scale in scales:
        if scale == 1:
            # No coarse-graining
            coarse = data
        else:
            # Coarse-grain the series
            n_coarse = len(data) // scale
            if n_coarse < m * delay + 10:
                continue
            
            coarse = np.zeros(n_coarse)
            for i in range(n_coarse):
                coarse[i] = np.mean(data[i * scale:(i + 1) * scale])
        
        # Calculate dispersion entropy
        de = dispersion_entropy(coarse, m, c, delay, normalize=True)
        results[f"de_scale_{scale}"] = de
    
    return results


# ═══════════════════════════════════════════════════════════════
# 🎯 FEATURE EXTRACTION
# ═══════════════════════════════════════════════════════════════

def extract_dispersion_entropy_features(prices, m_values=None, c_values=None):
    """
    Extract dispersion entropy features with multiple parameters
    
    Args:
        prices: Price series
        m_values: List of embedding dimensions (default: [2, 3])
        c_values: List of class counts (default: [3, 5])
        
    Returns:
        dict: Dispersion entropy features
    """
    if m_values is None:
        m_values = [2, 3]
    if c_values is None:
        c_values = [3, 5]
    
    features = {}
    prices = np.asarray(prices, dtype=np.float64)
    
    if len(prices) < 30:
        return features
    
    # Single-scale features
    for m in m_values:
        for c in c_values:
            de = dispersion_entropy(prices, m=m, c=c, delay=1, normalize=True)
            features[f"dispersion_entropy_m{m}_c{c}"] = de
    
    # Multiscale feature (default parameters)
    multiscale = dispersion_entropy_multiscale(prices, m=2, c=3, delay=1)
    features.update(multiscale)
    
    # Statistics of multiscale values
    if multiscale:
        de_values = list(multiscale.values())
        if de_values:
            features["de_multiscale_mean"] = float(np.mean(de_values))
            features["de_multiscale_std"] = float(np.std(de_values))
            features["de_multiscale_min"] = float(np.min(de_values))
            features["de_multiscale_max"] = float(np.max(de_values))
            
            # Complexity index (changes across scales)
            if len(de_values) > 1:
                features["de_complexity_index"] = float(np.std(de_values))
    
    return features
