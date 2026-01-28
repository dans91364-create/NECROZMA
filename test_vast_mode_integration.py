#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Integration test for VAST mode functionality
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))


def test_import_and_function_availability():
    """Test that all VAST mode functions are available and importable"""
    print("Testing imports and function availability...")
    
    from main import (
        detect_resources,
        print_resources_banner,
        run_vast_mode,
        run_generate_base_single,
        run_search_light_single
    )
    
    print("✅ All VAST mode functions imported successfully")
    return True


def test_detect_resources():
    """Test resource detection"""
    print("\nTesting resource detection...")
    
    from main import detect_resources
    
    resources = detect_resources()
    
    # Verify structure
    required_keys = [
        'cpu_cores',
        'ram_gb',
        'recommended_parallel_pairs',
        'recommended_workers_per_pair',
        'recommended_chunk_size'
    ]
    
    for key in required_keys:
        assert key in resources, f"Missing key: {key}"
        assert isinstance(resources[key], (int, float)), f"{key} should be numeric"
        assert resources[key] > 0, f"{key} should be positive"
    
    # Verify logic
    cpu_cores = resources['cpu_cores']
    expected_pairs = min(30, cpu_cores // 4)
    assert resources['recommended_parallel_pairs'] == expected_pairs, \
        f"Parallel pairs calculation incorrect: got {resources['recommended_parallel_pairs']}, expected {expected_pairs}"
    
    assert resources['recommended_workers_per_pair'] == 4, \
        "Workers per pair should be 4"
    
    print(f"✅ Resource detection working correctly")
    print(f"   CPU: {resources['cpu_cores']} cores")
    print(f"   RAM: {resources['ram_gb']:.1f} GB")
    print(f"   Recommended: {resources['recommended_parallel_pairs']} pairs, {resources['recommended_workers_per_pair']} workers/pair")
    
    return True


def test_banner_formatting():
    """Test banner formatting"""
    print("\nTesting banner formatting...")
    
    from main import print_resources_banner, detect_resources
    
    resources = detect_resources()
    
    # Test with various inputs
    test_cases = [
        (5, 2, 4),
        (30, 30, 4),
        (100, 50, 8),
    ]
    
    for num_files, parallel_pairs, workers in test_cases:
        # Should not raise any exceptions
        print_resources_banner(resources, num_files, parallel_pairs, workers)
    
    print("✅ Banner formatting working correctly")
    return True


def test_argument_parsing():
    """Test that new arguments are properly integrated"""
    print("\nTesting argument parsing...")
    
    from main import parse_arguments
    
    # Save original argv
    original_argv = sys.argv
    
    try:
        # Test vast-mode flag
        sys.argv = ['main.py', '--vast-mode', '--input-dir', 'test', '--generate-base']
        args = parse_arguments()
        
        assert hasattr(args, 'vast_mode'), "Missing vast_mode attribute"
        assert hasattr(args, 'input_dir'), "Missing input_dir attribute"
        assert hasattr(args, 'parallel_pairs'), "Missing parallel_pairs attribute"
        assert hasattr(args, 'max_workers'), "Missing max_workers attribute"
        
        assert args.vast_mode == True, "vast_mode should be True"
        assert args.input_dir == 'test', "input_dir should be 'test'"
        assert args.parallel_pairs == 1, "parallel_pairs should default to 1"
        assert args.max_workers is None, "max_workers should default to None"
        
        # Test with explicit values
        sys.argv = ['main.py', '--vast-mode', '--input-dir', 'test', 
                   '--parallel-pairs', '10', '--max-workers', '8', '--generate-base']
        args = parse_arguments()
        
        assert args.parallel_pairs == 10, "parallel_pairs should be 10"
        assert args.max_workers == 8, "max_workers should be 8"
        
        print("✅ Argument parsing working correctly")
        return True
        
    finally:
        # Restore original argv
        sys.argv = original_argv


def test_validation_logic():
    """Test validation logic in run_vast_mode"""
    print("\nTesting validation logic...")
    
    from main import run_vast_mode
    
    class MockArgs:
        vast_mode = True
        skip_telegram = True
        parallel_pairs = 1
        max_workers = None
    
    # Test 1: Missing input_dir
    args = MockArgs()
    args.input_dir = None
    args.generate_base = True
    args.search_light = False
    
    try:
        run_vast_mode(args)
        assert False, "Should have exited due to missing input_dir"
    except SystemExit:
        pass
    
    # Test 2: Missing mode flag
    args = MockArgs()
    args.input_dir = "/tmp"
    args.generate_base = False
    args.search_light = False
    
    try:
        run_vast_mode(args)
        assert False, "Should have exited due to missing mode flag"
    except SystemExit:
        pass
    
    # Test 3: Non-existent directory
    args = MockArgs()
    args.input_dir = "/nonexistent/directory/12345"
    args.generate_base = True
    args.search_light = False
    
    try:
        run_vast_mode(args)
        assert False, "Should have exited due to non-existent directory"
    except SystemExit:
        pass
    
    print("✅ Validation logic working correctly")
    return True


def test_worker_function_signatures():
    """Test worker function signatures"""
    print("\nTesting worker function signatures...")
    
    from main import run_generate_base_single, run_search_light_single
    import inspect
    
    # Check run_generate_base_single
    sig = inspect.signature(run_generate_base_single)
    params = list(sig.parameters.keys())
    
    assert 'parquet_file' in params, "Missing parquet_file parameter"
    assert 'workers_per_pair' in params, "Missing workers_per_pair parameter"
    assert 'skip_telegram' in params, "Missing skip_telegram parameter"
    
    # Check run_search_light_single
    sig = inspect.signature(run_search_light_single)
    params = list(sig.parameters.keys())
    
    assert 'parquet_file' in params, "Missing parquet_file parameter"
    assert 'workers_per_pair' in params, "Missing workers_per_pair parameter"
    assert 'skip_telegram' in params, "Missing skip_telegram parameter"
    assert 'force_rerun' in params, "Missing force_rerun parameter"
    
    print("✅ Worker function signatures correct")
    return True


def main():
    """Run all integration tests"""
    print("\n" + "="*80)
    print("🧪 VAST MODE INTEGRATION TESTS")
    print("="*80 + "\n")
    
    tests = [
        test_import_and_function_availability,
        test_detect_resources,
        test_banner_formatting,
        test_argument_parsing,
        test_validation_logic,
        test_worker_function_signatures,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"❌ {test.__name__} FAILED: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    print("\n" + "="*80)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("="*80 + "\n")
    
    if failed > 0:
        sys.exit(1)
    else:
        print("✅ ALL INTEGRATION TESTS PASSED\n")


if __name__ == "__main__":
    main()
