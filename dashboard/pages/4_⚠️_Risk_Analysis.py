#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚡🌟💎 NECROZMA DASHBOARD - RISK ANALYSIS PAGE 💎🌟⚡

Analyze risk-adjusted returns and drawdowns
Enhanced for batch processing data format
"""

import streamlit as st
import sys
from pathlib import Path
import pandas as pd

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from dashboard.utils.data_loader import load_all_results, detect_data_format
from dashboard.components.charts import (
    create_scatter_plot, create_distribution_chart, create_box_plot
)
from dashboard.components.metrics import (
    identify_efficient_frontier, calculate_risk_metrics
)
from dashboard.components.filters import create_parquet_filters, show_filter_summary
from dashboard.utils.formatters import format_percentage

# Page config
st.set_page_config(page_title="Risk Analysis", page_icon="⚠️", layout="wide")

st.title("⚠️ Risk Analysis")
st.markdown("Analyze risk-adjusted returns, drawdowns, and risk tiers")

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

# Apply filters
filtered_df = strategies_df.copy()
if data_format == 'parquet':
    filters = create_parquet_filters(strategies_df)
    
    # Apply filtering
    if 'lot_size' in filters and filters['lot_size']:
        filtered_df = filtered_df[filtered_df['lot_size'].isin(filters['lot_size'])]

show_filter_summary(len(strategies_df), len(filtered_df))

st.markdown("---")

# Risk metrics summary
st.header("📊 Risk Metrics Summary")

risk_metrics = calculate_risk_metrics(filtered_df)

if risk_metrics:
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if 'avg_sharpe' in risk_metrics:
            st.metric("Average Sharpe", f"{risk_metrics['avg_sharpe']:.2f}")
    
    with col2:
        if 'avg_sortino' in risk_metrics:
            st.metric("Average Sortino", f"{risk_metrics['avg_sortino']:.2f}")
    
    with col3:
        if 'avg_drawdown' in risk_metrics:
            dd = risk_metrics['avg_drawdown']
            if abs(dd) > 1:  # Already percentage
                st.metric("Average Drawdown", f"{dd:.2f}%")
            else:
                st.metric("Average Drawdown", format_percentage(dd))
    
    with col4:
        if 'max_drawdown' in risk_metrics:
            dd = risk_metrics['max_drawdown']
            if abs(dd) > 1:
                st.metric("Maximum Drawdown", f"{dd:.2f}%")
            else:
                st.metric("Maximum Drawdown", format_percentage(dd))

    # Additional metrics if available
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if 'avg_calmar' in risk_metrics:
            st.metric("Average Calmar", f"{risk_metrics['avg_calmar']:.2f}")

st.markdown("---")

# Risk Tier Classification
st.header("🎯 Risk Tier Classification")

if 'max_drawdown' in filtered_df.columns and 'sharpe_ratio' in filtered_df.columns:
    # Classify strategies into risk tiers
    filtered_df['dd_abs'] = filtered_df['max_drawdown'].abs()
    if filtered_df['dd_abs'].max() <= 1:
        filtered_df['dd_abs'] = filtered_df['dd_abs'] * 100
    
    def classify_risk(row):
        dd = row['dd_abs']
        sharpe = row.get('sharpe_ratio', 0)
        
        if dd < 10 and sharpe > 1.5:
            return 'Low Risk'
        elif dd < 20 and sharpe > 1.0:
            return 'Medium Risk'
        else:
            return 'High Risk'
    
    filtered_df['risk_tier'] = filtered_df.apply(classify_risk, axis=1)
    
    # Show distribution
    risk_counts = filtered_df['risk_tier'].value_counts()
    
    col1, col2, col3 = st.columns(3)
    
    for idx, (tier, col) in enumerate(zip(['Low Risk', 'Medium Risk', 'High Risk'], [col1, col2, col3])):
        count = risk_counts.get(tier, 0)
        pct = (count / len(filtered_df) * 100) if len(filtered_df) > 0 else 0
        
        with col:
            st.metric(tier, count, delta=f"{pct:.1f}%")

st.markdown("---")

# Return vs Risk scatter
st.header("📈 Risk-Return Analysis")

col1, col2 = st.columns(2)

with col1:
    if 'max_drawdown' in filtered_df.columns and 'sharpe_ratio' in filtered_df.columns:
        st.subheader("Sharpe Ratio vs Max Drawdown")
        
        plot_df = filtered_df.copy()
        plot_df['dd_pct'] = plot_df['max_drawdown'].abs()
        if plot_df['dd_pct'].max() <= 1:
            plot_df['dd_pct'] = plot_df['dd_pct'] * 100
        
        fig = create_scatter_plot(
            plot_df.head(500),
            x='dd_pct',
            y='sharpe_ratio',
            title="",
            color='risk_tier' if 'risk_tier' in plot_df else None,
            size='n_trades' if 'n_trades' in plot_df else None,
            hover_name='strategy_name' if 'strategy_name' in plot_df else None
        )
        
        fig.update_layout(
            xaxis_title="Maximum Drawdown (%)",
            yaxis_title="Sharpe Ratio"
        )
        st.plotly_chart(fig, use_container_width=True)
        
        st.info("💡 **Target**: Upper-left quadrant (low drawdown, high Sharpe)")

with col2:
    if 'sortino_ratio' in filtered_df.columns and 'calmar_ratio' in filtered_df.columns:
        st.subheader("Sortino vs Calmar Ratio")
        
        fig = create_scatter_plot(
            filtered_df.head(500),
            x='calmar_ratio',
            y='sortino_ratio',
            title="",
            color='sharpe_ratio',
            hover_name='strategy_name' if 'strategy_name' in filtered_df else None
        )
        
        fig.update_layout(
            xaxis_title="Calmar Ratio",
            yaxis_title="Sortino Ratio"
        )
        st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# Distribution Analysis
st.header("📊 Risk Metric Distributions")

col1, col2, col3 = st.columns(3)

with col1:
    if 'max_drawdown' in filtered_df.columns:
        st.subheader("Max Drawdown Distribution")
        dd_data = filtered_df['max_drawdown'].abs()
        if dd_data.max() <= 1:
            dd_data = dd_data * 100
        
        fig = create_distribution_chart(
            dd_data.dropna(),
            title="",
            x_label="Max Drawdown (%)",
            show_stats=True
        )
        st.plotly_chart(fig, use_container_width=True)

with col2:
    if 'sharpe_ratio' in filtered_df.columns:
        st.subheader("Sharpe Ratio Distribution")
        
        fig = create_distribution_chart(
            filtered_df['sharpe_ratio'].dropna(),
            title="",
            x_label="Sharpe Ratio",
            show_stats=True
        )
        st.plotly_chart(fig, use_container_width=True)

with col3:
    if 'sortino_ratio' in filtered_df.columns:
        st.subheader("Sortino Ratio Distribution")
        
        # Filter extreme values for better visualization
        sortino_data = filtered_df['sortino_ratio'].dropna()
        sortino_data = sortino_data[sortino_data < sortino_data.quantile(0.95)]
        
        fig = create_distribution_chart(
            sortino_data,
            title="",
            x_label="Sortino Ratio",
            show_stats=True
        )
        st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# Efficient Frontier
st.header("🎯 Efficient Frontier")

if 'max_drawdown' in filtered_df.columns and 'total_return' in filtered_df.columns:
    efficient = identify_efficient_frontier(filtered_df)
    
    if not efficient.empty:
        st.subheader(f"Efficient Frontier Strategies ({len(efficient)} found)")
        
        # Display table
        display_cols = ['strategy_name', 'sharpe_ratio', 'total_return', 'max_drawdown', 'win_rate']
        available_cols = [col for col in display_cols if col in efficient.columns]
        
        display_df = efficient[available_cols].copy()
        
        # Format percentages
        for col in ['total_return', 'max_drawdown', 'win_rate']:
            if col in display_df.columns:
                if display_df[col].abs().max() <= 1:
                    display_df[col] = (display_df[col] * 100).round(2)
        
        st.dataframe(display_df, use_container_width=True)
        
        # Visualize frontier
        plot_df = efficient.copy()
        plot_df['dd_pct'] = plot_df['max_drawdown'].abs()
        plot_df['return_pct'] = plot_df['total_return']
        
        if plot_df['dd_pct'].max() <= 1:
            plot_df['dd_pct'] = plot_df['dd_pct'] * 100
        if plot_df['return_pct'].abs().max() <= 1:
            plot_df['return_pct'] = plot_df['return_pct'] * 100
        
        fig = create_scatter_plot(
            plot_df,
            x='dd_pct',
            y='return_pct',
            title="Efficient Frontier: Return vs Drawdown",
            color='sharpe_ratio',
            hover_name='strategy_name'
        )
        
        fig.update_layout(
            xaxis_title="Maximum Drawdown (%)",
            yaxis_title="Total Return (%)"
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No efficient frontier strategies identified")

# Footer
st.markdown("---")
st.markdown("💡 **Insight**: Focus on strategies with high risk-adjusted returns (Sharpe > 1.5) and manageable drawdowns (< 20%)")

st.markdown("---")

# Efficient Frontier
st.header("🎯 Efficient Frontier")

efficient = identify_efficient_frontier(strategies_df)

if not efficient.empty:
    st.subheader("Strategies on the Efficient Frontier")
    
    st.markdown("""
    The **efficient frontier** represents strategies that offer the best return for a given level of risk.
    These strategies dominate others at similar risk levels.
    """)
    
    # Plot efficient frontier
    plot_df = efficient.copy()
    plot_df['total_return_pct'] = plot_df['total_return'] * 100
    plot_df['max_drawdown_pct'] = plot_df['max_drawdown'] * 100
    
    fig = create_scatter_plot(
        plot_df,
        x='max_drawdown_pct',
        y='total_return_pct',
        title="Efficient Frontier Strategies",
        color='sharpe_ratio' if 'sharpe_ratio' in plot_df else None,
        hover_name='strategy_name' if 'strategy_name' in plot_df else None
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Display table
    display_cols = ['strategy_name', 'universe_name', 'sharpe_ratio', 
                   'total_return_pct', 'max_drawdown_pct', 'n_trades']
    available_cols = [col for col in display_cols if col in plot_df.columns]
    
    if available_cols:
        display_df = plot_df[available_cols].copy()
        display_df = display_df.rename(columns={
            'strategy_name': 'Strategy',
            'universe_name': 'Universe',
            'sharpe_ratio': 'Sharpe',
            'total_return_pct': 'Return (%)',
            'max_drawdown_pct': 'Max DD (%)',
            'n_trades': 'Trades'
        })
        
        st.dataframe(display_df, use_container_width=True, height=300)
        
        st.success(f"✅ Found {len(efficient)} strategies on the efficient frontier")
else:
    st.info("Could not identify efficient frontier - insufficient data")

st.markdown("---")

# Distribution analysis
st.header("📊 Distribution Analysis")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Sharpe Ratio Distribution")
    
    if 'sharpe_ratio' in strategies_df.columns:
        fig = create_histogram(
            strategies_df['sharpe_ratio'],
            title="",
            x_label="Sharpe Ratio",
            bins=30
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Sharpe ratio data not available")

with col2:
    st.subheader("Return Distribution")
    
    if 'total_return' in strategies_df.columns:
        return_pct = strategies_df['total_return'] * 100
        fig = create_histogram(
            return_pct,
            title="",
            x_label="Return (%)",
            bins=30
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Return data not available")

# Drawdown distribution
st.subheader("Drawdown Distribution by Universe")

if 'universe_name' in strategies_df.columns and 'max_drawdown' in strategies_df.columns:
    top_universes = strategies_df['universe_name'].value_counts().head(10).index
    plot_df = strategies_df[strategies_df['universe_name'].isin(top_universes)].copy()
    plot_df['max_drawdown_pct'] = plot_df['max_drawdown'] * 100
    
    fig = create_box_plot(
        plot_df,
        y='max_drawdown_pct',
        x='universe_name',
        title=""
    )
    fig.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig, use_container_width=True)

# Footer
st.markdown("---")
st.markdown("""
💡 **Risk Management Tips**:
- Focus on strategies with Sharpe > 1.5 for better risk-adjusted returns
- Lower drawdown doesn't always mean better - consider total return
- Diversify across multiple strategies on the efficient frontier
- Monitor maximum drawdown in live trading
- Consider using position sizing based on Kelly Criterion
""")
