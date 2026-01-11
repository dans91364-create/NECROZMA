#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚡🌟💎 ULTRA NECROZMA - FEATURE TESTS 💎🌟⚡

Unit tests for feature extraction modules
"""

import pytest
import numpy as np
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from features.dispersion_entropy import dispersion_entropy, extract_dispersion_entropy_features
from features.bubble_entropy import bubble_entropy_v2, extract_bubble_entropy_features
from features.rcmse import refined_composite_multiscale_entropy
from features.complexity_entropy_plane import complexity_entropy_plane
from validation.synthetic_validator import (
    generate_fbm, generate_lorenz, generate_periodic, 
    generate_random_walk, generate_white_noise
)


# ═══════════════════════════════════════════════════════════════
# 🧪 SYNTHETIC DATA TESTS
# ═══════════════════════════════════════════════════════════════

def test_generate_fbm():
    """Test fBm generation"""
    fbm = generate_fbm(n=1000, hurst=0.7, seed=42)
    assert len(fbm) == 1000
    assert not np.any(np.isnan(fbm))


def test_generate_lorenz():
    """Test Lorenz attractor generation"""
    lorenz = generate_lorenz(n=1000, seed=42)
    assert len(lorenz) == 1000
    assert not np.any(np.isnan(lorenz))


def test_generate_periodic():
    """Test periodic signal generation"""
    periodic = generate_periodic(n=1000, freq=0.1, seed=42)
    assert len(periodic) == 1000
    assert not np.any(np.isnan(periodic))


# ═══════════════════════════════════════════════════════════════
# 📊 DISPERSION ENTROPY TESTS
# ═══════════════════════════════════════════════════════════════

def test_dispersion_entropy_basic():
    """Test basic dispersion entropy calculation"""
    # Random data should have high entropy
    np.random.seed(42)
    random_data = np.random.randn(1000)
    de = dispersion_entropy(random_data, m=2, c=3, normalize=True)
    
    assert 0 <= de <= 1
    assert de > 0.5  # Random should have relatively high entropy


def test_dispersion_entropy_periodic():
    """Test dispersion entropy on periodic data"""
    periodic = generate_periodic(n=1000, freq=0.05, noise=0.01, seed=42)
    de = dispersion_entropy(periodic, m=2, c=3, normalize=True)
    
    assert 0 <= de <= 1
    # Periodic signal should have lower entropy than random
    

def test_dispersion_entropy_features():
    """Test dispersion entropy feature extraction"""
    data = generate_random_walk(n=500, seed=42)
    features = extract_dispersion_entropy_features(data)
    
    assert isinstance(features, dict)
    assert len(features) > 0
    assert "dispersion_entropy_m2_c3" in features


# ═══════════════════════════════════════════════════════════════
# 🫧 BUBBLE ENTROPY TESTS
# ═══════════════════════════════════════════════════════════════

def test_bubble_entropy_sorted():
    """Test bubble entropy on sorted data"""
    sorted_data = np.arange(100, dtype=float)
    be = bubble_entropy_v2(sorted_data)
    
    # Sorted data should have very low bubble entropy
    assert 0 <= be <= 1
    assert be < 0.1


def test_bubble_entropy_reverse_sorted():
    """Test bubble entropy on reverse sorted data"""
    reverse_sorted = np.arange(100, dtype=float)[::-1]
    be = bubble_entropy_v2(reverse_sorted)
    
    # Reverse sorted should have high bubble entropy
    assert 0 <= be <= 1
    assert be > 0.9


def test_bubble_entropy_features():
    """Test bubble entropy feature extraction"""
    data = generate_white_noise(n=500, seed=42)
    features = extract_bubble_entropy_features(data)
    
    assert isinstance(features, dict)
    assert len(features) > 0
    assert "bubble_entropy_v2" in features


# ═══════════════════════════════════════════════════════════════
# 📈 RCMSE TESTS
# ═══════════════════════════════════════════════════════════════

def test_rcmse_basic():
    """Test RCMSE calculation"""
    data = generate_random_walk(n=1000, seed=42)
    rcmse = refined_composite_multiscale_entropy(data, m=2, max_scale=5)
    
    assert isinstance(rcmse, dict)
    assert len(rcmse) > 0
    assert "rcmse_scale_1" in rcmse


def test_rcmse_values_range():
    """Test RCMSE values are in reasonable range"""
    data = generate_random_walk(n=1000, seed=42)
    rcmse = refined_composite_multiscale_entropy(data, m=2, max_scale=5)
    
    for key, value in rcmse.items():
        assert value >= 0  # Entropy should be non-negative


# ═══════════════════════════════════════════════════════════════
# 🌀 COMPLEXITY-ENTROPY PLANE TESTS
# ═══════════════════════════════════════════════════════════════

def test_complexity_entropy_plane():
    """Test complexity-entropy plane calculation"""
    data = generate_lorenz(n=500, seed=42)[::2]
    ce = complexity_entropy_plane(data, order=3, delay=1)
    
    assert isinstance(ce, dict)
    assert "ce_entropy" in ce
    assert "ce_complexity" in ce
    assert "ce_regime" in ce


def test_complexity_entropy_range():
    """Test that H and C are in [0, 1]"""
    data = generate_random_walk(n=500, seed=42)
    ce = complexity_entropy_plane(data, order=3, delay=1)
    
    assert 0 <= ce["ce_entropy"] <= 1
    assert 0 <= ce["ce_complexity"] <= 1


def test_complexity_entropy_regimes():
    """Test regime classification"""
    # Periodic should be deterministic/periodic
    periodic = generate_periodic(n=500, freq=0.05, noise=0.01, seed=42)
    ce_periodic = complexity_entropy_plane(periodic, order=3, delay=1)
    
    # Lorenz should be chaotic/complex
    lorenz = generate_lorenz(n=500, seed=42)[::2]
    ce_lorenz = complexity_entropy_plane(lorenz, order=3, delay=1)
    
    # Both should have valid regimes
    assert ce_periodic["ce_regime"] in ["PERIODIC", "STRUCTURED", "TRANSITIONAL", "RANDOM", "CHAOTIC", "COMPLEX"]
    assert ce_lorenz["ce_regime"] in ["PERIODIC", "STRUCTURED", "TRANSITIONAL", "RANDOM", "CHAOTIC", "COMPLEX"]


# ═══════════════════════════════════════════════════════════════
# 🎯 INTEGRATION TESTS
# ═══════════════════════════════════════════════════════════════

def test_all_features_on_synthetic_data():
    """Test all features can be extracted from synthetic data"""
    test_data = {
        "fbm": generate_fbm(n=500, hurst=0.7, seed=42),
        "lorenz": generate_lorenz(n=500, seed=42)[::2],
        "periodic": generate_periodic(n=500, seed=42),
        "random_walk": generate_random_walk(n=500, seed=42)
    }
    
    for name, data in test_data.items():
        # Test each feature extractor
        de_features = extract_dispersion_entropy_features(data)
        be_features = extract_bubble_entropy_features(data)
        
        assert len(de_features) > 0, f"Dispersion entropy failed for {name}"
        assert len(be_features) > 0, f"Bubble entropy failed for {name}"


# ═══════════════════════════════════════════════════════════════
# 🚀 RUN TESTS
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
