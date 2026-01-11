#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚡🌟💎 ULTRA NECROZMA - TIMESTAMP VALIDATION TESTS 💎🌟⚡

Tests for timestamp validation fixes
"""

import pytest
import numpy as np
import pandas as pd
import sys
from pathlib import Path
from io import StringIO

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from data_loader import (
    ensure_datetime_column,
    crystal_info,
    resample_to_ohlc,
    load_crystal
)
from test_mode import TestModeSampler


class TestTimestampValidation:
    """Test timestamp validation utilities"""
    
    def test_ensure_datetime_column_with_string(self):
        """Test conversion of string timestamps to datetime"""
        df = pd.DataFrame({
            'timestamp': ['2025-01-01 00:00:00', '2025-01-01 01:00:00', '2025-01-01 02:00:00'],
            'value': [1, 2, 3]
        })
        
        result = ensure_datetime_column(df, 'timestamp')
        
        assert pd.api.types.is_datetime64_any_dtype(result['timestamp'])
        assert result['timestamp'].dt.tz is not None  # Should be UTC-aware
    
    def test_ensure_datetime_column_with_datetime(self):
        """Test that datetime columns remain unchanged"""
        df = pd.DataFrame({
            'timestamp': pd.date_range('2025-01-01', periods=3, freq='h'),
            'value': [1, 2, 3]
        })
        
        result = ensure_datetime_column(df, 'timestamp')
        
        assert pd.api.types.is_datetime64_any_dtype(result['timestamp'])
    
    def test_ensure_datetime_column_missing_column(self):
        """Test handling of missing timestamp column"""
        df = pd.DataFrame({
            'value': [1, 2, 3]
        })
        
        result = ensure_datetime_column(df, 'timestamp')
        
        assert 'timestamp' not in result.columns
        assert result.equals(df)
    
    def test_ensure_datetime_column_utc_conversion(self):
        """Test UTC timezone handling"""
        # Test with naive datetime
        df = pd.DataFrame({
            'timestamp': pd.date_range('2025-01-01', periods=3, freq='h'),
            'value': [1, 2, 3]
        })
        
        result = ensure_datetime_column(df, 'timestamp', utc=True)
        
        assert result['timestamp'].dt.tz is not None
        assert str(result['timestamp'].dt.tz) == 'UTC'


class TestCrystalInfoWithStringTimestamps:
    """Test crystal_info function with string timestamps"""
    
    def test_crystal_info_with_string_timestamps(self, capsys):
        """Test that crystal_info handles string timestamps correctly"""
        df = pd.DataFrame({
            'timestamp': ['2025-01-01 00:00:00', '2025-01-01 01:00:00', '2025-01-01 02:00:00'],
            'mid_price': [1.1000, 1.1001, 1.1002],
            'spread_pips': [1.0, 1.0, 1.0]
        })
        
        # Should not raise TypeError
        crystal_info(df)
        
        captured = capsys.readouterr()
        assert 'Duration:' in captured.out
        assert 'Unable to calculate' not in captured.out
    
    def test_crystal_info_with_datetime_timestamps(self, capsys):
        """Test that crystal_info works with proper datetime timestamps"""
        df = pd.DataFrame({
            'timestamp': pd.date_range('2025-01-01', periods=3, freq='h'),
            'mid_price': [1.1000, 1.1001, 1.1002],
            'spread_pips': [1.0, 1.0, 1.0]
        })
        
        # Should not raise TypeError
        crystal_info(df)
        
        captured = capsys.readouterr()
        assert 'Duration:' in captured.out
        assert 'Unable to calculate' not in captured.out


class TestResampleWithStringTimestamps:
    """Test resample_to_ohlc function with string timestamps"""
    
    def test_resample_with_string_timestamps(self, capsys):
        """Test that resample_to_ohlc handles string timestamps correctly"""
        df = pd.DataFrame({
            'timestamp': pd.date_range('2025-01-01', periods=100, freq='1min').astype(str),
            'mid_price': np.random.randn(100) * 0.0001 + 1.1000,
            'spread_pips': [1.0] * 100
        })
        
        # Should not raise TypeError
        result = resample_to_ohlc(df, interval_minutes=5)
        
        assert len(result) > 0
        assert 'open' in result.columns
        assert 'high' in result.columns
        assert 'low' in result.columns
        assert 'close' in result.columns
    
    def test_resample_with_datetime_timestamps(self, capsys):
        """Test that resample_to_ohlc works with proper datetime timestamps"""
        df = pd.DataFrame({
            'timestamp': pd.date_range('2025-01-01', periods=100, freq='1min'),
            'mid_price': np.random.randn(100) * 0.0001 + 1.1000,
            'spread_pips': [1.0] * 100
        })
        
        # Should not raise TypeError
        result = resample_to_ohlc(df, interval_minutes=5)
        
        assert len(result) > 0
        assert 'open' in result.columns


class TestTimezoneHandling:
    """Test timezone handling in test_mode.py"""
    
    def test_filter_holiday_weeks_with_tz_aware(self):
        """Test holiday filtering with timezone-aware timestamps"""
        sampler = TestModeSampler(seed=42)
        
        # Create test weeks with timezone-aware timestamps
        weeks = {
            202501: (pd.Timestamp('2025-01-01', tz='UTC'), pd.Timestamp('2025-01-07', tz='UTC')),
            202502: (pd.Timestamp('2025-01-08', tz='UTC'), pd.Timestamp('2025-01-14', tz='UTC')),
        }
        
        # Should not raise TypeError
        result = sampler._filter_holiday_weeks(weeks, 2025, avoid_holidays=True)
        
        # Week containing Jan 1 should be filtered out
        assert 202501 not in result
        assert 202502 in result
    
    def test_filter_holiday_weeks_with_tz_naive(self):
        """Test holiday filtering with timezone-naive timestamps"""
        sampler = TestModeSampler(seed=42)
        
        # Create test weeks with timezone-naive timestamps
        weeks = {
            202501: (pd.Timestamp('2025-01-01'), pd.Timestamp('2025-01-07')),
            202502: (pd.Timestamp('2025-01-08'), pd.Timestamp('2025-01-14')),
        }
        
        # Should not raise TypeError
        result = sampler._filter_holiday_weeks(weeks, 2025, avoid_holidays=True)
        
        # Week containing Jan 1 should be filtered out
        assert 202501 not in result
        assert 202502 in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
