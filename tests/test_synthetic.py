#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚡🌟💎 ULTRA NECROZMA - SYNTHETIC VALIDATION TESTS 💎🌟⚡

Tests for synthetic data validation
"""

import pytest
import numpy as np
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from validation.synthetic_validator import (
    generate_fbm,
    generate_lorenz,
    generate_periodic,
    generate_random_walk,
    generate_white_noise
)


def test_fbm_hurst_0_3():
    """Test fBm with H=0.3 (anti-persistent)"""
    fbm = generate_fbm(n=1000, hurst=0.3, seed=42)
    assert len(fbm) == 1000
    assert not np.any(np.isnan(fbm))
    assert not np.any(np.isinf(fbm))


def test_fbm_hurst_0_5():
    """Test fBm with H=0.5 (random walk)"""
    fbm = generate_fbm(n=1000, hurst=0.5, seed=42)
    assert len(fbm) == 1000
    assert not np.any(np.isnan(fbm))


def test_fbm_hurst_0_7():
    """Test fBm with H=0.7 (persistent)"""
    fbm = generate_fbm(n=1000, hurst=0.7, seed=42)
    assert len(fbm) == 1000
    assert not np.any(np.isnan(fbm))


def test_lorenz_attractor():
    """Test Lorenz attractor generation"""
    lorenz = generate_lorenz(n=5000, seed=42)
    
    assert len(lorenz) == 5000
    assert not np.any(np.isnan(lorenz))
    
    # Lorenz should have bounded values (not explode)
    assert np.abs(lorenz).max() < 100


def test_periodic_signal():
    """Test periodic signal generation"""
    periodic = generate_periodic(n=1000, freq=0.1, amplitude=2.0, noise=0.1, seed=42)
    
    assert len(periodic) == 1000
    assert not np.any(np.isnan(periodic))
    
    # Should have approximately the right amplitude
    assert np.abs(periodic).max() < 5.0


def test_random_walk():
    """Test random walk generation"""
    rw = generate_random_walk(n=1000, seed=42)
    
    assert len(rw) == 1000
    assert not np.any(np.isnan(rw))
    
    # First difference should be roughly N(0,1)
    diff = np.diff(rw)
    assert np.abs(np.mean(diff)) < 0.2  # Mean close to 0
    assert 0.8 < np.std(diff) < 1.2     # Std close to 1


def test_white_noise():
    """Test white noise generation"""
    noise = generate_white_noise(n=1000, seed=42)
    
    assert len(noise) == 1000
    assert not np.any(np.isnan(noise))
    
    # Should be N(0,1)
    assert np.abs(np.mean(noise)) < 0.2
    assert 0.8 < np.std(noise) < 1.2


def test_seed_reproducibility():
    """Test that same seed produces same results"""
    fbm1 = generate_fbm(n=100, hurst=0.7, seed=42)
    fbm2 = generate_fbm(n=100, hurst=0.7, seed=42)
    
    np.testing.assert_array_equal(fbm1, fbm2)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
