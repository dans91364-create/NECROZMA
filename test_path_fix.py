#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test to verify that the Path UnboundLocalError is fixed in main.py
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))


def test_path_import_in_main():
    """
    Test that Path is accessible throughout main() function.
    This test verifies that the UnboundLocalError is fixed.
    """
    # Import main module
    import main
    
    # Check that Path is imported at module level
    assert hasattr(main, 'Path'), "Path should be imported at module level"
    
    # Check that the main function exists
    assert hasattr(main, 'main'), "main() function should exist"
    
    # We can't easily test the full main() function without data,
    # but we can check that the import structure is correct
    import inspect
    source = inspect.getsource(main.main)
    
    # Count occurrences of "from pathlib import Path" in main()
    path_imports = source.count("from pathlib import Path")
    
    # Should be 0 - Path should only be imported at module level
    assert path_imports == 0, f"Found {path_imports} 'from pathlib import Path' in main(), expected 0. Path should only be imported at module level."
    
    print("✅ Test passed: Path is only imported at module level, not within main()")
    return True


if __name__ == "__main__":
    try:
        test_path_import_in_main()
        print("\n✅ All tests passed!")
        sys.exit(0)
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
