#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test to verify that the Path import fix resolves the UnboundLocalError
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

def test_path_import_fix():
    """
    Test that verifies the fix for UnboundLocalError in main.py
    
    The issue was:
    - Global import: from pathlib import Path (line 16)
    - Local import: from pathlib import Path (line 1389 inside if block)
    - Usage at line 1219: Path(args.parquet) - used BEFORE local import
    
    This caused UnboundLocalError because Python treated Path as local variable
    throughout the entire main() function.
    
    The fix: Remove redundant local import at line 1389
    """
    print("=" * 70)
    print("Testing Path import fix in main.py")
    print("=" * 70)
    
    # Verify that main.py can be imported without errors
    try:
        import main
        print("✅ main.py imported successfully (no UnboundLocalError)")
    except UnboundLocalError as e:
        print(f"❌ UnboundLocalError still exists: {e}")
        raise
    except Exception as e:
        # Other import errors might occur due to missing dependencies
        # but UnboundLocalError should not occur
        print(f"⚠️  Other import error (not UnboundLocalError): {e}")
        print("   This is expected if dependencies are missing")
    
    # Verify that Path is imported at module level in main.py
    with open('main.py', 'r') as f:
        content = f.read()
        
    # Count occurrences of "from pathlib import Path"
    import_count = content.count('from pathlib import Path')
    
    print(f"\n📊 Analysis of main.py:")
    print(f"   Number of 'from pathlib import Path' statements: {import_count}")
    
    if import_count == 1:
        print("   ✅ Correct! Only one import (global import at line 16)")
    else:
        print(f"   ❌ ERROR! Expected 1 import, found {import_count}")
        print("   There should only be the global import at line 16")
        raise AssertionError(f"Expected 1 Path import, found {import_count}")
    
    # Verify the global import is at the top of the file
    lines = content.split('\n')
    found_global_import = False
    for i, line in enumerate(lines[:30], 1):  # Check first 30 lines
        if 'from pathlib import Path' in line and not line.strip().startswith('#'):
            print(f"   ✅ Global import found at line {i}")
            found_global_import = True
            break
    
    if not found_global_import:
        raise AssertionError("Global 'from pathlib import Path' not found in first 30 lines")
    
    # Verify no local import inside main() function
    # Find the main() function and check for Path imports inside it
    in_main_function = False
    local_path_imports = []
    
    for i, line in enumerate(lines, 1):
        if 'def main():' in line:
            in_main_function = True
            continue
        
        if in_main_function:
            # Exit main() scope when we encounter another top-level function or class
            stripped = line.strip()
            if (stripped.startswith('def ') or stripped.startswith('class ')) and not line.startswith((' ', '\t')):
                # Reached another top-level definition, exit main() scope
                break
            
            # Check for Path import inside main function (excluding comments)
            if 'from pathlib import Path' in stripped and not stripped.startswith('#'):
                local_path_imports.append(i)
    
    if local_path_imports:
        print(f"   ❌ ERROR! Found local Path import(s) inside main() at line(s): {local_path_imports}")
        raise AssertionError(f"Local Path import found inside main() at lines: {local_path_imports}")
    else:
        print("   ✅ No local Path imports inside main() function")
    
    print("\n" + "=" * 70)
    print("✅ All tests passed! Path import fix is correct.")
    print("=" * 70)


if __name__ == "__main__":
    test_path_import_fix()
