#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚡🌟💎 NECROZMA - INTEGRATION TEST FOR LIGHT REPORT ⚡🌟💎

Integration test demonstrating both Dict and DataFrame usage
"""

import pandas as pd
import numpy as np
from pathlib import Path
from backtester import BacktestResults
from light_report import LightReportGenerator


def test_integration_dict_format():
    """Test integration with legacy Dict format"""
    print("\n" + "="*80)
    print("📊 Testing Integration with Dict[str, BacktestResults] format")
    print("="*80)
    
    # Create top strategies
    top_strategies = pd.DataFrame({
        "rank": [1, 2],
        "strategy_name": ["MACD_Cross_TP30_SL15", "RSI_Oversold_TP40_SL20"],
        "composite_score": [0.85, 0.78],
        "total_return": [0.45, 0.38],
        "sharpe_ratio": [2.5, 2.1],
        "win_rate": [0.65, 0.60],
        "max_drawdown": [0.10, 0.12],
    })
    
    # Create backtest results dict
    backtest_results = {}
    for _, row in top_strategies.iterrows():
        result = BacktestResults(
            strategy_name=row["strategy_name"],
            n_trades=100,
            win_rate=row["win_rate"],
            profit_factor=2.5,
            total_return=row["total_return"],
            sharpe_ratio=row["sharpe_ratio"],
            sortino_ratio=row["sharpe_ratio"] * 1.3,
            calmar_ratio=3.0,
            max_drawdown=row["max_drawdown"],
            avg_win=0.004,
            avg_loss=-0.002,
            largest_win=0.012,
            largest_loss=-0.008,
            expectancy=0.003,
            recovery_factor=3.5,
            ulcer_index=3.2,
            trades=pd.DataFrame(),
            equity_curve=pd.Series([10000, 14500]),
        )
        backtest_results[row["strategy_name"]] = result
    
    # Generate report
    generator = LightReportGenerator(output_dir=Path("/tmp/test_integration"))
    report = generator.generate_report(
        top_strategies=top_strategies,
        all_backtest_results=backtest_results,
        total_strategies=500
    )
    
    # Verify report
    assert len(report["top_strategies"]) == 2
    print(f"✅ Generated report with {len(report['top_strategies'])} strategies")
    print(f"   Best: {report['top_strategies'][0]['name']} (Sharpe: {report['top_strategies'][0]['performance']['sharpe_ratio']})")
    
    return report


def test_integration_dataframe_format():
    """Test integration with new DataFrame format (batch processing)"""
    print("\n" + "="*80)
    print("📊 Testing Integration with DataFrame format (batch processing)")
    print("="*80)
    
    # Create top strategies
    top_strategies = pd.DataFrame({
        "rank": [1, 2],
        "strategy_name": ["MACD_Cross_TP30_SL15", "RSI_Oversold_TP40_SL20"],
        "composite_score": [0.85, 0.78],
        "total_return": [0.45, 0.38],
        "sharpe_ratio": [2.5, 2.1],
        "win_rate": [0.65, 0.60],
        "max_drawdown": [0.10, 0.12],
    })
    
    # Create DataFrame results (like batch processing produces)
    # Multiple lot_sizes per strategy
    backtest_results_df = pd.DataFrame({
        'strategy_name': [
            'MACD_Cross_TP30_SL15', 'MACD_Cross_TP30_SL15', 'MACD_Cross_TP30_SL15',
            'RSI_Oversold_TP40_SL20', 'RSI_Oversold_TP40_SL20', 'RSI_Oversold_TP40_SL20'
        ],
        'lot_size': [0.01, 0.02, 0.05, 0.01, 0.02, 0.05],
        'sharpe_ratio': [2.3, 2.5, 2.1, 2.0, 2.1, 1.8],  # Best is lot_size 0.02 for strategy 1, 0.02 for strategy 2
        'sortino_ratio': [2.99, 3.25, 2.73, 2.60, 2.73, 2.34],
        'calmar_ratio': [2.8, 3.0, 2.6, 2.7, 2.9, 2.5],
        'total_return': [0.43, 0.45, 0.41, 0.37, 0.38, 0.35],
        'max_drawdown': [0.11, 0.10, 0.12, 0.13, 0.12, 0.14],
        'win_rate': [0.64, 0.65, 0.63, 0.59, 0.60, 0.58],
        'n_trades': [98, 100, 102, 95, 97, 99],
        'profit_factor': [2.4, 2.5, 2.3, 2.3, 2.4, 2.2],
        'avg_win': [0.0038, 0.004, 0.0037, 0.0036, 0.0037, 0.0035],
        'avg_loss': [-0.0019, -0.002, -0.0021, -0.002, -0.002, -0.0021],
        'expectancy': [0.0028, 0.003, 0.0026, 0.0027, 0.0028, 0.0025],
        'gross_pnl': [4300, 4500, 4100, 3700, 3800, 3500],
        'net_pnl': [4250, 4450, 4050, 3650, 3750, 3450],
        'total_commission': [50, 50, 50, 50, 50, 50],
    })
    
    # Generate report
    generator = LightReportGenerator(output_dir=Path("/tmp/test_integration"))
    report = generator.generate_report(
        top_strategies=top_strategies,
        all_backtest_results=backtest_results_df,
        total_strategies=500
    )
    
    # Verify report
    assert len(report["top_strategies"]) == 2
    print(f"✅ Generated report with {len(report['top_strategies'])} strategies")
    print(f"   Best: {report['top_strategies'][0]['name']} (Sharpe: {report['top_strategies'][0]['performance']['sharpe_ratio']})")
    
    # Verify best lot_size was selected
    assert report['top_strategies'][0]['performance']['sharpe_ratio'] == 2.5  # lot_size 0.02
    assert report['top_strategies'][1]['performance']['sharpe_ratio'] == 2.1  # lot_size 0.02
    print(f"   ✅ Correctly selected best lot_size based on sharpe_ratio")
    
    return report


def compare_reports(report_dict, report_df):
    """Compare reports from Dict and DataFrame formats"""
    print("\n" + "="*80)
    print("🔍 Comparing Dict vs DataFrame Reports")
    print("="*80)
    
    # Compare structure
    assert report_dict.keys() == report_df.keys()
    print("✅ Report structures match")
    
    # Compare number of strategies
    assert len(report_dict["top_strategies"]) == len(report_df["top_strategies"])
    print(f"✅ Both have {len(report_dict['top_strategies'])} strategies")
    
    # Compare strategy names
    dict_names = [s["name"] for s in report_dict["top_strategies"]]
    df_names = [s["name"] for s in report_df["top_strategies"]]
    assert dict_names == df_names
    print(f"✅ Strategy names match: {dict_names}")
    
    # Compare key metrics (they should be identical or very close)
    for i in range(len(report_dict["top_strategies"])):
        dict_strat = report_dict["top_strategies"][i]
        df_strat = report_df["top_strategies"][i]
        
        dict_sharpe = dict_strat["performance"]["sharpe_ratio"]
        df_sharpe = df_strat["performance"]["sharpe_ratio"]
        
        print(f"   Strategy {i+1}: {dict_strat['name']}")
        print(f"      Dict Sharpe:      {dict_sharpe}")
        print(f"      DataFrame Sharpe: {df_sharpe}")
    
    print("\n✅ Both formats produce valid reports with expected structure")


if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════════╗
║     🧪 LIGHT REPORT INTEGRATION TEST 🧪                     ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    # Test Dict format
    report_dict = test_integration_dict_format()
    
    # Test DataFrame format
    report_df = test_integration_dataframe_format()
    
    # Compare both
    compare_reports(report_dict, report_df)
    
    print("\n" + "="*80)
    print("✅ ALL INTEGRATION TESTS PASSED")
    print("="*80)
    print("\nBoth Dict[str, BacktestResults] and DataFrame formats work correctly!")
    print("The implementation is backward compatible and supports batch processing.")
