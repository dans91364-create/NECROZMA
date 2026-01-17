#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚡🌟💎 NECROZMA - LIGHT REPORT 💎🌟⚡

Final Report Generator - "Where The Light Is"
"The ultimate synthesis of all discoveries"

Features:
- Executive summary
- Top strategies with detailed rules
- Feature insights
- Regime analysis
- Implementation guide
"""

import json
import pandas as pd
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

from backtester import BacktestResults
from config import FILE_PREFIX
from typing import Union



# ═══════════════════════════════════════════════════════════════
# 📊 LIGHT REPORT GENERATOR
# ═══════════════════════════════════════════════════════════════

class LightReportGenerator:
    """
    Generate comprehensive "Where The Light Is" report
    
    Usage:
        generator = LightReportGenerator()
        report = generator.generate_report(top_strategies, feature_importance, regime_analysis)
    """
    
    def __init__(self, output_dir: Path = None):
        """
        Initialize report generator
        
        Args:
            output_dir: Output directory for reports
        """
        self.output_dir = output_dir or Path("ultra_necrozma_results/reports")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def _create_executive_summary(self, top_strategies: pd.DataFrame,
                                  total_strategies: int) -> Dict:
        """Create executive summary"""
        if len(top_strategies) == 0:
            return {
                "total_strategies_tested": total_strategies,
                "strategies_found": 0,
                "message": "No viable strategies found",
            }
        
        best_strategy = top_strategies.iloc[0]
        
        return {
            "total_strategies_tested": total_strategies,
            "viable_strategies_found": len(top_strategies),
            "best_strategy": {
                "name": best_strategy["strategy_name"],
                "rank": int(best_strategy["rank"]),
                "composite_score": float(best_strategy["composite_score"]),
                "total_return": float(best_strategy["total_return"]),
                "sharpe_ratio": float(best_strategy["sharpe_ratio"]),
                "win_rate": float(best_strategy["win_rate"]),
                "max_drawdown": float(best_strategy["max_drawdown"]),
            },
            "avg_return": float(top_strategies["total_return"].mean()),
            "avg_sharpe": float(top_strategies["sharpe_ratio"].mean()),
            "avg_win_rate": float(top_strategies["win_rate"].mean()),
        }
    
    def _df_to_results_lookup(self, df: pd.DataFrame) -> Dict:
        """
        Convert DataFrame to dict mapping strategy_name -> result dict
        
        Args:
            df: DataFrame with columns: strategy_name, lot_size, sharpe_ratio, etc.
            
        Returns:
            Dictionary mapping strategy_name to best result dict (highest sharpe_ratio)
        """
        lookup = {}
        for strategy_name in df['strategy_name'].unique():
            strategy_rows = df[df['strategy_name'] == strategy_name]
            # Use best lot_size (highest sharpe) or first row
            best_row = strategy_rows.loc[strategy_rows['sharpe_ratio'].idxmax()]
            lookup[strategy_name] = best_row.to_dict()
        return lookup
    
    def _create_strategy_details(self, strategy_name: str,
                                 result: Union[BacktestResults, Dict]) -> Dict:
        """
        Create detailed strategy information
        
        Args:
            strategy_name: Name of the strategy
            result: Either a BacktestResults object or a dict from DataFrame
            
        Returns:
            Dictionary with strategy details
        """
        # Handle both BacktestResults object and dict
        if isinstance(result, dict):
            # DataFrame result dict
            return {
                "name": strategy_name,
                "performance": {
                    "total_return": float(result.get('total_return', 0)),
                    "sharpe_ratio": float(result.get('sharpe_ratio', 0)),
                    "sortino_ratio": float(result.get('sortino_ratio', 0)),
                    "calmar_ratio": float(result.get('calmar_ratio', 0)),
                    "max_drawdown": float(result.get('max_drawdown', 0)),
                    "profit_factor": float(result.get('profit_factor', 0)),
                    "win_rate": float(result.get('win_rate', 0)),
                    "expectancy": float(result.get('expectancy', 0)),
                },
                "trading_stats": {
                    "total_trades": int(result.get('n_trades', 0)),
                    "avg_win": float(result.get('avg_win', 0)),
                    "avg_loss": float(result.get('avg_loss', 0)),
                    # These may not exist in DataFrame results
                    "largest_win": float(result.get('largest_win', 0)),
                    "largest_loss": float(result.get('largest_loss', 0)),
                },
            }
        else:
            # BacktestResults object
            return {
                "name": strategy_name,
                "performance": {
                    "total_return": float(result.total_return),
                    "sharpe_ratio": float(result.sharpe_ratio),
                    "sortino_ratio": float(result.sortino_ratio),
                    "calmar_ratio": float(result.calmar_ratio),
                    "max_drawdown": float(result.max_drawdown),
                    "profit_factor": float(result.profit_factor),
                    "win_rate": float(result.win_rate),
                    "expectancy": float(result.expectancy),
                },
                "trading_stats": {
                    "total_trades": int(result.n_trades),
                    "avg_win": float(result.avg_win),
                    "avg_loss": float(result.avg_loss),
                    "largest_win": float(result.largest_win),
                    "largest_loss": float(result.largest_loss),
                },
            }
    
    def _create_feature_insights(self, feature_importance: Dict) -> Dict:
        """Create feature insights section"""
        if not feature_importance or "aggregate" not in feature_importance:
            return {"message": "No feature importance data available"}
        
        agg_importance = feature_importance["aggregate"]
        
        # Top features
        top_10 = agg_importance.head(10)
        
        # Bottom features (useless)
        bottom_10 = agg_importance.tail(10)
        
        return {
            "most_important_features": [
                {
                    "rank": i + 1,
                    "feature": row["feature"],
                    "importance": float(row["avg_importance"]),
                }
                for i, row in top_10.iterrows()
            ],
            "least_important_features": [
                {
                    "feature": row["feature"],
                    "importance": float(row["avg_importance"]),
                }
                for _, row in bottom_10.iterrows()
            ],
            "key_insights": self._generate_feature_insights(top_10),
        }
    
    def _generate_feature_insights(self, top_features: pd.DataFrame) -> List[str]:
        """Generate human-readable insights from top features"""
        insights = []
        
        for _, row in top_features.head(5).iterrows():
            feature = row["feature"]
            
            if "volatility" in feature.lower():
                insights.append(f"Volatility indicators are crucial - {feature} is highly predictive")
            elif "momentum" in feature.lower():
                insights.append(f"Momentum matters - {feature} shows strong signal")
            elif "entropy" in feature.lower():
                insights.append(f"Market entropy/chaos is informative - {feature} captures regime changes")
            elif "trend" in feature.lower():
                insights.append(f"Trend identification is key - {feature} helps detect market direction")
            else:
                insights.append(f"{feature} is a strong predictor of future movements")
        
        return insights
    
    def _create_regime_insights(self, regime_analysis: Dict) -> Dict:
        """Create regime analysis section"""
        if not regime_analysis:
            return {"message": "No regime analysis available"}
        
        characteristics = regime_analysis.get("characteristics", {})
        
        regime_summary = []
        for regime_id, char in characteristics.items():
            regime_summary.append({
                "regime_id": regime_id,
                "name": char["name"],
                "percentage": float(char["percentage"]),
                "size": int(char["size"]),
            })
        
        return {
            "n_regimes": regime_analysis.get("n_regimes", 0),
            "regimes": regime_summary,
            "insights": [
                f"Market exhibits {regime_analysis.get('n_regimes', 0)} distinct behavioral regimes",
                "Different strategies perform better in different market conditions",
                "Regime-adaptive approaches may outperform single-strategy systems",
            ],
        }
    
    def _create_implementation_guide(self, top_strategies: pd.DataFrame) -> Dict:
        """Create implementation guide"""
        if len(top_strategies) == 0:
            return {"message": "No strategies to implement"}
        
        best = top_strategies.iloc[0]
        
        return {
            "recommended_strategy": best["strategy_name"],
            "implementation_steps": [
                "1. Extract features as defined in the feature importance section",
                "2. Implement the strategy rules outlined in the top strategies",
                "3. Use the recommended stop-loss and take-profit levels",
                "4. Start with paper trading to validate performance",
                "5. Monitor regime changes and adapt strategy if needed",
            ],
            "risk_management": {
                "recommended_stop_loss": "15-20 pips based on strategy parameters",
                "recommended_take_profit": "30-40 pips for 2:1 risk-reward",
                "max_drawdown_expectation": f"{best['max_drawdown']:.1%}",
                "position_sizing": "Risk no more than 1-2% of capital per trade",
            },
            "warnings": [
                "Past performance does not guarantee future results",
                "Market conditions change - monitor performance regularly",
                "Always use proper risk management",
                "Consider transaction costs and slippage in live trading",
            ],
        }
    
    def generate_report(self,
                       top_strategies: pd.DataFrame,
                       all_backtest_results: Union[Dict[str, BacktestResults], pd.DataFrame],
                       feature_importance: Dict = None,
                       regime_analysis: Dict = None,
                       total_strategies: int = 0) -> Dict:
        """
        Generate complete "Where The Light Is" report
        
        Args:
            top_strategies: Ranked top strategies DataFrame
            all_backtest_results: Either Dict mapping strategy_name -> BacktestResults (legacy)
                                or DataFrame with result columns (new batch format)
            feature_importance: Feature importance analysis results
            regime_analysis: Regime detection analysis results
            total_strategies: Total number of strategies tested
            
        Returns:
            Complete report dictionary
        """
        print("\n📝 Generating Light Report...")
        
        # Convert DataFrame to dict-like lookup if needed
        if isinstance(all_backtest_results, pd.DataFrame):
            results_lookup = self._df_to_results_lookup(all_backtest_results)
        else:
            results_lookup = all_backtest_results
        
        report = {
            "title": "⚡🌟💎 WHERE THE LIGHT IS - NECROZMA FINAL REPORT 💎🌟⚡",
            "subtitle": "Light That Burns The Sky - Complete Strategy Analysis",
            "generated_at": datetime.now().isoformat(),
            "executive_summary": self._create_executive_summary(top_strategies, total_strategies),
            "top_strategies": [],
            "feature_insights": self._create_feature_insights(feature_importance or {}),
            "regime_analysis": self._create_regime_insights(regime_analysis or {}),
            "implementation_guide": self._create_implementation_guide(top_strategies),
        }
        
        # Add detailed info for top strategies
        for _, row in top_strategies.iterrows():
            strategy_name = row["strategy_name"]
            if strategy_name in results_lookup:
                details = self._create_strategy_details(
                    strategy_name,
                    results_lookup[strategy_name]
                )
                details["rank"] = int(row["rank"])
                details["composite_score"] = float(row["composite_score"])
                report["top_strategies"].append(details)
        
        return report
    
    def save_report(self, report: Dict, filename: str = None) -> Path:
        """
        Save report to JSON file
        
        Args:
            report: Report dictionary
            filename: Output filename (auto-generated if None)
            
        Returns:
            Path to saved file
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{FILE_PREFIX}LIGHT_REPORT_{timestamp}.json"
        
        filepath = self.output_dir / filename
        
        with open(filepath, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n💾 Report saved to: {filepath}")
        
        return filepath
    
    def print_summary(self, report: Dict):
        """Print report summary to console"""
        print(f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║              ⚡🌟💎 WHERE THE LIGHT IS 💎🌟⚡                                ║
║                                                                              ║
║                    NECROZMA FINAL STRATEGY REPORT                            ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝

📊 EXECUTIVE SUMMARY
{'='*80}
Total Strategies Tested: {report['executive_summary']['total_strategies_tested']}
Viable Strategies Found: {report['executive_summary']['viable_strategies_found']}
        """)
        
        if report['executive_summary']['viable_strategies_found'] > 0:
            best = report['executive_summary']['best_strategy']
            print(f"""
🏆 BEST STRATEGY: {best['name']}
   Score:      {best['composite_score']:.3f}
   Return:     {best['total_return']:.1%}
   Sharpe:     {best['sharpe_ratio']:.2f}
   Win Rate:   {best['win_rate']:.1%}
   Max DD:     {best['max_drawdown']:.1%}

📈 AVERAGE PERFORMANCE (Top Strategies)
   Avg Return:   {report['executive_summary']['avg_return']:.1%}
   Avg Sharpe:   {report['executive_summary']['avg_sharpe']:.2f}
   Avg Win Rate: {report['executive_summary']['avg_win_rate']:.1%}
            """)
        
        # Feature insights
        if "most_important_features" in report['feature_insights']:
            print(f"\n💡 TOP 5 MOST IMPORTANT FEATURES")
            print("="*80)
            for feat in report['feature_insights']['most_important_features'][:5]:
                print(f"   {feat['rank']}. {feat['feature']:<40s} {feat['importance']:.4f}")
        
        # Implementation guide
        print(f"\n🔧 IMPLEMENTATION RECOMMENDATIONS")
        print("="*80)
        guide = report['implementation_guide']
        if 'recommended_strategy' in guide:
            print(f"\n   Recommended: {guide['recommended_strategy']}")
            print(f"\n   Risk Management:")
            for key, value in guide.get('risk_management', {}).items():
                print(f"      {key}: {value}")
        
        print(f"\n⚠️  WARNINGS")
        print("="*80)
        for warning in guide.get('warnings', []):
            print(f"   • {warning}")


# ═══════════════════════════════════════════════════════════════
# 🧪 TESTING
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════════╗
║           📝 LIGHT REPORT TEST 📝                            ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    # Create mock data
    import numpy as np
    from backtester import BacktestResults
    
    # Mock top strategies
    top_strategies = pd.DataFrame({
        "rank": [1, 2, 3],
        "strategy_name": ["Strategy_A", "Strategy_B", "Strategy_C"],
        "composite_score": [0.85, 0.78, 0.72],
        "total_return": [0.35, 0.28, 0.25],
        "sharpe_ratio": [2.1, 1.8, 1.6],
        "win_rate": [0.62, 0.58, 0.55],
        "max_drawdown": [0.12, 0.15, 0.18],
    })
    
    # Mock backtest results
    backtest_results = {}
    for _, row in top_strategies.iterrows():
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
        backtest_results[row["strategy_name"]] = result
    
    # Generate report
    generator = LightReportGenerator(output_dir=Path("/tmp/test_reports"))
    
    report = generator.generate_report(
        top_strategies=top_strategies,
        all_backtest_results=backtest_results,
        total_strategies=100
    )
    
    # Print summary
    generator.print_summary(report)
    
    # Save report
    filepath = generator.save_report(report)
    
    print(f"\n✅ Light report test complete!")
