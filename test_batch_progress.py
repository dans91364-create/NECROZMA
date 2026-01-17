#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for batch progress display
"""

import sys
import time
from pathlib import Path
import pandas as pd
import numpy as np

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from backtest_batch import BatchProgressTracker


def test_progress_tracker():
    """Test the BatchProgressTracker with simulated strategies"""
    print("\n" + "="*80)
    print("Testing BatchProgressTracker")
    print("="*80)
    
    # Simulate a batch with 20 strategies
    batch_number = 1
    total_batches = 24
    total_strategies = 20
    
    print(f"\nSimulating Batch {batch_number}/{total_batches} with {total_strategies} strategies...")
    print()
    
    # Create progress tracker
    progress = BatchProgressTracker(batch_number, total_batches, total_strategies, update_interval=5)
    
    # Simulate processing strategies
    strategy_names = [
        f"EMA_RSI_v{i}" for i in range(1, total_strategies + 1)
    ]
    
    for i, strategy_name in enumerate(strategy_names):
        # Update progress
        progress.update(strategy_name)
        
        # Simulate processing time (0.1 seconds per strategy)
        time.sleep(0.1)
    
    # Finish progress
    progress.finish()
    
    print("\n✅ Progress tracking test complete!")
    print("="*80)


def test_progress_without_batch_context():
    """Test progress tracker without batch context"""
    print("\n" + "="*80)
    print("Testing BatchProgressTracker WITHOUT batch context")
    print("="*80)
    
    total_strategies = 15
    
    print(f"\nSimulating {total_strategies} strategies without batch context...")
    print()
    
    # Create progress tracker without batch context
    progress = BatchProgressTracker(None, None, total_strategies, update_interval=3)
    
    # Simulate processing strategies
    for i in range(1, total_strategies + 1):
        strategy_name = f"Strategy_{i}"
        progress.update(strategy_name)
        time.sleep(0.08)
    
    # Finish progress
    progress.finish()
    
    print("\n✅ Progress tracking test complete!")
    print("="*80)


if __name__ == "__main__":
    # Test with batch context
    test_progress_tracker()
    
    # Test without batch context
    test_progress_without_batch_context()
    
    print("\n✅ All tests passed!")
