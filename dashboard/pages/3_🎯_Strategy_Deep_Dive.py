#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚡🌟💎 NECROZMA DASHBOARD - STRATEGY DEEP DIVE PAGE 💎🌟⚡

Detailed analysis of individual strategies
"""

import streamlit as st
import sys
from pathlib import Path
import pandas as pd

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from dashboard.utils.data_loader import load_all_results, get_strategy_list, get_universe_list
from dashboard.components.charts import (
    create_equity_curve, create_drawdown_chart, create_histogram, create_pie_chart
)
from dashboard.utils.formatters import format_percentage, format_number, format_currency

# Page config
st.set_page_config(page_title="Strategy Deep Dive", page_icon="🎯", layout="wide")

st.title("🎯 Strategy Deep Dive")
st.markdown("Detailed analysis of individual strategy performance")

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

# Strategy selector
st.sidebar.header("🔍 Select Strategy")

# Filter by universe first (optional)
universes = ['All'] + get_universe_list(results)
selected_universe = st.sidebar.selectbox("Filter by Universe", universes)

# Get strategies for selected universe
if selected_universe == 'All':
    filtered_df = strategies_df
else:
    filtered_df = strategies_df[strategies_df['universe_name'] == selected_universe]

if filtered_df.empty:
    st.warning(f"No strategies found for universe: {selected_universe}")
    st.stop()

# Get strategy names
strategy_names = sorted(filtered_df['strategy_name'].unique().tolist())

if not strategy_names:
    st.warning("No strategies available")
    st.stop()

selected_strategy = st.sidebar.selectbox("Select Strategy", strategy_names)

# Get selected strategy data
strategy_data = filtered_df[filtered_df['strategy_name'] == selected_strategy].iloc[0].to_dict()

# Display strategy information
st.header(f"📋 {selected_strategy}")

# Metadata
col1, col2, col3 = st.columns(3)

with col1:
    st.info(f"**Universe**: {strategy_data.get('universe_name', 'N/A')}")
with col2:
    if 'interval' in strategy_data:
        st.info(f"**Interval**: {strategy_data['interval']} min")
with col3:
    if 'lookback' in strategy_data:
        st.info(f"**Lookback**: {strategy_data['lookback']} periods")

st.markdown("---")

# Key metrics
st.header("📊 Performance Metrics")

col1, col2, col3, col4 = st.columns(4)

with col1:
    return_val = strategy_data.get('total_return', 0) * 100
    st.metric(
        "Total Return",
        format_percentage(return_val / 100, decimals=2),
        delta=None
    )

with col2:
    sharpe_val = strategy_data.get('sharpe_ratio', 0)
    st.metric(
        "Sharpe Ratio",
        f"{sharpe_val:.2f}",
        delta="Good" if sharpe_val > 1.0 else "Poor"
    )

with col3:
    win_rate = strategy_data.get('win_rate', 0) * 100
    st.metric(
        "Win Rate",
        format_percentage(win_rate / 100, decimals=1),
        delta=None
    )

with col4:
    max_dd = strategy_data.get('max_drawdown', 0) * 100
    st.metric(
        "Max Drawdown",
        format_percentage(max_dd / 100, decimals=2),
        delta=None
    )

# Second row of metrics
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Number of Trades",
        format_number(strategy_data.get('n_trades', 0), decimals=0)
    )

with col2:
    pf = strategy_data.get('profit_factor', 0)
    st.metric(
        "Profit Factor",
        f"{pf:.2f}",
        delta="Good" if pf > 1.5 else "Fair" if pf > 1.0 else "Poor"
    )

with col3:
    if 'sortino_ratio' in strategy_data:
        st.metric(
            "Sortino Ratio",
            f"{strategy_data['sortino_ratio']:.2f}"
        )

with col4:
    if 'calmar_ratio' in strategy_data:
        st.metric(
            "Calmar Ratio",
            f"{strategy_data['calmar_ratio']:.2f}"
        )

st.markdown("---")

# Trade statistics
st.header("💹 Trade Statistics")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Win/Loss Breakdown")
    
    n_trades = strategy_data.get('n_trades', 0)
    win_rate_val = strategy_data.get('win_rate', 0)
    
    if n_trades > 0:
        wins = int(n_trades * win_rate_val)
        losses = n_trades - wins
        
        fig = create_pie_chart(
            values=[wins, losses],
            labels=['Wins', 'Losses'],
            title=""
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No trade data available")

with col2:
    st.subheader("P&L Statistics")
    
    metrics = []
    
    if 'avg_win' in strategy_data:
        metrics.append(f"**Avg Win**: {format_currency(strategy_data['avg_win'], decimals=2)}")
    if 'avg_loss' in strategy_data:
        metrics.append(f"**Avg Loss**: {format_currency(strategy_data['avg_loss'], decimals=2)}")
    if 'largest_win' in strategy_data:
        metrics.append(f"**Largest Win**: {format_currency(strategy_data['largest_win'], decimals=2)}")
    if 'largest_loss' in strategy_data:
        metrics.append(f"**Largest Loss**: {format_currency(strategy_data['largest_loss'], decimals=2)}")
    if 'expectancy' in strategy_data:
        metrics.append(f"**Expectancy**: {format_currency(strategy_data['expectancy'], decimals=2)}")
    
    if metrics:
        for metric in metrics:
            st.markdown(metric)
    else:
        st.info("No P&L statistics available")

# Visualization note
st.markdown("---")
st.info("📌 **Note**: Detailed equity curves and trade-by-trade analysis require the backtester enhancement (Phase 5). Currently showing summary statistics only.")

# Additional metrics
if 'recovery_factor' in strategy_data:
    st.markdown("---")
    st.header("🔄 Risk Metrics")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Recovery Factor", f"{strategy_data['recovery_factor']:.2f}")
    
    with col2:
        if 'ulcer_index' in strategy_data:
            st.metric("Ulcer Index", f"{strategy_data['ulcer_index']:.2f}")
    
    with col3:
        if 'max_drawdown' in strategy_data and strategy_data['max_drawdown'] > 0:
            mar_ratio = strategy_data.get('total_return', 0) / strategy_data['max_drawdown']
            st.metric("MAR Ratio", f"{mar_ratio:.2f}")

# Footer
st.markdown("---")
st.markdown("💡 **Tip**: Compare multiple strategies by opening them in different browser tabs!")
