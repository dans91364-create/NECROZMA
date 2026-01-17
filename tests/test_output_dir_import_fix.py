#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test to verify OUTPUT_DIR and FILE_PREFIX import fix in run_strategy_discovery
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def test_output_dir_import_available_in_function():
    """
    Test that OUTPUT_DIR and FILE_PREFIX are properly imported in run_strategy_discovery.
    This test verifies the fix for the critical bug where these imports were missing.
    """
    # Import the function
    from main import run_strategy_discovery
    
    # Get the function's source code
    import inspect
    source = inspect.getsource(run_strategy_discovery)
    
    # Verify the imports are present in the function
    assert "from config import OUTPUT_DIR, FILE_PREFIX" in source, \
        "OUTPUT_DIR and FILE_PREFIX must be imported in run_strategy_discovery function"
    
    print("✅ Test passed: OUTPUT_DIR and FILE_PREFIX imports are present in run_strategy_discovery")


def test_config_exports_output_dir_and_file_prefix():
    """
    Test that config.py properly exports OUTPUT_DIR and FILE_PREFIX
    """
    from config import OUTPUT_DIR, FILE_PREFIX
    
    # Verify they are defined
    assert OUTPUT_DIR is not None, "OUTPUT_DIR must be defined in config.py"
    assert FILE_PREFIX is not None, "FILE_PREFIX must be defined in config.py"
    
    # Verify OUTPUT_DIR is a Path object
    assert isinstance(OUTPUT_DIR, Path), "OUTPUT_DIR must be a Path object"
    
    # Verify FILE_PREFIX is a string
    assert isinstance(FILE_PREFIX, str), "FILE_PREFIX must be a string"
    
    print(f"✅ Test passed: OUTPUT_DIR={OUTPUT_DIR}, FILE_PREFIX={FILE_PREFIX}")


def test_pandas_import_in_regime_detection():
    """
    Test that pandas is imported for reading parquet files in regime detection
    """
    from main import run_strategy_discovery
    import inspect
    
    source = inspect.getsource(run_strategy_discovery)
    
    # Verify pandas is imported for reading parquet
    assert "import pandas as pd" in source, \
        "pandas must be imported for reading regimes.parquet"
    
    print("✅ Test passed: pandas import is present for parquet reading")


if __name__ == "__main__":
    print("Running OUTPUT_DIR import fix tests...\n")
    
    test_output_dir_import_available_in_function()
    test_config_exports_output_dir_and_file_prefix()
    test_pandas_import_in_regime_detection()
    
    print("\n🎉 All tests passed!")
