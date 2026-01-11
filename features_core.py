#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚡🌟💎 ULTRA NECROZMA - CORE FEATURES 💎🌟⚡

Core Feature Extraction:  The Foundation of Light
"The prism's base frequencies that split all light"

Technical:  Core time series feature extraction
- Derivatives (D1-D5)
- Statistical Features
- Spectral Analysis (FFT, Wavelets)
- Chaos Theory (Lyapunov, DFA, Hurst, Fractal)
- Entropy Measures (Shannon, Sample, Permutation, Approximate)
"""

import numpy as np
from scipy import stats, signal
from scipy.fft import fft, fftfreq
import warnings

warnings.filterwarnings("ignore")

# ═══════════════════════════════════════════════════════════════
# ⚡ NUMBA JIT COMPILATION (Light Speed)
# ═══════════════════════════════════════════════════════════════

try:
    from numba import njit, prange
    NUMBA_AVAILABLE = True
    print("⚡ Numba JIT:  ENABLED (Light Speed Mode)")
except ImportError:
    NUMBA_AVAILABLE = False
    print("⚠️ Numba not available, using pure NumPy")
    def njit(*args, **kwargs):
        def decorator(func):
            return func
        return decorator
    prange = range


# ═══════════════════════════════════════════════════════════════
# 📊 GRUPO 0: STATISTICAL FEATURES (Foundation)
# Technical: Basic descriptive statistics
# ═══════════════════════════════════════════════════════════════

def statistical_features(prices):
    """
    Basic Statistical Features (Crystal Foundation)
    Technical: Descriptive statistics and moments
    """
    features = {}
    
    if len(prices) < 5:
        return features
    
    prices = np.asarray(prices, dtype=np.float64)
    
    # Central tendency
    features["stat_mean"] = float(np. mean(prices))
    features["stat_median"] = float(np.median(prices))
    
    # Dispersion
    features["stat_std"] = float(np.std(prices))
    features["stat_var"] = float(np.var(prices))
    features["stat_range"] = float(np.max(prices) - np.min(prices))
    features["stat_iqr"] = float(np. percentile(prices, 75) - np.percentile(prices, 25))
    
    # Shape
    features["stat_skewness"] = float(stats.skew(prices))
    features["stat_kurtosis"] = float(stats.kurtosis(prices))
    
    # Extremes
    features["stat_min"] = float(np.min(prices))
    features["stat_max"] = float(np.max(prices))
    features["stat_q10"] = float(np.percentile(prices, 10))
    features["stat_q90"] = float(np.percentile(prices, 90))
    
    # Variation
    mean_val = np.mean(prices)
    if mean_val != 0:
        features["stat_cv"] = float(np.std(prices) / abs(mean_val))  # Coefficient of variation
    
    # Trend
    x = np.arange(len(prices))
    slope, intercept, r_value, _, _ = stats.linregress(x, prices)
    features["stat_trend_slope"] = float(slope)
    features["stat_trend_r2"] = float(r_value ** 2)
    
    # Autocorrelation lag-1
    if len(prices) > 1:
        autocorr = np.corrcoef(prices[:-1], prices[1:])[0, 1]
        features["stat_autocorr_1"] = float(autocorr) if not np.isnan(autocorr) else 0.0
    
    return features


# ═══════════════════════════════════════════════════════════════
# 🌟 GRUPO 1: DERIVATIVES (Velocity, Acceleration, Jerk...)
# Technical: Numerical differentiation up to 5th order
# ═══════════════════════════════════════════════════════════════

def calculate_derivatives(prices):
    """
    Calculate derivatives up to 5th order (Motion Analysis)
    Technical: Discrete differentiation using np.diff
    
    D1 = Velocity (price momentum)
    D2 = Acceleration (momentum change)
    D3 = Jerk (acceleration change)
    D4 = Snap (jerk change)
    D5 = Crackle (snap change)
    """
    features = {}
    
    if len(prices) < 6:
        return features
    
    prices = np.asarray(prices, dtype=np.float64)
    
    # D1: First derivative (Velocity / Momentum)
    d1 = np.diff(prices)
    features. update({
        "d1_mean": float(np. mean(d1)),
        "d1_std": float(np.std(d1)),
        "d1_current": float(d1[-1]),
        "d1_max": float(np.max(d1)),
        "d1_min": float(np.min(d1)),
        "d1_abs_mean": float(np.mean(np.abs(d1))),
        "d1_positive_ratio": float(np.mean(d1 > 0)),
    })
    
    if len(d1) < 2:
        return features
    
    # D2: Second derivative (Acceleration)
    d2 = np. diff(d1)
    features.update({
        "d2_mean": float(np.mean(d2)),
        "d2_std": float(np. std(d2)),
        "d2_current": float(d2[-1]),
        "d2_abs_mean": float(np.mean(np.abs(d2))),
    })
    
    if len(d2) < 2:
        return features
    
    # D3: Third derivative (Jerk)
    d3 = np.diff(d2)
    features.update({
        "d3_mean":  float(np.mean(d3)),
        "d3_std": float(np.std(d3)),
        "d3_current": float(d3[-1]),
    })
    
    if len(d3) < 2:
        return features
    
    # D4: Fourth derivative (Snap)
    d4 = np.diff(d3)
    features.update({
        "d4_mean": float(np. mean(d4)),
        "d4_current": float(d4[-1]),
    })
    
    if len(d4) < 2:
        return features
    
    # D5: Fifth derivative (Crackle)
    d5 = np.diff(d4)
    features.update({
        "d5_mean":  float(np.mean(d5)),
        "d5_current": float(d5[-1]),
    })
    
    return features


# ═══════════════════════════════════════════════════════════════
# 💎 GRUPO 2: SPECTRAL ANALYSIS (FFT + Wavelets)
# Technical: Frequency domain analysis
# ═══════════════════════════════════════════════════════════════

def spectral_features(prices):
    """
    FFT-based spectral decomposition (Prismatic Light Analysis)
    Technical: Fast Fourier Transform for frequency domain features
    """
    features = {}
    
    if len(prices) < 16:
        return features
    
    prices = np.asarray(prices, dtype=np.float64)
    
    try:
        # Center the data
        prices_centered = prices - np.mean(prices)
        
        # FFT
        fft_vals = fft(prices_centered)
        power = np.abs(fft_vals) ** 2
        freqs = fftfreq(len(prices))
        
        # Positive frequencies only
        n = len(prices) // 2
        power_pos = power[1:n]
        freqs_pos = freqs[1:n]
        
        if len(power_pos) == 0:
            return features
        
        total_power = np.sum(power_pos)
        
        if total_power == 0:
            return features
        
        # Top 5 dominant frequencies
        top_idx = np.argsort(power_pos)[::-1][:5]
        for i, idx in enumerate(top_idx):
            if idx < len(freqs_pos):
                features[f"fft_freq_{i+1}"] = float(freqs_pos[idx])
                features[f"fft_power_{i+1}"] = float(power_pos[idx])
        
        # Spectral bands energy distribution
        n_bands = 4
        band_size = len(power_pos) // n_bands
        if band_size > 0:
            for i in range(n_bands):
                start = i * band_size
                end = start + band_size if i < n_bands - 1 else len(power_pos)
                band_power = np.sum(power_pos[start:end])
                features[f"fft_band_{i+1}_ratio"] = float(band_power / total_power)
        
        # Spectral centroid (center of mass of spectrum)
        spectral_centroid = np.sum(freqs_pos * power_pos) / total_power
        features["spectral_centroid"] = float(spectral_centroid)
        
        # Spectral spread (standard deviation around centroid)
        spectral_spread = np.sqrt(
            np.sum(((freqs_pos - spectral_centroid) ** 2) * power_pos) / total_power
        )
        features["spectral_spread"] = float(spectral_spread)
        
        # Spectral flatness (measure of noise vs tonal)
        geometric_mean = np.exp(np.mean(np.log(power_pos + 1e-10)))
        arithmetic_mean = np.mean(power_pos)
        features["spectral_flatness"] = float(geometric_mean / (arithmetic_mean + 1e-10))
        
        # Spectral entropy
        power_norm = power_pos / (total_power + 1e-10)
        spectral_entropy = -np.sum(power_norm * np.log2(power_norm + 1e-10))
        features["spectral_entropy"] = float(spectral_entropy)
        
        # Spectral rolloff (frequency below which 85% of energy)
        cumsum = np.cumsum(power_pos)
        rolloff_idx = np.searchsorted(cumsum, 0.85 * total_power)
        if rolloff_idx < len(freqs_pos):
            features["spectral_rolloff"] = float(freqs_pos[rolloff_idx])
        
    except Exception: 
        pass
    
    return features


def wavelet_features(prices, levels=5):
    """
    Multi-scale wavelet analysis (Crystal Refraction)
    Technical: Haar wavelet decomposition
    """
    features = {}
    
    if len(prices) < 2 ** levels:
        return features
    
    prices = np.asarray(prices, dtype=np.float64)
    
    try:
        signal_data = prices.copy()
        total_energy = 0.0
        level_energies = []
        
        for level in range(1, levels + 1):
            if len(signal_data) < 2:
                break
            
            # Downsample
            n = len(signal_data) // 2 * 2
            signal_data = signal_data[: n]
            
            # Approximation and detail coefficients
            approx = (signal_data[:: 2] + signal_data[1::2]) / 2
            detail = (signal_data[::2] - signal_data[1::2]) / 2
            
            # Features from detail coefficients
            energy = float(np.sum(detail ** 2))
            level_energies.append(energy)
            total_energy += energy
            
            features[f"wavelet_d{level}_energy"] = energy
            features[f"wavelet_d{level}_std"] = float(np.std(detail))
            features[f"wavelet_d{level}_max"] = float(np.max(np.abs(detail)))
            features[f"wavelet_d{level}_mean"] = float(np.mean(np.abs(detail)))
            
            signal_data = approx
        
        # Energy ratios
        if total_energy > 0:
            for i, energy in enumerate(level_energies, 1):
                features[f"wavelet_d{i}_ratio"] = float(energy / total_energy)
        
        # Final approximation features
        if len(signal_data) > 0:
            features["wavelet_approx_mean"] = float(np.mean(signal_data))
            features["wavelet_approx_std"] = float(np.std(signal_data))
            features["wavelet_approx_energy"] = float(np.sum(signal_data ** 2))
        
    except Exception:
        pass
    
    return features


# ═══════════════════════════════════════════════════════════════
# 🔥 GRUPO 3: CHAOS THEORY (Lyapunov, DFA, Fractal, Hurst)
# Technical: Nonlinear dynamics and chaos measures
# ═══════════════════════════════════════════════════════════════

if NUMBA_AVAILABLE: 
    @njit(cache=True)
    def _lyapunov_core(prices):
        """Numba-optimized Lyapunov calculation core"""
        n = len(prices)
        divergences = []
        lags = [3, 5, 10, 15, 20]
        
        for i in range(n - 20):
            d0 = abs(prices[i] - prices[i + 1])
            if d0 > 1e-10:
                for lag in lags:
                    if i + lag + 1 < n:
                        dt = abs(prices[i + lag] - prices[i + lag + 1])
                        if dt > 1e-10:
                            divergences.append(np.log(dt / d0) / lag)
        
        return divergences
else:
    def _lyapunov_core(prices):
        """Pure Python Lyapunov calculation"""
        n = len(prices)
        divergences = []
        lags = [3, 5, 10, 15, 20]
        
        for i in range(n - 20):
            d0 = abs(prices[i] - prices[i + 1])
            if d0 > 1e-10:
                for lag in lags: 
                    if i + lag + 1 < n:
                        dt = abs(prices[i + lag] - prices[i + lag + 1])
                        if dt > 1e-10:
                            divergences.append(np.log(dt / d0) / lag)
        
        return divergences


def lyapunov_exponent(prices):
    """
    Lyapunov Exponent (Chaos Sensitivity / Giratina's Distortion)
    Technical: Measures sensitivity to initial conditions
    
    > 0: Chaotic (sensitive to initial conditions)
    ≈ 0: Edge of chaos
    < 0: Stable/periodic
    """
    if len(prices) < 30:
        return 0.0
    
    prices = np. asarray(prices, dtype=np.float64)
    
    try:
        divergences = _lyapunov_core(prices)
        return float(np.mean(divergences)) if len(divergences) > 0 else 0.0
    except: 
        return 0.0


if NUMBA_AVAILABLE: 
    @njit(cache=True)
    def _dfa_core(prices):
        """Numba-optimized DFA calculation core"""
        n = len(prices)
        
        # Integrate the series
        mean_val = np.mean(prices)
        y = np.zeros(n)
        cumsum = 0.0
        for i in range(n):
            cumsum += prices[i] - mean_val
            y[i] = cumsum
        
        # Scales
        scales = np.array([4, 8, 16, 32, 64])
        fluctuations = np.zeros(len(scales))
        
        for s_idx in range(len(scales)):
            s = scales[s_idx]
            if s >= n:
                continue
            
            n_segments = n // s
            if n_segments == 0:
                continue
            
            f2 = 0.0
            for v in range(n_segments):
                start = v * s
                
                # Linear fit manually
                x_mean = (s - 1) / 2.0
                y_mean = 0.0
                for i in range(s):
                    y_mean += y[start + i]
                y_mean /= s
                
                num = 0.0
                den = 0.0
                for i in range(s):
                    x_diff = i - x_mean
                    num += x_diff * (y[start + i] - y_mean)
                    den += x_diff * x_diff
                
                if den > 1e-10:
                    slope = num / den
                    intercept = y_mean - slope * x_mean
                    
                    # Variance from trend
                    var = 0.0
                    for i in range(s):
                        trend = intercept + slope * i
                        diff = y[start + i] - trend
                        var += diff * diff
                    var /= s
                    f2 += var
            
            if n_segments > 0:
                fluctuations[s_idx] = np.sqrt(f2 / n_segments)
        
        return scales, fluctuations
else: 
    def _dfa_core(prices):
        """Pure NumPy DFA calculation"""
        n = len(prices)
        y = np.cumsum(prices - np.mean(prices))
        
        scales = np.array([4, 8, 16, 32, 64])
        fluctuations = np.zeros(len(scales))
        
        for s_idx, s in enumerate(scales):
            if s >= n:
                continue
            
            n_segments = n // s
            if n_segments == 0:
                continue
            
            f2 = 0.0
            for v in range(n_segments):
                segment = y[v * s:(v + 1) * s]
                x = np.arange(s)
                coeffs = np.polyfit(x, segment, 1)
                trend = np.polyval(coeffs, x)
                f2 += np.mean((segment - trend) ** 2)
            
            fluctuations[s_idx] = np.sqrt(f2 / n_segments)
        
        return scales, fluctuations


def dfa_alpha(prices):
    """
    Detrended Fluctuation Analysis - DFA Alpha (Dialga's Temporal Signature)
    Technical: Measures long-range correlations
    
    α ≈ 0.5: Random walk (no correlation)
    α > 0.5: Persistent (trending)
    α < 0.5: Anti-persistent (mean-reverting)
    """
    if len(prices) < 64:
        return 0.5
    
    prices = np. asarray(prices, dtype=np.float64)
    
    try:
        scales, fluctuations = _dfa_core(prices)
        
        # Linear fit in log-log space
        valid = fluctuations > 0
        if np.sum(valid) < 2:
            return 0.5
        
        log_scales = np.log(scales[valid])
        log_fluct = np.log(fluctuations[valid])
        alpha = np.polyfit(log_scales, log_fluct, 1)[0]
        
        return float(alpha)
    except:
        return 0.5


def hurst_exponent(prices):
    """
    Hurst Exponent (Palkia's Dimensional Memory)
    Technical: Measures persistence/anti-persistence
    
    H = 0.5: Random walk
    H > 0.5: Persistent (trend-following)
    H < 0.5: Anti-persistent (mean-reverting)
    """
    if len(prices) < 20:
        return 0.5
    
    prices = np. asarray(prices, dtype=np.float64)
    
    try:
        lags = range(2, min(25, len(prices) // 2))
        tau = []
        
        for lag in lags: 
            diff = prices[lag: ] - prices[:-lag]
            std = np.std(diff)
            if std > 0:
                tau.append(std)
            else:
                tau.append(1e-10)
        
        if len(tau) < 2:
            return 0.5
        
        # H = slope in log-log space
        log_lags = np.log(list(lags)[:len(tau)])
        log_tau = np.log(tau)
        slope = np.polyfit(log_lags, log_tau, 1)[0]
        
        return float(slope)
    except:
        return 0.5


def fractal_dimension_higuchi(prices, k_max=10):
    """
    Higuchi Fractal Dimension (Crystal Complexity)
    Technical: Measures curve complexity
    
    D ≈ 1.0: Simple, smooth
    D ≈ 1.5: Brownian motion
    D ≈ 2.0: Very complex, space-filling
    """
    if len(prices) < k_max * 4:
        return 1.0
    
    prices = np. asarray(prices, dtype=np.float64)
    n = len(prices)
    
    try:
        L = []
        k_values = range(1, k_max + 1)
        
        for k in k_values:
            Lk = []
            for m in range(1, k + 1):
                Lmk = 0
                n_max = (n - m) // k
                
                for i in range(1, n_max + 1):
                    idx1 = m + i * k - 1
                    idx2 = m + (i - 1) * k - 1
                    if idx1 < n and idx2 < n: 
                        Lmk += abs(prices[idx1] - prices[idx2])
                
                if n_max > 0 and k > 0:
                    Lmk = (Lmk * (n - 1)) / (k * n_max * k)
                    Lk.append(Lmk)
            
            if Lk:
                L.append(np.mean(Lk))
        
        if len(L) < 2:
            return 1.0
        
        # Slope in log-log space
        valid_k = list(k_values[: len(L)])
        log_k = np.log(valid_k)
        log_L = np.log(np.array(L) + 1e-10)
        slope = np.polyfit(log_k, log_L, 1)[0]
        
        return float(-slope)
    except:
        return 1.0


def chaos_features(prices):
    """
    Combined Chaos Features (Giratina's Domain)
    Technical: All chaos-related measures in one call
    """
    features = {}
    
    prices = np.asarray(prices, dtype=np.float64)
    
    # Giratina reveals chaos in the distortion world
    # 👻 The antimatter lord analyzes entropy and disorder
    
    # Lyapunov
    features["lyapunov"] = lyapunov_exponent(prices)
    
    # DFA
    features["dfa_alpha"] = dfa_alpha(prices)
    
    # Hurst
    features["hurst"] = hurst_exponent(prices)
    
    # Fractal Dimension
    features["fractal_dim"] = fractal_dimension_higuchi(prices)
    
    # Derived interpretations
    dfa = features["dfa_alpha"]
    hurst = features["hurst"]
    
    # Market regime classification (Giratina detects hidden states)
    if dfa > 0.6: 
        features["regime_dfa"] = 1  # Trending
    elif dfa < 0.4:
        features["regime_dfa"] = -1  # Mean-reverting
    else: 
        features["regime_dfa"] = 0  # Random
    
    if hurst > 0.55:
        features["regime_hurst"] = 1  # Persistent
    elif hurst < 0.45:
        features["regime_hurst"] = -1  # Anti-persistent
    else: 
        features["regime_hurst"] = 0  # Random
    
    return features


# ═══════════════════════════════════════════════════════════════
# 🔮 GRUPO 4: ENTROPY MEASURES
# Technical: Information theory measures of randomness
# ═══════════════════════════════════════════════════════════════

def shannon_entropy(data):
    """
    Shannon Entropy (Arceus Information Field)
    Technical: Measures uncertainty/randomness
    
    Higher = More random/unpredictable
    Lower = More structured/predictable
    """
    if len(data) < 5:
        return 0.0
    
    data = np. asarray(data, dtype=np.float64)
    
    try:
        # Histogram-based estimation
        n_bins = min(15, max(5, len(data) // 3))
        hist, _ = np.histogram(data, bins=n_bins)
        hist = hist[hist > 0]
        
        if len(hist) == 0:
            return 0.0
        
        probs = hist / len(data)
        entropy = -np.sum(probs * np.log2(probs))
        
        return float(entropy)
    except:
        return 0.0


if NUMBA_AVAILABLE: 
    @njit(cache=True)
    def _sample_entropy_core(data, m, r):
        """Numba-optimized Sample Entropy calculation"""
        n = len(data)
        
        # Count matches for template length m
        B = 0
        for i in range(n - m):
            for j in range(i + 1, n - m):
                match = True
                for k in range(m):
                    if abs(data[i + k] - data[j + k]) > r:
                        match = False
                        break
                if match: 
                    B += 1
        
        # Count matches for template length m+1
        A = 0
        for i in range(n - m - 1):
            for j in range(i + 1, n - m - 1):
                match = True
                for k in range(m + 1):
                    if abs(data[i + k] - data[j + k]) > r:
                        match = False
                        break
                if match:
                    A += 1
        
        return A, B
else:
    def _sample_entropy_core(data, m, r):
        """Pure Python Sample Entropy calculation"""
        n = len(data)
        
        B = 0
        for i in range(n - m):
            for j in range(i + 1, n - m):
                if np.max(np.abs(data[i:i+m] - data[j: j+m])) <= r:
                    B += 1
        
        A = 0
        for i in range(n - m - 1):
            for j in range(i + 1, n - m - 1):
                if np.max(np.abs(data[i:i+m+1] - data[j:j+m+1])) <= r:
                    A += 1
        
        return A, B


def sample_entropy(data, m=2, r_mult=0.2):
    """
    Sample Entropy (Crystal Regularity)
    Technical: Measures time series regularity
    
    Lower = More regular/predictable
    Higher = More irregular/complex
    """
    if len(data) < 30:
        return 0.0
    
    data = np. asarray(data, dtype=np.float64)
    
    # Limit size for performance
    if len(data) > 300:
        data = data[-300:]
    
    r = r_mult * np.std(data)
    
    if r == 0:
        return 0.0
    
    try:
        A, B = _sample_entropy_core(data, m, r)
        
        if B == 0:
            return 0.0
        
        return float(-np.log(A / B)) if A > 0 else 0.0
    except:
        return 0.0


def permutation_entropy(data, order=3, delay=1):
    """
    Permutation Entropy (Ordinal Crystal Patterns)
    Technical: Measures complexity via ordinal patterns
    
    Normalized between 0 (deterministic) and 1 (random)
    """
    if len(data) < order * delay + 10:
        return 0.0
    
    data = np. asarray(data, dtype=np.float64)
    
    try:
        n = len(data)
        permutations = {}
        total = 0
        
        for i in range(n - (order - 1) * delay):
            pattern = tuple(np.argsort(data[i:i + order * delay: delay]))
            permutations[pattern] = permutations.get(pattern, 0) + 1
            total += 1
        
        if total == 0:
            return 0.0
        
        # Calculate entropy
        probs = np.array(list(permutations.values())) / total
        entropy = -np.sum(probs * np. log2(probs))
        
        # Normalize by maximum entropy
        import math
        max_entropy = np.log2(math.factorial(order))
        
        return float(entropy / max_entropy) if max_entropy > 0 else 0.0
    except:
        return 0.0


def approximate_entropy(data, m=2, r_mult=0.2):
    """
    Approximate Entropy - ApEn (System Complexity)
    Technical: Measures system complexity and regularity
    """
    if len(data) < 30:
        return 0.0
    
    data = np.asarray(data, dtype=np.float64)
    
    # Limit size for performance
    if len(data) > 200:
        data = data[-200:]
    
    n = len(data)
    r = r_mult * np.std(data)
    
    if r == 0:
        return 0.0
    
    try:
        def phi(m_val):
            templates = np.array([data[i:i + m_val] for i in range(n - m_val + 1)])
            counts = np.zeros(len(templates))
            
            for i, template in enumerate(templates):
                diffs = np.max(np.abs(templates - template), axis=1)
                counts[i] = np.sum(diffs <= r)
            
            counts /= (n - m_val + 1)
            return np. mean(np.log(counts + 1e-10))
        
        return float(phi(m) - phi(m + 1))
    except:
        return 0.0


def entropy_features(data):
    """
    Combined Entropy Features (Arceus Judgment Data)
    Technical: All entropy measures in one call
    """
    features = {}
    
    data = np.asarray(data, dtype=np.float64)
    
    features["entropy_shannon"] = shannon_entropy(data)
    features["entropy_sample"] = sample_entropy(data)
    features["entropy_permutation"] = permutation_entropy(data)
    features["entropy_approximate"] = approximate_entropy(data)
    
    # Average entropy (overall randomness measure)
    entropies = [v for v in features.values() if v > 0]
    features["entropy_average"] = float(np.mean(entropies)) if entropies else 0.0
    
    return features


# ═══════════════════════════════════════════════════════════════
# 🎯 CORE FEATURE EXTRACTION (Combined)
# ═══════════════════════════════════════════════════════════════

def extract_core_features(prices, pips=None):
    """
    Extract all core features from price series (Prism Core Analysis)
    Technical: Combined feature extraction for core modules
    
    Args:
        prices: Price series (numpy array or list)
        pips: Optional pips/returns series
        
    Returns:
        dict: All core features
    """
    features = {}
    
    prices = np.asarray(prices, dtype=np.float64)
    
    if len(prices) < 10:
        return features
    
    # Use pips if provided, otherwise calculate
    if pips is None:
        pips = np. diff(prices) * 10000  # Convert to pips for EURUSD
    else:
        pips = np. asarray(pips, dtype=np.float64)
    
    # Statistical features
    features. update(statistical_features(prices))
    
    # Derivatives
    features.update(calculate_derivatives(prices))
    
    # Spectral
    features.update(spectral_features(prices))
    features.update(wavelet_features(prices))
    
    # Chaos
    features.update(chaos_features(prices))
    
    # Entropy (on pips for better results)
    if len(pips) >= 30:
        features.update(entropy_features(pips))
    
    return features


# ═══════════════════════════════════════════════════════════════
# 🎮 TEST
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__": 
    print("""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║        ⚡ ULTRA NECROZMA CORE FEATURES TEST ⚡               ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    # Generate test data (random walk)
    np.random.seed(42)
    n = 500
    prices = 1.10 + np.cumsum(np.random.randn(n) * 0.0001)
    
    print(f"📊 Test data: {n} prices")
    print(f"   Range: {prices.min():.5f} - {prices.max():.5f}")
    print()
    
    # Test individual functions
    import time
    
    print("🔬 Testing individual feature groups:")
    print("─" * 50)
    
    # Statistical
    start = time.time()
    stat_feat = statistical_features(prices)
    print(f"   📊 Statistical: {len(stat_feat)} features ({time.time()-start:.3f}s)")
    
    # Derivatives
    start = time.time()
    deriv_feat = calculate_derivatives(prices)
    print(f"   📈 Derivatives: {len(deriv_feat)} features ({time.time()-start:.3f}s)")
    
    # Spectral
    start = time.time()
    spectral_feat = spectral_features(prices)
    wavelet_feat = wavelet_features(prices)
    print(f"   🌈 Spectral: {len(spectral_feat) + len(wavelet_feat)} features ({time.time()-start:.3f}s)")
    
    # Chaos
    start = time.time()
    chaos_feat = chaos_features(prices)
    print(f"   🔥 Chaos: {len(chaos_feat)} features ({time.time()-start:.3f}s)")
    
    # Entropy
    start = time.time()
    pips = np.diff(prices) * 10000
    entropy_feat = entropy_features(pips)
    print(f"   🔮 Entropy: {len(entropy_feat)} features ({time.time()-start:.3f}s)")
    
    print()
    
    # Test combined
    print("⚡ Testing combined extraction:")
    print("─" * 50)
    
    start = time.time()
    all_features = extract_core_features(prices)
    total_time = time.time() - start
    
    print(f"   ✅ Total features: {len(all_features)}")
    print(f"   ⏱️  Time: {total_time:.3f}s")
    print()
    
    # Show some key features
    print("🎯 Key feature values:")
    print("─" * 50)
    key_features = ["dfa_alpha", "hurst", "lyapunov", "fractal_dim", 
                    "entropy_shannon", "spectral_centroid"]
    for key in key_features:
        if key in all_features:
            print(f"   {key}:  {all_features[key]:. 4f}")
    
    print()
    print("✅ Core features test complete!")