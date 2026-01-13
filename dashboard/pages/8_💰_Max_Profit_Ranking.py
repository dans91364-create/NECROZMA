#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚡🌟💎 NECROZMA DASHBOARD - MAX PROFIT RANKING PAGE 💎🌟⚡

Multi-perspective profit analysis across different profit metrics
"""

import streamlit as st
import sys
from pathlib import Path
import pandas as pd
import numpy as np

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from dashboard.utils.data_loader import load_all_results
from dashboard.utils.formatters import format_percentage, format_number

# Page config
st.set_page_config(page_title="Max Profit Ranking", page_icon="💰", layout="wide")

st.title("💰 Maximum Profit Rankings")
st.markdown("Analyze strategies from 5 different profit-focused perspectives")

# Information box
st.info("""
📌 **Five Profit Perspectives**

Different profit metrics reveal different aspects of strategy quality:

1. **Total Return** - Absolute performance over the entire backtest period
2. **Largest Single Win** - Maximum profit from a single trade (upside potential)
3. **Average Win Size** - Consistency of profitable trades
4. **Profit Factor** - Ratio of total wins to total losses (efficiency)
5. **Expectancy** - Expected profit per trade (statistical edge)

**Why Multiple Views Matter:**
- Total return shows overall performance
- Largest win reveals maximum upside potential  
- Average win indicates trade quality
- Profit factor measures win/loss efficiency
- Expectancy shows per-trade edge

Use these perspectives to understand different aspects of profitability!
""")

# Load data
with st.spinner("Loading backtest results..."):
    results = load_all_results()

if results['metadata']['total_strategies'] == 0:
    st.error("❌ No backtest results found. Please run backtests first.")
    st.stop()

strategies_df = results.get('strategies_df')

if strategies_df is None or strategies_df.empty:
    st.error("❌ No strategy data available")
    st.stop()

st.success(f"✅ Loaded {len(strategies_df)} strategies from {results['metadata']['total_universes']} universes")

# Create tabs for different profit perspectives
tabs = st.tabs([
    "📈 Total Return",
    "🚀 Largest Single Win",
    "⭐ Average Win Size",
    "💎 Profit Factor",
    "🎯 Expectancy"
])

# Helper function to create ranking table
def create_ranking_table(df, metric_col, metric_name, top_n=20):
    """Create a ranking table for a specific metric"""
    
    if metric_col not in df.columns:
        st.warning(f"⚠️ '{metric_col}' column not found in data")
        return None
    
    # Remove invalid values
    valid_df = df[df[metric_col].notna()].copy()
    
    # For profit factor, filter out unrealistic values (> 100)
    if metric_col == 'profit_factor':
        valid_df = valid_df[valid_df[metric_col] <= 100].copy()
    
    # Sort and get top N
    top_df = valid_df.nlargest(top_n, metric_col).copy()
    
    if top_df.empty:
        st.warning(f"No valid data for {metric_name}")
        return None
    
    # Select display columns
    display_cols = ['strategy_name', metric_col]
    
    # Add key metrics if available
    for col in ['total_return', 'sharpe_ratio', 'win_rate', 'max_drawdown', 'n_trades', 'profit_factor', 'expectancy']:
        if col in top_df.columns and col != metric_col:
            display_cols.append(col)
    
    display_df = top_df[display_cols].copy()
    
    # Format columns for display
    if 'total_return' in display_df.columns:
        display_df['return_pct'] = (display_df['total_return'] * 100).round(2)
        display_df = display_df.drop('total_return', axis=1)
    
    if 'win_rate' in display_df.columns:
        display_df['win_rate_pct'] = (display_df['win_rate'] * 100).round(2)
        display_df = display_df.drop('win_rate', axis=1)
    
    if 'max_drawdown' in display_df.columns:
        display_df['drawdown_pct'] = (display_df['max_drawdown'] * 100).round(2)
        display_df = display_df.drop('max_drawdown', axis=1)
    
    # Round numeric columns
    for col in display_df.columns:
        if col != 'strategy_name' and pd.api.types.is_numeric_dtype(display_df[col]):
            display_df[col] = display_df[col].round(3)
    
    # Highlight best
    best = top_df.iloc[0]
    st.success(f"""
    🥇 **Best by {metric_name}**: `{best['strategy_name']}`
    - **{metric_name}**: {best[metric_col]:.4f}
    - Sharpe: {best.get('sharpe_ratio', 0):.2f}
    - Return: {best.get('total_return', 0) * 100:.2f}%
    - Trades: {best.get('n_trades', 0):.0f}
    """)
    
    # Display table
    st.dataframe(display_df, use_container_width=True, height=500, hide_index=True)
    
    # Download button
    csv = display_df.to_csv(index=False)
    st.download_button(
        label=f"📥 Download Top {top_n} by {metric_name}",
        data=csv,
        file_name=f"top_{metric_col}.csv",
        mime="text/csv",
        key=f"download_{metric_col}"
    )
    
    return display_df


# Tab 1: Total Return
with tabs[0]:
    st.header("📈 Top 20 by Total Return")
    st.markdown("Strategies with the highest absolute return percentage")
    
    create_ranking_table(strategies_df, 'total_return', 'Total Return')


# Tab 2: Largest Single Win
with tabs[1]:
    st.header("🚀 Top 20 by Largest Single Win")
    st.markdown("Strategies with the biggest individual winning trade (in pips)")
    
    if 'largest_win' in strategies_df.columns:
        create_ranking_table(strategies_df, 'largest_win', 'Largest Win (pips)')
    else:
        st.warning("⚠️ 'largest_win' data not available. This requires detailed trade tracking.")
        st.info("""
        **To enable this metric:**
        - Ensure backtester tracks individual trade results
        - Re-run backtests with detailed trade logging enabled
        """)


# Tab 3: Average Win Size
with tabs[2]:
    st.header("⭐ Top 20 by Average Win Size")
    st.markdown("Strategies with the most consistent winning trades")
    
    if 'avg_win_size' in strategies_df.columns:
        create_ranking_table(strategies_df, 'avg_win_size', 'Average Win Size (pips)')
    elif 'avg_win' in strategies_df.columns:
        create_ranking_table(strategies_df, 'avg_win', 'Average Win (pips)')
    else:
        st.warning("⚠️ 'avg_win_size' or 'avg_win' data not available.")
        st.info("""
        **To enable this metric:**
        - Ensure backtester calculates average win size
        - Check that win/loss statistics are tracked
        """)


# Tab 4: Profit Factor
with tabs[3]:
    st.header("💎 Top 20 by Profit Factor")
    st.markdown("Ratio of total winning trades to total losing trades (higher = better)")
    
    st.info("📌 Profit Factor = Total Win $ / Total Loss $ (values > 100 filtered as unrealistic)")
    
    if 'profit_factor' in strategies_df.columns:
        create_ranking_table(strategies_df, 'profit_factor', 'Profit Factor')
    else:
        st.warning("⚠️ 'profit_factor' data not available.")


# Tab 5: Expectancy
with tabs[4]:
    st.header("🎯 Top 20 by Expectancy")
    st.markdown("Expected profit per trade - the statistical edge")
    
    st.info("📌 Expectancy = (Win Rate × Avg Win) - (Loss Rate × Avg Loss)")
    
    if 'expectancy' in strategies_df.columns:
        create_ranking_table(strategies_df, 'expectancy', 'Expectancy (pips per trade)')
    else:
        st.warning("⚠️ 'expectancy' data not available.")
        st.info("""
        **To enable this metric:**
        - Ensure backtester calculates expectancy
        - Formula: (Win% × AvgWin) - (Loss% × AvgLoss)
        """)


# Summary statistics
st.markdown("---")
st.header("📊 Summary Statistics Across All Strategies")

col1, col2, col3, col4 = st.columns(4)

with col1:
    if 'total_return' in strategies_df.columns:
        avg_return = strategies_df['total_return'].mean() * 100
        max_return = strategies_df['total_return'].max() * 100
        st.metric("Avg Return", f"{avg_return:.2f}%")
        st.caption(f"Max: {max_return:.2f}%")

with col2:
    if 'profit_factor' in strategies_df.columns:
        # Filter realistic values
        pf_valid = strategies_df[strategies_df['profit_factor'] <= 100]['profit_factor']
        avg_pf = pf_valid.mean()
        max_pf = pf_valid.max()
        st.metric("Avg Profit Factor", f"{avg_pf:.2f}")
        st.caption(f"Max: {max_pf:.2f}")

with col3:
    if 'expectancy' in strategies_df.columns:
        avg_exp = strategies_df['expectancy'].mean()
        max_exp = strategies_df['expectancy'].max()
        st.metric("Avg Expectancy", f"{avg_exp:.2f} pips")
        st.caption(f"Max: {max_exp:.2f} pips")

with col4:
    if 'largest_win' in strategies_df.columns:
        max_win = strategies_df['largest_win'].max()
        avg_max_win = strategies_df['largest_win'].mean()
        st.metric("Best Single Win", f"{max_win:.2f} pips")
        st.caption(f"Avg: {avg_max_win:.2f} pips")


# Footer insights
st.markdown("---")
st.header("💡 Interpretation Guide")

st.markdown("""
### 🎯 How to Use These Rankings

**Total Return**
- Shows overall performance
- Best for identifying most profitable strategies
- Consider alongside Sharpe ratio for risk-adjusted view

**Largest Single Win**
- Indicates upside potential
- Useful for understanding maximum profit ceiling
- High values may indicate rare but lucrative setups

**Average Win Size**
- Shows consistency of winning trades
- Higher values = more reliable wins
- Compare with average loss size for risk/reward

**Profit Factor**
- Measures efficiency (win $ / loss $)
- > 2.0 is typically excellent
- > 1.5 is good, < 1.0 means losing strategy

**Expectancy**
- Expected profit per trade
- Positive = profitable strategy on average
- Higher is better, accounts for win rate and sizes

### 🚀 Next Steps

1. **Cross-reference**: Check if strategies appear in multiple top-20 lists
2. **Deep Dive**: Analyze top performers with Strategy Deep Dive page
3. **Risk Check**: Verify max drawdown on high-return strategies
4. **Universe Analysis**: See if winners cluster in specific timeframes
""")
