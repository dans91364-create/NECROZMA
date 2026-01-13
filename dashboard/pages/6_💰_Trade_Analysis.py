#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚡🌟💎 NECROZMA DASHBOARD - TRADE ANALYSIS PAGE 💎🌟⚡

Analyze best and worst trades with market context
"""

import streamlit as st
import sys
from pathlib import Path
import pandas as pd

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from dashboard.utils.data_loader import load_all_results, get_strategy_list
from dashboard.components.charts import create_bar_chart, create_scatter_plot
from dashboard.utils.trade_analyzer import (
    analyze_patterns, analyze_market_conditions, generate_insights
)
from dashboard.utils.formatters import (
    format_pips, format_currency, format_duration, format_datetime
)

# Page config
st.set_page_config(page_title="Trade Analysis", page_icon="💰", layout="wide")

st.title("💰 Trade Analysis")
st.markdown("Analyze individual trades to understand wins and losses")

# Load data
with st.spinner("Loading backtest results..."):
    results = load_all_results()

if results['total_strategies'] == 0:
    st.error("❌ No backtest results found. Please run backtests first.")
    st.stop()

strategies_df = results.get('strategies_df')

if strategies_df is None or strategies_df.empty:
    st.error("❌ No strategy data available")
    st.stop()

# Important note about trade detail data
st.info("""
📌 **Note**: This page requires detailed trade data from the enhanced backtester (Phase 5).

Currently showing **summary-level analysis** only. To enable full trade-by-trade analysis:
1. Implement the backtester enhancements to save detailed trade information
2. Re-run backtests to generate detailed trade data
3. Detailed trade cards with market context will then be available

**Available now**: Pattern analysis, aggregate statistics, and insights from available data.
""")

st.markdown("---")

# Strategy selector for trade analysis
st.sidebar.header("🔍 Select Strategy")

strategy_names = get_strategy_list(results)

if not strategy_names:
    st.warning("No strategies available")
    st.stop()

selected_strategy = st.sidebar.selectbox("Select Strategy", strategy_names[:50])  # Limit for performance

# Get selected strategy data
strategy_data = strategies_df[strategies_df['strategy_name'] == selected_strategy].iloc[0].to_dict()

# Display strategy summary
st.header(f"📋 {selected_strategy}")

col1, col2, col3, col4 = st.columns(4)

with col1:
    n_trades = strategy_data.get('n_trades', 0)
    st.metric("Total Trades", f"{n_trades}")

with col2:
    win_rate = strategy_data.get('win_rate', 0) * 100
    st.metric("Win Rate", f"{win_rate:.1f}%")

with col3:
    total_return = strategy_data.get('total_return', 0) * 100
    st.metric("Total Return", f"{total_return:.2f}%")

with col4:
    sharpe = strategy_data.get('sharpe_ratio', 0)
    st.metric("Sharpe Ratio", f"{sharpe:.2f}")

st.markdown("---")

# Trade statistics
st.header("📊 Trade Statistics")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Win/Loss Breakdown")
    
    if n_trades > 0:
        wins = int(n_trades * strategy_data.get('win_rate', 0))
        losses = n_trades - wins
        
        st.markdown(f"""
        - **Winning Trades**: {wins} ({wins/n_trades*100:.1f}%)
        - **Losing Trades**: {losses} ({losses/n_trades*100:.1f}%)
        - **Win/Loss Ratio**: {wins/losses:.2f} if losses > 0 else "N/A"
        """)
        
        if 'avg_win' in strategy_data and 'avg_loss' in strategy_data:
            avg_win = strategy_data['avg_win']
            avg_loss = abs(strategy_data['avg_loss'])
            
            st.markdown(f"""
            - **Average Win**: {format_currency(avg_win)}
            - **Average Loss**: {format_currency(avg_loss)}
            - **Profit Factor**: {strategy_data.get('profit_factor', 0):.2f}
            """)
    else:
        st.info("No trade data available")

with col2:
    st.subheader("Best & Worst Trades")
    
    if 'largest_win' in strategy_data and 'largest_loss' in strategy_data:
        st.markdown(f"""
        **Best Trade**:
        - P&L: {format_currency(strategy_data['largest_win'])}
        
        **Worst Trade**:
        - P&L: {format_currency(strategy_data['largest_loss'])}
        
        **Range**: {format_currency(strategy_data['largest_win'] - strategy_data['largest_loss'])}
        """)
        
        # Win/Loss comparison bar
        import plotly.graph_objects as go
        
        fig = go.Figure(data=[
            go.Bar(name='Largest Win', x=['Best'], y=[strategy_data['largest_win']], 
                   marker_color='green'),
            go.Bar(name='Largest Loss', x=['Worst'], y=[abs(strategy_data['largest_loss'])], 
                   marker_color='red')
        ])
        fig.update_layout(title="Best vs Worst Trade", yaxis_title="P&L ($)")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Trade detail data not available")

st.markdown("---")

# Expected value analysis
st.header("💡 Expected Value Analysis")

if 'expectancy' in strategy_data:
    expectancy = strategy_data['expectancy']
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Expectancy", format_currency(expectancy))
        
        if expectancy > 0:
            st.success("✅ Positive expectancy - profitable strategy")
        else:
            st.error("❌ Negative expectancy - unprofitable strategy")
    
    with col2:
        if n_trades > 0:
            expected_profit = expectancy * n_trades
            st.metric("Expected Total Profit", format_currency(expected_profit))
    
    with col3:
        if 'avg_win' in strategy_data and 'avg_loss' in strategy_data:
            avg_win = strategy_data['avg_win']
            avg_loss = abs(strategy_data['avg_loss'])
            
            if avg_loss > 0:
                payoff_ratio = avg_win / avg_loss
                st.metric("Payoff Ratio", f"{payoff_ratio:.2f}")
            else:
                st.metric("Payoff Ratio", "N/A")

st.markdown("---")

# Insights
st.header("🧠 Insights & Recommendations")

insights = []

# Generate insights based on available data
if strategy_data.get('win_rate', 0) > 0.6:
    insights.append(f"🎯 High win rate ({win_rate:.1f}%) suggests good entry signals")
elif strategy_data.get('win_rate', 0) < 0.4:
    insights.append(f"⚠️ Low win rate ({win_rate:.1f}%) - consider refining entry criteria")

if 'profit_factor' in strategy_data:
    pf = strategy_data['profit_factor']
    if pf > 2.0:
        insights.append(f"💰 Excellent profit factor ({pf:.2f}) - strong risk/reward management")
    elif pf < 1.0:
        insights.append(f"⚠️ Profit factor below 1.0 ({pf:.2f}) - losing more than winning")

if 'avg_win' in strategy_data and 'avg_loss' in strategy_data:
    avg_win = strategy_data['avg_win']
    avg_loss = abs(strategy_data['avg_loss'])
    
    if avg_loss > 0:
        ratio = avg_win / avg_loss
        if ratio > 2.0:
            insights.append(f"✅ Large average wins relative to losses (ratio: {ratio:.2f})")
        elif ratio < 1.0:
            insights.append(f"⚠️ Average losses exceed average wins (ratio: {ratio:.2f})")

if n_trades < 30:
    insights.append(f"📊 Limited sample size ({n_trades} trades) - results may not be statistically significant")
elif n_trades > 100:
    insights.append(f"✅ Large sample size ({n_trades} trades) provides statistical confidence")

# Display insights
if insights:
    for insight in insights:
        st.markdown(f"- {insight}")
else:
    st.info("Insufficient data for detailed insights")

st.markdown("---")

# Recommendations
st.header("📋 Recommendations")

st.markdown("""
### To Enable Full Trade Analysis:

The complete trade analysis feature requires implementing the backtester enhancements:

1. **Modify `backtester.py`** to save detailed trade information:
   - Entry/exit prices and timestamps
   - Trade duration
   - P&L in pips, USD, and percentage
   - Exit reason (SL/TP/signal)
   - Market context (volatility, trend, volume, spread)
   - Pattern detected
   - Price history around the trade

2. **Re-run backtests** to generate the enhanced data

3. **Return to this page** to see:
   - Trade-by-trade cards with full context
   - Price charts for each trade
   - Market condition analysis
   - Pattern performance breakdown
   - Timing analysis (best/worst hours/days)
   - AI-generated insights from trade patterns

### Current Analysis Capabilities:

With the current data, you can:
- ✅ View aggregate statistics
- ✅ Compare strategies in Overview
- ✅ Analyze universe performance
- ✅ Examine risk metrics
- ✅ Review summary-level trade stats

### Next Steps:

1. Review the implementation plan in the problem statement
2. Implement Phase 5 (Backtester Enhancement)
3. Re-run your backtests
4. Return here for detailed trade-by-trade analysis
""")

# Footer
st.markdown("---")
st.markdown("💡 **Tip**: Use the Strategy Deep Dive page to compare detailed metrics across strategies!")
