#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚡🌟💎 NECROZMA - LIGHT REPORT DATAFRAME COMPATIBILITY TESTS 💎🌟⚡

Test suite for light_report.py DataFrame compatibility
Tests both legacy Dict[str, BacktestResults] and new DataFrame formats
"""

import pytest
import pandas as pd
import numpy as np
from pathlib import Path
from backtester import BacktestResults
from light_report import LightReportGenerator


@pytest.fixture
def top_strategies_df():
    """Create sample top strategies DataFrame"""
    return pd.DataFrame({
        "rank": [1, 2, 3],
        "strategy_name": ["Strategy_A", "Strategy_B", "Strategy_C"],
        "composite_score": [0.85, 0.78, 0.72],
        "total_return": [0.35, 0.28, 0.25],
        "sharpe_ratio": [2.1, 1.8, 1.6],
        "win_rate": [0.62, 0.58, 0.55],
        "max_drawdown": [0.12, 0.15, 0.18],
    })


@pytest.fixture
def backtest_results_dict(top_strategies_df):
    """Create legacy Dict[str, BacktestResults] format"""
    results = {}
    for _, row in top_strategies_df.iterrows():
        result = BacktestResults(
            strategy_name=row["strategy_name"],
            n_trades=50,
            win_rate=row["win_rate"],
            profit_factor=2.0,
            total_return=row["total_return"],
            sharpe_ratio=row["sharpe_ratio"],
            sortino_ratio=row["sharpe_ratio"] * 1.2,
            calmar_ratio=2.5,
            max_drawdown=row["max_drawdown"],
            avg_win=0.003,
            avg_loss=-0.0015,
            largest_win=0.008,
            largest_loss=-0.005,
            expectancy=0.002,
            recovery_factor=2.0,
            ulcer_index=2.5,
            trades=pd.DataFrame(),
            equity_curve=pd.Series([10000, 13500]),
        )
        results[row["strategy_name"]] = result
    return results


@pytest.fixture
def backtest_results_dataframe():
    """Create new DataFrame format with batch processing results"""
    return pd.DataFrame({
        'strategy_name': ['Strategy_A', 'Strategy_A', 'Strategy_B', 'Strategy_B', 'Strategy_C', 'Strategy_C'],
        'lot_size': [0.01, 0.02, 0.01, 0.02, 0.01, 0.02],
        'sharpe_ratio': [2.1, 1.9, 1.8, 1.6, 1.6, 1.4],
        'sortino_ratio': [2.52, 2.28, 2.16, 1.92, 1.92, 1.68],
        'calmar_ratio': [2.5, 2.3, 2.4, 2.2, 2.3, 2.1],
        'total_return': [0.35, 0.33, 0.28, 0.26, 0.25, 0.23],
        'max_drawdown': [0.12, 0.13, 0.15, 0.16, 0.18, 0.19],
        'win_rate': [0.62, 0.60, 0.58, 0.56, 0.55, 0.53],
        'n_trades': [50, 52, 48, 50, 45, 47],
        'profit_factor': [2.0, 1.9, 1.95, 1.85, 1.9, 1.8],
        'avg_win': [0.003, 0.0029, 0.0028, 0.0027, 0.0026, 0.0025],
        'avg_loss': [-0.0015, -0.0016, -0.0015, -0.0016, -0.0015, -0.0016],
        'expectancy': [0.002, 0.0019, 0.0018, 0.0017, 0.0016, 0.0015],
        'gross_pnl': [3500, 3300, 2800, 2600, 2500, 2300],
        'net_pnl': [3450, 3250, 2750, 2550, 2450, 2250],
        'total_commission': [50, 50, 50, 50, 50, 50],
    })


class TestLightReportDataFrameCompatibility:
    """Test DataFrame compatibility for LightReportGenerator"""
    
    def test_generate_report_with_dict_legacy(self, top_strategies_df, backtest_results_dict):
        """Test that legacy Dict[str, BacktestResults] format still works"""
        generator = LightReportGenerator(output_dir=Path("/tmp/test_reports"))
        
        report = generator.generate_report(
            top_strategies=top_strategies_df,
            all_backtest_results=backtest_results_dict,
            total_strategies=100
        )
        
        # Verify report structure
        assert "title" in report
        assert "executive_summary" in report
        assert "top_strategies" in report
        assert len(report["top_strategies"]) == 3
        
        # Verify strategy details
        strategy_a = report["top_strategies"][0]
        assert strategy_a["name"] == "Strategy_A"
        assert strategy_a["rank"] == 1
        assert strategy_a["performance"]["sharpe_ratio"] == 2.1
        assert strategy_a["performance"]["total_return"] == 0.35
        assert strategy_a["trading_stats"]["total_trades"] == 50
        assert strategy_a["trading_stats"]["avg_win"] == 0.003
    
    def test_generate_report_with_dataframe(self, top_strategies_df, backtest_results_dataframe):
        """Test that new DataFrame format works"""
        generator = LightReportGenerator(output_dir=Path("/tmp/test_reports"))
        
        report = generator.generate_report(
            top_strategies=top_strategies_df,
            all_backtest_results=backtest_results_dataframe,
            total_strategies=100
        )
        
        # Verify report structure
        assert "title" in report
        assert "executive_summary" in report
        assert "top_strategies" in report
        assert len(report["top_strategies"]) == 3
        
        # Verify strategy details
        strategy_a = report["top_strategies"][0]
        assert strategy_a["name"] == "Strategy_A"
        assert strategy_a["rank"] == 1
        assert strategy_a["performance"]["sharpe_ratio"] == 2.1  # Best lot_size
        assert strategy_a["performance"]["total_return"] == 0.35  # Best lot_size
        assert strategy_a["trading_stats"]["total_trades"] == 50  # Best lot_size
    
    def test_df_to_results_lookup(self, backtest_results_dataframe):
        """Test _df_to_results_lookup helper method"""
        generator = LightReportGenerator(output_dir=Path("/tmp/test_reports"))
        
        lookup = generator._df_to_results_lookup(backtest_results_dataframe)
        
        # Verify lookup structure
        assert "Strategy_A" in lookup
        assert "Strategy_B" in lookup
        assert "Strategy_C" in lookup
        
        # Verify best lot_size is selected (highest sharpe_ratio)
        strategy_a = lookup["Strategy_A"]
        assert strategy_a["lot_size"] == 0.01  # lot_size with sharpe 2.1
        assert strategy_a["sharpe_ratio"] == 2.1
        
        strategy_b = lookup["Strategy_B"]
        assert strategy_b["lot_size"] == 0.01  # lot_size with sharpe 1.8
        assert strategy_b["sharpe_ratio"] == 1.8
    
    def test_create_strategy_details_with_dict(self):
        """Test _create_strategy_details with dict input"""
        generator = LightReportGenerator(output_dir=Path("/tmp/test_reports"))
        
        result_dict = {
            'total_return': 0.35,
            'sharpe_ratio': 2.1,
            'sortino_ratio': 2.52,
            'calmar_ratio': 2.5,
            'max_drawdown': 0.12,
            'profit_factor': 2.0,
            'win_rate': 0.62,
            'expectancy': 0.002,
            'n_trades': 50,
            'avg_win': 0.003,
            'avg_loss': -0.0015,
        }
        
        details = generator._create_strategy_details("Strategy_A", result_dict)
        
        assert details["name"] == "Strategy_A"
        assert details["performance"]["sharpe_ratio"] == 2.1
        assert details["performance"]["total_return"] == 0.35
        assert details["trading_stats"]["total_trades"] == 50
        assert details["trading_stats"]["avg_win"] == 0.003
        assert details["trading_stats"]["largest_win"] == 0  # Default for missing
        assert details["trading_stats"]["largest_loss"] == 0  # Default for missing
    
    def test_create_strategy_details_with_backtest_results(self):
        """Test _create_strategy_details with BacktestResults object"""
        generator = LightReportGenerator(output_dir=Path("/tmp/test_reports"))
        
        result = BacktestResults(
            strategy_name="Strategy_Test",
            n_trades=50,
            win_rate=0.62,
            profit_factor=2.0,
            total_return=0.35,
            sharpe_ratio=2.1,
            sortino_ratio=2.52,
            calmar_ratio=2.5,
            max_drawdown=0.12,
            avg_win=0.003,
            avg_loss=-0.0015,
            largest_win=0.008,
            largest_loss=-0.005,
            expectancy=0.002,
            recovery_factor=2.0,
            ulcer_index=2.5,
            trades=pd.DataFrame(),
            equity_curve=pd.Series([10000, 13500]),
        )
        
        details = generator._create_strategy_details("Strategy_Test", result)
        
        assert details["name"] == "Strategy_Test"
        assert details["performance"]["sharpe_ratio"] == 2.1
        assert details["performance"]["total_return"] == 0.35
        assert details["trading_stats"]["total_trades"] == 50
        assert details["trading_stats"]["avg_win"] == 0.003
        assert details["trading_stats"]["largest_win"] == 0.008
        assert details["trading_stats"]["largest_loss"] == -0.005
    
    def test_dict_and_dataframe_produce_same_output(self, top_strategies_df, 
                                                     backtest_results_dict, 
                                                     backtest_results_dataframe):
        """Test that Dict and DataFrame formats produce equivalent reports"""
        generator = LightReportGenerator(output_dir=Path("/tmp/test_reports"))
        
        # Generate report with dict
        report_dict = generator.generate_report(
            top_strategies=top_strategies_df,
            all_backtest_results=backtest_results_dict,
            total_strategies=100
        )
        
        # Generate report with dataframe
        report_df = generator.generate_report(
            top_strategies=top_strategies_df,
            all_backtest_results=backtest_results_dataframe,
            total_strategies=100
        )
        
        # Compare key metrics (should be very similar)
        assert len(report_dict["top_strategies"]) == len(report_df["top_strategies"])
        
        for i in range(len(report_dict["top_strategies"])):
            dict_strat = report_dict["top_strategies"][i]
            df_strat = report_df["top_strategies"][i]
            
            assert dict_strat["name"] == df_strat["name"]
            assert dict_strat["rank"] == df_strat["rank"]
            # Sharpe ratios should match (both use best lot_size)
            assert dict_strat["performance"]["sharpe_ratio"] == df_strat["performance"]["sharpe_ratio"]
    
    def test_dataframe_with_missing_columns(self, top_strategies_df):
        """Test DataFrame with minimal columns (missing largest_win, largest_loss)"""
        generator = LightReportGenerator(output_dir=Path("/tmp/test_reports"))
        
        # Create DataFrame with minimal columns
        minimal_df = pd.DataFrame({
            'strategy_name': ['Strategy_A'],
            'lot_size': [0.01],
            'sharpe_ratio': [2.1],
            'sortino_ratio': [2.52],
            'calmar_ratio': [2.5],
            'total_return': [0.35],
            'max_drawdown': [0.12],
            'win_rate': [0.62],
            'n_trades': [50],
            'profit_factor': [2.0],
            'avg_win': [0.003],
            'avg_loss': [-0.0015],
            'expectancy': [0.002],
        })
        
        report = generator.generate_report(
            top_strategies=top_strategies_df.head(1),
            all_backtest_results=minimal_df,
            total_strategies=100
        )
        
        # Verify defaults are used for missing columns
        strategy = report["top_strategies"][0]
        assert strategy["trading_stats"]["largest_win"] == 0
        assert strategy["trading_stats"]["largest_loss"] == 0
    
    def test_dataframe_with_nan_sharpe_ratios(self, top_strategies_df):
        """Test DataFrame with NaN sharpe ratios (should fallback to first row)"""
        generator = LightReportGenerator(output_dir=Path("/tmp/test_reports"))
        
        # Create DataFrame where all sharpe ratios are NaN
        nan_df = pd.DataFrame({
            'strategy_name': ['Strategy_A', 'Strategy_A'],
            'lot_size': [0.01, 0.02],
            'sharpe_ratio': [float('nan'), float('nan')],
            'sortino_ratio': [2.52, 2.28],
            'calmar_ratio': [2.5, 2.3],
            'total_return': [0.35, 0.33],
            'max_drawdown': [0.12, 0.13],
            'win_rate': [0.62, 0.60],
            'n_trades': [50, 52],
            'profit_factor': [2.0, 1.9],
            'avg_win': [0.003, 0.0029],
            'avg_loss': [-0.0015, -0.0016],
            'expectancy': [0.002, 0.0019],
        })
        
        # Should not raise an error, should use first row
        lookup = generator._df_to_results_lookup(nan_df)
        
        assert 'Strategy_A' in lookup
        # Should select first row when sharpe is NaN
        assert lookup['Strategy_A']['lot_size'] == 0.01
    
    def test_dataframe_with_mixed_nan_sharpe_ratios(self):
        """Test DataFrame with some NaN sharpe ratios (should select best valid value)"""
        generator = LightReportGenerator(output_dir=Path("/tmp/test_reports"))
        
        # Create DataFrame where some sharpe ratios are NaN
        mixed_nan_df = pd.DataFrame({
            'strategy_name': ['Strategy_B', 'Strategy_B', 'Strategy_B'],
            'lot_size': [0.01, 0.02, 0.05],
            'sharpe_ratio': [float('nan'), 2.5, 2.1],  # First is NaN, should select 0.02
            'sortino_ratio': [2.52, 2.28, 2.1],
            'calmar_ratio': [2.5, 2.3, 2.2],
            'total_return': [0.35, 0.33, 0.30],
            'max_drawdown': [0.12, 0.13, 0.14],
            'win_rate': [0.62, 0.60, 0.58],
            'n_trades': [50, 52, 54],
            'profit_factor': [2.0, 1.9, 1.8],
            'avg_win': [0.003, 0.0029, 0.0028],
            'avg_loss': [-0.0015, -0.0016, -0.0017],
            'expectancy': [0.002, 0.0019, 0.0018],
        })
        
        # Should select best valid sharpe_ratio (2.5 at lot_size 0.02)
        lookup = generator._df_to_results_lookup(mixed_nan_df)
        
        assert 'Strategy_B' in lookup
        # Should select lot_size with best valid sharpe_ratio
        assert lookup['Strategy_B']['lot_size'] == 0.02
        assert lookup['Strategy_B']['sharpe_ratio'] == 2.5


if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════════╗
║     📝 LIGHT REPORT DATAFRAME COMPATIBILITY TESTS 📝        ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    pytest.main([__file__, "-v"])
