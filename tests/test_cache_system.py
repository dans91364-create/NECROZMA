#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚡🌟💎 ULTRA NECROZMA - CACHE SYSTEM TESTS 💎🌟⚡

Tests for cache and resume functionality
"""

import pytest
import json
import pickle
import numpy as np
import pandas as pd
from pathlib import Path
import tempfile
import shutil
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from labeler import (
    _generate_data_hash,
    _load_cache,
    _save_cache,
    _load_progress,
    _save_progress,
    clear_label_cache,
    label_dataframe
)


@pytest.fixture
def temp_cache_dir():
    """Create temporary cache directory for tests"""
    temp = tempfile.mkdtemp()
    yield Path(temp)
    shutil.rmtree(temp)


@pytest.fixture
def mock_dataframe():
    """Create mock tick data for testing"""
    n_samples = 1000
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


class TestDataHashing:
    """Test data hashing for cache keys"""
    
    def test_hash_generation(self, mock_dataframe):
        """Test that hash is generated consistently"""
        hash1 = _generate_data_hash(mock_dataframe)
        hash2 = _generate_data_hash(mock_dataframe)
        
        assert hash1 == hash2, "Hash should be consistent for same data"
        assert len(hash1) == 8, "Hash should be 8 characters"
    
    def test_hash_differs_for_different_data(self, mock_dataframe):
        """Test that different data produces different hashes"""
        hash1 = _generate_data_hash(mock_dataframe)
        
        # Modify data
        modified_df = mock_dataframe.copy()
        modified_df['mid_price'] = modified_df['mid_price'] + 0.001
        
        hash2 = _generate_data_hash(modified_df)
        
        assert hash1 != hash2, "Different data should produce different hashes"


class TestCacheSaveLoad:
    """Test cache save and load functionality"""
    
    def test_save_and_load_cache(self, temp_cache_dir):
        """Test saving and loading cache"""
        cache_file = temp_cache_dir / "test_cache.pkl"
        
        # Create test data
        test_data = {
            'T10_S5_H60': pd.DataFrame({'a': [1, 2, 3]}),
            'T20_S10_H120': pd.DataFrame({'b': [4, 5, 6]})
        }
        
        # Save cache
        _save_cache(cache_file, test_data)
        
        assert cache_file.exists(), "Cache file should be created"
        
        # Load cache
        loaded_data = _load_cache(cache_file)
        
        assert loaded_data is not None, "Cache should be loaded"
        assert len(loaded_data) == 2, "Should have 2 items"
        assert 'T10_S5_H60' in loaded_data, "Should have first key"
        assert 'T20_S10_H120' in loaded_data, "Should have second key"
    
    def test_load_nonexistent_cache(self, temp_cache_dir):
        """Test loading cache that doesn't exist"""
        cache_file = temp_cache_dir / "nonexistent.pkl"
        
        loaded_data = _load_cache(cache_file)
        
        assert loaded_data is None, "Should return None for nonexistent cache"


class TestProgressCheckpoint:
    """Test progress checkpoint functionality"""
    
    def test_save_and_load_progress(self, temp_cache_dir):
        """Test saving and loading progress"""
        progress_file = temp_cache_dir / "progress.json"
        
        # Save progress
        completed = {'T10_S5_H60', 'T20_S10_H120', 'T30_S15_H240'}
        _save_progress(progress_file, completed)
        
        assert progress_file.exists(), "Progress file should be created"
        
        # Load progress
        loaded_progress = _load_progress(progress_file)
        
        assert isinstance(loaded_progress, set), "Progress should be a set"
        assert len(loaded_progress) == 3, "Should have 3 completed items"
        assert 'T10_S5_H60' in loaded_progress, "Should have first item"
    
    def test_load_nonexistent_progress(self, temp_cache_dir):
        """Test loading progress that doesn't exist"""
        progress_file = temp_cache_dir / "nonexistent.json"
        
        loaded_progress = _load_progress(progress_file)
        
        assert isinstance(loaded_progress, set), "Should return empty set"
        assert len(loaded_progress) == 0, "Should be empty"


class TestLabelDataframeCache:
    """Test label_dataframe caching functionality"""
    
    def test_labeling_creates_cache(self, mock_dataframe, temp_cache_dir, monkeypatch):
        """Test that labeling creates cache files"""
        # Mock the cache directory
        from config import CACHE_CONFIG
        original_cache_dir = CACHE_CONFIG.get("cache_dir")
        CACHE_CONFIG["cache_dir"] = temp_cache_dir
        
        try:
            # Run labeling with small config
            results = label_dataframe(
                mock_dataframe,
                target_pips=[10],
                stop_pips=[5],
                horizons=[60],
                num_workers=1,
                use_cache=True
            )
            
            assert len(results) > 0, "Should have results"
            
            # Check cache file was created
            cache_files = list(temp_cache_dir.glob("labels_*.pkl"))
            assert len(cache_files) > 0, "Cache file should be created"
            
        finally:
            # Restore original cache dir
            CACHE_CONFIG["cache_dir"] = original_cache_dir
    
    def test_labeling_uses_existing_cache(self, mock_dataframe, temp_cache_dir):
        """Test that labeling uses existing cache"""
        from config import CACHE_CONFIG
        original_cache_dir = CACHE_CONFIG.get("cache_dir")
        CACHE_CONFIG["cache_dir"] = temp_cache_dir
        
        try:
            # First run - create cache
            results1 = label_dataframe(
                mock_dataframe,
                target_pips=[10],
                stop_pips=[5],
                horizons=[60],
                num_workers=1,
                use_cache=True
            )
            
            # Second run - should use cache
            import time
            start_time = time.time()
            results2 = label_dataframe(
                mock_dataframe,
                target_pips=[10],
                stop_pips=[5],
                horizons=[60],
                num_workers=1,
                use_cache=True
            )
            elapsed = time.time() - start_time
            
            # Cache should be very fast (< 1 second)
            assert elapsed < 1.0, "Cache load should be fast"
            assert len(results2) == len(results1), "Results should be same size"
            
        finally:
            CACHE_CONFIG["cache_dir"] = original_cache_dir
    
    def test_labeling_without_cache(self, mock_dataframe):
        """Test labeling with cache disabled"""
        results = label_dataframe(
            mock_dataframe,
            target_pips=[10],
            stop_pips=[5],
            horizons=[60],
            num_workers=1,
            use_cache=False
        )
        
        assert len(results) > 0, "Should have results without cache"


class TestUniverseCache:
    """Test universe cache functionality"""
    
    def test_universe_exists_check(self, temp_cache_dir):
        """Test checking if universe exists"""
        from analyzer import UltraNecrozmaAnalyzer
        from config import CACHE_CONFIG
        
        # Create mock data
        timestamps = pd.date_range('2025-01-01', periods=100, freq='1s')
        df = pd.DataFrame({
            'timestamp': timestamps,
            'bid': 1.1,
            'ask': 1.1001,
            'mid_price': 1.10005,
        })
        
        # Create analyzer
        analyzer = UltraNecrozmaAnalyzer(df)
        
        # Check non-existent universe
        exists = analyzer._universe_exists("universe_1m_5lb")
        assert exists == False, "Non-existent universe should return False"
        
        # Create universe file
        universe_dir = analyzer.output_dirs["universes"]
        universe_file = universe_dir / "universe_1m_5lb.parquet"
        
        # Create empty parquet file (mock)
        test_df = pd.DataFrame({'a': [1, 2, 3]})
        test_df.to_parquet(universe_file)
        
        # Check again
        exists = analyzer._universe_exists("universe_1m_5lb")
        assert exists == True, "Existing universe should return True"
        
        # Clean up
        if universe_file.exists():
            universe_file.unlink()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
