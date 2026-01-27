#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for run_mass_test.py

Validates:
1. Subprocess calling with correct arguments
2. Progress tracking functionality
3. CLI arguments work correctly
"""

import sys
import json
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Import the module
import run_mass_test


def test_load_save_progress():
    """Test progress loading and saving"""
    print("Testing progress tracking...")
    
    # Create a temporary directory for testing
    with tempfile.TemporaryDirectory() as tmpdir:
        # Override the PROGRESS_FILE path
        original_results_dir = run_mass_test.RESULTS_DIR
        original_progress_file = run_mass_test.PROGRESS_FILE
        
        run_mass_test.RESULTS_DIR = Path(tmpdir) / "results"
        run_mass_test.PROGRESS_FILE = run_mass_test.RESULTS_DIR / "progress.json"
        
        try:
            # Test loading when file doesn't exist
            progress = run_mass_test.load_progress()
            assert progress["completed"] == []
            assert progress["failed"] == []
            assert progress["in_progress"] is None
            print("✅ Load empty progress works")
            
            # Test saving progress
            progress["completed"] = ["EURUSD_2024"]
            progress["failed"] = ["GBPUSD_2023"]
            run_mass_test.save_progress(progress)
            assert run_mass_test.PROGRESS_FILE.exists()
            print("✅ Save progress works")
            
            # Test loading saved progress
            loaded = run_mass_test.load_progress()
            assert "EURUSD_2024" in loaded["completed"]
            assert "GBPUSD_2023" in loaded["failed"]
            assert loaded["last_update"] is not None
            print("✅ Load saved progress works")
            
            # Test mark_completed
            run_mass_test.mark_completed(loaded, "AUDJPY_2023", {"status": "success"})
            assert "AUDJPY_2023" in loaded["completed"]
            assert "AUDJPY_2023" in loaded["results"]
            print("✅ mark_completed works")
            
            # Test mark_failed
            run_mass_test.mark_failed(loaded, "USDJPY_2024", "Test error")
            assert "USDJPY_2024" in loaded["failed"]
            assert "USDJPY_2024" in loaded["errors"]
            print("✅ mark_failed works")
            
            # Test mark_in_progress
            run_mass_test.mark_in_progress(loaded, "EURJPY_2025")
            assert loaded["in_progress"] == "EURJPY_2025"
            assert loaded["started_at"] is not None
            print("✅ mark_in_progress works")
            
        finally:
            # Restore original paths
            run_mass_test.RESULTS_DIR = original_results_dir
            run_mass_test.PROGRESS_FILE = original_progress_file
    
    print("✅ All progress tracking tests passed!\n")


def test_get_available_datasets():
    """Test dataset discovery"""
    print("Testing dataset discovery...")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create mock parquet directory
        parquet_dir = Path(tmpdir) / "data" / "parquet"
        parquet_dir.mkdir(parents=True)
        
        # Create mock files
        (parquet_dir / "EURUSD_2024.parquet").touch()
        (parquet_dir / "GBPUSD_2023.parquet").touch()
        (parquet_dir / "INVALID.txt").touch()  # Should be ignored
        
        # Override PARQUET_DIR
        original_parquet_dir = run_mass_test.PARQUET_DIR
        run_mass_test.PARQUET_DIR = parquet_dir
        
        try:
            datasets = run_mass_test.get_available_datasets()
            
            assert len(datasets) == 2
            assert datasets[0]["pair"] == "EURUSD"
            assert datasets[0]["year"] == "2024"
            assert datasets[0]["key"] == "EURUSD_2024"
            assert datasets[1]["pair"] == "GBPUSD"
            assert datasets[1]["year"] == "2023"
            print("✅ Dataset discovery works correctly")
            
        finally:
            run_mass_test.PARQUET_DIR = original_parquet_dir
    
    print("✅ All dataset discovery tests passed!\n")


def test_subprocess_command():
    """Test that subprocess.run is called with correct arguments"""
    print("Testing subprocess command construction...")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create mock files
        parquet_dir = Path(tmpdir) / "data" / "parquet"
        parquet_dir.mkdir(parents=True)
        parquet_file = parquet_dir / "EURUSD_2024.parquet"
        parquet_file.touch()
        
        dataset = {
            "pair": "EURUSD",
            "year": "2024",
            "file": parquet_file,
            "name": "EURUSD_2024",
            "key": "EURUSD_2024"
        }
        
        # Mock subprocess.run to capture the command
        with patch('subprocess.run') as mock_run:
            # Mock the subprocess result
            mock_run.return_value = MagicMock(returncode=0)
            
            # Call the function
            result = run_mass_test.run_single_backtest(dataset)
            
            # Verify subprocess.run was called
            assert mock_run.called
            call_args = mock_run.call_args[0][0]  # Get the command list
            
            # Check command structure
            assert call_args[0] == sys.executable  # Python executable
            assert call_args[1] == "main.py"
            assert "--strategy-discovery" in call_args
            assert "--batch-mode" in call_args
            assert "--parquet" in call_args
            assert str(parquet_file) in call_args
            
            print(f"✅ Subprocess command correct: {' '.join(call_args)}")
    
    print("✅ All subprocess tests passed!\n")


def test_cli_arguments():
    """Test CLI argument parsing"""
    print("Testing CLI arguments...")
    
    # Test --list argument
    with patch('sys.argv', ['run_mass_test.py', '--list']):
        with patch('run_mass_test.get_available_datasets', return_value=[]):
            with patch('builtins.print') as mock_print:
                try:
                    run_mass_test.main()
                except SystemExit:
                    pass
                # Verify it printed something
                assert mock_print.called
                print("✅ --list argument works")
    
    # Test --status argument
    with patch('sys.argv', ['run_mass_test.py', '--status']):
        with patch('run_mass_test.show_status') as mock_status:
            try:
                run_mass_test.main()
            except SystemExit:
                pass
            assert mock_status.called
            print("✅ --status argument works")
    
    # Test --fresh argument
    with patch('sys.argv', ['run_mass_test.py', '--fresh']):
        with patch('run_mass_test.run_mass_test') as mock_run:
            with patch('run_mass_test.get_available_datasets', return_value=[]):
                try:
                    run_mass_test.main()
                except SystemExit:
                    pass
                assert mock_run.called
                call_kwargs = mock_run.call_args[1]
                assert call_kwargs['fresh'] is True
                print("✅ --fresh argument works")
    
    # Test --retry-failed argument
    with patch('sys.argv', ['run_mass_test.py', '--retry-failed']):
        with patch('run_mass_test.run_mass_test') as mock_run:
            with patch('run_mass_test.get_available_datasets', return_value=[]):
                try:
                    run_mass_test.main()
                except SystemExit:
                    pass
                assert mock_run.called
                call_kwargs = mock_run.call_args[1]
                assert call_kwargs['retry_failed'] is True
                print("✅ --retry-failed argument works")
    
    print("✅ All CLI argument tests passed!\n")


def main():
    """Run all tests"""
    print("\n" + "="*70)
    print("🧪 TESTING run_mass_test.py")
    print("="*70 + "\n")
    
    try:
        test_load_save_progress()
        test_get_available_datasets()
        test_subprocess_command()
        test_cli_arguments()
        
        print("\n" + "="*70)
        print("✅ ALL TESTS PASSED!")
        print("="*70 + "\n")
        return 0
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}\n")
        import traceback
        traceback.print_exc()
        return 1
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}\n")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
