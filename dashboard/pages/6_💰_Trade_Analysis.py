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
import plotly.graph_objects as go

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from dashboard.utils.data_loader import (
    load_all_strategies_metrics,
    load_strategy_detailed_trades,
    get_strategies_with_trades,
    load_all_results
)
from dashboard.utils.formatters import (
    format_currency, format_datetime
)

# Page config
st.set_page_config(page_title="Trade Analysis", page_icon="💰", layout="wide")

st.title("💰 Trade-by-Trade Analysis")

# Load metrics (lightweight, fast)
metrics_df = load_all_strategies_metrics()

if metrics_df.empty:
    st.error("❌ No backtest results found")
    st.info("""
    **No results found.** Please run backtests first:
    
    ```bash
    python run_sequential_backtest.py
    ```
    """)
    st.stop()

# Get strategies with detailed trades available
strategies_with_trades = get_strategies_with_trades()

if not strategies_with_trades:
    st.warning("⚠️ No detailed trades available. Run backtest to generate trade data.")
    st.info("""
    **Note:** Only the top 50 strategies per universe have detailed trade data saved.
    
    This is by design to keep storage manageable while still allowing deep analysis 
    of the best performers.
    
    **To generate detailed trades:**
    1. Run backtests with the updated system
    2. Top 50 strategies per universe will have detailed trades saved
    3. Return to this page to analyze them
    """)
    
    # Show summary statistics for all strategies
    st.markdown("---")
    st.header("📊 Summary Statistics (All Strategies)")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Strategies", f"{len(metrics_df):,}")
    
    with col2:
        avg_sharpe = metrics_df['sharpe_ratio'].mean() if 'sharpe_ratio' in metrics_df.columns else 0
        st.metric("Avg Sharpe Ratio", f"{avg_sharpe:.2f}")
    
    with col3:
        avg_return = metrics_df['total_return'].mean() if 'total_return' in metrics_df.columns else 0
        st.metric("Avg Return", f"{avg_return*100:.1f}%")
    
    with col4:
        avg_win_rate = metrics_df['win_rate'].mean() if 'win_rate' in metrics_df.columns else 0
        st.metric("Avg Win Rate", f"{avg_win_rate*100:.1f}%")
    
    st.stop()

st.success(f"✅ {len(strategies_with_trades)} strategies have detailed trade data available")

# Strategy selector (only show those with trades)
available_metrics = metrics_df[metrics_df['strategy_name'].isin(strategies_with_trades)]

if available_metrics.empty:
    st.error("No matching strategies found")
    st.stop()

# Sidebar filters
st.sidebar.header("🔍 Filter Strategies")

# Universe filter
if 'universe' in available_metrics.columns:
    universes = ['All'] + sorted(available_metrics['universe'].unique().tolist())
    selected_universe = st.sidebar.selectbox("Universe", universes)
    
    if selected_universe != 'All':
        available_metrics = available_metrics[available_metrics['universe'] == selected_universe]

# Sort by metric
sort_options = {
    'Sharpe Ratio': 'sharpe_ratio',
    'Total Return': 'total_return',
    'Win Rate': 'win_rate',
    'Strategy Name': 'strategy_name'
}

sort_by = st.sidebar.selectbox("Sort By", list(sort_options.keys()), index=0)
sort_col = sort_options[sort_by]

if sort_col in available_metrics.columns:
    available_metrics = available_metrics.sort_values(sort_col, ascending=False)

selected_strategy = st.sidebar.selectbox(
    "Select Strategy (Top 50 only)",
    options=available_metrics['strategy_name'].tolist(),
    help="Only top 50 strategies per universe have detailed trade data saved"
)

if selected_strategy:
    # Load trades ON-DEMAND (only when user selects)
    with st.spinner(f"Loading trades for {selected_strategy}..."):
        strategy_data = load_strategy_detailed_trades(selected_strategy)
    
    if strategy_data is None:
        st.error(f"Could not load trades for {selected_strategy}")
        st.stop()
    
    # Display strategy info
    st.header(f"📊 {selected_strategy}")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.caption(f"**Universe:** {strategy_data.get('universe', 'Unknown')}")
    
    with col2:
        rank = strategy_data.get('rank', '?')
        st.caption(f"**Rank:** #{rank} in universe")
    
    st.markdown("---")
    
    # Metrics
    metrics = strategy_data.get("metrics", {})
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        total_return = metrics.get('total_return', 0)
        st.metric("Total Return", f"{total_return*100:.1f}%")
    
    with col2:
        sharpe = metrics.get('sharpe_ratio', 0)
        st.metric("Sharpe Ratio", f"{sharpe:.2f}")
    
    with col3:
        win_rate = metrics.get('win_rate', 0)
        st.metric("Win Rate", f"{win_rate*100:.1f}%")
    
    with col4:
        n_trades = metrics.get('n_trades', 0)
        st.metric("Total Trades", f"{n_trades:,}")
    
    with col5:
        max_dd = metrics.get('max_drawdown', 0)
        st.metric("Max Drawdown", f"{max_dd*100:.1f}%")
    
    # Equity curve
    st.subheader("📈 Equity Curve")
    
    equity = strategy_data.get("equity_curve", [])
    if equity and len(equity) > 0:
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            y=equity, 
            mode='lines', 
            name='Equity',
            line=dict(color='#00CC96', width=2)
        ))
        fig.update_layout(
            title="Equity Curve Over Time",
            yaxis_title="Balance ($)",
            xaxis_title="Trade Number",
            height=400,
            hovermode='x unified'
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No equity curve data available")
    
    # Trades table
    st.subheader("🔍 Trade History")
    
    trades = strategy_data.get("trades", [])
    if trades and len(trades) > 0:
        trades_df = pd.DataFrame(trades)
        
        # Format trades for display
        display_cols = []
        available_cols = trades_df.columns.tolist()
        
        # Prioritize these columns if available
        priority_cols = [
            'entry_time', 'exit_time', 'direction', 
            'entry_price', 'exit_price', 'pnl_usd', 'pnl_pct', 
            'duration_minutes', 'exit_reason'
        ]
        
        for col in priority_cols:
            if col in available_cols:
                display_cols.append(col)
        
        # Add any remaining columns
        for col in available_cols:
            if col not in display_cols:
                display_cols.append(col)
        
        # Show trade statistics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Winning Trades", f"{sum(trades_df.get('pnl_usd', [0]) > 0) if 'pnl_usd' in trades_df else 0}")
        
        with col2:
            st.metric("Losing Trades", f"{sum(trades_df.get('pnl_usd', [0]) < 0) if 'pnl_usd' in trades_df else 0}")
        
        with col3:
            avg_pnl = trades_df['pnl_usd'].mean() if 'pnl_usd' in trades_df else 0
            st.metric("Avg P&L per Trade", f"${avg_pnl:.2f}")
        
        st.markdown("---")
        
        # Show first 100 trades in UI
        st.dataframe(
            trades_df[display_cols].head(100),
            use_container_width=True,
            height=600
        )
        
        if len(trades_df) > 100:
            st.caption(f"Showing first 100 of {len(trades_df)} trades. Download CSV to see all trades.")
        
        # Download ALL trades as CSV
        csv = trades_df.to_csv(index=False)
        st.download_button(
            label=f"📥 Download All {len(trades_df)} Trades as CSV",
            data=csv,
            file_name=f"{selected_strategy}_trades.csv",
            mime="text/csv"
        )
    else:
        st.warning("No trade data available for this strategy")
    
    # Additional insights
    st.markdown("---")
    st.subheader("💡 Insights")
    
    insights = []
    
    if win_rate > 0.6:
        insights.append(f"🎯 **High win rate** ({win_rate*100:.1f}%) suggests good entry signals")
    elif win_rate < 0.4:
        insights.append(f"⚠️ **Low win rate** ({win_rate*100:.1f}%) - consider refining entry criteria")
    
    profit_factor = metrics.get('profit_factor', 0)
    if profit_factor > 2.0:
        insights.append(f"💰 **Excellent profit factor** ({profit_factor:.2f}) - strong risk/reward management")
    elif profit_factor < 1.0:
        insights.append(f"⚠️ **Profit factor below 1.0** ({profit_factor:.2f}) - losing more than winning")
    
    if n_trades < 30:
        insights.append(f"📊 **Limited sample size** ({n_trades} trades) - results may not be statistically significant")
    elif n_trades > 100:
        insights.append(f"✅ **Large sample size** ({n_trades} trades) provides statistical confidence")
    
    if sharpe > 2.0:
        insights.append(f"🌟 **Exceptional Sharpe ratio** ({sharpe:.2f}) - excellent risk-adjusted returns")
    
    if insights:
        for insight in insights:
            st.markdown(f"- {insight}")
    else:
        st.info("Insufficient data for detailed insights")

# Footer
st.markdown("---")
st.markdown("💡 **Tip**: Use filters to find strategies by universe or sort by different metrics!")

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
