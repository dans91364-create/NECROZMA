#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚡🌟💎 ULTRA NECROZMA - COMPLEXITY-ENTROPY PLANE 💎🌟⚡

Complexity-Entropy Plane (Bandt-Pompe)
"Where chaos meets order in 2D space"

Technical: Bandt-Pompe Complexity-Entropy Analysis
- Maps series to 2D plane (Entropy H vs Complexity C)
- Permutation Entropy for randomness
- Statistical Complexity for structure
- Excellent for regime classification
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
# 🌟 PERMUTATION ENTROPY
# ═══════════════════════════════════════════════════════════════

@njit(cache=True, fastmath=True)
def _ordinal_patterns(data, order, delay):
    """
    Extract ordinal patterns from time series
    
    Args:
        data: Time series
        order: Pattern order (dimension)
        delay: Time delay
        
    Returns:
        array: Pattern indices
    """
    n = len(data)
    n_patterns = n - (order - 1) * delay
    
    if n_patterns <= 0:
        return np.zeros(0, dtype=np.int32)
    
    patterns = np.zeros(n_patterns, dtype=np.int32)
    
    for i in range(n_patterns):
        # Extract values
        pattern = np.zeros(order)
        for j in range(order):
            pattern[j] = data[i + j * delay]
        
        # Get ordinal pattern (permutation)
        ranks = np.zeros(order, dtype=np.int32)
        for j in range(order):
            rank = 0
            for k in range(order):
                if pattern[k] < pattern[j]:
                    rank += 1
                elif pattern[k] == pattern[j] and k < j:
                    rank += 1
            ranks[j] = rank
        
        # Convert to index
        index = 0
        factorial = 1
        for j in range(order):
            index += ranks[order - 1 - j] * factorial
            factorial *= (j + 1)
        
        patterns[i] = index
    
    return patterns


def permutation_entropy(data, order=3, delay=1, normalize=True):
    """
    Calculate Permutation Entropy
    
    Args:
        data: Time series
        order: Pattern order (3-7 recommended)
        delay: Time delay
        normalize: Normalize by maximum entropy
        
    Returns:
        float: Permutation entropy
    """
    data = np.asarray(data, dtype=np.float64)
    
    # Get ordinal patterns
    patterns = _ordinal_patterns(data, order, delay)
    
    if len(patterns) == 0:
        return 0.0
    
    # Count patterns
    max_patterns = 1
    for i in range(1, order + 1):
        max_patterns *= i
    
    pattern_counts = np.zeros(max_patterns)
    for p in patterns:
        if 0 <= p < max_patterns:
            pattern_counts[p] += 1
    
    # Calculate probabilities
    total = len(patterns)
    probabilities = pattern_counts / total
    
    # Calculate entropy
    entropy = 0.0
    for prob in probabilities:
        if prob > 0:
            entropy -= prob * np.log(prob)
    
    # Normalize if requested
    if normalize:
        max_entropy = np.log(max_patterns)
        if max_entropy > 0:
            entropy /= max_entropy
    
    return float(entropy)


# ═══════════════════════════════════════════════════════════════
# 💎 STATISTICAL COMPLEXITY
# ═══════════════════════════════════════════════════════════════

def jensen_shannon_divergence(p, q):
    """
    Calculate Jensen-Shannon divergence between two distributions
    
    Args:
        p, q: Probability distributions
        
    Returns:
        float: JSD
    """
    # Ensure same length
    if len(p) != len(q):
        return 0.0
    
    # Mixture distribution
    m = 0.5 * (p + q)
    
    # KL divergences
    def kl_div(p_dist, q_dist):
        kl = 0.0
        for i in range(len(p_dist)):
            if p_dist[i] > 0 and q_dist[i] > 0:
                kl += p_dist[i] * np.log(p_dist[i] / q_dist[i])
        return kl
    
    jsd = 0.5 * kl_div(p, m) + 0.5 * kl_div(q, m)
    
    return jsd


def statistical_complexity(data, order=3, delay=1):
    """
    Calculate Statistical Complexity (Bandt-Pompe)
    
    C = H * Q, where:
    - H is normalized permutation entropy
    - Q is disequilibrium (distance from uniform distribution)
    
    Args:
        data: Time series
        order: Pattern order
        delay: Time delay
        
    Returns:
        tuple: (complexity, entropy, disequilibrium)
    """
    data = np.asarray(data, dtype=np.float64)
    
    # Get ordinal patterns
    patterns = _ordinal_patterns(data, order, delay)
    
    if len(patterns) == 0:
        return 0.0, 0.0, 0.0
    
    # Count patterns
    max_patterns = 1
    for i in range(1, order + 1):
        max_patterns *= i
    
    pattern_counts = np.zeros(max_patterns)
    for p in patterns:
        if 0 <= p < max_patterns:
            pattern_counts[p] += 1
    
    # Probability distribution
    total = len(patterns)
    P = pattern_counts / total
    
    # Permutation entropy (normalized)
    H = 0.0
    for prob in P:
        if prob > 0:
            H -= prob * np.log(prob)
    
    max_entropy = np.log(max_patterns)
    if max_entropy > 0:
        H_norm = H / max_entropy
    else:
        H_norm = 0.0
    
    # Uniform distribution
    P_uniform = np.ones(max_patterns) / max_patterns
    
    # Disequilibrium (Jensen-Shannon divergence)
    Q = jensen_shannon_divergence(P, P_uniform)
    
    # Normalize Q
    Q_max = jensen_shannon_divergence(
        np.array([1.0] + [0.0] * (max_patterns - 1)),
        P_uniform
    )
    
    if Q_max > 0:
        Q_norm = Q / Q_max
    else:
        Q_norm = 0.0
    
    # Statistical Complexity
    C = H_norm * Q_norm
    
    return float(C), float(H_norm), float(Q_norm)


# ═══════════════════════════════════════════════════════════════
# 🎯 COMPLEXITY-ENTROPY PLANE
# ═══════════════════════════════════════════════════════════════

def complexity_entropy_plane(data, order=3, delay=1):
    """
    Map time series to Complexity-Entropy plane
    
    Returns coordinates (H, C) that can be used for classification
    
    Args:
        data: Time series
        order: Pattern order
        delay: Time delay
        
    Returns:
        dict: H, C, Q, and regime classification
    """
    C, H, Q = statistical_complexity(data, order, delay)
    
    # Classify regime based on position in H-C plane
    regime = classify_hc_regime(H, C)
    
    return {
        "ce_entropy": H,
        "ce_complexity": C,
        "ce_disequilibrium": Q,
        "ce_regime": regime
    }


def classify_hc_regime(H, C):
    """
    Classify regime based on position in H-C plane
    
    Args:
        H: Normalized entropy
        C: Statistical complexity
        
    Returns:
        str: Regime classification
    """
    # High entropy, low complexity: Random
    if H > 0.8 and C < 0.2:
        return "RANDOM"
    
    # Low entropy, low complexity: Deterministic/Periodic
    if H < 0.3 and C < 0.3:
        return "PERIODIC"
    
    # Medium entropy, high complexity: Chaotic
    if 0.4 < H < 0.8 and C > 0.3:
        return "CHAOTIC"
    
    # High entropy, high complexity: Complex
    if H > 0.6 and C > 0.3:
        return "COMPLEX"
    
    # Low entropy, medium complexity: Structured
    if H < 0.5 and 0.2 < C < 0.5:
        return "STRUCTURED"
    
    # Default
    return "TRANSITIONAL"


# ═══════════════════════════════════════════════════════════════
# 📊 FEATURE EXTRACTION
# ═══════════════════════════════════════════════════════════════

def extract_complexity_entropy_features(prices, orders=None, delays=None):
    """
    Extract Complexity-Entropy plane features
    
    Args:
        prices: Price series
        orders: List of pattern orders (default: [3, 4, 5])
        delays: List of delays (default: [1, 2])
        
    Returns:
        dict: Complexity-Entropy features
    """
    if orders is None:
        orders = [3, 4, 5]
    if delays is None:
        delays = [1, 2]
    
    features = {}
    prices = np.asarray(prices, dtype=np.float64)
    
    if len(prices) < 50:
        return features
    
    # Calculate for different parameters
    for order in orders:
        for delay in delays:
            if len(prices) < (order - 1) * delay + 20:
                continue
            
            ce_plane = complexity_entropy_plane(prices, order, delay)
            
            prefix = f"ce_o{order}_d{delay}"
            features[f"{prefix}_entropy"] = ce_plane["ce_entropy"]
            features[f"{prefix}_complexity"] = ce_plane["ce_complexity"]
            features[f"{prefix}_disequilibrium"] = ce_plane["ce_disequilibrium"]
    
    # Default configuration for regime
    if len(prices) >= 30:
        ce_default = complexity_entropy_plane(prices, order=3, delay=1)
        features["ce_regime"] = ce_default["ce_regime"]
        features["ce_entropy_main"] = ce_default["ce_entropy"]
        features["ce_complexity_main"] = ce_default["ce_complexity"]
    
    # Calculate for returns as well
    if len(prices) > 1:
        returns = np.diff(prices)
        if len(returns) >= 30:
            ce_returns = complexity_entropy_plane(returns, order=3, delay=1)
            features["ce_returns_entropy"] = ce_returns["ce_entropy"]
            features["ce_returns_complexity"] = ce_returns["ce_complexity"]
            features["ce_returns_regime"] = ce_returns["ce_regime"]
    
    # Distance from origin (measure of overall disorder)
    if "ce_entropy_main" in features and "ce_complexity_main" in features:
        H = features["ce_entropy_main"]
        C = features["ce_complexity_main"]
        features["ce_distance_origin"] = float(np.sqrt(H**2 + C**2))
        
        # Angle in H-C plane
        features["ce_angle"] = float(np.arctan2(C, H))
    
    return features
