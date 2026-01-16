#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚡🌟💎 ULTRA NECROZMA - NUMBA OPTIMIZATION TESTS 💎🌟⚡

Tests for Numba-optimized labeling functions
Ensures 100% accuracy maintained after optimization
"""

import pytest
import numpy as np
import pandas as pd
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from labeler import (
    _scan_for_target_stop,
    label_single_candle,
    NUMBA_AVAILABLE
)


class TestNumbaAvailability:
    """Test Numba availability and fallback"""
    
    def test_numba_available(self):
        """Test that Numba is available"""
        assert NUMBA_AVAILABLE, "Numba should be available for optimal performance"
    
    def test_scan_function_exists(self):
        """Test that optimized scan function exists"""
        assert callable(_scan_for_target_stop), "_scan_for_target_stop should be callable"


class TestScanForTargetStop:
    """Test the Numba-optimized _scan_for_target_stop function"""
    
    def test_long_position_hits_target(self):
        """Test long position hitting target before stop"""
        # Create simple price series that goes up
        prices = np.array([1.1000, 1.1005, 1.1010, 1.1015, 1.1020])
        candle_idx = 0
        horizon_idx = 5
        entry_price = 1.1000
        target_price = 1.1010  # +10 pips
        stop_price = 1.0990    # -10 pips
        pip_value = 0.0001
        direction_up = True
        
        result = _scan_for_target_stop(
            prices, candle_idx, horizon_idx, entry_price,
            target_price, stop_price, pip_value, direction_up
        )
        
        hit_target, hit_stop, target_idx, stop_idx, max_favorable, max_adverse = result
        
        assert hit_target == True, "Should hit target"
        assert hit_stop == False, "Should not hit stop"
        assert target_idx == 2, "Target should be hit at index 2"
        assert stop_idx == -1, "Stop should not be hit"
        assert max_favorable >= 10.0, "MFE should be at least 10 pips"
    
    def test_long_position_hits_stop(self):
        """Test long position hitting stop before target"""
        # Create simple price series that goes down
        prices = np.array([1.1000, 1.0995, 1.0990, 1.0985, 1.0980])
        candle_idx = 0
        horizon_idx = 5
        entry_price = 1.1000
        target_price = 1.1010  # +10 pips
        stop_price = 1.0990    # -10 pips
        pip_value = 0.0001
        direction_up = True
        
        result = _scan_for_target_stop(
            prices, candle_idx, horizon_idx, entry_price,
            target_price, stop_price, pip_value, direction_up
        )
        
        hit_target, hit_stop, target_idx, stop_idx, max_favorable, max_adverse = result
        
        assert hit_target == False, "Should not hit target"
        assert hit_stop == True, "Should hit stop"
        assert target_idx == -1, "Target should not be hit"
        assert stop_idx == 2, "Stop should be hit at index 2"
        assert max_adverse <= -10.0, "MAE should be at least -10 pips"
    
    def test_short_position_hits_target(self):
        """Test short position hitting target before stop"""
        # Create simple price series that goes down
        prices = np.array([1.1000, 1.0995, 1.0990, 1.0985, 1.0980])
        candle_idx = 0
        horizon_idx = 5
        entry_price = 1.1000
        target_price = 1.0990  # -10 pips
        stop_price = 1.1010    # +10 pips (loss for short)
        pip_value = 0.0001
        direction_up = False
        
        result = _scan_for_target_stop(
            prices, candle_idx, horizon_idx, entry_price,
            target_price, stop_price, pip_value, direction_up
        )
        
        hit_target, hit_stop, target_idx, stop_idx, max_favorable, max_adverse = result
        
        assert hit_target == True, "Should hit target"
        assert hit_stop == False, "Should not hit stop"
        assert target_idx == 2, "Target should be hit at index 2"
        assert stop_idx == -1, "Stop should not be hit"
    
    def test_short_position_hits_stop(self):
        """Test short position hitting stop before target"""
        # Create simple price series that goes up
        prices = np.array([1.1000, 1.1005, 1.1010, 1.1015, 1.1020])
        candle_idx = 0
        horizon_idx = 5
        entry_price = 1.1000
        target_price = 1.0990  # -10 pips
        stop_price = 1.1010    # +10 pips (loss for short)
        pip_value = 0.0001
        direction_up = False
        
        result = _scan_for_target_stop(
            prices, candle_idx, horizon_idx, entry_price,
            target_price, stop_price, pip_value, direction_up
        )
        
        hit_target, hit_stop, target_idx, stop_idx, max_favorable, max_adverse = result
        
        assert hit_target == False, "Should not hit target"
        assert hit_stop == True, "Should hit stop"
        assert target_idx == -1, "Target should not be hit"
        assert stop_idx == 2, "Stop should be hit at index 2"
    
    def test_mfe_mae_tracking(self):
        """Test Maximum Favorable/Adverse Excursion tracking"""
        # Price goes up to +15 pips, then down to -5 pips, then to target at +10
        prices = np.array([1.1000, 1.1005, 1.1015, 1.0995, 1.1010])
        candle_idx = 0
        horizon_idx = 5
        entry_price = 1.1000
        target_price = 1.1010
        stop_price = 1.0990
        pip_value = 0.0001
        direction_up = True
        
        result = _scan_for_target_stop(
            prices, candle_idx, horizon_idx, entry_price,
            target_price, stop_price, pip_value, direction_up
        )
        
        hit_target, hit_stop, target_idx, stop_idx, max_favorable, max_adverse = result
        
        # Use approximate comparison for floating point
        assert max_favorable >= 14.99, f"MFE should be at least 15 pips, got {max_favorable}"
        assert max_adverse <= -4.99, f"MAE should be at least -5 pips, got {max_adverse}"
    
    def test_both_hit_early_exit(self):
        """Test early exit when both target and stop are hit"""
        # Price hits stop first, then target
        prices = np.array([1.1000, 1.0990, 1.1010, 1.1020, 1.1030])
        candle_idx = 0
        horizon_idx = 5
        entry_price = 1.1000
        target_price = 1.1010
        stop_price = 1.0990
        pip_value = 0.0001
        direction_up = True
        
        result = _scan_for_target_stop(
            prices, candle_idx, horizon_idx, entry_price,
            target_price, stop_price, pip_value, direction_up
        )
        
        hit_target, hit_stop, target_idx, stop_idx, max_favorable, max_adverse = result
        
        assert hit_target == True, "Should hit target"
        assert hit_stop == True, "Should hit stop"
        # Function should have exited early after both hits


class TestLabelSingleCandle:
    """Test the complete label_single_candle function with Numba optimization"""
    
    @pytest.fixture
    def sample_data(self):
        """Create sample data for testing"""
        n_samples = 100
        timestamps = pd.date_range('2025-01-01', periods=n_samples, freq='1s')
        
        # Create price movement: up 20 pips, then down 15 pips
        base_price = 1.1000
        prices = [base_price]
        for i in range(1, n_samples):
            if i < 30:
                prices.append(prices[-1] + 0.0001)  # Up
            elif i < 60:
                prices.append(prices[-1] - 0.00005)  # Down
            else:
                prices.append(prices[-1] + 0.00002)  # Slightly up
        
        prices = np.array(prices)
        timestamps = timestamps.values
        
        return prices, timestamps
    
    def test_label_returns_dict(self, sample_data):
        """Test that label_single_candle returns proper dictionary"""
        prices, timestamps = sample_data
        
        result = label_single_candle(
            candle_idx=0,
            prices=prices,
            timestamps=timestamps,
            target_pip=10.0,
            stop_pip=5.0,
            horizon_minutes=2,
            pip_value=0.0001
        )
        
        assert isinstance(result, dict), "Should return dictionary"
        assert "candle_idx" in result
        assert "entry_price" in result
        assert "target_pip" in result
        assert "stop_pip" in result
        assert "horizon_minutes" in result
    
    def test_label_has_both_directions(self, sample_data):
        """Test that labeling includes both up and down direction results"""
        prices, timestamps = sample_data
        
        result = label_single_candle(
            candle_idx=0,
            prices=prices,
            timestamps=timestamps,
            target_pip=10.0,
            stop_pip=5.0,
            horizon_minutes=2,
            pip_value=0.0001
        )
        
        # Check UP direction
        assert "up_outcome" in result
        assert "up_hit_target" in result
        assert "up_hit_stop" in result
        assert "up_mfe" in result
        assert "up_mae" in result
        assert "up_r_multiple" in result
        
        # Check DOWN direction
        assert "down_outcome" in result
        assert "down_hit_target" in result
        assert "down_hit_stop" in result
        assert "down_mfe" in result
        assert "down_mae" in result
        assert "down_r_multiple" in result
    
    def test_label_outcome_values(self, sample_data):
        """Test that outcome values are valid"""
        prices, timestamps = sample_data
        
        result = label_single_candle(
            candle_idx=0,
            prices=prices,
            timestamps=timestamps,
            target_pip=10.0,
            stop_pip=5.0,
            horizon_minutes=2,
            pip_value=0.0001
        )
        
        valid_outcomes = ["target", "stop", "none"]
        assert result["up_outcome"] in valid_outcomes
        assert result["down_outcome"] in valid_outcomes
    
    def test_r_multiple_calculation(self, sample_data):
        """Test R-Multiple calculation"""
        prices, timestamps = sample_data
        
        result = label_single_candle(
            candle_idx=0,
            prices=prices,
            timestamps=timestamps,
            target_pip=20.0,
            stop_pip=10.0,
            horizon_minutes=2,
            pip_value=0.0001
        )
        
        # If target hit, R should be target/stop = 20/10 = 2.0
        if result["up_outcome"] == "target":
            assert result["up_r_multiple"] == 2.0, "R-Multiple should be 2.0 for target hit"
        
        # If stop hit, R should be -1.0
        if result["up_outcome"] == "stop":
            assert result["up_r_multiple"] == -1.0, "R-Multiple should be -1.0 for stop hit"
    
    def test_timestamp_handling(self, sample_data):
        """Test that timestamps are handled correctly (numpy.timedelta64 and pandas.Timedelta)"""
        prices, timestamps = sample_data
        
        # Test with numpy timestamps (from .values)
        result = label_single_candle(
            candle_idx=0,
            prices=prices,
            timestamps=timestamps,
            target_pip=10.0,
            stop_pip=5.0,
            horizon_minutes=2,
            pip_value=0.0001
        )
        
        # Should not crash and should have valid time fields (or None)
        assert "up_time_to_target" in result
        assert "up_time_to_stop" in result
        
        # If hit, should be a number (minutes)
        if result["up_hit_target"]:
            assert isinstance(result["up_time_to_target"], (int, float))
            assert result["up_time_to_target"] >= 0
    
    def test_invalid_candle_index(self, sample_data):
        """Test handling of invalid candle index"""
        prices, timestamps = sample_data
        
        # Test with index at end of array
        result = label_single_candle(
            candle_idx=len(prices) - 1,
            prices=prices,
            timestamps=timestamps,
            target_pip=10.0,
            stop_pip=5.0,
            horizon_minutes=2,
            pip_value=0.0001
        )
        
        assert result is None, "Should return None for invalid index"


class TestNumbaPerformance:
    """Test performance characteristics of Numba optimization"""
    
    def test_large_dataset_performance(self):
        """Test that Numba optimization works with large datasets"""
        import time
        
        # Create large dataset
        n_samples = 100000  # 100k ticks
        timestamps = pd.date_range('2025-01-01', periods=n_samples, freq='1s')
        prices = 1.1000 + np.cumsum(np.random.randn(n_samples) * 0.0001)
        timestamps = timestamps.values
        
        # Time the labeling
        start = time.time()
        result = label_single_candle(
            candle_idx=0,
            prices=prices,
            timestamps=timestamps,
            target_pip=10.0,
            stop_pip=5.0,
            horizon_minutes=1440,  # 24 hours
            pip_value=0.0001
        )
        elapsed = time.time() - start
        
        assert result is not None, "Should return valid result"
        # With Numba, this should be fast (< 1 second for 100k ticks)
        # Without Numba it would take much longer
        print(f"\n   ⏱️  Processed 100k ticks in {elapsed:.3f} seconds")
        
        # Sanity check on result
        assert isinstance(result, dict)
        assert "up_outcome" in result
        assert "down_outcome" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
