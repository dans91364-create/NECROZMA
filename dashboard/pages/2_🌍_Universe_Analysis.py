#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚡🌟💎 NECROZMA DASHBOARD - UNIVERSE ANALYSIS PAGE 💎🌟⚡

Compare performance across 25 universes
"""

import streamlit as st
import sys
from pathlib import Path
import pandas as pd

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from dashboard.utils.data_loader import load_all_results
from dashboard.components.charts import (
    create_heatmap, create_line_chart, create_box_plot, create_scatter_plot
)
from dashboard.components.metrics import (
    calculate_universe_stats, create_universe_matrix
)
from dashboard.components.tables import create_sortable_table
from dashboard.utils.formatters import format_percentage, format_number

# Page config
st.set_page_config(page_title="Universe Analysis", page_icon="🌍", layout="wide")

st.title("🌍 Universe Comparison")
st.markdown("Compare performance across different timeframe configurations")

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

# Universe statistics
st.header("📊 Universe Statistics")

universe_stats = calculate_universe_stats(strategies_df)

if not universe_stats.empty:
    # Display universe comparison table
    display_cols = [col for col in universe_stats.columns if col in [
        'universe_name', 'sharpe_ratio_mean', 'sharpe_ratio_max',
        'total_return_mean', 'total_return_max', 'win_rate_mean',
        'n_trades_mean', 'max_drawdown_mean', 'sharpe_ratio_count'
    ]]
    
    display_df = universe_stats[display_cols].copy()
    
    # Rename columns for readability
    display_df = display_df.rename(columns={
        'universe_name': 'Universe',
        'sharpe_ratio_mean': 'Avg Sharpe',
        'sharpe_ratio_max': 'Max Sharpe',
        'sharpe_ratio_count': 'Strategy Count',
        'total_return_mean': 'Avg Return',
        'total_return_max': 'Max Return',
        'win_rate_mean': 'Avg Win Rate',
        'n_trades_mean': 'Avg Trades',
        'max_drawdown_mean': 'Avg DD'
    })
    
    # Convert percentages
    for col in ['Avg Return', 'Max Return', 'Avg Win Rate', 'Avg DD']:
        if col in display_df.columns:
            display_df[col] = display_df[col] * 100
    
    create_sortable_table(display_df, key="universe_stats_table", height=400)
    
    # Best universe highlight
    if 'Max Sharpe' in display_df.columns:
        best_idx = display_df['Max Sharpe'].idxmax()
        best_universe = display_df.loc[best_idx]
        
        st.success(f"🏆 **Best Universe**: {best_universe['Universe']} (Max Sharpe: {best_universe['Max Sharpe']:.2f})")
    
    # Download button
    csv = display_df.to_csv(index=False)
    st.download_button(
        label="📥 Download Universe Stats as CSV",
        data=csv,
        file_name="universe_statistics.csv",
        mime="text/csv"
    )

st.markdown("---")

# Heatmap visualization
st.header("🔥 Performance Heatmap")

# Create heatmap if interval and lookback data available
if 'interval' in strategies_df.columns and 'lookback' in strategies_df.columns:
    matrix = create_universe_matrix(strategies_df)
    
    if not matrix.empty:
        st.subheader("Sharpe Ratio by Interval × Lookback")
        
        fig = create_heatmap(
            matrix,
            title="",
            x_label="Lookback Period",
            y_label="Interval (minutes)",
            colorscale='RdYlGn'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        st.info("💡 **Interpretation**: Green areas indicate better Sharpe ratios. Look for clusters of high performance.")
    else:
        st.warning("Unable to create heatmap - insufficient interval/lookback data")
else:
    st.warning("Interval and lookback data not available for heatmap")

st.markdown("---")

# Comparison charts
st.header("📈 Comparative Analysis")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Return Distribution by Universe")
    
    # Box plot of returns by universe (top 10 universes)
    if 'universe_name' in strategies_df.columns and 'total_return' in strategies_df.columns:
        top_universes = strategies_df['universe_name'].value_counts().head(10).index
        plot_df = strategies_df[strategies_df['universe_name'].isin(top_universes)].copy()
        plot_df['total_return_pct'] = plot_df['total_return'] * 100
        
        fig = create_box_plot(
            plot_df,
            y='total_return_pct',
            x='universe_name',
            title=""
        )
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Return data not available")

with col2:
    st.subheader("Trades vs Return")
    
    # Scatter plot: number of trades vs return
    if 'n_trades' in strategies_df.columns and 'total_return' in strategies_df.columns:
        plot_df = strategies_df.copy()
        plot_df['total_return_pct'] = plot_df['total_return'] * 100
        
        fig = create_scatter_plot(
            plot_df.head(100),  # Limit to 100 for performance
            x='n_trades',
            y='total_return_pct',
            title="",
            color='sharpe_ratio' if 'sharpe_ratio' in plot_df.columns else None,
            hover_name='strategy_name' if 'strategy_name' in plot_df.columns else None
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Trade count data not available")

# Performance by lookback
if 'lookback' in strategies_df.columns and 'sharpe_ratio' in strategies_df.columns:
    st.subheader("Performance by Lookback Period")
    
    lookback_perf = strategies_df.groupby('lookback').agg({
        'sharpe_ratio': 'mean',
        'total_return': 'mean',
        'win_rate': 'mean'
    }).reset_index()
    
    lookback_perf['total_return'] = lookback_perf['total_return'] * 100
    lookback_perf['win_rate'] = lookback_perf['win_rate'] * 100
    
    fig = create_line_chart(
        lookback_perf,
        x='lookback',
        y='sharpe_ratio',
        title="Average Sharpe Ratio by Lookback Period"
    )
    st.plotly_chart(fig, use_container_width=True)

# Performance by interval
if 'interval' in strategies_df.columns and 'sharpe_ratio' in strategies_df.columns:
    st.subheader("Performance by Interval")
    
    interval_perf = strategies_df.groupby('interval').agg({
        'sharpe_ratio': 'mean',
        'total_return': 'mean',
        'win_rate': 'mean'
    }).reset_index()
    
    interval_perf['total_return'] = interval_perf['total_return'] * 100
    interval_perf['win_rate'] = interval_perf['win_rate'] * 100
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig = create_line_chart(
            interval_perf,
            x='interval',
            y='sharpe_ratio',
            title="Average Sharpe by Interval"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = create_line_chart(
            interval_perf,
            x='interval',
            y='total_return',
            title="Average Return by Interval"
        )
        st.plotly_chart(fig, use_container_width=True)

# Footer
st.markdown("---")
st.markdown("💡 **Tip**: Use the heatmap to identify optimal interval/lookback combinations, then explore those universes in the Strategy Deep Dive page!")
