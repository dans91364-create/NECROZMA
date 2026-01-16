#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚡🌟💎 ULTRA NECROZMA - MEMORY-EFFICIENT LABELER TESTS 💎🌟⚡

Tests for the memory-efficient labeling system that saves each config immediately
to disk instead of accumulating all results in RAM.
"""

import pytest
import numpy as np
import pandas as pd
from pathlib import Path
import tempfile
import shutil
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from labeler import (
    label_dataframe,
    load_label_results,
    load_all_label_results,
    _get_labels_dir
)


@pytest.fixture
def temp_labels_dir(monkeypatch):
    """Create temporary labels directory for tests"""
    temp = Path(tempfile.mkdtemp())
    labels_dir = temp / "labels"
    
    # Monkeypatch the _get_labels_dir function to use temp directory
    def mock_get_labels_dir():
        labels_dir.mkdir(exist_ok=True)
        return labels_dir
    
    monkeypatch.setattr('labeler._get_labels_dir', mock_get_labels_dir)
    
    yield labels_dir
    
    # Cleanup
    shutil.rmtree(temp)


@pytest.fixture
def small_dataframe():
    """Create small mock tick data for fast testing"""
    n_samples = 200  # Small dataset for quick testing
    timestamps = pd.date_range('2025-01-01', periods=n_samples, freq='1min')
    
    # Generate realistic price movements
    base_price = 1.1000
    noise = np.random.randn(n_samples) * 0.0001
    cumsum = np.cumsum(noise)
    
    df = pd.DataFrame({
        'timestamp': timestamps,
        'mid_price': base_price + cumsum,
    })
    
    return df


class TestMemoryEfficientLabeling:
    """Test memory-efficient labeling that saves each config immediately"""
    
    def test_saves_individual_parquet_files(self, small_dataframe, temp_labels_dir):
        """Test that each config is saved as a separate parquet file"""
        # Run labeling with minimal configs
        saved_files = label_dataframe(
            small_dataframe,
            target_pips=[5, 10],
            stop_pips=[5],
            horizons=[30, 60],
            use_cache=False,
            return_dict=False  # Memory-efficient mode
        )
        
        # Should have saved 2 * 1 * 2 = 4 files
        assert len(saved_files) == 4, f"Should have 4 saved files, got {len(saved_files)}"
        
        # Check that files exist
        for file_path in saved_files:
            assert Path(file_path).exists(), f"File should exist: {file_path}"
        
        # Check file names
        expected_configs = ['T5_S5_H30', 'T5_S5_H60', 'T10_S5_H30', 'T10_S5_H60']
        saved_names = [Path(f).stem for f in saved_files]
        
        for config in expected_configs:
            assert config in saved_names, f"Config {config} should be saved"
    
    def test_parquet_files_have_correct_structure(self, small_dataframe, temp_labels_dir):
        """Test that saved parquet files have the correct columns and data"""
        # Run labeling
        saved_files = label_dataframe(
            small_dataframe,
            target_pips=[10],
            stop_pips=[5],
            horizons=[60],
            use_cache=False,
            return_dict=False
        )
        
        # Load the saved file
        assert len(saved_files) == 1
        df = pd.read_parquet(saved_files[0])
        
        # Check structure
        assert len(df) == len(small_dataframe) - 1, "Should have N-1 rows"
        
        # Check expected columns exist
        expected_columns = [
            'candle_idx', 'entry_price', 'target_pip', 'stop_pip', 'horizon_minutes',
            'up_outcome', 'up_hit_target', 'up_hit_stop', 'up_time_to_target', 'up_time_to_stop',
            'up_mfe', 'up_mae', 'up_r_multiple',
            'down_outcome', 'down_hit_target', 'down_hit_stop', 'down_time_to_target', 'down_time_to_stop',
            'down_mfe', 'down_mae', 'down_r_multiple'
        ]
        
        for col in expected_columns:
            assert col in df.columns, f"Column {col} should exist"
        
        # Check data types
        assert df['target_pip'].iloc[0] == 10
        assert df['stop_pip'].iloc[0] == 5
        assert df['horizon_minutes'].iloc[0] == 60
    
    def test_resume_support_skips_existing_files(self, small_dataframe, temp_labels_dir):
        """Test that labeling can resume and skip already processed configs"""
        # First run - process only 2 configs
        saved_files_1 = label_dataframe(
            small_dataframe,
            target_pips=[5],
            stop_pips=[5],
            horizons=[30, 60],
            use_cache=False,
            return_dict=False
        )
        
        assert len(saved_files_1) == 2, "First run should save 2 files"
        
        # Second run - add more configs (should skip the existing ones)
        saved_files_2 = label_dataframe(
            small_dataframe,
            target_pips=[5, 10],
            stop_pips=[5],
            horizons=[30, 60],
            use_cache=False,
            return_dict=False
        )
        
        # Should now have 4 total files (2 from first run + 2 new)
        assert len(saved_files_2) == 4, "Second run should have 4 total files"
        
        # Verify all files exist
        for file_path in saved_files_2:
            assert Path(file_path).exists(), f"File should exist: {file_path}"
    
    def test_load_label_results_single_config(self, small_dataframe, temp_labels_dir):
        """Test loading a single config result"""
        # Save some results
        label_dataframe(
            small_dataframe,
            target_pips=[10],
            stop_pips=[5],
            horizons=[60],
            use_cache=False,
            return_dict=False
        )
        
        # Load the result
        df = load_label_results("T10_S5_H60")
        
        assert isinstance(df, pd.DataFrame)
        assert len(df) == len(small_dataframe) - 1
        assert 'up_outcome' in df.columns
        assert 'down_outcome' in df.columns
    
    def test_load_label_results_missing_file_raises_error(self, temp_labels_dir):
        """Test that loading non-existent config raises FileNotFoundError"""
        with pytest.raises(FileNotFoundError):
            load_label_results("T999_S999_H999")
    
    def test_load_all_label_results(self, small_dataframe, temp_labels_dir):
        """Test loading all label results at once"""
        # Save multiple configs
        label_dataframe(
            small_dataframe,
            target_pips=[5, 10],
            stop_pips=[5],
            horizons=[30, 60],
            use_cache=False,
            return_dict=False
        )
        
        # Load all results
        results = load_all_label_results()
        
        assert isinstance(results, dict)
        assert len(results) == 4
        
        expected_configs = ['T5_S5_H30', 'T5_S5_H60', 'T10_S5_H30', 'T10_S5_H60']
        for config in expected_configs:
            assert config in results, f"Config {config} should be in results"
            assert isinstance(results[config], pd.DataFrame)
    
    def test_return_dict_backward_compatibility(self, small_dataframe, temp_labels_dir):
        """Test that return_dict=True works for backward compatibility"""
        # Use return_dict=True to get old behavior
        results = label_dataframe(
            small_dataframe,
            target_pips=[5],
            stop_pips=[5],
            horizons=[30],
            use_cache=False,
            return_dict=True  # Old behavior
        )
        
        # Should return dict, not list
        assert isinstance(results, dict)
        assert 'T5_S5_H30' in results
        assert isinstance(results['T5_S5_H30'], pd.DataFrame)
        
        # Files should still be saved on disk
        assert (temp_labels_dir / "T5_S5_H30.parquet").exists()
    
    def test_memory_efficient_returns_file_list(self, small_dataframe, temp_labels_dir):
        """Test that default behavior returns list of file paths"""
        # Default behavior (return_dict=False)
        result = label_dataframe(
            small_dataframe,
            target_pips=[5],
            stop_pips=[5],
            horizons=[30],
            use_cache=False
        )
        
        # Should return list of file paths
        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], str)
        assert result[0].endswith('.parquet')
    
    def test_multiple_runs_accumulate_files(self, small_dataframe, temp_labels_dir):
        """Test that multiple runs accumulate files correctly"""
        # First run
        label_dataframe(
            small_dataframe,
            target_pips=[5],
            stop_pips=[5],
            horizons=[30],
            use_cache=False,
            return_dict=False
        )
        
        # Check we have 1 file
        files = list(temp_labels_dir.glob("*.parquet"))
        assert len(files) == 1
        
        # Second run with different config
        label_dataframe(
            small_dataframe,
            target_pips=[10],
            stop_pips=[10],
            horizons=[60],
            use_cache=False,
            return_dict=False
        )
        
        # Check we now have 2 files
        files = list(temp_labels_dir.glob("*.parquet"))
        assert len(files) == 2
    
    def test_file_naming_convention(self, small_dataframe, temp_labels_dir):
        """Test that files follow the T{target}_S{stop}_H{horizon} naming convention"""
        label_dataframe(
            small_dataframe,
            target_pips=[5, 10, 15],
            stop_pips=[5, 10],
            horizons=[30, 60],
            use_cache=False,
            return_dict=False
        )
        
        files = list(temp_labels_dir.glob("*.parquet"))
        
        # Check naming pattern
        for file in files:
            name = file.stem
            assert name.startswith('T'), f"File {name} should start with 'T'"
            assert '_S' in name, f"File {name} should contain '_S'"
            assert '_H' in name, f"File {name} should contain '_H'"
            
            # Verify it can be parsed
            parts = name.split('_')
            assert len(parts) == 3, f"File {name} should have 3 parts"
            assert parts[0].startswith('T')
            assert parts[1].startswith('S')
            assert parts[2].startswith('H')


class TestLabelDataIntegrity:
    """Test that the memory-efficient version produces identical results"""
    
    def test_results_match_original_format(self, small_dataframe, temp_labels_dir):
        """Test that saved results match the original in-memory format"""
        # Get results using return_dict=True (backward compatibility)
        dict_results = label_dataframe(
            small_dataframe,
            target_pips=[10],
            stop_pips=[5],
            horizons=[60],
            use_cache=False,
            return_dict=True
        )
        
        # Load from disk
        disk_result = load_label_results("T10_S5_H60")
        
        # Compare
        memory_result = dict_results['T10_S5_H60']
        
        assert len(disk_result) == len(memory_result)
        assert list(disk_result.columns) == list(memory_result.columns)
        
        # Check data equality (allowing for floating point differences)
        pd.testing.assert_frame_equal(disk_result, memory_result)


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s'])
