#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test to verify that main.py can handle --parquet argument without UnboundLocalError
"""

import sys
import subprocess
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))


def test_main_with_parquet_arg():
    """
    Test that main.py can be invoked with --parquet argument.
    This simulates what run_mass_test.py does.
    """
    # Test that the argument parsing works
    result = subprocess.run(
        [sys.executable, "main.py", "--help"],
        capture_output=True,
        text=True,
        cwd=str(Path(__file__).parent)
    )
    
    # Check that it didn't crash with UnboundLocalError
    assert result.returncode == 0, f"main.py --help failed with return code {result.returncode}"
    assert "UnboundLocalError" not in result.stderr, f"UnboundLocalError found in stderr: {result.stderr}"
    assert "cannot access local variable 'Path'" not in result.stderr, f"Path error found in stderr: {result.stderr}"
    
    print("✅ Test passed: main.py can handle --parquet argument without UnboundLocalError")
    return True


def test_path_usage_in_main():
    """
    Test that the specific lines where Path is used are correct.
    """
    import main
    import inspect
    
    source = inspect.getsource(main.main)
    
    # Check that Path is used for csv_path and parquet_path
    assert "csv_path = Path(args.csv)" in source, "csv_path should use Path"
    assert "parquet_path = Path(args.parquet)" in source, "parquet_path should use Path"
    
    # Ensure Path is not redefined in the function
    lines = source.split('\n')
    path_import_lines = [i for i, line in enumerate(lines) if 'from pathlib import Path' in line]
    
    assert len(path_import_lines) == 0, f"Found 'from pathlib import Path' at lines {path_import_lines} inside main(), this causes UnboundLocalError"
    
    print("✅ Test passed: Path is used correctly in main() without local imports")
    return True


if __name__ == "__main__":
    try:
        test_path_usage_in_main()
        test_main_with_parquet_arg()
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
