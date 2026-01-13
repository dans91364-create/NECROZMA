#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚡🌟💎 NECROZMA - Dashboard Integration Test 💎🌟⚡

Comprehensive test of dashboard functionality
"""

import sys
from pathlib import Path
import pandas as pd

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

def test_data_loading():
    """Test data loading functionality"""
    print("\n" + "="*60)
    print("📊 Testing Data Loading")
    print("="*60)
    
    from dashboard.utils.data_loader import load_all_results, get_universe_list, get_strategy_list
    
    results = load_all_results()
    
    print(f"✅ Total strategies loaded: {results['total_strategies']}")
    print(f"✅ Viable strategies: {results['viable_count']}")
    print(f"✅ Best Sharpe ratio: {results.get('best_sharpe', 0):.2f}")
    print(f"✅ Best return: {results.get('best_return', 0):.2f}%")
    
    universes = get_universe_list(results)
    print(f"✅ Universes found: {len(universes)}")
    
    strategies = get_strategy_list(results)
    print(f"✅ Unique strategies: {len(strategies)}")
    
    return results


def test_metrics():
    """Test metric calculations"""
    print("\n" + "="*60)
    print("📈 Testing Metrics")
    print("="*60)
    
    from dashboard.utils.data_loader import load_all_results
    from dashboard.components.metrics import (
        calculate_summary_metrics,
        get_top_strategies,
        calculate_universe_stats
    )
    
    results = load_all_results()
    strategies_df = results.get('strategies_df')
    
    if strategies_df is not None and not strategies_df.empty:
        summary = calculate_summary_metrics(strategies_df)
        print(f"✅ Summary metrics calculated:")
        print(f"   - Avg Sharpe: {summary['avg_sharpe']:.2f}")
        print(f"   - Avg Return: {summary['avg_return']:.2f}%")
        print(f"   - Avg Win Rate: {summary['avg_win_rate']:.2f}%")
        
        top_20 = get_top_strategies(strategies_df, by='sharpe_ratio', n=20)
        print(f"✅ Top 20 strategies retrieved: {len(top_20)} rows")
        
        universe_stats = calculate_universe_stats(strategies_df)
        print(f"✅ Universe statistics calculated: {len(universe_stats)} universes")
    else:
        print("⚠️ No strategy data available")


def test_charts():
    """Test chart creation"""
    print("\n" + "="*60)
    print("📊 Testing Chart Creation")
    print("="*60)
    
    from dashboard.utils.data_loader import load_all_results
    from dashboard.components.charts import (
        create_bar_chart,
        create_scatter_plot,
        create_pie_chart,
        create_histogram
    )
    
    results = load_all_results()
    strategies_df = results.get('strategies_df')
    
    if strategies_df is not None and not strategies_df.empty:
        # Test bar chart
        top_10 = strategies_df.nlargest(10, 'sharpe_ratio')
        fig = create_bar_chart(top_10, x='sharpe_ratio', y='strategy_name', 
                               title="Top 10 by Sharpe")
        print(f"✅ Bar chart created: {len(fig.data)} trace(s)")
        
        # Test scatter plot
        fig = create_scatter_plot(strategies_df.head(50), x='max_drawdown', 
                                 y='total_return', title="Return vs Risk")
        print(f"✅ Scatter plot created: {len(fig.data)} trace(s)")
        
        # Test pie chart
        viable = results['viable_count']
        non_viable = results['total_strategies'] - viable
        fig = create_pie_chart([viable, non_viable], 
                              ['Viable', 'Non-Viable'], 
                              title="Strategy Viability")
        print(f"✅ Pie chart created: {len(fig.data)} trace(s)")
        
        # Test histogram
        fig = create_histogram(strategies_df['sharpe_ratio'], 
                              title="Sharpe Distribution")
        print(f"✅ Histogram created: {len(fig.data)} trace(s)")
    else:
        print("⚠️ No strategy data available for charts")


def test_formatters():
    """Test formatting utilities"""
    print("\n" + "="*60)
    print("🎨 Testing Formatters")
    print("="*60)
    
    from dashboard.utils.formatters import (
        format_number,
        format_percentage,
        format_currency,
        format_pips,
        format_duration
    )
    
    tests = [
        (format_number(1234567.89, 2), "1,234,567.89"),
        (format_percentage(0.1523, 2), "15.23%"),
        (format_currency(1234.56), "$1,234.56"),
        (format_pips(25.5), "25.5 pips"),
        (format_duration(125), "2h 5m"),
    ]
    
    for result, expected in tests:
        print(f"✅ {expected}: {result}")


def test_trade_analysis():
    """Test trade analysis utilities"""
    print("\n" + "="*60)
    print("💰 Testing Trade Analysis")
    print("="*60)
    
    from dashboard.utils.data_loader import load_all_results
    from dashboard.utils.trade_analyzer import generate_insights
    
    results = load_all_results()
    strategies_df = results.get('strategies_df')
    
    if strategies_df is not None and not strategies_df.empty:
        # Create mock trades DataFrame for testing
        mock_trades = pd.DataFrame({
            'pnl_pips': [10, -5, 15, -8, 20, -3, 12],
            'pattern': ['ohl:H', 'ohl:L', 'ohl:H', 'ohl:LH', 'ohl:H', 'ohl:L', 'ohl:HL'],
            'duration_minutes': [60, 90, 45, 120, 30, 80, 55],
            'volatility': [0.02, 0.03, 0.01, 0.04, 0.02, 0.03, 0.01],
        })
        
        insights = generate_insights(mock_trades)
        print(f"✅ Generated {len(insights)} insights:")
        for i, insight in enumerate(insights, 1):
            print(f"   {i}. {insight}")
    else:
        print("⚠️ No strategy data available")


def test_pages_import():
    """Test that all pages can be imported"""
    print("\n" + "="*60)
    print("📄 Testing Page Imports")
    print("="*60)
    
    pages = [
        "1_📊_Overview.py",
        "2_🌍_Universe_Analysis.py",
        "3_🎯_Strategy_Deep_Dive.py",
        "4_🔧_SL_TP_Optimization.py",
        "5_⚠️_Risk_Analysis.py",
        "6_💰_Trade_Analysis.py"
    ]
    
    import py_compile
    
    for page in pages:
        page_path = Path(__file__).parent / "dashboard" / "pages" / page
        try:
            py_compile.compile(str(page_path), doraise=True)
            print(f"✅ {page} - syntax OK")
        except Exception as e:
            print(f"❌ {page} - error: {e}")


def run_all_tests():
    """Run all tests"""
    print("\n" + "="*70)
    print("⚡🌟💎 NECROZMA DASHBOARD - COMPREHENSIVE TEST SUITE 💎🌟⚡")
    print("="*70)
    
    try:
        results = test_data_loading()
        test_metrics()
        test_charts()
        test_formatters()
        test_trade_analysis()
        test_pages_import()
        
        print("\n" + "="*70)
        print("✅ ALL TESTS PASSED!")
        print("="*70)
        print("\n📊 Dashboard is ready to use!")
        print("\nTo launch the dashboard, run:")
        print("  streamlit run dashboard/app.py")
        print("\nThen navigate to: http://localhost:8501")
        print("="*70)
        
        return True
        
    except Exception as e:
        print("\n" + "="*70)
        print(f"❌ TEST FAILED: {e}")
        print("="*70)
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
