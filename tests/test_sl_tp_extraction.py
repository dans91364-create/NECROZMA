#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚡🌟💎 NECROZMA DASHBOARD - SL/TP EXTRACTION TESTS 💎🌟⚡

Tests for extracting SL/TP parameters from strategy names
"""

import pytest
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dashboard.utils.data_loader import extract_sl_tp_from_name


# ═══════════════════════════════════════════════════════════════
# 🧪 TEST CASES
# ═══════════════════════════════════════════════════════════════

class TestSLTPExtraction:
    """Test SL/TP extraction from various strategy name formats"""
    
    def test_uppercase_format(self):
        """Test TrendFollower_L5_T0.5_SL10_TP50 format"""
        sl, tp = extract_sl_tp_from_name('TrendFollower_L5_T0.5_SL10_TP50')
        assert sl == 10
        assert tp == 50
        
    def test_uppercase_format_variations(self):
        """Test various uppercase format variations"""
        test_cases = [
            ('TrendFollower_L5_T0.5_SL15_TP30', 15, 30),
            ('TrendFollower_L5_T0.5_SL10_TP40', 10, 40),
            ('TrendFollower_L5_T0.5_SL20_TP50', 20, 50),
            ('MeanReversion_SL10_TP20', 10, 20),
        ]
        
        for name, expected_sl, expected_tp in test_cases:
            sl, tp = extract_sl_tp_from_name(name)
            assert sl == expected_sl, f"Failed for {name}: expected SL={expected_sl}, got {sl}"
            assert tp == expected_tp, f"Failed for {name}: expected TP={expected_tp}, got {tp}"
    
    def test_lowercase_underscore_format(self):
        """Test strategy_sl_20_tp_40 format"""
        sl, tp = extract_sl_tp_from_name('strategy_sl_20_tp_40')
        assert sl == 20
        assert tp == 40
        
    def test_lowercase_variations(self):
        """Test lowercase format variations"""
        test_cases = [
            ('momentum_sl_15_tp_30', 15, 30),
            ('scalper_sl_5_tp_10', 5, 10),
        ]
        
        for name, expected_sl, expected_tp in test_cases:
            sl, tp = extract_sl_tp_from_name(name)
            assert sl == expected_sl, f"Failed for {name}: expected SL={expected_sl}, got {sl}"
            assert tp == expected_tp, f"Failed for {name}: expected TP={expected_tp}, got {tp}"
    
    def test_no_separator_format(self):
        """Test sl10tp50 format (no separators)"""
        sl, tp = extract_sl_tp_from_name('BreakoutStrategy_sl10tp50')
        assert sl == 10
        assert tp == 50
    
    def test_case_insensitive(self):
        """Test case-insensitive matching"""
        test_cases = [
            ('Strategy_SL10_TP50', 10, 50),
            ('Strategy_sl10_tp50', 10, 50),
            ('Strategy_Sl10_Tp50', 10, 50),
            ('STRATEGY_SL10_TP50', 10, 50),
        ]
        
        for name, expected_sl, expected_tp in test_cases:
            sl, tp = extract_sl_tp_from_name(name)
            assert sl == expected_sl, f"Failed for {name}: expected SL={expected_sl}, got {sl}"
            assert tp == expected_tp, f"Failed for {name}: expected TP={expected_tp}, got {tp}"
    
    def test_sl_tp_at_start(self):
        """Test format with SL/TP at the start"""
        sl, tp = extract_sl_tp_from_name('SL5_TP25_Strategy')
        assert sl == 5
        assert tp == 25
    
    def test_edge_cases(self):
        """Test edge cases that should return None"""
        test_cases = [
            ('NoSLTP_Strategy', None, None),
            ('OnlySL10_NoTP', None, None),
            ('', None, None),
            (None, None, None),
            ('JustAName', None, None),
            ('TP50_NoSL', None, None),  # TP without SL
        ]
        
        for name, expected_sl, expected_tp in test_cases:
            sl, tp = extract_sl_tp_from_name(name)
            assert sl == expected_sl, f"Failed for {name}: expected SL={expected_sl}, got {sl}"
            assert tp == expected_tp, f"Failed for {name}: expected TP={expected_tp}, got {tp}"
    
    def test_multi_digit_values(self):
        """Test extraction of multi-digit SL/TP values"""
        test_cases = [
            ('Strategy_SL100_TP250', 100, 250),
            ('Strategy_SL999_TP1000', 999, 1000),
        ]
        
        for name, expected_sl, expected_tp in test_cases:
            sl, tp = extract_sl_tp_from_name(name)
            assert sl == expected_sl, f"Failed for {name}: expected SL={expected_sl}, got {sl}"
            assert tp == expected_tp, f"Failed for {name}: expected TP={expected_tp}, got {tp}"
    
    def test_returns_integers(self):
        """Test that function returns integers, not floats"""
        sl, tp = extract_sl_tp_from_name('TrendFollower_SL10_TP50')
        assert isinstance(sl, int)
        assert isinstance(tp, int)


# ═══════════════════════════════════════════════════════════════
# 🧪 INTEGRATION TESTS
# ═══════════════════════════════════════════════════════════════

class TestSLTPIntegration:
    """Test integration with metrics module"""
    
    def test_metrics_import(self):
        """Test that metrics module can import the function"""
        from dashboard.components.metrics import calculate_sl_tp_matrix
        assert callable(calculate_sl_tp_matrix)
    
    def test_statistics_function(self):
        """Test extract_sl_tp_statistics function"""
        import pandas as pd
        from dashboard.components.metrics import extract_sl_tp_statistics
        
        # Create test data
        test_data = {
            'strategy_name': [
                'TrendFollower_L5_T0.5_SL10_TP50',
                'TrendFollower_L5_T0.5_SL15_TP30',
                'NoSLTP_Strategy',
            ],
            'total_return': [0.33, 0.28, 0.25],
            'sharpe_ratio': [2.2, 1.9, 1.5],
            'win_rate': [0.65, 0.60, 0.55],
            'n_trades': [100, 95, 90]
        }
        
        df = pd.DataFrame(test_data)
        stats = extract_sl_tp_statistics(df)
        
        assert stats['total_strategies'] == 3
        assert stats['strategies_with_sl_tp'] == 2
        assert abs(stats['coverage_pct'] - 66.67) < 0.1
        assert 10 in stats['unique_sl_values']
        assert 15 in stats['unique_sl_values']
        assert 30 in stats['unique_tp_values']
        assert 50 in stats['unique_tp_values']


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
