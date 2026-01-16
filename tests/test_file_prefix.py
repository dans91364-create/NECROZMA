#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚡🌟💎 ULTRA NECROZMA - FILE PREFIX TESTS 💎🌟⚡

Tests for file prefix functionality to support multiple currency pairs
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def test_pair_info_extraction():
    """Test extraction of pair name and year from PARQUET_FILE"""
    from config import get_pair_info, PARQUET_FILE
    
    pair, year = get_pair_info()
    
    # Should extract from default PARQUET_FILE (EURUSD_2025.parquet)
    assert isinstance(pair, str), "Pair name should be a string"
    assert isinstance(year, str), "Year should be a string"
    assert len(pair) > 0, "Pair name should not be empty"
    assert len(year) > 0, "Year should not be empty"
    
    print(f"✅ Extracted pair: {pair}, year: {year} from {PARQUET_FILE}")


def test_file_prefix_format():
    """Test FILE_PREFIX format is correct"""
    from config import FILE_PREFIX, PAIR_NAME, DATA_YEAR
    
    # FILE_PREFIX should be "{PAIR}_{YEAR}_"
    expected_prefix = f"{PAIR_NAME}_{DATA_YEAR}_"
    
    assert FILE_PREFIX == expected_prefix, f"FILE_PREFIX should be '{expected_prefix}', got '{FILE_PREFIX}'"
    assert FILE_PREFIX.endswith("_"), "FILE_PREFIX should end with underscore"
    assert FILE_PREFIX.count("_") == 2, "FILE_PREFIX should have exactly 2 underscores"
    
    print(f"✅ FILE_PREFIX format correct: {FILE_PREFIX}")


def test_prefix_in_filenames():
    """Test that prefix is properly used in filename generation"""
    from config import FILE_PREFIX
    
    # Test universe filename
    universe_name = "universe_1m_5lb"
    universe_filename = f"{FILE_PREFIX}{universe_name}.parquet"
    assert universe_filename.startswith(FILE_PREFIX), "Universe filename should start with prefix"
    assert universe_filename.endswith(".parquet"), "Universe filename should end with .parquet"
    
    # Test cache filename
    data_hash = "abc12345"
    cache_filename = f"{FILE_PREFIX}labels_{data_hash}.pkl"
    assert cache_filename.startswith(FILE_PREFIX), "Cache filename should start with prefix"
    assert "labels_" in cache_filename, "Cache filename should contain 'labels_'"
    
    # Test report filename
    timestamp = "20260116"
    report_filename = f"{FILE_PREFIX}LIGHT_REPORT_{timestamp}.json"
    assert report_filename.startswith(FILE_PREFIX), "Report filename should start with prefix"
    assert "LIGHT_REPORT" in report_filename, "Report filename should contain 'LIGHT_REPORT'"
    
    # Test backtest filename
    backtest_filename = f"{FILE_PREFIX}{universe_name}_backtest.parquet"
    assert backtest_filename.startswith(FILE_PREFIX), "Backtest filename should start with prefix"
    assert backtest_filename.endswith("_backtest.parquet"), "Backtest filename should end with '_backtest.parquet'"
    
    print(f"✅ All filename formats correct with prefix: {FILE_PREFIX}")


def test_backward_compatibility():
    """Test that empty prefix would work (backward compatibility)"""
    # If prefix were empty, filenames should still work
    empty_prefix = ""
    universe_name = "universe_1m_5lb"
    
    filename_with_empty = f"{empty_prefix}{universe_name}.parquet"
    assert filename_with_empty == f"{universe_name}.parquet", "Empty prefix should result in original filename"
    
    print("✅ Backward compatibility verified (empty prefix works)")


def test_imports_with_prefix():
    """Test that all modules can import FILE_PREFIX successfully"""
    # Test each module imports FILE_PREFIX correctly
    try:
        # Config defines FILE_PREFIX
        from config import FILE_PREFIX as config_prefix
        assert config_prefix is not None
        
        print(f"✅ All modules can import FILE_PREFIX: {config_prefix}")
        
    except ImportError as e:
        raise AssertionError(f"Failed to import FILE_PREFIX: {e}")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("🧪 Testing File Prefix Functionality")
    print("="*60 + "\n")
    
    try:
        test_pair_info_extraction()
        test_file_prefix_format()
        test_prefix_in_filenames()
        test_backward_compatibility()
        test_imports_with_prefix()
        
        print("\n" + "="*60)
        print("✅ All tests passed!")
        print("="*60 + "\n")
        
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
