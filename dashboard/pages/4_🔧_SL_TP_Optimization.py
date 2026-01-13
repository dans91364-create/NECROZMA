#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚡🌟💎 NECROZMA DASHBOARD - SL/TP OPTIMIZATION PAGE 💎🌟⚡

Analyze and optimize stop-loss and take-profit parameters
"""

import streamlit as st
import sys
from pathlib import Path
import pandas as pd
import numpy as np

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from dashboard.utils.data_loader import load_all_results
from dashboard.components.charts import create_heatmap, create_scatter_plot, create_bar_chart
from dashboard.components.metrics import calculate_sl_tp_matrix
from dashboard.utils.formatters import format_percentage

# Page config
st.set_page_config(page_title="SL/TP Optimization", page_icon="🔧", layout="wide")

st.title("🔧 SL/TP Optimization Matrix")
st.markdown("Find optimal stop-loss and take-profit parameters")

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

# Information about SL/TP extraction
st.info("""
📌 **Note**: This page analyzes stop-loss (SL) and take-profit (TP) parameters. 
The current implementation extracts these from strategy names if available.
For full SL/TP optimization, ensure strategies are named with SL/TP values (e.g., 'strategy_sl_20_tp_40').
""")

# Try to create SL/TP matrix
matrix = calculate_sl_tp_matrix(strategies_df)

if not matrix.empty:
    st.header("🔥 SL/TP Performance Heatmap")
    
    st.subheader("Average Return by SL × TP Configuration")
    
    # Convert to percentage
    matrix_pct = matrix * 100
    
    fig = create_heatmap(
        matrix_pct,
        title="",
        x_label="Take Profit (pips)",
        y_label="Stop Loss (pips)",
        colorscale='RdYlGn'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Best combinations
    st.header("🏆 Top SL/TP Combinations")
    
    # Flatten matrix and get top combinations
    flat_data = []
    for sl in matrix.index:
        for tp in matrix.columns:
            flat_data.append({
                'SL (pips)': sl,
                'TP (pips)': tp,
                'Return (%)': matrix.loc[sl, tp] * 100,
                'Risk/Reward': tp / sl if sl > 0 else 0
            })
    
    combo_df = pd.DataFrame(flat_data).sort_values('Return (%)', ascending=False)
    
    # Display top 10
    st.dataframe(combo_df.head(10), use_container_width=True, height=400)
    
    # Download button
    csv = combo_df.to_csv(index=False)
    st.download_button(
        label="📥 Download All Combinations as CSV",
        data=csv,
        file_name="sl_tp_combinations.csv",
        mime="text/csv"
    )
    
    st.markdown("---")
    
    # Additional analysis
    st.header("📊 Parameter Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Risk/Reward vs Return")
        
        # Filter out infinite values
        plot_df = combo_df[combo_df['Risk/Reward'] < 10].copy()
        
        fig = create_scatter_plot(
            plot_df,
            x='Risk/Reward',
            y='Return (%)',
            title="",
            color='SL (pips)',
            size=None
        )
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("""
        **Interpretation**: 
        - Higher risk/reward ratios (TP/SL) may not always yield better returns
        - Look for the sweet spot balancing risk and reward
        """)
    
    with col2:
        st.subheader("Performance by Risk/Reward Ratio")
        
        # Bin by risk/reward ratio
        plot_df['RR_bin'] = pd.cut(plot_df['Risk/Reward'], bins=5)
        rr_perf = plot_df.groupby('RR_bin', observed=True)['Return (%)'].mean().reset_index()
        rr_perf['RR_bin'] = rr_perf['RR_bin'].astype(str)
        
        fig = create_bar_chart(
            rr_perf,
            x='RR_bin',
            y='Return (%)',
            title=""
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Insights
    st.header("💡 Insights")
    
    # Find best combination
    best_idx = combo_df['Return (%)'].idxmax()
    best_combo = combo_df.loc[best_idx]
    
    st.success(f"""
    **Best Combination Found**: 
    - SL: {best_combo['SL (pips)']} pips
    - TP: {best_combo['TP (pips)']} pips
    - Risk/Reward: {best_combo['Risk/Reward']:.2f}
    - Return: {best_combo['Return (%)']:.2f}%
    """)
    
    # Optimal risk/reward
    optimal_rr = combo_df.loc[combo_df['Return (%)'].idxmax(), 'Risk/Reward']
    st.info(f"**Optimal Risk/Reward Ratio**: {optimal_rr:.2f} (TP/SL)")
    
    # Statistics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        avg_rr = combo_df[combo_df['Risk/Reward'] < 10]['Risk/Reward'].mean()
        st.metric("Average R/R Ratio", f"{avg_rr:.2f}")
    
    with col2:
        best_sl = combo_df.loc[combo_df['Return (%)'].idxmax(), 'SL (pips)']
        st.metric("Most Profitable SL", f"{best_sl:.0f} pips")
    
    with col3:
        best_tp = combo_df.loc[combo_df['Return (%)'].idxmax(), 'TP (pips)']
        st.metric("Most Profitable TP", f"{best_tp:.0f} pips")

else:
    st.warning("""
    ⚠️ **SL/TP data not found in strategy names.**
    
    To use this page effectively:
    1. Ensure strategies are named with SL/TP parameters (e.g., 'momentum_sl_20_tp_40')
    2. Or implement explicit SL/TP tracking in the backtester
    3. Re-run backtests with updated naming convention
    
    **Alternative**: You can manually analyze the effect of different SL/TP values by:
    - Running multiple backtests with different parameters
    - Naming strategies accordingly
    - Regenerating this dashboard
    """)
    
    # Show summary statistics instead
    st.header("📊 Current Strategy Performance")
    
    st.markdown("While SL/TP optimization data is unavailable, here's an overview of your strategies:")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        avg_return = strategies_df.get('total_return', pd.Series([0])).mean() * 100
        st.metric("Average Return", format_percentage(avg_return / 100))
    
    with col2:
        avg_sharpe = strategies_df.get('sharpe_ratio', pd.Series([0])).mean()
        st.metric("Average Sharpe", f"{avg_sharpe:.2f}")
    
    with col3:
        avg_trades = strategies_df.get('n_trades', pd.Series([0])).mean()
        st.metric("Average Trades", f"{avg_trades:.0f}")

# Footer
st.markdown("---")
st.markdown("""
💡 **Recommendations**:
- Test multiple SL/TP combinations systematically
- Consider market volatility when setting SL/TP
- Higher risk/reward isn't always better - balance is key
- Account for spread and slippage in real trading
""")
