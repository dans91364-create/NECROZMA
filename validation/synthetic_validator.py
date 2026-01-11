#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚡🌟💎 ULTRA NECROZMA - SYNTHETIC VALIDATOR 💎🌟⚡

Synthetic Data Validation
"Test with known ground truth"

Technical: Synthetic data generation and validation
- Generate series with known properties (fBm with H=0.7, etc.)
- Verify NECROZMA detects properties correctly
- Calibrate parameters with ground truth
"""

import numpy as np


# ═══════════════════════════════════════════════════════════════
# 🌟 SYNTHETIC DATA GENERATORS
# ═══════════════════════════════════════════════════════════════

def generate_fbm(n=1000, hurst=0.5, seed=None):
    """
    Generate Fractional Brownian Motion
    
    Args:
        n: Number of points
        hurst: Hurst exponent (0.5 = random walk, >0.5 = persistent, <0.5 = anti-persistent)
        seed: Random seed
        
    Returns:
        array: fBm series
    """
    if seed is not None:
        np.random.seed(seed)
    
    # Davies-Harte method (simplified)
    dW = np.random.randn(n)
    
    # Create covariance structure
    gamma = lambda k: 0.5 * (abs(k - 1)**(2*hurst) - 2*abs(k)**(2*hurst) + abs(k + 1)**(2*hurst))
    
    # Build autocovariance
    cov = np.array([gamma(i) for i in range(n)])
    
    # FFT method for correlated noise
    fft_cov = np.fft.fft(cov)
    fft_noise = np.fft.fft(dW)
    
    # Multiply in frequency domain
    fft_result = np.sqrt(np.abs(fft_cov)) * fft_noise
    
    # Transform back
    fbm = np.real(np.fft.ifft(fft_result))
    
    # Cumulative sum for integrated process
    fbm = np.cumsum(fbm)
    
    return fbm


def generate_lorenz(n=10000, dt=0.01, sigma=10, rho=28, beta=8/3, seed=None):
    """
    Generate Lorenz attractor (chaotic system)
    
    Known Lyapunov exponent ≈ 0.9
    
    Args:
        n: Number of points
        dt: Time step
        sigma, rho, beta: Lorenz parameters
        seed: Random seed
        
    Returns:
        array: x component of Lorenz attractor
    """
    if seed is not None:
        np.random.seed(seed)
    
    # Initial conditions
    x, y, z = 1.0, 1.0, 1.0
    
    # Integrate
    xs = []
    for _ in range(n):
        dx = sigma * (y - x) * dt
        dy = (x * (rho - z) - y) * dt
        dz = (x * y - beta * z) * dt
        
        x += dx
        y += dy
        z += dz
        
        xs.append(x)
    
    return np.array(xs)


def generate_periodic(n=1000, freq=0.1, amplitude=1.0, noise=0.1, seed=None):
    """
    Generate periodic signal with noise
    
    Args:
        n: Number of points
        freq: Frequency
        amplitude: Amplitude
        noise: Noise level
        seed: Random seed
        
    Returns:
        array: Periodic series
    """
    if seed is not None:
        np.random.seed(seed)
    
    t = np.arange(n)
    signal = amplitude * np.sin(2 * np.pi * freq * t)
    
    if noise > 0:
        signal += np.random.randn(n) * noise
    
    return signal


def generate_random_walk(n=1000, seed=None):
    """
    Generate pure random walk (Hurst = 0.5)
    
    Args:
        n: Number of points
        seed: Random seed
        
    Returns:
        array: Random walk
    """
    if seed is not None:
        np.random.seed(seed)
    
    return np.cumsum(np.random.randn(n))


def generate_white_noise(n=1000, seed=None):
    """
    Generate white noise (no correlation)
    
    Args:
        n: Number of points
        seed: Random seed
        
    Returns:
        array: White noise
    """
    if seed is not None:
        np.random.seed(seed)
    
    return np.random.randn(n)


# ═══════════════════════════════════════════════════════════════
# 🔬 VALIDATION FUNCTIONS
# ═══════════════════════════════════════════════════════════════

def validate_hurst_estimation(hurst_estimator, tolerance=0.1):
    """
    Validate Hurst exponent estimation
    
    Args:
        hurst_estimator: Function that estimates Hurst
        tolerance: Acceptable error
        
    Returns:
        dict: Validation results
    """
    results = {}
    
    # Test different Hurst values
    test_values = [0.3, 0.5, 0.7, 0.9]
    
    for true_hurst in test_values:
        fbm = generate_fbm(n=2000, hurst=true_hurst, seed=42)
        estimated_hurst = hurst_estimator(fbm)
        
        error = abs(estimated_hurst - true_hurst)
        passed = error < tolerance
        
        results[f"hurst_{true_hurst}"] = {
            "true": true_hurst,
            "estimated": estimated_hurst,
            "error": error,
            "passed": passed
        }
    
    # Overall pass rate
    passed_count = sum(1 for r in results.values() if r["passed"])
    results["pass_rate"] = passed_count / len(test_values)
    
    return results


def validate_lyapunov_estimation(lyapunov_estimator, tolerance=0.3):
    """
    Validate Lyapunov exponent estimation
    
    Args:
        lyapunov_estimator: Function that estimates Lyapunov
        tolerance: Acceptable error
        
    Returns:
        dict: Validation results
    """
    results = {}
    
    # Lorenz system (known Lyapunov ≈ 0.9)
    lorenz = generate_lorenz(n=5000, seed=42)
    estimated_lyap = lyapunov_estimator(lorenz)
    
    true_lyap = 0.9
    error = abs(estimated_lyap - true_lyap)
    
    results["lorenz"] = {
        "true": true_lyap,
        "estimated": estimated_lyap,
        "error": error,
        "passed": error < tolerance
    }
    
    # Random walk (Lyapunov ≈ 0)
    rw = generate_random_walk(n=2000, seed=42)
    estimated_lyap_rw = lyapunov_estimator(rw)
    
    results["random_walk"] = {
        "true": 0.0,
        "estimated": estimated_lyap_rw,
        "error": abs(estimated_lyap_rw),
        "passed": abs(estimated_lyap_rw) < 0.1
    }
    
    return results


def validate_entropy_estimation(entropy_estimator):
    """
    Validate entropy estimation
    
    Args:
        entropy_estimator: Function that estimates entropy
        
    Returns:
        dict: Validation results
    """
    results = {}
    
    # Periodic signal (low entropy)
    periodic = generate_periodic(n=1000, freq=0.05, noise=0.01, seed=42)
    entropy_periodic = entropy_estimator(periodic)
    
    results["periodic"] = {
        "entropy": entropy_periodic,
        "expected": "low",
        "passed": entropy_periodic < 0.5
    }
    
    # White noise (high entropy)
    noise = generate_white_noise(n=1000, seed=42)
    entropy_noise = entropy_estimator(noise)
    
    results["white_noise"] = {
        "entropy": entropy_noise,
        "expected": "high",
        "passed": entropy_noise > 0.7
    }
    
    # Lorenz (medium entropy)
    lorenz = generate_lorenz(n=2000, seed=42)
    entropy_lorenz = entropy_estimator(lorenz[::2])  # Subsample
    
    results["lorenz"] = {
        "entropy": entropy_lorenz,
        "expected": "medium",
        "passed": 0.3 < entropy_lorenz < 0.8
    }
    
    return results


# ═══════════════════════════════════════════════════════════════
# 🎯 COMPREHENSIVE VALIDATION
# ═══════════════════════════════════════════════════════════════

def run_comprehensive_validation(feature_extractors):
    """
    Run comprehensive validation with all synthetic data
    
    Args:
        feature_extractors: Dict of feature extraction functions
        
    Returns:
        dict: Comprehensive validation results
    """
    results = {
        "timestamp": np.datetime64('now').astype(str),
        "tests": {}
    }
    
    # Test data
    test_data = {
        "fbm_H03": generate_fbm(n=2000, hurst=0.3, seed=42),
        "fbm_H05": generate_fbm(n=2000, hurst=0.5, seed=42),
        "fbm_H07": generate_fbm(n=2000, hurst=0.7, seed=42),
        "lorenz": generate_lorenz(n=2000, seed=42)[::2],
        "periodic": generate_periodic(n=1000, freq=0.05, seed=42),
        "white_noise": generate_white_noise(n=1000, seed=42),
        "random_walk": generate_random_walk(n=1000, seed=42)
    }
    
    # Extract features for each test series
    for name, data in test_data.items():
        results["tests"][name] = {}
        
        for extractor_name, extractor_func in feature_extractors.items():
            try:
                features = extractor_func(data)
                results["tests"][name][extractor_name] = features
            except Exception as e:
                results["tests"][name][extractor_name] = {"error": str(e)}
    
    return results
