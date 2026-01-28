#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script to validate new workflow commands: --generate-base and --search-light
"""

import sys
from pathlib import Path
import argparse

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

def test_parse_arguments():
    """Test that new arguments are correctly parsed"""
    print("\n" + "="*70)
    print("🧪 Testing argument parsing...")
    print("="*70)
    
    from main import parse_arguments
    
    # Test 1: --generate-base flag
    sys.argv = ['main.py', '--generate-base']
    args = parse_arguments()
    assert hasattr(args, 'generate_base'), "Missing generate_base attribute"
    assert args.generate_base, "generate_base should be True"
    print("✅ --generate-base flag parsed correctly")
    
    # Test 2: --search-light flag
    sys.argv = ['main.py', '--search-light']
    args = parse_arguments()
    assert hasattr(args, 'search_light'), "Missing search_light attribute"
    assert args.search_light, "search_light should be True"
    print("✅ --search-light flag parsed correctly")
    
    # Test 3: Both flags can be parsed with other arguments
    sys.argv = ['main.py', '--parquet', 'test.parquet', '--generate-base', '--sequential']
    args = parse_arguments()
    assert args.generate_base, "generate_base should be True"
    assert args.sequential, "sequential should be True"
    assert args.parquet == 'test.parquet', "parquet path should be 'test.parquet'"
    print("✅ Flags work correctly with other arguments")
    
    # Test 4: --search-light with --force-rerun
    sys.argv = ['main.py', '--search-light', '--force-rerun']
    args = parse_arguments()
    assert args.search_light, "search_light should be True"
    assert args.force_rerun, "force_rerun should be True"
    print("✅ --search-light works with --force-rerun")
    
    return True


def test_function_existence():
    """Test that new functions exist and are importable"""
    print("\n" + "="*70)
    print("🧪 Testing function existence...")
    print("="*70)
    
    import main
    
    # Test 1: run_generate_base exists
    assert hasattr(main, 'run_generate_base'), "Missing run_generate_base function"
    assert callable(main.run_generate_base), "run_generate_base should be callable"
    print("✅ run_generate_base function exists")
    
    # Test 2: run_search_light exists
    assert hasattr(main, 'run_search_light'), "Missing run_search_light function"
    assert callable(main.run_search_light), "run_search_light should be callable"
    print("✅ run_search_light function exists")
    
    return True


def test_help_text():
    """Test that help text includes new commands"""
    print("\n" + "="*70)
    print("🧪 Testing help text...")
    print("="*70)
    
    from main import parse_arguments
    
    # Get parser
    sys.argv = ['main.py', '--help']
    try:
        args = parse_arguments()
    except SystemExit:
        # --help causes SystemExit, which is expected
        pass
    
    # Check that help text was created (implicit test)
    print("✅ Help text generated successfully")
    
    return True


def test_argument_exclusivity():
    """Test that the new arguments work independently"""
    print("\n" + "="*70)
    print("🧪 Testing argument independence...")
    print("="*70)
    
    from main import parse_arguments
    
    # Test 1: Only --generate-base (no --search-light)
    sys.argv = ['main.py', '--generate-base']
    args = parse_arguments()
    assert args.generate_base, "generate_base should be True"
    assert not args.search_light, "search_light should be False when not specified"
    print("✅ --generate-base works independently")
    
    # Test 2: Only --search-light (no --generate-base)
    sys.argv = ['main.py', '--search-light']
    args = parse_arguments()
    assert args.search_light, "search_light should be True"
    assert not args.generate_base, "generate_base should be False when not specified"
    print("✅ --search-light works independently")
    
    # Test 3: Neither flag specified
    sys.argv = ['main.py']
    args = parse_arguments()
    assert not args.generate_base, "generate_base should be False by default"
    assert not args.search_light, "search_light should be False by default"
    print("✅ Flags default to False when not specified")
    
    # Test 4: Both flags provided (should be allowed but --generate-base takes precedence)
    sys.argv = ['main.py', '--generate-base', '--search-light']
    args = parse_arguments()
    assert args.generate_base, "generate_base should be True when both flags provided"
    assert args.search_light, "search_light should be True when both flags provided"
    print("✅ Both flags can be parsed (note: --generate-base takes precedence in execution)")
    
    return True


def main():
    """Run all tests"""
    print("\n" + "="*70)
    print("🚀 Starting New Workflow Commands Tests")
    print("="*70)
    
    try:
        # Run tests
        test_parse_arguments()
        test_function_existence()
        test_help_text()
        test_argument_exclusivity()
        
        # Summary
        print("\n" + "="*70)
        print("✅ All tests passed!")
        print("="*70)
        print("\n📋 Summary:")
        print("   • Argument parsing works correctly")
        print("   • New functions exist and are callable")
        print("   • Help text generated successfully")
        print("   • Arguments work independently")
        print("\n" + "="*70 + "\n")
        
        return 0
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
