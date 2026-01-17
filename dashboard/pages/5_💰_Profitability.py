#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚡🌟💎 NECROZMA DASHBOARD - PROFITABILITY PAGE 💎🌟⚡

Comprehensive PnL and profitability analysis
"""

import streamlit as st
import sys
from pathlib import Path
import pandas as pd

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from dashboard.utils.data_loader import load_all_results, detect_data_format
from dashboard.components.charts import create_bar_chart, create_scatter_plot, create_distribution_chart
from dashboard.components.metrics import get_profitability_metrics, get_top_strategies
from dashboard.components.filters import create_parquet_filters, show_filter_summary
from dashboard.components.tables import create_sortable_table

# Page config
st.set_page_config(page_title="Profitability", page_icon="💰", layout="wide")

st.title("💰 Profitability Analysis")
st.markdown("Analyze net PnL, gross PnL, commission impact, and profit factors")

# Load data
with st.spinner("Loading backtest results..."):
    results = load_all_results()
    data_format = detect_data_format()

if results['total_strategies'] == 0:
    st.error("❌ No backtest results found.")
    st.stop()

strategies_df = results.get('strategies_df')

# Apply filters
filtered_df = strategies_df.copy()
if data_format == 'parquet':
    filters = create_parquet_filters(strategies_df)
    
    # Apply filtering logic (simplified for brevity)
    if 'lot_size' in filters and filters['lot_size']:
        filtered_df = filtered_df[filtered_df['lot_size'].isin(filters['lot_size'])]

show_filter_summary(len(strategies_df), len(filtered_df))

st.markdown("---")

# Profitability Metrics Summary
st.header("📊 Profitability Metrics")

pnl_metrics = get_profitability_metrics(filtered_df)

if pnl_metrics:
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if 'total_net_pnl' in pnl_metrics:
            st.metric("Total Net PnL", f"${pnl_metrics['total_net_pnl']:,.2f}")
    
    with col2:
        if 'avg_net_pnl' in pnl_metrics:
            st.metric("Avg Net PnL", f"${pnl_metrics['avg_net_pnl']:,.2f}")
    
    with col3:
        if 'profitable_strategies' in pnl_metrics:
            total = len(filtered_df)
            pct = (pnl_metrics['profitable_strategies'] / total * 100) if total > 0 else 0
            st.metric("Profitable Strategies", f"{pnl_metrics['profitable_strategies']}", delta=f"{pct:.1f}%")
    
    with col4:
        if 'total_commission' in pnl_metrics:
            st.metric("Total Commission", f"${abs(pnl_metrics['total_commission']):,.2f}")
    
    # Second row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if 'max_net_pnl' in pnl_metrics:
            st.metric("Max Net PnL", f"${pnl_metrics['max_net_pnl']:,.2f}")
    
    with col2:
        if 'min_net_pnl' in pnl_metrics:
            st.metric("Min Net PnL", f"${pnl_metrics['min_net_pnl']:,.2f}")
    
    with col3:
        if 'avg_expectancy' in pnl_metrics:
            st.metric("Avg Expectancy", f"${pnl_metrics['avg_expectancy']:,.2f}")
    
    with col4:
        if 'total_gross_pnl' in pnl_metrics:
            st.metric("Total Gross PnL", f"${pnl_metrics['total_gross_pnl']:,.2f}")

st.markdown("---")

# Top Performers by PnL
st.header("🏆 Top Performers by Net PnL")

if 'net_pnl' in filtered_df.columns:
    top_pnl = filtered_df.nlargest(20, 'net_pnl')
    
    display_cols = ['strategy_name', 'net_pnl']
    for col in ['gross_pnl', 'total_commission', 'expectancy', 'profit_factor', 'sharpe_ratio', 'n_trades']:
        if col in top_pnl.columns:
            display_cols.append(col)
    
    display_df = top_pnl[display_cols].copy()
    display_df = display_df.rename(columns={
        'strategy_name': 'Strategy',
        'net_pnl': 'Net PnL',
        'gross_pnl': 'Gross PnL',
        'total_commission': 'Commission',
        'expectancy': 'Expectancy',
        'profit_factor': 'Profit Factor',
        'sharpe_ratio': 'Sharpe',
        'n_trades': 'Trades'
    })
    
    create_sortable_table(display_df, key="top_pnl_table", height=400)
    
    # Download button
    csv = display_df.to_csv(index=False)
    st.download_button(
        label="📥 Download Top PnL Strategies",
        data=csv,
        file_name="top_pnl_strategies.csv",
        mime="text/csv"
    )

st.markdown("---")

# Visualizations
st.header("📈 PnL Visualizations")

col1, col2 = st.columns(2)

with col1:
    if 'net_pnl' in filtered_df.columns:
        st.subheader("Net PnL Distribution")
        fig = create_distribution_chart(
            filtered_df['net_pnl'].dropna(),
            title="",
            x_label="Net PnL ($)",
            show_stats=True
        )
        st.plotly_chart(fig, use_container_width=True)

with col2:
    if 'profit_factor' in filtered_df.columns:
        st.subheader("Profit Factor Distribution")
        # Filter out extreme values for better visualization
        pf_data = filtered_df['profit_factor'].dropna()
        pf_data = pf_data[pf_data < pf_data.quantile(0.95)]  # Remove top 5% outliers
        
        fig = create_distribution_chart(
            pf_data,
            title="",
            x_label="Profit Factor",
            show_stats=True
        )
        st.plotly_chart(fig, use_container_width=True)

# Gross PnL vs Commission
st.subheader("Gross PnL vs Commission Analysis")

if 'gross_pnl' in filtered_df.columns and 'total_commission' in filtered_df.columns:
    # Create scatter plot
    scatter_df = filtered_df[['strategy_name', 'gross_pnl', 'total_commission', 'net_pnl']].dropna()
    scatter_df['commission_abs'] = scatter_df['total_commission'].abs()
    
    fig = create_scatter_plot(
        scatter_df,
        x='gross_pnl',
        y='commission_abs',
        title="",
        color='net_pnl',
        hover_name='strategy_name'
    )
    fig.update_layout(
        xaxis_title="Gross PnL ($)",
        yaxis_title="Commission ($)",
        coloraxis_colorbar_title="Net PnL"
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Commission impact statistics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        avg_commission_pct = (scatter_df['commission_abs'].mean() / scatter_df['gross_pnl'].mean() * 100) if scatter_df['gross_pnl'].mean() != 0 else 0
        st.metric("Avg Commission Impact", f"{avg_commission_pct:.2f}%")
    
    with col2:
        total_commission_impact = scatter_df['commission_abs'].sum() / scatter_df['gross_pnl'].sum() * 100 if scatter_df['gross_pnl'].sum() != 0 else 0
        st.metric("Total Commission Impact", f"{total_commission_impact:.2f}%")
    
    with col3:
        profitable_after_commission = (scatter_df['net_pnl'] > 0).sum()
        st.metric("Profitable After Commission", f"{profitable_after_commission} / {len(scatter_df)}")

st.markdown("---")

# Expectancy Analysis
if 'expectancy' in filtered_df.columns:
    st.header("🎯 Expectancy Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Top 20 by Expectancy")
        top_exp = filtered_df.nlargest(20, 'expectancy')[['strategy_name', 'expectancy', 'n_trades', 'net_pnl']]
        top_exp = top_exp.rename(columns={
            'strategy_name': 'Strategy',
            'expectancy': 'Expectancy',
            'n_trades': 'Trades',
            'net_pnl': 'Net PnL'
        })
        create_sortable_table(top_exp, key="top_exp_table", height=400)
    
    with col2:
        st.subheader("Expectancy Distribution")
        # Filter extreme values
        exp_data = filtered_df['expectancy'].dropna()
        exp_data = exp_data[(exp_data > exp_data.quantile(0.05)) & (exp_data < exp_data.quantile(0.95))]
        
        fig = create_distribution_chart(
            exp_data,
            title="",
            x_label="Expectancy ($)",
            show_stats=True
        )
        st.plotly_chart(fig, use_container_width=True)

# Footer
st.markdown("---")
st.markdown("💡 **Insight**: Focus on strategies with positive net PnL, high expectancy, and manageable commission impact")
