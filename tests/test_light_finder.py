#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests for LightFinder with both BacktestResults objects and DataFrame input
"""

import pytest
import numpy as np
import pandas as pd

from backtester import BacktestResults
from light_finder import LightFinder


@pytest.fixture
def mock_backtest_results():
    """Create mock BacktestResults objects for testing"""
    results = []
    for i in range(10):
        result = BacktestResults(
            strategy_name=f"Strategy_{i+1}",
            n_trades=np.random.randint(30, 100),
            win_rate=np.random.uniform(0.4, 0.7),
            profit_factor=np.random.uniform(1.0, 2.5),
            total_return=np.random.uniform(0.1, 0.5),
            sharpe_ratio=np.random.uniform(0.5, 2.5),
            sortino_ratio=np.random.uniform(0.5, 3.0),
            calmar_ratio=np.random.uniform(0, 3.0),
            max_drawdown=np.random.uniform(0.05, 0.3),
            avg_win=np.random.uniform(0.001, 0.005),
            avg_loss=np.random.uniform(-0.005, -0.001),
            largest_win=np.random.uniform(0.005, 0.01),
            largest_loss=np.random.uniform(-0.01, -0.005),
            expectancy=np.random.uniform(-0.001, 0.003),
            recovery_factor=np.random.uniform(0.5, 3.0),
            ulcer_index=np.random.uniform(1.0, 5.0),
            trades=pd.DataFrame(),
            equity_curve=pd.Series([10000, 11000]),
        )
        results.append(result)
    return results


@pytest.fixture
def mock_dataframe():
    """Create mock DataFrame for testing (batch processing format)"""
    np.random.seed(42)
    data = []
    for i in range(10):
        for lot_size in [0.01, 0.1, 1.0]:
            data.append({
                'strategy_name': f"Strategy_{i+1}",
                'lot_size': lot_size,
                'sharpe_ratio': np.random.uniform(0.5, 2.5),
                'sortino_ratio': np.random.uniform(0.5, 3.0),
                'calmar_ratio': np.random.uniform(0, 3.0),
                'total_return': np.random.uniform(0.1, 0.5),
                'max_drawdown': np.random.uniform(0.05, 0.3),
                'win_rate': np.random.uniform(0.4, 0.7),
                'n_trades': np.random.randint(30, 100),
                'profit_factor': np.random.uniform(1.0, 2.5),
                'avg_win': np.random.uniform(0.001, 0.005),
                'avg_loss': np.random.uniform(-0.005, -0.001),
                'expectancy': np.random.uniform(-0.001, 0.003),
                'gross_pnl': np.random.uniform(100, 1000),
                'net_pnl': np.random.uniform(90, 950),
                'total_commission': np.random.uniform(5, 50),
            })
    return pd.DataFrame(data)


@pytest.fixture
def mock_dataframe_without_ulcer():
    """Create mock DataFrame without ulcer_index column"""
    np.random.seed(42)
    data = []
    for i in range(10):
        data.append({
            'strategy_name': f"Strategy_{i+1}",
            'lot_size': 0.1,
            'sharpe_ratio': np.random.uniform(0.5, 2.5),
            'sortino_ratio': np.random.uniform(0.5, 3.0),
            'calmar_ratio': np.random.uniform(0, 3.0),
            'total_return': np.random.uniform(0.1, 0.5),
            'max_drawdown': np.random.uniform(0.05, 0.3),
            'win_rate': np.random.uniform(0.4, 0.7),
            'n_trades': np.random.randint(30, 100),
            'profit_factor': np.random.uniform(1.0, 2.5),
            'avg_win': np.random.uniform(0.001, 0.005),
            'avg_loss': np.random.uniform(-0.005, -0.001),
            'expectancy': np.random.uniform(-0.001, 0.003),
            'gross_pnl': np.random.uniform(100, 1000),
            'net_pnl': np.random.uniform(90, 950),
            'total_commission': np.random.uniform(5, 50),
        })
    return pd.DataFrame(data)


class TestLightFinderBackwardCompatibility:
    """Test that LightFinder still works with BacktestResults objects"""
    
    def test_rank_strategies_with_backtest_results(self, mock_backtest_results):
        """Test ranking with BacktestResults objects (legacy format)"""
        finder = LightFinder()
        ranked = finder.rank_strategies(mock_backtest_results, top_n=5)
        
        # Verify output
        assert isinstance(ranked, pd.DataFrame)
        assert len(ranked) <= 5
        assert 'rank' in ranked.columns
        assert 'composite_score' in ranked.columns
        assert 'strategy_name' in ranked.columns
        assert 'total_return' in ranked.columns
        assert 'sharpe_ratio' in ranked.columns
        
        # Verify ranking is in descending order by composite_score
        assert ranked['composite_score'].is_monotonic_decreasing
        
        # Verify ranks are sequential
        assert list(ranked['rank']) == list(range(1, len(ranked) + 1))
    
    def test_calculate_scores_from_objects(self, mock_backtest_results):
        """Test _calculate_scores_from_objects method directly"""
        finder = LightFinder()
        scores_df = finder._calculate_scores_from_objects(mock_backtest_results)
        
        # Verify output structure
        assert isinstance(scores_df, pd.DataFrame)
        assert len(scores_df) == len(mock_backtest_results)
        
        required_cols = [
            'strategy_name', 'return_score', 'risk_score',
            'consistency_score', 'robustness_score', 'n_trades',
            'total_return', 'sharpe_ratio', 'max_drawdown', 'win_rate'
        ]
        for col in required_cols:
            assert col in scores_df.columns
        
        # Verify all scores are numeric
        assert scores_df['return_score'].dtype in [np.float64, float]
        assert scores_df['risk_score'].dtype in [np.float64, float]
        assert scores_df['consistency_score'].dtype in [np.float64, float]
        assert scores_df['robustness_score'].dtype in [np.float64, float]


class TestLightFinderDataFrameSupport:
    """Test that LightFinder works with DataFrame input (batch processing format)"""
    
    def test_rank_strategies_with_dataframe(self, mock_dataframe):
        """Test ranking with DataFrame input (batch format)"""
        finder = LightFinder()
        ranked = finder.rank_strategies(mock_dataframe, top_n=5)
        
        # Verify output
        assert isinstance(ranked, pd.DataFrame)
        assert len(ranked) <= 5
        assert 'rank' in ranked.columns
        assert 'composite_score' in ranked.columns
        assert 'strategy_name' in ranked.columns
        assert 'total_return' in ranked.columns
        assert 'sharpe_ratio' in ranked.columns
        
        # Verify ranking is in descending order by composite_score
        assert ranked['composite_score'].is_monotonic_decreasing
        
        # Verify ranks are sequential
        assert list(ranked['rank']) == list(range(1, len(ranked) + 1))
    
    def test_calculate_scores_from_df(self, mock_dataframe):
        """Test _calculate_scores_from_df method directly"""
        finder = LightFinder()
        scores_df = finder._calculate_scores_from_df(mock_dataframe)
        
        # Verify output structure
        assert isinstance(scores_df, pd.DataFrame)
        
        # Should have one row per unique strategy (handles multiple lot_sizes)
        unique_strategies = mock_dataframe['strategy_name'].nunique()
        assert len(scores_df) == unique_strategies
        
        required_cols = [
            'strategy_name', 'return_score', 'risk_score',
            'consistency_score', 'robustness_score', 'n_trades',
            'total_return', 'sharpe_ratio', 'max_drawdown', 'win_rate'
        ]
        for col in required_cols:
            assert col in scores_df.columns
        
        # Verify all scores are numeric
        assert scores_df['return_score'].dtype in [np.float64, float]
        assert scores_df['risk_score'].dtype in [np.float64, float]
        assert scores_df['consistency_score'].dtype in [np.float64, float]
        assert scores_df['robustness_score'].dtype in [np.float64, float]
    
    def test_dataframe_without_ulcer_index(self, mock_dataframe_without_ulcer):
        """Test that DataFrame without ulcer_index column uses default value"""
        finder = LightFinder()
        scores_df = finder._calculate_scores_from_df(mock_dataframe_without_ulcer)
        
        # Verify it doesn't crash and produces valid output
        assert isinstance(scores_df, pd.DataFrame)
        assert len(scores_df) > 0
        
        # Verify robustness_score is calculated (using default ulcer_index)
        assert 'robustness_score' in scores_df.columns
        assert scores_df['robustness_score'].notna().all()
    
    def test_dataframe_with_multiple_lot_sizes(self, mock_dataframe):
        """Test that DataFrame with multiple lot_sizes per strategy selects best one"""
        finder = LightFinder()
        scores_df = finder._calculate_scores_from_df(mock_dataframe)
        
        # Verify one row per strategy
        unique_strategies = mock_dataframe['strategy_name'].nunique()
        assert len(scores_df) == unique_strategies
        
        # Verify all strategy names are unique
        assert scores_df['strategy_name'].nunique() == len(scores_df)
    
    def test_calculate_scores_detects_dataframe(self, mock_dataframe):
        """Test that _calculate_scores correctly detects DataFrame input"""
        finder = LightFinder()
        scores_df = finder._calculate_scores(mock_dataframe)
        
        # Should call _calculate_scores_from_df and return valid results
        assert isinstance(scores_df, pd.DataFrame)
        assert len(scores_df) > 0
        assert 'strategy_name' in scores_df.columns
    
    def test_calculate_scores_detects_list(self, mock_backtest_results):
        """Test that _calculate_scores correctly detects List[BacktestResults] input"""
        finder = LightFinder()
        scores_df = finder._calculate_scores(mock_backtest_results)
        
        # Should call _calculate_scores_from_objects and return valid results
        assert isinstance(scores_df, pd.DataFrame)
        assert len(scores_df) == len(mock_backtest_results)
        assert 'strategy_name' in scores_df.columns


class TestLightFinderConsistency:
    """Test that both input formats produce consistent results"""
    
    def test_same_data_different_formats_similar_ranking(self):
        """Test that same data in different formats produces similar rankings"""
        np.random.seed(123)
        
        # Create matching data in both formats
        strategies_data = []
        for i in range(5):
            strategies_data.append({
                'strategy_name': f"Strategy_{i+1}",
                'n_trades': 50,
                'win_rate': 0.6,
                'profit_factor': 1.5,
                'total_return': 0.3 + i * 0.05,  # Increasing returns
                'sharpe_ratio': 1.5,
                'sortino_ratio': 2.0,
                'max_drawdown': 0.15,
                'ulcer_index': 3.0,
            })
        
        # Create BacktestResults objects
        results_objects = []
        for data in strategies_data:
            result = BacktestResults(
                strategy_name=data['strategy_name'],
                n_trades=data['n_trades'],
                win_rate=data['win_rate'],
                profit_factor=data['profit_factor'],
                total_return=data['total_return'],
                sharpe_ratio=data['sharpe_ratio'],
                sortino_ratio=data['sortino_ratio'],
                calmar_ratio=2.0,
                max_drawdown=data['max_drawdown'],
                avg_win=0.003,
                avg_loss=-0.002,
                largest_win=0.01,
                largest_loss=-0.008,
                expectancy=0.001,
                recovery_factor=2.0,
                ulcer_index=data['ulcer_index'],
                trades=pd.DataFrame(),
                equity_curve=pd.Series([10000, 13000]),
            )
            results_objects.append(result)
        
        # Create DataFrame
        df_data = []
        for data in strategies_data:
            df_data.append({
                'strategy_name': data['strategy_name'],
                'lot_size': 0.1,
                'n_trades': data['n_trades'],
                'win_rate': data['win_rate'],
                'profit_factor': data['profit_factor'],
                'total_return': data['total_return'],
                'sharpe_ratio': data['sharpe_ratio'],
                'sortino_ratio': data['sortino_ratio'],
                'calmar_ratio': 2.0,
                'max_drawdown': data['max_drawdown'],
                'avg_win': 0.003,
                'avg_loss': -0.002,
                'expectancy': 0.001,
                'gross_pnl': 300,
                'net_pnl': 295,
                'total_commission': 5,
            })
        results_df = pd.DataFrame(df_data)
        
        # Rank both
        finder = LightFinder()
        ranked_objects = finder.rank_strategies(results_objects, top_n=5)
        ranked_df = finder.rank_strategies(results_df, top_n=5)
        
        # Verify same number of results
        assert len(ranked_objects) == len(ranked_df)
        
        # Verify same top strategy (highest return in this case)
        assert ranked_objects.iloc[0]['strategy_name'] == ranked_df.iloc[0]['strategy_name']
        
        # Verify all strategy names are present in both
        assert set(ranked_objects['strategy_name']) == set(ranked_df['strategy_name'])
    
    def test_get_top_strategies_by_metric_with_dataframe(self):
        """Test get_top_strategies_by_metric with DataFrame input"""
        np.random.seed(123)
        
        # Create DataFrame with varying sharpe ratios
        df = pd.DataFrame({
            'strategy_name': ['Strategy_A', 'Strategy_B', 'Strategy_C', 'Strategy_D'],
            'lot_size': [0.1, 0.1, 0.1, 0.1],
            'total_return': [0.3, 0.2, 0.4, 0.35],
            'sharpe_ratio': [1.5, 2.0, 1.2, 1.8],  # Strategy_B has highest Sharpe
            'sortino_ratio': [2.0, 2.5, 1.8, 2.2],
            'max_drawdown': [0.15, 0.20, 0.12, 0.18],
            'win_rate': [0.6, 0.55, 0.65, 0.58],
            'n_trades': [50, 45, 55, 52],
            'profit_factor': [1.5, 1.3, 1.7, 1.6],
            'avg_win': [0.003, 0.002, 0.004, 0.0035],
            'avg_loss': [-0.002, -0.003, -0.002, -0.0025],
            'expectancy': [0.001, 0.0008, 0.0012, 0.0011],
            'gross_pnl': [300, 200, 400, 350],
            'net_pnl': [295, 195, 395, 345],
            'total_commission': [5, 5, 5, 5],
        })
        
        finder = LightFinder()
        
        # Get top 2 by sharpe_ratio
        top_sharpe = finder.get_top_strategies_by_metric(df, metric='sharpe_ratio', top_n=2)
        
        # Verify output
        assert isinstance(top_sharpe, pd.DataFrame)
        assert len(top_sharpe) == 2
        assert top_sharpe.iloc[0]['strategy_name'] == 'Strategy_B'  # Highest Sharpe
        assert top_sharpe.iloc[1]['strategy_name'] == 'Strategy_D'  # Second highest
        
        # Get top 2 by total_return
        top_return = finder.get_top_strategies_by_metric(df, metric='total_return', top_n=2)
        
        # Verify output
        assert isinstance(top_return, pd.DataFrame)
        assert len(top_return) == 2
        assert top_return.iloc[0]['strategy_name'] == 'Strategy_C'  # Highest return
        assert top_return.iloc[1]['strategy_name'] == 'Strategy_D'  # Second highest
    
    def test_get_top_strategies_by_metric_with_objects(self):
        """Test get_top_strategies_by_metric with BacktestResults objects"""
        np.random.seed(123)
        
        # Create BacktestResults objects with varying sharpe ratios
        results = []
        for i, (name, sharpe) in enumerate([('A', 1.5), ('B', 2.0), ('C', 1.2), ('D', 1.8)]):
            result = BacktestResults(
                strategy_name=f'Strategy_{name}',
                n_trades=50, win_rate=0.6, profit_factor=1.5,
                total_return=0.3, sharpe_ratio=sharpe, sortino_ratio=2.0,
                calmar_ratio=1.2, max_drawdown=0.15, avg_win=0.003,
                avg_loss=-0.002, largest_win=0.01, largest_loss=-0.008,
                expectancy=0.001, recovery_factor=2.0, ulcer_index=3.0,
                trades=pd.DataFrame(), equity_curve=pd.Series([10000, 13000])
            )
            results.append(result)
        
        finder = LightFinder()
        
        # Get top 2 by sharpe_ratio
        top_sharpe = finder.get_top_strategies_by_metric(results, metric='sharpe_ratio', top_n=2)
        
        # Verify output
        assert isinstance(top_sharpe, list)
        assert len(top_sharpe) == 2
        assert top_sharpe[0].strategy_name == 'Strategy_B'  # Highest Sharpe
        assert top_sharpe[1].strategy_name == 'Strategy_D'  # Second highest


if __name__ == "__main__":
    # Run with: pytest tests/test_light_finder.py -v
    pytest.main([__file__, "-v"])
