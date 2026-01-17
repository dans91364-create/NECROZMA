#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for batch progress display with error handling
"""

import sys
import time
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from backtest_batch import BatchProgressTracker


def test_progress_with_errors():
    """Test the BatchProgressTracker with simulated errors"""
    print("\n" + "="*80)
    print("Testing BatchProgressTracker with Error Handling")
    print("="*80)
    
    # Simulate a batch with 15 strategies
    batch_number = 2
    total_batches = 24
    total_strategies = 15
    
    print(f"\nSimulating Batch {batch_number}/{total_batches} with {total_strategies} strategies...")
    print("(Simulating errors on strategies 5 and 12)")
    print()
    
    # Create progress tracker
    progress = BatchProgressTracker(batch_number, total_batches, total_strategies, update_interval=3)
    
    # Simulate processing strategies with some errors
    for i in range(1, total_strategies + 1):
        strategy_name = f"Strategy_Test_{i}"
        
        # Update progress
        progress.update(strategy_name)
        
        # Simulate errors on specific strategies
        if i == 5 or i == 12:
            # Clear the line and print error (use class constant)
            print(f"\r{' ' * BatchProgressTracker.PROGRESS_LINE_LENGTH}\r", end="")
            print(f"   ⚠️  Strategy '{strategy_name}' failed: Simulated error for testing")
            # Restore progress line
            progress.reprint_current()
        
        # Simulate processing time
        time.sleep(0.1)
    
    # Finish progress
    progress.finish()
    
    print("\n✅ Error handling test complete!")
    print("="*80)


if __name__ == "__main__":
    test_progress_with_errors()
    print("\n✅ All tests passed!")
