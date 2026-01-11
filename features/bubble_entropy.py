#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚡🌟💎 ULTRA NECROZMA - BUBBLE ENTROPY 💎🌟⚡

Bubble Entropy - Parameter-free entropy measure
"No tuning needed, pure chaos measurement"

Technical: Bubble Entropy Analysis
- NO parameters needed (no r, no m)
- Based on bubble sort algorithm
- More reproducible than Sample/Approximate Entropy
- Measures disorder in the sorting process
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
# 🌟 BUBBLE ENTROPY
# ═══════════════════════════════════════════════════════════════

@njit(cache=True, fastmath=True)
def _bubble_sort_swaps(data):
    """
    Count swaps needed in bubble sort
    
    Args:
        data: Array to sort
        
    Returns:
        int: Number of swaps
    """
    n = len(data)
    arr = data.copy()
    swaps = 0
    
    for i in range(n):
        for j in range(0, n - i - 1):
            if arr[j] > arr[j + 1]:
                # Swap
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                swaps += 1
    
    return swaps


@njit(cache=True, fastmath=True)
def _rank_data(data):
    """
    Convert data to ranks (1 to n)
    
    Args:
        data: Data array
        
    Returns:
        array: Ranks
    """
    n = len(data)
    ranks = np.zeros(n, dtype=np.int32)
    
    for i in range(n):
        rank = 1
        for j in range(n):
            if data[j] < data[i]:
                rank += 1
            elif data[j] == data[i] and j < i:
                rank += 1
        ranks[i] = rank
    
    return ranks


def bubble_entropy(data, window_size=None):
    """
    Calculate Bubble Entropy
    
    The entropy is based on the number of swaps needed to sort
    subsequences. More chaotic series require more swaps.
    
    Args:
        data: Time series (1D array)
        window_size: Size of sliding window (default: sqrt(n))
        
    Returns:
        float: Bubble entropy value
    """
    data = np.asarray(data, dtype=np.float64)
    n = len(data)
    
    if n < 10:
        return 0.0
    
    # Default window size
    if window_size is None:
        window_size = max(3, int(np.sqrt(n)))
    
    if window_size > n:
        window_size = n
    
    # Convert to ranks to handle different scales
    ranks = _rank_data(data)
    
    # Slide window and count swaps
    n_windows = n - window_size + 1
    swap_counts = []
    
    for i in range(n_windows):
        window = ranks[i:i + window_size].astype(np.float64)
        swaps = _bubble_sort_swaps(window)
        swap_counts.append(swaps)
    
    if not swap_counts:
        return 0.0
    
    # Maximum possible swaps for window
    max_swaps = (window_size * (window_size - 1)) / 2
    
    # Normalize swap counts
    if max_swaps > 0:
        normalized_swaps = [s / max_swaps for s in swap_counts]
    else:
        return 0.0
    
    # Calculate entropy of swap distribution
    # Discretize into bins
    n_bins = min(10, window_size)
    hist, _ = np.histogram(normalized_swaps, bins=n_bins, range=(0, 1))
    
    # Calculate entropy
    total = np.sum(hist)
    if total == 0:
        return 0.0
    
    entropy = 0.0
    for count in hist:
        if count > 0:
            prob = count / total
            entropy -= prob * np.log(prob)
    
    # Normalize by max entropy
    max_entropy = np.log(n_bins)
    if max_entropy > 0:
        entropy = entropy / max_entropy
    
    return float(entropy)


def bubble_entropy_v2(data):
    """
    Alternative Bubble Entropy calculation
    
    This version uses the total number of swaps as a measure
    of disorder, normalized by the maximum possible.
    
    Args:
        data: Time series
        
    Returns:
        float: Normalized bubble entropy (0 = sorted, 1 = reverse sorted)
    """
    data = np.asarray(data, dtype=np.float64)
    n = len(data)
    
    if n < 3:
        return 0.0
    
    # Rank the data
    ranks = _rank_data(data).astype(np.float64)
    
    # Count swaps
    total_swaps = _bubble_sort_swaps(ranks)
    
    # Maximum possible swaps (reverse sorted)
    max_swaps = (n * (n - 1)) / 2
    
    if max_swaps == 0:
        return 0.0
    
    # Normalize
    be = total_swaps / max_swaps
    
    return float(be)


def bubble_entropy_local(data, window_size=None, step=1):
    """
    Local Bubble Entropy (sliding window)
    
    Args:
        data: Time series
        window_size: Window size (default: sqrt(n))
        step: Step size for sliding
        
    Returns:
        array: Bubble entropy at each position
    """
    data = np.asarray(data, dtype=np.float64)
    n = len(data)
    
    if window_size is None:
        window_size = max(10, int(np.sqrt(n)))
    
    if window_size > n:
        window_size = n
    
    local_be = []
    
    for i in range(0, n - window_size + 1, step):
        window = data[i:i + window_size]
        be = bubble_entropy_v2(window)
        local_be.append(be)
    
    return np.array(local_be)


# ═══════════════════════════════════════════════════════════════
# 🎯 FEATURE EXTRACTION
# ═══════════════════════════════════════════════════════════════

def extract_bubble_entropy_features(prices):
    """
    Extract bubble entropy features
    
    Args:
        prices: Price series
        
    Returns:
        dict: Bubble entropy features
    """
    features = {}
    prices = np.asarray(prices, dtype=np.float64)
    
    if len(prices) < 10:
        return features
    
    # Global bubble entropy (method 1)
    be1 = bubble_entropy(prices)
    features["bubble_entropy"] = be1
    
    # Global bubble entropy (method 2)
    be2 = bubble_entropy_v2(prices)
    features["bubble_entropy_v2"] = be2
    
    # Local bubble entropy statistics
    if len(prices) >= 20:
        window_size = max(10, int(np.sqrt(len(prices))))
        local_be = bubble_entropy_local(prices, window_size=window_size)
        
        if len(local_be) > 0:
            features["bubble_entropy_local_mean"] = float(np.mean(local_be))
            features["bubble_entropy_local_std"] = float(np.std(local_be))
            features["bubble_entropy_local_min"] = float(np.min(local_be))
            features["bubble_entropy_local_max"] = float(np.max(local_be))
            
            # Trend in local entropy
            if len(local_be) > 1:
                x = np.arange(len(local_be))
                slope = np.polyfit(x, local_be, 1)[0]
                features["bubble_entropy_local_trend"] = float(slope)
    
    # Apply to returns as well
    if len(prices) > 1:
        returns = np.diff(prices)
        if len(returns) >= 10:
            be_returns = bubble_entropy_v2(returns)
            features["bubble_entropy_returns"] = be_returns
    
    return features
