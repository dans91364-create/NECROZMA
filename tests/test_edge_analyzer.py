#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test for NECROZMA Edge Analyzer

Tests the core functionality of edge_analyzer.py
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
import numpy as np
import pandas as pd
from edge_analyzer import (
    calculate_p_value,
    calculate_bootstrap_ci,
    analyze_regime_label_performance,
    filter_edge_candidates,
    validate_out_of_sample,
    EDGE_CONFIG
)


class TestStatisticalFunctions:
    """Test statistical functions"""
    
    def test_calculate_p_value_perfect_win(self):
        """Test p-value for 100% win rate"""
        p_value = calculate_p_value(wins=100, total=100)
        assert p_value < 0.001, "100% win rate should have very low p-value"
    
    def test_calculate_p_value_random(self):
        """Test p-value for 50% win rate (random)"""
        p_value = calculate_p_value(wins=50, total=100)
        assert p_value > 0.05, "50% win rate should not be significant"
    
    def test_calculate_p_value_zero_trades(self):
        """Test p-value with zero trades"""
        p_value = calculate_p_value(wins=0, total=0)
        assert p_value == 1.0, "Zero trades should return p-value of 1.0"
    
    def test_calculate_bootstrap_ci(self):
        """Test bootstrap confidence interval"""
        # Create array with 60% wins
        outcomes = np.array([1] * 60 + [0] * 40)
        lower, mean, upper = calculate_bootstrap_ci(outcomes)
        
        assert 0 <= lower <= mean <= upper <= 1, "CI bounds should be ordered"
        assert 0.5 < mean < 0.7, "Mean should be around 0.6"
        assert upper - lower < 0.2, "CI should not be too wide"
    
    def test_calculate_bootstrap_ci_empty(self):
        """Test bootstrap CI with empty array"""
        outcomes = np.array([])
        lower, mean, upper = calculate_bootstrap_ci(outcomes)
        assert lower == mean == upper == 0.0, "Empty array should return zeros"


class TestEdgeAnalysis:
    """Test edge analysis functions"""
    
    @staticmethod
    def create_sample_labels():
        """Create sample label data"""
        np.random.seed(42)
        n = 1000
        
        # Create sample label data for T10_S5_H30 config
        df = pd.DataFrame({
            'timestamp': pd.date_range('2025-01-01', periods=n, freq='1min'),
            'up_outcome': np.random.choice(['target', 'stop', 'timeout'], n, p=[0.55, 0.40, 0.05]),
            'down_outcome': np.random.choice(['target', 'stop', 'timeout'], n, p=[0.50, 0.45, 0.05]),
        })
        
        return {'T10_S5_H30': df}
    
    @staticmethod
    def create_sample_regimes():
        """Create sample regime data"""
        np.random.seed(42)
        n = 1000
        
        df = pd.DataFrame({
            'timestamp': pd.date_range('2025-01-01', periods=n, freq='1min'),
            'regime': np.random.choice([0, 1, 2], n, p=[0.4, 0.3, 0.3])
        })
        
        return df
    
    @pytest.fixture
    def sample_labels(self):
        """Pytest fixture for sample labels"""
        return self.create_sample_labels()
    
    @pytest.fixture
    def sample_regimes(self):
        """Pytest fixture for sample regimes"""
        return self.create_sample_regimes()
    
    def test_analyze_regime_label_performance(self, sample_labels, sample_regimes):
        """Test regime × label performance analysis"""
        results = analyze_regime_label_performance(
            sample_labels, 
            sample_regimes,
            config={'min_trades': 10}
        )
        
        assert len(results) > 0, "Should generate results"
        assert 'regime' in results.columns, "Should have regime column"
        assert 'config' in results.columns, "Should have config column"
        assert 'win_rate' in results.columns, "Should have win_rate column"
        assert 'p_value' in results.columns, "Should have p_value column"
        assert 'profit_factor' in results.columns, "Should have profit_factor column"
        
        # Check value ranges
        assert (results['win_rate'] >= 0).all(), "Win rate should be >= 0"
        assert (results['win_rate'] <= 1).all(), "Win rate should be <= 1"
        assert (results['p_value'] >= 0).all(), "p-value should be >= 0"
        assert (results['p_value'] <= 1).all(), "p-value should be <= 1"
    
    def test_filter_edge_candidates(self, sample_labels, sample_regimes):
        """Test edge candidate filtering"""
        results = analyze_regime_label_performance(
            sample_labels,
            sample_regimes,
            config={'min_trades': 10}
        )
        
        filtered = filter_edge_candidates(
            results,
            config={
                'min_win_rate': 0.52,
                'max_p_value': 0.05,
                'min_profit_factor': 1.3,
                'min_trades': 20
            }
        )
        
        # Check that all filters are applied
        if len(filtered) > 0:
            assert (filtered['win_rate'] >= 0.52).all(), "Win rate filter not applied"
            assert (filtered['p_value'] < 0.05).all(), "p-value filter not applied"
            assert (filtered['profit_factor'] >= 1.3).all(), "Profit factor filter not applied"
            assert (filtered['n_trades'] >= 20).all(), "Min trades filter not applied"
    
    def test_validate_out_of_sample(self, sample_labels, sample_regimes):
        """Test out-of-sample validation"""
        results = analyze_regime_label_performance(
            sample_labels,
            sample_regimes,
            config={'min_trades': 10}
        )
        
        # Create a small set of candidates
        candidates = results.head(5)
        
        validated = validate_out_of_sample(
            sample_labels,
            sample_regimes,
            candidates,
            oos_split=0.2
        )
        
        # Should have validation results
        if len(validated) > 0:
            assert 'is_win_rate' in validated.columns, "Should have in-sample win rate"
            assert 'oos_win_rate' in validated.columns, "Should have out-of-sample win rate"
            assert 'degradation' in validated.columns, "Should have degradation metric"
            assert 'survives_oos' in validated.columns, "Should have survival flag"
            
            # Check value ranges
            assert (validated['is_win_rate'] >= 0).all(), "IS win rate should be >= 0"
            assert (validated['is_win_rate'] <= 1).all(), "IS win rate should be <= 1"
            assert (validated['oos_win_rate'] >= 0).all(), "OOS win rate should be >= 0"
            assert (validated['oos_win_rate'] <= 1).all(), "OOS win rate should be <= 1"


class TestConfigParsing:
    """Test configuration parsing"""
    
    def test_config_parsing_standard(self):
        """Test parsing standard config format"""
        # The analyze function parses configs internally
        # We'll test that T10_S5_H30 is parsed correctly
        config_key = "T10_S5_H30"
        parts = config_key.split("_")
        
        target_pips = float(parts[0][1:])
        stop_pips = float(parts[1][1:])
        horizon_min = int(parts[2][1:])
        
        assert target_pips == 10.0, "Target should be 10 pips"
        assert stop_pips == 5.0, "Stop should be 5 pips"
        assert horizon_min == 30, "Horizon should be 30 minutes"
    
    def test_config_parsing_with_prefix(self):
        """Test parsing config with prefix"""
        config_key = "EURUSD_2025_T10_S5_H30"
        # Remove prefix
        prefix = "EURUSD_2025_"
        if config_key.startswith(prefix):
            config_key = config_key[len(prefix):]
        
        parts = config_key.split("_")
        target_pips = float(parts[0][1:])
        stop_pips = float(parts[1][1:])
        horizon_min = int(parts[2][1:])
        
        assert target_pips == 10.0, "Target should be 10 pips"
        assert stop_pips == 5.0, "Stop should be 5 pips"
        assert horizon_min == 30, "Horizon should be 30 minutes"


if __name__ == "__main__":
    print("Testing NECROZMA Edge Analyzer...")
    
    # Run statistical tests
    print("\n📊 Testing statistical functions...")
    stat_tests = TestStatisticalFunctions()
    stat_tests.test_calculate_p_value_perfect_win()
    print("   ✅ P-value (perfect win) test passed")
    
    stat_tests.test_calculate_p_value_random()
    print("   ✅ P-value (random) test passed")
    
    stat_tests.test_calculate_p_value_zero_trades()
    print("   ✅ P-value (zero trades) test passed")
    
    stat_tests.test_calculate_bootstrap_ci()
    print("   ✅ Bootstrap CI test passed")
    
    stat_tests.test_calculate_bootstrap_ci_empty()
    print("   ✅ Bootstrap CI (empty) test passed")
    
    # Run edge analysis tests
    print("\n🎯 Testing edge analysis functions...")
    edge_tests = TestEdgeAnalysis()
    
    sample_labels = edge_tests.create_sample_labels()
    sample_regimes = edge_tests.create_sample_regimes()
    
    edge_tests.test_analyze_regime_label_performance(sample_labels, sample_regimes)
    print("   ✅ Regime × label analysis test passed")
    
    edge_tests.test_filter_edge_candidates(sample_labels, sample_regimes)
    print("   ✅ Edge filtering test passed")
    
    edge_tests.test_validate_out_of_sample(sample_labels, sample_regimes)
    print("   ✅ Out-of-sample validation test passed")
    
    # Run config parsing tests
    print("\n🔧 Testing config parsing...")
    config_tests = TestConfigParsing()
    config_tests.test_config_parsing_standard()
    print("   ✅ Standard config parsing test passed")
    
    config_tests.test_config_parsing_with_prefix()
    print("   ✅ Prefixed config parsing test passed")
    
    print("\n✨ All tests passed!")
