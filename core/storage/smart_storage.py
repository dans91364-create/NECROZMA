#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚡🌟💎 ULTRA NECROZMA - Smart Tiered Storage 💎🌟⚡

Intelligent 2-tier storage system for backtest results:
- Tier 1: Lightweight metrics for ALL strategies (fast loading)
- Tier 2: Detailed trades for TOP N strategies only (on-demand)

This reduces storage from ~115 GB to ~5 GB (95% reduction!)
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime


class SmartBacktestStorage:
    """
    Intelligent 2-tier storage:
    - Tier 1: Metrics for ALL strategies (lightweight, always saved)
    - Tier 2: Detailed trades for TOP N strategies only (heavy, on-demand)
    """
    
    def __init__(self, output_dir: str = "ultra_necrozma_results/backtest_results"):
        """
        Initialize smart storage
        
        Args:
            output_dir: Output directory for backtest results
        """
        self.output_dir = Path(output_dir)
        self.metrics_file = self.output_dir / "all_strategies_metrics.json"
        self.trades_dir = self.output_dir / "detailed_trades"
        
        # Create directories
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.trades_dir.mkdir(parents=True, exist_ok=True)
    
    def save_universe_results(self, universe_name: str, results: List[Dict], top_n: int = 50):
        """
        Save results with smart filtering:
        1. Add ALL metrics to global metrics file
        2. Save detailed trades only for top N strategies (by composite score)
        
        Args:
            universe_name: Universe identifier (e.g., "universe_001_5min_5lb")
            results: List of strategy results with metrics + trades
            top_n: Number of top strategies to save detailed trades for (default: 50)
        """
        # 1. Rank strategies by composite score
        ranked = self._rank_strategies(results)
        
        # 2. Update global metrics file (ALL strategies)
        all_metrics = self._load_all_metrics()
        
        for result in ranked:
            strategy_metrics = {
                "strategy_name": result["strategy_name"],
                "universe": universe_name,
                "metrics": self._extract_metrics_only(result)  # No trades!
            }
            
            # Update or append
            self._upsert_metrics(all_metrics, strategy_metrics)
        
        self._save_all_metrics(all_metrics)
        
        # 3. Save detailed trades for TOP N only
        print(f"\n💾 Saving detailed trades for top {top_n} strategies...")
        
        for i, result in enumerate(ranked[:top_n]):
            strategy_name = result["strategy_name"]
            trade_file = self.trades_dir / f"{strategy_name}.json"
            
            # Save FULL data (metrics + trades + equity curve)
            detailed_data = {
                "strategy_name": strategy_name,
                "universe": universe_name,
                "rank": i + 1,
                "metrics": self._extract_metrics_only(result),
                "trades": result.get("trades_detailed", []),
                "equity_curve": self._serialize_equity_curve(result.get("equity_curve")),
                "drawdown_curve": result.get("drawdown_curve", [])
            }
            
            with open(trade_file, 'w') as f:
                json.dump(detailed_data, f, indent=2)
            
            file_size = trade_file.stat().st_size / 1e6
            print(f"  ✅ {i+1:2d}. {strategy_name[:50]:<50} ({file_size:.1f} MB)")
        
        # Print storage summary
        print(f"\n📊 Storage Summary:")
        metrics_size = self.metrics_file.stat().st_size / 1e6 if self.metrics_file.exists() else 0
        print(f"  All metrics: {len(all_metrics)} strategies ({metrics_size:.1f} MB)")
        print(f"  Detailed trades: {min(top_n, len(ranked))} strategies saved")
    
    def load_strategy_trades(self, strategy_name: str) -> Optional[Dict]:
        """
        Load detailed trades for ONE strategy (on-demand)
        Returns None if not in top N
        
        Args:
            strategy_name: Name of the strategy
            
        Returns:
            Dictionary with strategy data or None if not found
        """
        trade_file = self.trades_dir / f"{strategy_name}.json"
        
        if not trade_file.exists():
            return None
        
        with open(trade_file, 'r') as f:
            return json.load(f)
    
    def get_available_detailed_strategies(self) -> List[str]:
        """
        Get list of strategies with detailed trades available
        
        Returns:
            List of strategy names
        """
        return [f.stem for f in self.trades_dir.glob("*.json")]
    
    def _rank_strategies(self, results: List[Dict]) -> List[Dict]:
        """
        Rank strategies by composite score (or Sharpe if not available)
        
        Args:
            results: List of strategy result dictionaries
            
        Returns:
            Sorted list of strategy results (best first)
        """
        # Use composite_score if exists, else sharpe_ratio
        for result in results:
            if "composite_score" not in result:
                result["composite_score"] = result.get("sharpe_ratio", 0.0)
        
        return sorted(results, key=lambda x: x.get("composite_score", 0), reverse=True)
    
    def _extract_metrics_only(self, result: Dict) -> Dict:
        """
        Extract metrics, exclude heavy data (trades, equity curves)
        
        Args:
            result: Strategy result dictionary
            
        Returns:
            Dictionary with only metrics (no trades/curves)
        """
        return {k: v for k, v in result.items() 
                if k not in ["trades_detailed", "equity_curve", "drawdown_curve", "trades"]}
    
    def _serialize_equity_curve(self, equity_curve: Any) -> List:
        """
        Serialize equity curve to list format
        
        Args:
            equity_curve: Equity curve (pd.Series, list, or None)
            
        Returns:
            List representation of equity curve
        """
        if equity_curve is None:
            return []
        
        # Handle pandas Series
        if hasattr(equity_curve, 'tolist'):
            return equity_curve.tolist()
        
        # Already a list
        if isinstance(equity_curve, list):
            return equity_curve
        
        # Try to convert to list
        try:
            return list(equity_curve)
        except (TypeError, ValueError):
            return []
    
    def _load_all_metrics(self) -> List[Dict]:
        """
        Load existing metrics file
        
        Returns:
            List of strategy metrics
        """
        if not self.metrics_file.exists():
            return []
        
        try:
            with open(self.metrics_file, 'r') as f:
                data = json.load(f)
                return data.get("strategies", [])
        except (json.JSONDecodeError, KeyError):
            return []
    
    def _save_all_metrics(self, metrics: List[Dict]):
        """
        Save metrics file
        
        Args:
            metrics: List of strategy metrics
        """
        with open(self.metrics_file, 'w') as f:
            json.dump({
                "total_strategies": len(metrics),
                "last_updated": datetime.now().isoformat(),
                "strategies": metrics
            }, f, indent=2)
    
    def _upsert_metrics(self, all_metrics: List[Dict], new_metric: Dict):
        """
        Update existing or append new metric
        
        Args:
            all_metrics: List of all metrics (modified in place)
            new_metric: New metric to add or update
        """
        existing_idx = next(
            (i for i, s in enumerate(all_metrics) 
             if s["strategy_name"] == new_metric["strategy_name"] 
             and s["universe"] == new_metric["universe"]),
            None
        )
        
        if existing_idx is not None:
            all_metrics[existing_idx] = new_metric
        else:
            all_metrics.append(new_metric)
