#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚡🌟💎 NECROZMA DASHBOARD - STRATEGY EXPLORER PAGE 💎🌟⚡

Search, filter, and compare strategies side-by-side
Enhanced for batch processing data format
"""

import streamlit as st
import sys
from pathlib import Path
import pandas as pd

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from dashboard.utils.data_loader import load_all_results, detect_data_format, extract_strategy_template
from dashboard.components.charts import create_comparison_chart, create_scatter_plot
from dashboard.components.filters import create_search_filter
from dashboard.utils.formatters import format_percentage, format_number

# Page config
st.set_page_config(page_title="Strategy Explorer", page_icon="🎯", layout="wide")

st.title("🎯 Strategy Explorer")
st.markdown("Search, filter, and compare up to 5 strategies side-by-side")

# Load data
with st.spinner("Loading backtest results..."):
    results = load_all_results()
    data_format = detect_data_format()

if results['total_strategies'] == 0:
    st.error("❌ No backtest results found.")
    st.stop()

strategies_df = results.get('strategies_df')

if strategies_df is None or strategies_df.empty:
    st.error("❌ No strategy data available")
    st.stop()

# Add template column
if 'strategy_name' in strategies_df.columns:
    strategies_df['template'] = strategies_df['strategy_name'].apply(extract_strategy_template)

st.markdown("---")

# Search and Filter
st.header("🔍 Search & Filter")

col1, col2 = st.columns([2, 1])

with col1:
    search_term = st.text_input("Search by strategy name", placeholder="Enter keywords...")

with col2:
    # Sort options
    sort_by = st.selectbox(
        "Sort By",
        ['sharpe_ratio', 'total_return', 'win_rate', 'profit_factor', 'net_pnl'],
        index=0
    )

# Apply search filter
filtered_df = strategies_df.copy()

if search_term:
    filtered_df = filtered_df[
        filtered_df['strategy_name'].str.contains(search_term, case=False, na=False)
    ]

# Sort
if sort_by in filtered_df.columns:
    filtered_df = filtered_df.sort_values(sort_by, ascending=False)

st.info(f"📊 Found {len(filtered_df)} strategies")

st.markdown("---")

# Display top matches
st.header("📋 Search Results")

if not filtered_df.empty:
    # Display top 50
    display_cols = ['strategy_name']
    
    for col in ['lot_size', 'sharpe_ratio', 'total_return', 'win_rate', 'max_drawdown', 
                'profit_factor', 'n_trades', 'net_pnl']:
        if col in filtered_df.columns:
            display_cols.append(col)
    
    display_df = filtered_df[display_cols].head(50).copy()
    
    # Format percentages
    for col in ['total_return', 'win_rate', 'max_drawdown']:
        if col in display_df.columns:
            if display_df[col].abs().max() <= 1:
                display_df[col] = (display_df[col] * 100).round(2)
    
    st.dataframe(display_df, use_container_width=True, height=400)
else:
    st.warning("No strategies match your search criteria")
    st.stop()

st.markdown("---")

# Strategy Comparison
st.header("📊 Compare Strategies")

st.info("Select up to 5 strategies to compare side-by-side")

# Multi-select for comparison
available_strategies = filtered_df['strategy_name'].head(100).tolist()

selected_strategies = st.multiselect(
    "Select strategies to compare (max 5)",
    options=available_strategies,
    max_selections=5,
    default=available_strategies[:min(3, len(available_strategies))]
)

if selected_strategies and len(selected_strategies) > 0:
    comparison_df = filtered_df[filtered_df['strategy_name'].isin(selected_strategies)]
    
    st.subheader(f"Comparing {len(selected_strategies)} Strategies")
    
    # Display detailed comparison table
    detail_cols = ['strategy_name']
    
    for col in ['lot_size', 'template', 'sharpe_ratio', 'sortino_ratio', 'calmar_ratio',
                'total_return', 'win_rate', 'max_drawdown', 'profit_factor', 
                'n_trades', 'avg_win', 'avg_loss', 'expectancy', 'net_pnl', 'total_commission']:
        if col in comparison_df.columns:
            detail_cols.append(col)
    
    detail_df = comparison_df[detail_cols].copy()
    
    # Format for display
    for col in ['total_return', 'win_rate', 'max_drawdown']:
        if col in detail_df.columns:
            if detail_df[col].abs().max() <= 1:
                detail_df[col] = (detail_df[col] * 100).round(2)
    
    # Remove duplicate columns before transpose
    detail_df = detail_df.loc[:, ~detail_df.columns.duplicated()]
    
    # Transpose for easier comparison
    detail_df_T = detail_df.set_index('strategy_name').T
    st.dataframe(detail_df_T, use_container_width=True)
    
    st.markdown("---")
    
    # Visual comparison
    st.subheader("📈 Visual Comparison")
    
    # Select metrics to compare
    metrics_to_compare = []
    for metric in ['sharpe_ratio', 'total_return', 'win_rate', 'max_drawdown', 
                   'profit_factor', 'n_trades']:
        if metric in comparison_df.columns:
            metrics_to_compare.append(metric)
    
    if metrics_to_compare:
        selected_metrics = st.multiselect(
            "Select metrics to visualize",
            options=metrics_to_compare,
            default=metrics_to_compare[:min(4, len(metrics_to_compare))]
        )
        
        if selected_metrics:
            try:
                fig = create_comparison_chart(
                    comparison_df,
                    strategies=selected_strategies,
                    metrics=selected_metrics,
                    title="Strategy Metrics Comparison"
                )
                st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                st.error(f"Error creating comparison chart: {e}")
    
    st.markdown("---")
    
    # Parameter breakdown
    st.subheader("🔧 Parameter Breakdown")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if 'template' in comparison_df.columns:
            st.write("**Strategy Templates:**")
            template_counts = comparison_df['template'].value_counts()
            st.dataframe(template_counts, use_container_width=True)
    
    with col2:
        if 'lot_size' in comparison_df.columns:
            st.write("**Lot Sizes:**")
            lot_counts = comparison_df['lot_size'].value_counts()
            st.dataframe(lot_counts, use_container_width=True)
    
    # Export comparison
    st.markdown("---")
    st.subheader("💾 Export Comparison")
    
    csv = detail_df.to_csv(index=False)
    st.download_button(
        label="📥 Download Comparison as CSV",
        data=csv,
        file_name="strategy_comparison.csv",
        mime="text/csv"
    )

else:
    st.info("👆 Select strategies above to compare")

st.markdown("---")

# Individual Strategy Details
st.header("📝 Individual Strategy Details")

selected_strategy = st.selectbox(
    "Select a strategy to view details",
    options=available_strategies,
    index=0 if available_strategies else None
)

if selected_strategy:
    strategy_data = strategies_df[strategies_df['strategy_name'] == selected_strategy].iloc[0]
    
    st.subheader(f"Details for: {selected_strategy}")
    
    # Show all available metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if 'sharpe_ratio' in strategy_data:
            st.metric("Sharpe Ratio", f"{strategy_data['sharpe_ratio']:.2f}")
        if 'sortino_ratio' in strategy_data:
            st.metric("Sortino Ratio", f"{strategy_data['sortino_ratio']:.2f}")
    
    with col2:
        if 'total_return' in strategy_data:
            ret = strategy_data['total_return']
            if abs(ret) <= 1:
                ret = ret * 100
            st.metric("Total Return", f"{ret:.2f}%")
        if 'win_rate' in strategy_data:
            wr = strategy_data['win_rate']
            if wr <= 1:
                wr = wr * 100
            st.metric("Win Rate", f"{wr:.2f}%")
    
    with col3:
        if 'max_drawdown' in strategy_data:
            dd = abs(strategy_data['max_drawdown'])
            if dd <= 1:
                dd = dd * 100
            st.metric("Max Drawdown", f"{dd:.2f}%")
        if 'profit_factor' in strategy_data:
            st.metric("Profit Factor", f"{strategy_data['profit_factor']:.2f}")
    
    with col4:
        if 'n_trades' in strategy_data:
            st.metric("Number of Trades", int(strategy_data['n_trades']))
        if 'net_pnl' in strategy_data:
            st.metric("Net PnL", f"${strategy_data['net_pnl']:,.2f}")
    
    # Additional details
    st.subheader("Additional Information")
    
    info_data = {}
    
    for col in ['template', 'lot_size', 'calmar_ratio', 'avg_win', 'avg_loss', 
                'expectancy', 'gross_pnl', 'total_commission']:
        if col in strategy_data and pd.notna(strategy_data[col]):
            info_data[col.replace('_', ' ').title()] = strategy_data[col]
    
    if info_data:
        info_df = pd.DataFrame([info_data]).T
        info_df.columns = ['Value']
        st.dataframe(info_df, use_container_width=True)

# Footer
st.markdown("---")
st.markdown("💡 **Tip**: Use search and filters to find strategies, then compare them to identify the best performers")
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
