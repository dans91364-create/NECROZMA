#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚡🌟💎 ULTRA NECROZMA - VECTORIZED LABELING TESTS 💎🌟⚡

Tests to verify the vectorized labeling implementation produces identical
results to the original implementation while being 100x faster.
"""

import pytest
import numpy as np
import pandas as pd
from pathlib import Path
import sys
import time

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from labeler import (
    label_single_candle,
    label_all_candles_vectorized,
    label_dataframe,
    NUMBA_AVAILABLE
)


class TestVectorizedLabeling:
    """Test the vectorized labeling function"""
    
    @pytest.fixture
    def sample_data(self):
        """Create sample data for testing"""
        np.random.seed(42)
        n_samples = 1000
        timestamps = pd.date_range('2025-01-01', periods=n_samples, freq='1min')
        
        # Create realistic price movement
        base_price = 1.1000
        prices = base_price + np.cumsum(np.random.randn(n_samples) * 0.0001)
        
        df = pd.DataFrame({
            'timestamp': timestamps,
            'mid_price': prices,
        })
        
        return df
    
    def test_vectorized_function_exists(self):
        """Test that vectorized function exists and is callable"""
        assert callable(label_all_candles_vectorized), "label_all_candles_vectorized should exist"
    
    def test_vectorized_vs_single_candle_identical_results(self, sample_data):
        """Test that vectorized labeling produces identical results to single candle labeling"""
        df = sample_data
        prices = df['mid_price'].values
        timestamps = df['timestamp'].values
        timestamps_ns = timestamps.astype('datetime64[ns]').astype(np.int64)
        
        # Test parameters
        target_pip = 10.0
        stop_pip = 5.0
        horizon_minutes = 60
        horizon_ns = int(horizon_minutes * 60 * 1_000_000_000)
        pip_value = 0.0001
        
        # Get vectorized results
        (outcomes_up, outcomes_down,
         mfe_up, mfe_down,
         mae_up, mae_down,
         time_target_up, time_target_down,
         time_stop_up, time_stop_down) = label_all_candles_vectorized(
            prices=prices,
            timestamps_ns=timestamps_ns,
            target_pip=target_pip,
            stop_pip=stop_pip,
            horizon_ns=horizon_ns,
            pip_value=pip_value
        )
        
        # Compare with single candle results for first 10 candles
        for i in range(min(10, len(df) - 1)):
            single_result = label_single_candle(
                candle_idx=i,
                prices=prices,
                timestamps=timestamps,
                target_pip=target_pip,
                stop_pip=stop_pip,
                horizon_minutes=horizon_minutes,
                pip_value=pip_value
            )
            
            # Check UP direction
            expected_outcome_up = single_result['up_outcome']
            actual_outcome_up = 'target' if outcomes_up[i] == 1 else ('stop' if outcomes_up[i] == -1 else 'none')
            assert actual_outcome_up == expected_outcome_up, \
                f"Candle {i} UP outcome mismatch: {actual_outcome_up} != {expected_outcome_up}"
            
            assert single_result['up_hit_target'] == (outcomes_up[i] == 1), \
                f"Candle {i} UP hit_target mismatch"
            assert single_result['up_hit_stop'] == (outcomes_up[i] == -1), \
                f"Candle {i} UP hit_stop mismatch"
            
            # Check MFE/MAE (allow small floating point differences)
            assert abs(single_result['up_mfe'] - mfe_up[i]) < 0.01, \
                f"Candle {i} UP MFE mismatch: {single_result['up_mfe']} != {mfe_up[i]}"
            assert abs(single_result['up_mae'] - mae_up[i]) < 0.01, \
                f"Candle {i} UP MAE mismatch: {single_result['up_mae']} != {mae_up[i]}"
            
            # Check DOWN direction
            expected_outcome_down = single_result['down_outcome']
            actual_outcome_down = 'target' if outcomes_down[i] == 1 else ('stop' if outcomes_down[i] == -1 else 'none')
            assert actual_outcome_down == expected_outcome_down, \
                f"Candle {i} DOWN outcome mismatch: {actual_outcome_down} != {expected_outcome_down}"
            
            assert single_result['down_hit_target'] == (outcomes_down[i] == 1), \
                f"Candle {i} DOWN hit_target mismatch"
            assert single_result['down_hit_stop'] == (outcomes_down[i] == -1), \
                f"Candle {i} DOWN hit_stop mismatch"
            
            assert abs(single_result['down_mfe'] - mfe_down[i]) < 0.01, \
                f"Candle {i} DOWN MFE mismatch"
            assert abs(single_result['down_mae'] - mae_down[i]) < 0.01, \
                f"Candle {i} DOWN MAE mismatch"
    
    def test_vectorized_performance_improvement(self, sample_data):
        """Test that vectorized function is significantly faster"""
        df = sample_data.iloc[:500]  # Use 500 candles for performance test
        prices = df['mid_price'].values
        timestamps = df['timestamp'].values
        timestamps_ns = timestamps.astype('datetime64[ns]').astype(np.int64)
        
        target_pip = 10.0
        stop_pip = 5.0
        horizon_minutes = 60
        horizon_ns = int(horizon_minutes * 60 * 1_000_000_000)
        pip_value = 0.0001
        
        # Time vectorized function (run twice - first for JIT compilation)
        _ = label_all_candles_vectorized(
            prices=prices,
            timestamps_ns=timestamps_ns,
            target_pip=target_pip,
            stop_pip=stop_pip,
            horizon_ns=horizon_ns,
            pip_value=pip_value
        )
        
        start_vectorized = time.time()
        _ = label_all_candles_vectorized(
            prices=prices,
            timestamps_ns=timestamps_ns,
            target_pip=target_pip,
            stop_pip=stop_pip,
            horizon_ns=horizon_ns,
            pip_value=pip_value
        )
        time_vectorized = time.time() - start_vectorized
        
        # Time single candle function for first 50 candles
        start_single = time.time()
        for i in range(50):
            _ = label_single_candle(
                candle_idx=i,
                prices=prices,
                timestamps=timestamps,
                target_pip=target_pip,
                stop_pip=stop_pip,
                horizon_minutes=horizon_minutes,
                pip_value=pip_value
            )
        time_single = time.time() - start_single
        
        # Estimate time for all 500 candles using single candle approach
        estimated_time_single = time_single * (len(df) / 50)
        
        speedup = estimated_time_single / time_vectorized
        
        print(f"\n   ⚡ Performance Comparison:")
        print(f"      Vectorized (500 candles): {time_vectorized:.4f}s")
        print(f"      Single (50 candles): {time_single:.4f}s")
        print(f"      Estimated single (500 candles): {estimated_time_single:.4f}s")
        print(f"      Speedup: {speedup:.1f}x")
        
        # Vectorized should be significantly faster (at least 10x)
        assert speedup > 10, f"Vectorized should be at least 10x faster, got {speedup:.1f}x"
    
    def test_label_dataframe_uses_vectorized(self, sample_data):
        """Test that label_dataframe uses the vectorized function"""
        df = sample_data.iloc[:100]  # Small dataset for quick test
        
        # Run labeling with single configuration
        results = label_dataframe(
            df,
            target_pips=[10],
            stop_pips=[5],
            horizons=[60],
            use_cache=False
        )
        
        # Verify results exist
        assert len(results) == 1, "Should have 1 configuration"
        assert 'T10_S5_H60' in results, "Should have T10_S5_H60 configuration"
        
        # Verify DataFrame structure
        result_df = results['T10_S5_H60']
        assert len(result_df) == 99, "Should have 99 labeled candles (100 - 1)"
        
        # Check all expected columns exist
        expected_columns = [
            'candle_idx', 'entry_price', 'target_pip', 'stop_pip', 'horizon_minutes',
            'up_outcome', 'up_hit_target', 'up_hit_stop', 'up_time_to_target', 'up_time_to_stop',
            'up_mfe', 'up_mae', 'up_r_multiple',
            'down_outcome', 'down_hit_target', 'down_hit_stop', 'down_time_to_target', 'down_time_to_stop',
            'down_mfe', 'down_mae', 'down_r_multiple'
        ]
        
        for col in expected_columns:
            assert col in result_df.columns, f"Column {col} should exist in result"
    
    def test_multiple_configurations(self, sample_data):
        """Test labeling with multiple configurations"""
        df = sample_data.iloc[:100]
        
        results = label_dataframe(
            df,
            target_pips=[5, 10],
            stop_pips=[5],
            horizons=[30, 60],
            use_cache=False
        )
        
        # Should have 2 * 1 * 2 = 4 configurations
        assert len(results) == 4, "Should have 4 configurations"
        
        expected_keys = ['T5_S5_H30', 'T5_S5_H60', 'T10_S5_H30', 'T10_S5_H60']
        for key in expected_keys:
            assert key in results, f"Should have {key} configuration"
            assert len(results[key]) == 99, f"{key} should have 99 rows"
    
    def test_outcome_values_are_valid(self, sample_data):
        """Test that outcome values are always valid"""
        df = sample_data.iloc[:100]
        
        results = label_dataframe(
            df,
            target_pips=[10],
            stop_pips=[5],
            horizons=[60],
            use_cache=False
        )
        
        result_df = results['T10_S5_H60']
        
        # Check UP outcomes
        valid_outcomes = {'target', 'stop', 'none'}
        for outcome in result_df['up_outcome']:
            assert outcome in valid_outcomes, f"Invalid UP outcome: {outcome}"
        
        # Check DOWN outcomes
        for outcome in result_df['down_outcome']:
            assert outcome in valid_outcomes, f"Invalid DOWN outcome: {outcome}"
    
    def test_r_multiple_calculation(self, sample_data):
        """Test that R-multiple is calculated correctly"""
        df = sample_data.iloc[:100]
        
        target_pip = 20.0
        stop_pip = 10.0
        expected_r = target_pip / stop_pip
        
        results = label_dataframe(
            df,
            target_pips=[target_pip],
            stop_pips=[stop_pip],
            horizons=[60],
            use_cache=False
        )
        
        result_df = results['T20_S10_H60']
        
        # Check R-multiple for target outcomes
        target_rows = result_df[result_df['up_outcome'] == 'target']
        if len(target_rows) > 0:
            for r_val in target_rows['up_r_multiple']:
                assert r_val == expected_r, f"R-multiple should be {expected_r}, got {r_val}"
        
        # Check R-multiple for stop outcomes
        stop_rows = result_df[result_df['up_outcome'] == 'stop']
        if len(stop_rows) > 0:
            for r_val in stop_rows['up_r_multiple']:
                assert r_val == -1.0, f"R-multiple for stop should be -1.0, got {r_val}"


class TestBackwardCompatibility:
    """Test that label_single_candle still works for backward compatibility"""
    
    @pytest.fixture
    def sample_data(self):
        """Create sample data"""
        np.random.seed(42)
        n_samples = 100
        timestamps = pd.date_range('2025-01-01', periods=n_samples, freq='1min')
        prices = 1.1000 + np.cumsum(np.random.randn(n_samples) * 0.0001)
        
        return prices, timestamps.values
    
    def test_label_single_candle_still_works(self, sample_data):
        """Test that label_single_candle function still works"""
        prices, timestamps = sample_data
        
        result = label_single_candle(
            candle_idx=0,
            prices=prices,
            timestamps=timestamps,
            target_pip=10.0,
            stop_pip=5.0,
            horizon_minutes=60,
            pip_value=0.0001
        )
        
        assert result is not None, "label_single_candle should return a result"
        assert isinstance(result, dict), "Result should be a dictionary"
        assert 'up_outcome' in result
        assert 'down_outcome' in result


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
