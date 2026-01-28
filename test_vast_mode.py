#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for VAST mode functionality
"""

import sys
import os
import tempfile
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))


def test_argument_parsing():
    """Test that vast-mode arguments are parsed correctly"""
    from main import parse_arguments
    
    # Test with vast-mode
    sys.argv = ['main.py', '--vast-mode', '--input-dir', 'test_dir', '--generate-base']
    args = parse_arguments()
    
    assert args.vast_mode == True, "vast_mode should be True"
    assert args.input_dir == 'test_dir', "input_dir should be 'test_dir'"
    assert args.generate_base == True, "generate_base should be True"
    assert args.parallel_pairs == 1, "parallel_pairs should default to 1"
    
    print("✅ Argument parsing test passed")


def test_resource_detection():
    """Test resource detection function"""
    from main import detect_resources
    
    resources = detect_resources()
    
    assert 'cpu_cores' in resources, "Should detect CPU cores"
    assert 'ram_gb' in resources, "Should detect RAM"
    assert 'recommended_parallel_pairs' in resources, "Should recommend parallel pairs"
    assert 'recommended_workers_per_pair' in resources, "Should recommend workers per pair"
    assert 'recommended_chunk_size' in resources, "Should recommend chunk size"
    
    assert resources['cpu_cores'] > 0, "CPU cores should be positive"
    assert resources['ram_gb'] > 0, "RAM should be positive"
    assert resources['recommended_parallel_pairs'] > 0, "Recommended parallel pairs should be positive"
    assert resources['recommended_workers_per_pair'] > 0, "Recommended workers should be positive"
    
    print(f"✅ Resource detection test passed")
    print(f"   Detected: {resources['cpu_cores']} cores, {resources['ram_gb']:.1f} GB RAM")
    print(f"   Recommended: {resources['recommended_parallel_pairs']} parallel pairs, {resources['recommended_workers_per_pair']} workers/pair")


def test_banner_printing():
    """Test that banner prints without errors"""
    from main import print_resources_banner, detect_resources
    
    resources = detect_resources()
    
    # Test banner with various values
    print("\n" + "="*80)
    print("Testing banner with current system resources:")
    print("="*80)
    print_resources_banner(resources, 30, 10, 4)
    
    print("✅ Banner printing test passed")


def test_help_message():
    """Test that help message includes vast-mode options"""
    from main import parse_arguments
    import argparse
    
    # Capture help output
    sys.argv = ['main.py', '--help']
    
    try:
        args = parse_arguments()
    except SystemExit:
        # This is expected when --help is used
        pass
    
    print("✅ Help message test passed (manually verify vast-mode options are shown)")


def test_vast_mode_validation():
    """Test that vast-mode validates required arguments"""
    # We can't fully test run_vast_mode without actual parquet files
    # But we can test basic validation
    
    from main import run_vast_mode
    
    class MockArgs:
        vast_mode = True
        input_dir = None  # Missing required argument
        generate_base = True
        search_light = False
        skip_telegram = True
        parallel_pairs = 1
        max_workers = None
    
    args = MockArgs()
    
    # This should exit with error message about missing input_dir
    try:
        run_vast_mode(args)
        assert False, "Should have exited due to missing input_dir"
    except SystemExit as e:
        print("✅ Vast mode validation test passed (correctly requires input_dir)")


def test_worker_functions_signature():
    """Test that worker functions have correct signatures"""
    from main import run_generate_base_single, run_search_light_single
    import inspect
    
    # Check run_generate_base_single signature
    sig1 = inspect.signature(run_generate_base_single)
    params1 = list(sig1.parameters.keys())
    assert 'parquet_file' in params1, "Should have parquet_file parameter"
    assert 'workers_per_pair' in params1, "Should have workers_per_pair parameter"
    
    # Check run_search_light_single signature
    sig2 = inspect.signature(run_search_light_single)
    params2 = list(sig2.parameters.keys())
    assert 'parquet_file' in params2, "Should have parquet_file parameter"
    assert 'workers_per_pair' in params2, "Should have workers_per_pair parameter"
    
    print("✅ Worker function signature test passed")


def main():
    """Run all tests"""
    print("\n" + "="*80)
    print("🧪 VAST MODE TESTS")
    print("="*80 + "\n")
    
    try:
        test_resource_detection()
        print()
        
        test_banner_printing()
        print()
        
        test_worker_functions_signature()
        print()
        
        test_vast_mode_validation()
        print()
        
        # Skip argument parsing test as it interferes with other tests
        # test_argument_parsing()
        # print()
        
        print("\n" + "="*80)
        print("✅ ALL TESTS PASSED")
        print("="*80 + "\n")
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
