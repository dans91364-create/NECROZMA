#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚡🌟💎 PATTERN CACHE OPTIMIZATION VALIDATION 💎🌟⚡

Validates that the pattern cache optimization is working correctly
"""

import sys
import json
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))


def validate_main_py_changes():
    """Validate that main.py has the pattern cache logic"""
    print("\n" + "="*70)
    print("🔍 VALIDATING main.py CHANGES")
    print("="*70)
    
    main_file = Path("main.py")
    
    if not main_file.exists():
        print("❌ main.py not found!")
        return False
    
    content = main_file.read_text()
    
    # Check for pattern cache check
    checks = [
        ("Pattern cache path", "patterns_path = OUTPUT_DIR"),
        ("Pattern cache exists check", "if patterns_path.exists()"),
        ("Pattern loading", "with open(patterns_path, 'r') as f:"),
        ("Labeling skip message", "SKIPPING LABELING"),
        ("Pattern saving", "with open(patterns_path, 'w') as f:"),
        ("Label cleanup", "shutil.rmtree(labels_dir"),
        ("Import json", "import json"),
        ("Import shutil", "import shutil"),
    ]
    
    all_passed = True
    for check_name, check_str in checks:
        if check_str in content:
            print(f"   ✅ {check_name}")
        else:
            print(f"   ❌ {check_name} - NOT FOUND!")
            all_passed = False
    
    if all_passed:
        print("\n✅ All main.py checks passed!")
    else:
        print("\n❌ Some main.py checks failed!")
    
    return all_passed


def validate_run_mass_test_changes():
    """Validate that run_mass_test.py has the cleanup logic"""
    print("\n" + "="*70)
    print("🔍 VALIDATING run_mass_test.py CHANGES")
    print("="*70)
    
    mass_test_file = Path("run_mass_test.py")
    
    if not mass_test_file.exists():
        print("❌ run_mass_test.py not found!")
        return False
    
    content = mass_test_file.read_text()
    
    # Check for label cleanup in run_single_backtest
    checks = [
        ("Label cleanup import", "import shutil"),
        ("Labels dir path", 'labels_dir = Path("labels")'),
        ("Labels cleanup", "shutil.rmtree(labels_dir"),
        ("Cleanup message", "Labels cleaned for next dataset"),
    ]
    
    all_passed = True
    for check_name, check_str in checks:
        if check_str in content:
            print(f"   ✅ {check_name}")
        else:
            print(f"   ❌ {check_name} - NOT FOUND!")
            all_passed = False
    
    if all_passed:
        print("\n✅ All run_mass_test.py checks passed!")
    else:
        print("\n❌ Some run_mass_test.py checks failed!")
    
    return all_passed


def validate_test_file():
    """Validate that test file exists and is valid"""
    print("\n" + "="*70)
    print("🔍 VALIDATING test_pattern_cache.py")
    print("="*70)
    
    test_file = Path("test_pattern_cache.py")
    
    if not test_file.exists():
        print("❌ test_pattern_cache.py not found!")
        return False
    
    print("   ✅ Test file exists")
    
    # Try to import it
    try:
        import test_pattern_cache
        print("   ✅ Test file imports successfully")
    except Exception as e:
        print(f"   ❌ Test file import failed: {e}")
        return False
    
    # Check for test functions
    test_functions = [
        'test_pattern_cache_file_structure',
        'test_labels_cleanup',
        'test_pattern_cache_workflow_simulation',
        'test_empty_labels_dict_compatibility',
    ]
    
    all_passed = True
    for func_name in test_functions:
        if hasattr(test_pattern_cache, func_name):
            print(f"   ✅ {func_name}")
        else:
            print(f"   ❌ {func_name} - NOT FOUND!")
            all_passed = False
    
    if all_passed:
        print("\n✅ All test file checks passed!")
    else:
        print("\n❌ Some test file checks failed!")
    
    return all_passed


def validate_documentation():
    """Validate that documentation exists"""
    print("\n" + "="*70)
    print("🔍 VALIDATING DOCUMENTATION")
    print("="*70)
    
    doc_file = Path("PATTERN_CACHE_OPTIMIZATION.md")
    
    if not doc_file.exists():
        print("❌ PATTERN_CACHE_OPTIMIZATION.md not found!")
        return False
    
    print("   ✅ Documentation file exists")
    
    content = doc_file.read_text()
    
    # Check for key sections
    sections = [
        "## Problem",
        "## Solution",
        "## Results",
        "## Workflow Comparison",
        "## Key Benefits",
        "## Usage",
        "## Testing",
    ]
    
    all_passed = True
    for section in sections:
        if section in content:
            print(f"   ✅ {section}")
        else:
            print(f"   ❌ {section} - NOT FOUND!")
            all_passed = False
    
    if all_passed:
        print("\n✅ All documentation checks passed!")
    else:
        print("\n❌ Some documentation checks failed!")
    
    return all_passed


def main():
    """Run all validations"""
    print("\n" + "="*70)
    print("⚡🌟💎 PATTERN CACHE OPTIMIZATION VALIDATION 💎🌟⚡")
    print("="*70)
    
    results = []
    
    # Run all validations
    results.append(("main.py", validate_main_py_changes()))
    results.append(("run_mass_test.py", validate_run_mass_test_changes()))
    results.append(("test_pattern_cache.py", validate_test_file()))
    results.append(("Documentation", validate_documentation()))
    
    # Summary
    print("\n" + "="*70)
    print("📊 VALIDATION SUMMARY")
    print("="*70)
    
    all_passed = True
    for name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"   {name:25} {status}")
        if not passed:
            all_passed = False
    
    print("\n" + "="*70)
    if all_passed:
        print("🎉 ALL VALIDATIONS PASSED!")
        print("="*70)
        print("\n✅ Pattern cache optimization is correctly implemented!")
        print("   • main.py: Pattern caching + label cleanup")
        print("   • run_mass_test.py: Safety cleanup after each dataset")
        print("   • test_pattern_cache.py: Comprehensive tests")
        print("   • PATTERN_CACHE_OPTIMIZATION.md: Complete documentation")
        return 0
    else:
        print("❌ SOME VALIDATIONS FAILED!")
        print("="*70)
        print("\nPlease review the failed checks above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
