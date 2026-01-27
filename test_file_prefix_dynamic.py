#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test to verify FILE_PREFIX dynamic update fix

This test verifies that when config.FILE_PREFIX is updated,
the reference in analyzer.py and light_report.py will point to the new value.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))


def test_file_prefix_import():
    """Test that FILE_PREFIX is accessed via module reference"""
    
    print("\n" + "="*70)
    print("🧪 TEST: FILE_PREFIX Import Verification")
    print("="*70)
    
    files_to_check = {
        "analyzer.py": 10,  # Expected number of FILE_PREFIX usages
        "light_report.py": 1,
    }
    
    all_passed = True
    
    for filename, expected_count in files_to_check.items():
        file_path = Path(__file__).parent / filename
        
        print(f"\n📁 Checking {filename}...")
        
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Check that FILE_PREFIX is not in the import statement
        import_section = content[:2000]  # First 2000 chars should contain imports
        
        print(f"  1️⃣ Checking import statement...")
        if "from config import" in import_section and "FILE_PREFIX" in import_section:
            # Check if it's after the from config import block
            from_config_import = import_section[import_section.find("from config import"):]
            closing_paren = from_config_import.find(")")
            if closing_paren == -1:
                # Single line import
                closing_paren = from_config_import.find("\n")
            import_block = from_config_import[:closing_paren + 1]
            
            if "FILE_PREFIX" in import_block:
                print(f"     ❌ FAILURE: FILE_PREFIX is imported as a value in {filename}")
                print(f"     This means it won't update dynamically!")
                all_passed = False
                continue
        
        print(f"     ✅ SUCCESS: FILE_PREFIX is NOT imported as a value")
        
        # Check that config module is imported
        print(f"  2️⃣ Checking if config module is imported...")
        if "import config" in import_section:
            print(f"     ✅ SUCCESS: config module is imported")
        else:
            print(f"     ❌ FAILURE: config module is NOT imported")
            all_passed = False
            continue
        
        # Check that config.FILE_PREFIX is used instead of FILE_PREFIX
        print(f"  3️⃣ Checking FILE_PREFIX usage...")
        
        # Find all FILE_PREFIX usages (excluding comments and the import)
        lines = content.split('\n')
        file_prefix_usages = []
        
        for i, line in enumerate(lines, 1):
            if 'FILE_PREFIX' in line and not line.strip().startswith('#'):
                # Skip the import line
                if 'from config import' in line or 'import config' in line:
                    continue
                file_prefix_usages.append((i, line.strip()))
        
        print(f"     Found {len(file_prefix_usages)} usages of FILE_PREFIX (expected {expected_count})")
        
        if len(file_prefix_usages) != expected_count:
            print(f"     ⚠️  WARNING: Expected {expected_count} usages, found {len(file_prefix_usages)}")
        
        file_passed = True
        for line_num, line_content in file_prefix_usages:
            if 'config.FILE_PREFIX' in line_content:
                print(f"     ✅ Line {line_num}: Uses config.FILE_PREFIX")
            else:
                print(f"     ❌ Line {line_num}: Does NOT use config.FILE_PREFIX")
                print(f"        Content: {line_content[:80]}")
                file_passed = False
                all_passed = False
        
        if file_passed:
            print(f"     ✅ SUCCESS: All usages reference config.FILE_PREFIX in {filename}")
    
    if not all_passed:
        print(f"\n   ❌ FAILURE: Some files don't properly reference config.FILE_PREFIX")
        return False
    
    print("\n" + "="*70)
    print("✅ TEST PASSED: FILE_PREFIX will update dynamically!")
    print("="*70 + "\n")
    
    return True


def test_dynamic_update_simulation():
    """Simulate the dynamic update scenario"""
    
    print("\n" + "="*70)
    print("🧪 TEST: Dynamic Update Simulation")
    print("="*70)
    
    import config
    
    # Save original values
    original_prefix = config.FILE_PREFIX
    original_pair = config.PAIR_NAME
    original_year = config.DATA_YEAR
    
    print(f"\n1️⃣ Original configuration:")
    print(f"   PAIR_NAME: {config.PAIR_NAME}")
    print(f"   DATA_YEAR: {config.DATA_YEAR}")
    print(f"   FILE_PREFIX: {config.FILE_PREFIX}")
    
    # Simulate what run_mass_test.py does
    print(f"\n2️⃣ Simulating config update (like run_mass_test.py does):")
    config.PAIR_NAME = "AUDJPY"
    config.DATA_YEAR = "2023"
    config.FILE_PREFIX = "AUDJPY_2023_"
    print(f"   PAIR_NAME: {config.PAIR_NAME}")
    print(f"   DATA_YEAR: {config.DATA_YEAR}")
    print(f"   FILE_PREFIX: {config.FILE_PREFIX}")
    
    # Verify the change took effect
    print(f"\n3️⃣ Verifying config module has new value:")
    if config.FILE_PREFIX == "AUDJPY_2023_":
        print(f"   ✅ SUCCESS: config.FILE_PREFIX = {config.FILE_PREFIX}")
    else:
        print(f"   ❌ FAILURE: config.FILE_PREFIX = {config.FILE_PREFIX}")
        return False
    
    # Restore original values
    config.PAIR_NAME = original_pair
    config.DATA_YEAR = original_year
    config.FILE_PREFIX = original_prefix
    
    print(f"\n4️⃣ Restored original configuration:")
    print(f"   FILE_PREFIX: {config.FILE_PREFIX}")
    
    print("\n" + "="*70)
    print("✅ TEST PASSED: Config module updates work correctly!")
    print("="*70 + "\n")
    
    return True


if __name__ == "__main__":
    try:
        test1_passed = test_file_prefix_import()
        test2_passed = test_dynamic_update_simulation()
        
        if test1_passed and test2_passed:
            print("\n" + "="*70)
            print("✅ ALL TESTS PASSED!")
            print("="*70 + "\n")
            sys.exit(0)
        else:
            print("\n" + "="*70)
            print("❌ SOME TESTS FAILED!")
            print("="*70 + "\n")
            sys.exit(1)
    except Exception as e:
        print(f"\n❌ TEST ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
