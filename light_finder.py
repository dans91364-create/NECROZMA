#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚡🌟💎 NECROZMA - LIGHT FINDER 💎🌟⚡

Strategy Ranking System
"Finding the brightest strategies that burn through the sky"

Features:
- Multi-objective ranking (return, risk, consistency, robustness)
- Overfitting detection
- Strategy clustering
- Regime-specific rankings
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Union
from sklearn.preprocessing import MinMaxScaler

from config import RANKING_WEIGHTS, TOP_N_STRATEGIES, OVERFITTING_CONFIG
from backtester import BacktestResults


# ═══════════════════════════════════════════════════════════════
# 🔧 CONSTANTS
# ═══════════════════════════════════════════════════════════════

# Score normalization constants
MAX_SHARPE_FOR_NORMALIZATION = 3.0
MAX_ULCER_FOR_NORMALIZATION = 10.0
MAX_PROFIT_FACTOR_FOR_NORMALIZATION = 3.0
DEFAULT_SCORE = 0.5  # Score when no variation exists


# ═══════════════════════════════════════════════════════════════
# 🌟 LIGHT FINDER
# ═══════════════════════════════════════════════════════════════

class LightFinder:
    """
    Multi-objective strategy ranking system
    
    Usage:
        finder = LightFinder()
        rankings = finder.rank_strategies(backtest_results)
    """
    
    def __init__(self, weights: Dict = None):
        """
        Initialize light finder
        
        Args:
            weights: Objective weights (uses RANKING_WEIGHTS if None)
        """
        self.weights = weights or RANKING_WEIGHTS
        self.scaler = MinMaxScaler()
        
    def _calculate_scores(self, results) -> pd.DataFrame:
        """
        Calculate scores for all strategies
        
        Args:
            results: Either a List[BacktestResults] (legacy) or pd.DataFrame (batch format)
            
        Returns:
            DataFrame with calculated scores
        """
        # Handle DataFrame input (from batch processing)
        if isinstance(results, pd.DataFrame):
            return self._calculate_scores_from_df(results)
        
        # Handle list of BacktestResults objects (legacy)
        return self._calculate_scores_from_objects(results)
    
    def _calculate_scores_from_objects(self, results: List[BacktestResults]) -> pd.DataFrame:
        """Calculate scores from list of BacktestResults objects (legacy format)"""
        records = []
        
        for result in results:
            # Return score
            return_score = result.total_return
            
            # Risk score (inverse of metrics - lower is better)
            risk_score = 1.0 - result.max_drawdown if result.max_drawdown < 1 else 0.0
            
            # Consistency score
            consistency_score = (
                result.win_rate * 0.4 +
                (result.sharpe_ratio / MAX_SHARPE_FOR_NORMALIZATION) * 0.3 +
                (result.sortino_ratio / MAX_SHARPE_FOR_NORMALIZATION) * 0.3
            )
            consistency_score = min(consistency_score, 1.0)
            
            # Robustness score (stability)
            robustness_score = (
                (result.profit_factor / MAX_PROFIT_FACTOR_FOR_NORMALIZATION) * 0.5 +
                (1.0 - result.ulcer_index / MAX_ULCER_FOR_NORMALIZATION) * 0.5 
                if result.ulcer_index < MAX_ULCER_FOR_NORMALIZATION else 0.0
            )
            robustness_score = max(0.0, min(robustness_score, 1.0))
            
            records.append({
                "strategy_name": result.strategy_name,
                "return_score": return_score,
                "risk_score": risk_score,
                "consistency_score": consistency_score,
                "robustness_score": robustness_score,
                "n_trades": result.n_trades,
                "total_return": result.total_return,
                "sharpe_ratio": result.sharpe_ratio,
                "max_drawdown": result.max_drawdown,
                "win_rate": result.win_rate,
            })
        
        return pd.DataFrame(records)
    
    def _calculate_scores_from_df(self, results_df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate scores from DataFrame (batch processing format)
        
        Handles DataFrames with columns:
        - strategy_name, total_return, max_drawdown, win_rate, sharpe_ratio,
          sortino_ratio, profit_factor, n_trades
        - ulcer_index (optional - defaults to 5.0 if missing)
        - lot_size (optional - groups by strategy_name if present)
        
        Args:
            results_df: DataFrame with backtest results
            
        Returns:
            DataFrame with calculated scores for each strategy
        """
        # Create a copy to avoid modifying the original
        df = results_df.copy()
        
        # Handle missing ulcer_index column
        if 'ulcer_index' not in df.columns:
            df['ulcer_index'] = 5.0  # Default value
        
        # If DataFrame has multiple rows per strategy (different lot_sizes),
        # we need to select the best one for each strategy
        # For now, select the row with highest total_return per strategy
        if 'lot_size' in df.columns and df['strategy_name'].duplicated().any():
            # Group by strategy_name and select row with max total_return
            df = df.loc[df.groupby('strategy_name')['total_return'].idxmax()]
        
        records = []
        
        for _, row in df.iterrows():
            # Return score
            return_score = row['total_return']
            
            # Risk score (inverse of metrics - lower is better)
            max_dd = row['max_drawdown']
            risk_score = 1.0 - max_dd if max_dd < 1 else 0.0
            
            # Consistency score
            consistency_score = (
                row['win_rate'] * 0.4 +
                (row['sharpe_ratio'] / MAX_SHARPE_FOR_NORMALIZATION) * 0.3 +
                (row['sortino_ratio'] / MAX_SHARPE_FOR_NORMALIZATION) * 0.3
            )
            consistency_score = min(consistency_score, 1.0)
            
            # Robustness score (stability)
            ulcer = row.get('ulcer_index', 5.0)  # Use default if key doesn't exist
            robustness_score = (
                (row['profit_factor'] / MAX_PROFIT_FACTOR_FOR_NORMALIZATION) * 0.5 +
                (1.0 - ulcer / MAX_ULCER_FOR_NORMALIZATION) * 0.5 
                if ulcer < MAX_ULCER_FOR_NORMALIZATION else 0.0
            )
            robustness_score = max(0.0, min(robustness_score, 1.0))
            
            records.append({
                "strategy_name": row['strategy_name'],
                "return_score": return_score,
                "risk_score": risk_score,
                "consistency_score": consistency_score,
                "robustness_score": robustness_score,
                "n_trades": row['n_trades'],
                "total_return": row['total_return'],
                "sharpe_ratio": row['sharpe_ratio'],
                "max_drawdown": row['max_drawdown'],
                "win_rate": row['win_rate'],
            })
        
        return pd.DataFrame(records)
    
    def _calculate_composite_score(self, scores_df: pd.DataFrame) -> pd.DataFrame:
        """Calculate weighted composite score"""
        # Normalize all scores to 0-1 range
        score_cols = ["return_score", "risk_score", "consistency_score", "robustness_score"]
        
        # Handle edge cases
        for col in score_cols:
            if scores_df[col].max() == scores_df[col].min():
                scores_df[f"{col}_norm"] = DEFAULT_SCORE
            else:
                scores_df[f"{col}_norm"] = (
                    (scores_df[col] - scores_df[col].min()) /
                    (scores_df[col].max() - scores_df[col].min())
                )
        
        # Calculate composite score
        scores_df["composite_score"] = (
            scores_df["return_score_norm"] * self.weights.get("return", 0.3) +
            scores_df["risk_score_norm"] * self.weights.get("risk", 0.25) +
            scores_df["consistency_score_norm"] * self.weights.get("consistency", 0.25) +
            scores_df["robustness_score_norm"] * self.weights.get("robustness", 0.2)
        )
        
        return scores_df
    
    def detect_overfitting(self, is_results: BacktestResults,
                          oos_results: BacktestResults) -> Dict:
        """
        Detect overfitting by comparing in-sample vs out-of-sample
        
        Args:
            is_results: In-sample backtest results
            oos_results: Out-of-sample backtest results
            
        Returns:
            Dictionary with overfitting metrics
        """
        # Compare returns
        return_ratio = (
            is_results.total_return / oos_results.total_return
            if oos_results.total_return != 0 else float('inf')
        )
        
        # Compare Sharpe
        sharpe_ratio = (
            is_results.sharpe_ratio / oos_results.sharpe_ratio
            if oos_results.sharpe_ratio != 0 else float('inf')
        )
        
        # Overfitting detected if IS >> OOS
        max_ratio = OVERFITTING_CONFIG.get("max_is_oos_ratio", 2.0)
        
        is_overfitted = (
            return_ratio > max_ratio or
            sharpe_ratio > max_ratio or
            oos_results.n_trades < 10
        )
        
        return {
            "is_overfitted": is_overfitted,
            "return_ratio": return_ratio,
            "sharpe_ratio": sharpe_ratio,
            "is_return": is_results.total_return,
            "oos_return": oos_results.total_return,
            "is_sharpe": is_results.sharpe_ratio,
            "oos_sharpe": oos_results.sharpe_ratio,
        }
    
    def rank_strategies(self, results, top_n: int = None) -> pd.DataFrame:
        """
        Rank strategies by composite score
        
        Args:
            results: Either List[BacktestResults] (legacy) or pd.DataFrame (batch format)
            top_n: Number of top strategies to return
            
        Returns:
            Ranked DataFrame
        """
        if top_n is None:
            top_n = TOP_N_STRATEGIES
        
        # Determine the count based on input type
        if isinstance(results, pd.DataFrame):
            # For DataFrame, count unique strategy names
            n_strategies = results['strategy_name'].nunique() if 'strategy_name' in results.columns else len(results)
        else:
            n_strategies = len(results)
        
        print(f"\n🌟 Ranking {n_strategies} strategies...")
        
        # Calculate scores
        scores_df = self._calculate_scores(results)
        
        # Calculate composite score
        scores_df = self._calculate_composite_score(scores_df)
        
        # Sort by composite score
        ranked_df = scores_df.sort_values("composite_score", ascending=False)
        
        # Add rank
        ranked_df["rank"] = range(1, len(ranked_df) + 1)
        
        # Show top strategies
        print(f"\n💎 Top {min(top_n, len(ranked_df))} Strategies:")
        for i, row in ranked_df.head(top_n).iterrows():
            print(f"\n   #{row['rank']:2d} {row['strategy_name']}")
            print(f"       Score: {row['composite_score']:.3f}")
            print(f"       Return: {row['total_return']:.1%}, "
                  f"Sharpe: {row['sharpe_ratio']:.2f}, "
                  f"Win Rate: {row['win_rate']:.1%}")
        
        return ranked_df.head(top_n)
    
    def get_top_strategies_by_metric(self, results: List[BacktestResults],
                                     metric: str = "sharpe_ratio",
                                     top_n: int = 10) -> List[BacktestResults]:
        """Get top N strategies by specific metric"""
        sorted_results = sorted(
            results,
            key=lambda r: getattr(r, metric),
            reverse=True
        )
        return sorted_results[:top_n]


# ═══════════════════════════════════════════════════════════════
# 🧪 TESTING
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════════╗
║           🌟 LIGHT FINDER TEST 🌟                            ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    # Create mock results
    from backtester import BacktestResults
    import pandas as pd
    
    mock_results = []
    for i in range(20):
        result = BacktestResults(
            strategy_name=f"Strategy_{i+1}",
            n_trades=np.random.randint(30, 100),
            win_rate=np.random.uniform(0.4, 0.7),
            profit_factor=np.random.uniform(1.0, 2.5),
            total_return=np.random.uniform(-0.1, 0.5),
            sharpe_ratio=np.random.uniform(-0.5, 2.5),
            sortino_ratio=np.random.uniform(-0.5, 3.0),
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
        mock_results.append(result)
    
    # Test ranking
    finder = LightFinder()
    rankings = finder.rank_strategies(mock_results, top_n=10)
    
    print("\n📊 Full Rankings Table:")
    print(rankings[["rank", "strategy_name", "composite_score", 
                    "total_return", "sharpe_ratio", "win_rate"]].to_string(index=False))
    
    print("\n✅ Light finder test complete!")
