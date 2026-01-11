#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚡🌟💎 ULTRA NECROZMA - NUMBA JIT FUNCTIONS 💎🌟⚡

Numba-optimized functions for maximum performance
"Compiled at light speed"

Technical: JIT-compiled numerical functions
- 10-100x speedup for heavy calculations
- Applied to Lyapunov, Entropies, DFA, RQA
"""

import numpy as np

# ═══════════════════════════════════════════════════════════════
# ⚡ NUMBA SETUP
# ═══════════════════════════════════════════════════════════════

try:
    from numba import njit, prange
    NUMBA_AVAILABLE = True
except ImportError:
    NUMBA_AVAILABLE = False
    # Dummy decorators if Numba not available
    def njit(*args, **kwargs):
        def decorator(func):
            return func
        if args and callable(args[0]):
            return args[0]
        return decorator
    prange = range


# ═══════════════════════════════════════════════════════════════
# 🔢 NUMBA-OPTIMIZED CALCULATIONS
# ═══════════════════════════════════════════════════════════════

@njit(cache=True, fastmath=True)
def numba_lyapunov_rosenstein(data, lag=1, max_steps=10):
    """
    Numba-optimized Lyapunov exponent (Rosenstein method)
    
    Args:
        data: Time series array
        lag: Time lag for nearest neighbors
        max_steps: Number of divergence steps to track
        
    Returns:
        float: Largest Lyapunov exponent
    """
    n = len(data)
    if n < 100:
        return 0.0
    
    # Embed in 2D
    embedded = np.zeros((n - lag, 2))
    for i in range(n - lag):
        embedded[i, 0] = data[i]
        embedded[i, 1] = data[i + lag]
    
    m = len(embedded)
    if m < max_steps + 10:
        return 0.0
    
    # Find nearest neighbors
    divergences = []
    
    for i in range(m - max_steps - 1):
        # Find nearest neighbor (excluding self and temporal neighbors)
        min_dist = np.inf
        min_j = -1
        
        for j in range(m - max_steps - 1):
            if abs(i - j) < 2:  # Skip self and immediate neighbors
                continue
            
            dist = np.sqrt((embedded[i, 0] - embedded[j, 0])**2 + 
                          (embedded[i, 1] - embedded[j, 1])**2)
            
            if dist < min_dist and dist > 0:
                min_dist = dist
                min_j = j
        
        if min_j == -1 or min_dist == 0:
            continue
        
        # Track divergence
        for k in range(1, max_steps + 1):
            if i + k >= m or min_j + k >= m:
                break
            
            new_dist = np.sqrt((embedded[i + k, 0] - embedded[min_j + k, 0])**2 +
                              (embedded[i + k, 1] - embedded[min_j + k, 1])**2)
            
            if new_dist > 0:
                log_div = np.log(new_dist / min_dist)
                divergences.append(log_div / k)
    
    if len(divergences) == 0:
        return 0.0
    
    return np.mean(np.array(divergences))


@njit(cache=True, fastmath=True)
def numba_sample_entropy(data, m=2, r=0.2):
    """
    Numba-optimized Sample Entropy
    
    Args:
        data: Time series array
        m: Pattern length
        r: Tolerance (fraction of std)
        
    Returns:
        float: Sample entropy
    """
    n = len(data)
    if n < m + 10:
        return 0.0
    
    tolerance = r * np.std(data)
    
    # Count template matches
    def count_matches(template_len):
        count = 0
        n_templates = n - template_len
        
        for i in range(n_templates - 1):
            for j in range(i + 1, n_templates):
                # Check if templates match
                match = True
                for k in range(template_len):
                    if abs(data[i + k] - data[j + k]) > tolerance:
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


@njit(cache=True, fastmath=True)
def numba_dfa(data, min_box=4, max_box=None):
    """
    Numba-optimized Detrended Fluctuation Analysis
    
    Args:
        data: Time series array
        min_box: Minimum box size
        max_box: Maximum box size
        
    Returns:
        float: DFA alpha exponent
    """
    n = len(data)
    if max_box is None:
        max_box = n // 4
    
    if n < min_box * 4:
        return 0.5
    
    # Integrate the series
    y = np.cumsum(data - np.mean(data))
    
    # Box sizes
    box_sizes = []
    current = min_box
    while current <= max_box:
        box_sizes.append(current)
        current = int(current * 1.2)
    
    if len(box_sizes) < 4:
        return 0.5
    
    fluctuations = np.zeros(len(box_sizes))
    
    for idx, box_size in enumerate(box_sizes):
        n_boxes = n // box_size
        
        if n_boxes < 1:
            continue
        
        box_fluct = 0.0
        
        for i in range(n_boxes):
            start = i * box_size
            end = (i + 1) * box_size
            
            if end > n:
                break
            
            # Fit line in box
            x = np.arange(box_size, dtype=np.float64)
            y_box = y[start:end]
            
            # Linear regression
            x_mean = np.mean(x)
            y_mean = np.mean(y_box)
            
            numerator = 0.0
            denominator = 0.0
            for j in range(box_size):
                numerator += (x[j] - x_mean) * (y_box[j] - y_mean)
                denominator += (x[j] - x_mean) ** 2
            
            if denominator > 0:
                slope = numerator / denominator
                intercept = y_mean - slope * x_mean
                
                # Calculate fluctuation
                for j in range(box_size):
                    fit = slope * x[j] + intercept
                    box_fluct += (y_box[j] - fit) ** 2
        
        fluctuations[idx] = np.sqrt(box_fluct / (n_boxes * box_size))
    
    # Linear regression on log-log plot
    valid = fluctuations > 0
    if np.sum(valid) < 3:
        return 0.5
    
    log_boxes = np.log(np.array(box_sizes, dtype=np.float64)[valid])
    log_flucts = np.log(fluctuations[valid])
    
    x_mean = np.mean(log_boxes)
    y_mean = np.mean(log_flucts)
    
    numerator = 0.0
    denominator = 0.0
    for i in range(len(log_boxes)):
        numerator += (log_boxes[i] - x_mean) * (log_flucts[i] - y_mean)
        denominator += (log_boxes[i] - x_mean) ** 2
    
    if denominator == 0:
        return 0.5
    
    alpha = numerator / denominator
    return alpha


@njit(cache=True, fastmath=True)
def numba_approximate_entropy(data, m=2, r=0.2):
    """
    Numba-optimized Approximate Entropy
    
    Args:
        data: Time series array
        m: Pattern length
        r: Tolerance (fraction of std)
        
    Returns:
        float: Approximate entropy
    """
    n = len(data)
    if n < m + 10:
        return 0.0
    
    tolerance = r * np.std(data)
    
    def phi(m_val):
        n_templates = n - m_val + 1
        patterns = np.zeros(n_templates)
        
        for i in range(n_templates):
            count = 0
            for j in range(n_templates):
                match = True
                for k in range(m_val):
                    if abs(data[i + k] - data[j + k]) > tolerance:
                        match = False
                        break
                if match:
                    count += 1
            
            patterns[i] = count / n_templates
        
        result = 0.0
        for i in range(n_templates):
            if patterns[i] > 0:
                result += np.log(patterns[i])
        
        return result / n_templates
    
    return phi(m) - phi(m + 1)


@njit(cache=True, parallel=True)
def numba_recurrence_matrix(data, threshold, dim=3, delay=1):
    """
    Numba-optimized recurrence matrix computation
    
    Args:
        data: Time series array
        threshold: Distance threshold
        dim: Embedding dimension
        delay: Time delay
        
    Returns:
        2D array: Recurrence matrix
    """
    n = len(data)
    n_vectors = n - (dim - 1) * delay
    
    if n_vectors < 10:
        return np.zeros((10, 10))
    
    # Build embedded vectors
    vectors = np.zeros((n_vectors, dim))
    for i in range(n_vectors):
        for j in range(dim):
            vectors[i, j] = data[i + j * delay]
    
    # Compute recurrence matrix
    rec_matrix = np.zeros((n_vectors, n_vectors))
    
    for i in prange(n_vectors):
        for j in range(n_vectors):
            dist = 0.0
            for k in range(dim):
                dist += (vectors[i, k] - vectors[j, k]) ** 2
            dist = np.sqrt(dist)
            
            if dist < threshold:
                rec_matrix[i, j] = 1.0
    
    return rec_matrix


@njit(cache=True, fastmath=True)
def numba_permutation_entropy(data, order=3, delay=1):
    """
    Numba-optimized Permutation Entropy
    
    Args:
        data: Time series array
        order: Permutation order
        delay: Time delay
        
    Returns:
        float: Permutation entropy (normalized)
    """
    n = len(data)
    n_patterns = n - (order - 1) * delay
    
    if n_patterns < order:
        return 0.0
    
    # Count permutation patterns
    max_patterns = 1
    for i in range(1, order + 1):
        max_patterns *= i
    
    pattern_counts = np.zeros(max_patterns)
    
    for i in range(n_patterns):
        # Extract pattern
        pattern = np.zeros(order)
        for j in range(order):
            pattern[j] = data[i + j * delay]
        
        # Get permutation rank
        ranks = np.zeros(order)
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
        multiplier = 1
        for j in range(order - 1, -1, -1):
            index += int(ranks[j]) * multiplier
            multiplier *= (j + 1)
        
        if index < max_patterns:
            pattern_counts[index] += 1
    
    # Calculate entropy
    entropy = 0.0
    for count in pattern_counts:
        if count > 0:
            prob = count / n_patterns
            entropy -= prob * np.log(prob)
    
    # Normalize
    max_entropy = np.log(max_patterns)
    if max_entropy > 0:
        return entropy / max_entropy
    
    return 0.0


# ═══════════════════════════════════════════════════════════════
# 📊 UTILITY FUNCTIONS
# ═══════════════════════════════════════════════════════════════

def get_numba_status():
    """Get Numba availability status"""
    return {
        "available": NUMBA_AVAILABLE,
        "functions": [
            "numba_lyapunov_rosenstein",
            "numba_sample_entropy",
            "numba_dfa",
            "numba_approximate_entropy",
            "numba_recurrence_matrix",
            "numba_permutation_entropy"
        ]
    }
