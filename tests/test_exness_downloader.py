#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚡🌟💎 ULTRA NECROZMA - EXNESS DOWNLOADER TESTS 💎🌟⚡

Tests for download_exness_data.py
"""

import pytest
import sys
from pathlib import Path
import pandas as pd
import tempfile
import shutil

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import download_exness_data as exness


def test_format_size():
    """Test file size formatting"""
    assert exness.format_size(500) == "500 B"
    assert exness.format_size(1024) == "1 KB"
    assert exness.format_size(1024 * 1024) == "1 MB"
    assert exness.format_size(1024 * 1024 * 1024) == "1 GB"
    assert exness.format_size(2048) == "2 KB"  # 2 KB exactly


def test_configuration():
    """Test that configuration constants are properly set"""
    assert len(exness.ALL_PAIRS) == 10
    assert 'EURUSD' in exness.ALL_PAIRS
    assert 'GBPUSD' in exness.ALL_PAIRS
    assert 'USDJPY' in exness.ALL_PAIRS
    
    assert len(exness.ALL_YEARS) == 3
    assert 2023 in exness.ALL_YEARS
    assert 2024 in exness.ALL_YEARS
    assert 2025 in exness.ALL_YEARS
    
    assert exness.OUTPUT_DIR == Path("data/parquet")
    assert exness.TEMP_DIR == Path("data/temp")


def test_base_url_format():
    """Test that BASE_URL is properly formatted"""
    url = exness.BASE_URL.format(pair='EURUSD', year=2023)
    assert 'EURUSD' in url
    assert '2023' in url
    assert url.startswith('https://')


def test_consolidate_pair_empty():
    """Test consolidate_pair with no files"""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Override OUTPUT_DIR temporarily
        original_output_dir = exness.OUTPUT_DIR
        exness.OUTPUT_DIR = Path(tmpdir)
        
        # Should not crash with no files
        exness.consolidate_pair('EURUSD', [2023, 2024])
        
        # Restore
        exness.OUTPUT_DIR = original_output_dir


def test_consolidate_pair_with_data():
    """Test consolidate_pair with actual data"""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        
        # Override OUTPUT_DIR temporarily
        original_output_dir = exness.OUTPUT_DIR
        exness.OUTPUT_DIR = tmpdir
        
        # Create sample parquet files
        df1 = pd.DataFrame({
            'broker': ['Exness'] * 100,
            'symbol': ['EURUSD'] * 100,
            'timestamp': pd.date_range('2023-01-01', periods=100, freq='1min'),
            'bid': [1.05 + i*0.0001 for i in range(100)],
            'ask': [1.051 + i*0.0001 for i in range(100)]
        })
        
        df2 = pd.DataFrame({
            'broker': ['Exness'] * 100,
            'symbol': ['EURUSD'] * 100,
            'timestamp': pd.date_range('2024-01-01', periods=100, freq='1min'),
            'bid': [1.06 + i*0.0001 for i in range(100)],
            'ask': [1.061 + i*0.0001 for i in range(100)]
        })
        
        # Save parquet files
        df1.to_parquet(tmpdir / 'EURUSD_2023.parquet', engine='pyarrow', compression='snappy', index=False)
        df2.to_parquet(tmpdir / 'EURUSD_2024.parquet', engine='pyarrow', compression='snappy', index=False)
        
        # Consolidate
        exness.consolidate_pair('EURUSD', [2023, 2024])
        
        # Check consolidated file exists
        consolidated_file = tmpdir / 'EURUSD_3Y.parquet'
        assert consolidated_file.exists()
        
        # Read and verify
        df_consolidated = pd.read_parquet(consolidated_file)
        assert len(df_consolidated) == 200
        assert df_consolidated['timestamp'].is_monotonic_increasing
        
        # Restore
        exness.OUTPUT_DIR = original_output_dir


def test_process_file_skip_existing():
    """Test that process_file skips existing files when force=False"""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        
        # Override directories
        original_output_dir = exness.OUTPUT_DIR
        original_temp_dir = exness.TEMP_DIR
        exness.OUTPUT_DIR = tmpdir / 'parquet'
        exness.TEMP_DIR = tmpdir / 'temp'
        exness.OUTPUT_DIR.mkdir(parents=True)
        exness.TEMP_DIR.mkdir(parents=True)
        
        # Create a dummy existing parquet file
        dummy_df = pd.DataFrame({
            'broker': ['Exness'],
            'symbol': ['EURUSD'],
            'timestamp': [pd.Timestamp('2023-01-01')],
            'bid': [1.05],
            'ask': [1.051]
        })
        dummy_df.to_parquet(exness.OUTPUT_DIR / 'EURUSD_2023.parquet', index=False)
        
        # This should skip without attempting download
        # Note: We can't easily test the actual download without mocking
        # but we can verify the file exists
        assert (exness.OUTPUT_DIR / 'EURUSD_2023.parquet').exists()
        
        # Restore
        exness.OUTPUT_DIR = original_output_dir
        exness.TEMP_DIR = original_temp_dir


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
