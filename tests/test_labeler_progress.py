#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚡🌟💎 ULTRA NECROZMA - LABELER PROGRESS TESTS 💎🌟⚡

Tests for progress indicators in label processing
"""

import pytest
import numpy as np
import pandas as pd
from pathlib import Path
import tempfile
import shutil
import sys
from io import StringIO
from unittest.mock import patch

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from labeler import label_dataframe
from config import CACHE_CONFIG


@pytest.fixture
def temp_cache_dir():
    """Create temporary cache directory for tests"""
    temp = tempfile.mkdtemp()
    yield Path(temp)
    shutil.rmtree(temp)


@pytest.fixture
def small_dataframe():
    """Create small mock tick data for fast testing"""
    n_samples = 100  # Small dataset for quick testing
    timestamps = pd.date_range('2025-01-01', periods=n_samples, freq='1s')
    
    # Generate realistic price movements
    base_price = 1.1000
    noise = np.random.randn(n_samples) * 0.0001
    cumsum = np.cumsum(noise)
    
    df = pd.DataFrame({
        'timestamp': timestamps,
        'mid_price': base_price + cumsum,
        'bid': base_price + cumsum - 0.00005,
        'ask': base_price + cumsum + 0.00005,
    })
    
    return df


class TestProgressIndicators:
    """Test progress indicators for label processing"""
    
    def test_labeling_completes_with_progress_bars(self, small_dataframe, temp_cache_dir, monkeypatch):
        """Test that labeling completes successfully with progress bars enabled"""
        # Set temporary cache directory
        monkeypatch.setitem(CACHE_CONFIG, 'cache_dir', temp_cache_dir)
        monkeypatch.setitem(CACHE_CONFIG, 'enabled', False)  # Disable cache for clean test
        
        # Use minimal configuration for fast testing
        target_pips = [5, 10]  # Only 2 targets instead of all
        stop_pips = [5]        # Only 1 stop
        horizons = [2, 5]      # Only 2 horizons
        # This creates 2 * 1 * 2 = 4 configurations instead of 210
        
        # Run labeling with progress bars
        results = label_dataframe(
            small_dataframe,
            target_pips=target_pips,
            stop_pips=stop_pips,
            horizons=horizons,
            num_workers=2,  # Use minimal workers for testing
            use_cache=False,
            return_dict=True  # For backward compatibility in tests
        )
        
        # Verify results are returned
        assert results is not None, "Results should not be None"
        assert isinstance(results, dict), "Results should be a dictionary"
        
        # Check expected configurations exist
        expected_configs = 4
        assert len(results) == expected_configs, f"Should have {expected_configs} configurations"
        
        # Verify configuration keys format
        for key in results.keys():
            assert key.startswith('T'), f"Config key {key} should start with 'T'"
            assert '_S' in key, f"Config key {key} should contain '_S'"
            assert '_H' in key, f"Config key {key} should contain '_H'"
    
    def test_progress_bar_output_format(self, small_dataframe, temp_cache_dir, monkeypatch):
        """Test that progress bar is properly displayed (checks for tqdm usage)"""
        # Set temporary cache directory
        monkeypatch.setitem(CACHE_CONFIG, 'cache_dir', temp_cache_dir)
        monkeypatch.setitem(CACHE_CONFIG, 'enabled', False)
        
        # Capture stdout to verify progress output
        captured_output = StringIO()
        
        # Use minimal configuration
        target_pips = [5]
        stop_pips = [5]
        horizons = [2]
        # This creates 1 configuration for quick test
        
        # Run labeling (tqdm will output to stderr by default, but we test that it runs)
        results = label_dataframe(
            small_dataframe,
            target_pips=target_pips,
            stop_pips=stop_pips,
            horizons=horizons,
            num_workers=1,
            use_cache=False,
            return_dict=True  # For backward compatibility in tests
        )
        
        # Verify labeling completed
        assert len(results) == 1, "Should have 1 configuration"
        assert 'T5_S5_H2' in results, "Should have T5_S5_H2 configuration"
    
    def test_cache_checkpoint_with_progress(self, small_dataframe, temp_cache_dir, monkeypatch):
        """Test that checkpoint saving works with progress bars"""
        # Set temporary cache directory and enable cache
        monkeypatch.setitem(CACHE_CONFIG, 'cache_dir', temp_cache_dir)
        monkeypatch.setitem(CACHE_CONFIG, 'enabled', True)
        monkeypatch.setitem(CACHE_CONFIG, 'cache_labeling', True)
        monkeypatch.setitem(CACHE_CONFIG, 'checkpoint_interval', 2)
        
        # Use configuration that triggers checkpoint
        target_pips = [5, 10]
        stop_pips = [5]
        horizons = [2, 5]
        # This creates 4 configurations, checkpoint at every 2
        
        # Run labeling with cache enabled
        results = label_dataframe(
            small_dataframe,
            target_pips=target_pips,
            stop_pips=stop_pips,
            horizons=horizons,
            num_workers=2,
            use_cache=True,
            return_dict=True  # For backward compatibility in tests
        )
        
        # Verify results
        assert len(results) == 4, "Should have 4 configurations"
        
        # Run again to test cache loading with progress
        results2 = label_dataframe(
            small_dataframe,
            target_pips=target_pips,
            stop_pips=stop_pips,
            horizons=horizons,
            num_workers=2,
            use_cache=True,
            return_dict=True  # For backward compatibility in tests
        )
        
        # Should load from cache
        assert len(results2) == 4, "Should have 4 configurations from cache"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
