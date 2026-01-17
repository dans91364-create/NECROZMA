#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚡🌟💎 NECROZMA DASHBOARD - LOT SIZE ANALYSIS PAGE 💎🌟⚡

Compare strategy performance across different lot sizes
"""

import streamlit as st
import sys
from pathlib import Path
import pandas as pd

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from dashboard.utils.data_loader import load_all_results, detect_data_format
from dashboard.components.charts import create_bar_chart, create_line_chart, create_scatter_plot
from dashboard.components.metrics import calculate_lot_size_impact
from dashboard.components.tables import create_sortable_table

# Page config
st.set_page_config(page_title="Lot Size Analysis", page_icon="🔧", layout="wide")

st.title("🔧 Lot Size Analysis")
st.markdown("Compare same strategies across different lot sizes and optimize position sizing")

# Load data
with st.spinner("Loading backtest results..."):
    results = load_all_results()
    data_format = detect_data_format()

if results['total_strategies'] == 0:
    st.error("❌ No backtest results found.")
    st.stop()

strategies_df = results.get('strategies_df')

# Check if lot size data is available
if 'lot_size' not in strategies_df.columns:
    st.warning("⚠️ Lot size data not available. This page requires batch processing parquet data format.")
    st.info("💡 Run batch processing to generate data with multiple lot sizes")
    st.stop()

st.markdown("---")

# Lot Size Overview
st.header("📊 Lot Size Overview")

lot_stats = calculate_lot_size_impact(strategies_df)

if not lot_stats.empty:
    st.subheader("Performance Metrics by Lot Size")
    st.dataframe(lot_stats, use_container_width=True)
    
    # Visualizations
    col1, col2 = st.columns(2)
    
    with col1:
        if 'sharpe_ratio_mean' in lot_stats.columns:
            st.subheader("Average Sharpe Ratio by Lot Size")
            fig = create_bar_chart(
                lot_stats,
                x='lot_size',
                y='sharpe_ratio_mean',
                title=""
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        if 'total_return_mean' in lot_stats.columns:
            st.subheader("Average Return by Lot Size")
            # Convert to percentage if needed
            display_stats = lot_stats.copy()
            if display_stats['total_return_mean'].abs().max() <= 1:
                display_stats['total_return_mean'] = display_stats['total_return_mean'] * 100
            
            fig = create_bar_chart(
                display_stats,
                x='lot_size',
                y='total_return_mean',
                title=""
            )
            st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# Strategy Comparison Across Lot Sizes
st.header("🔍 Strategy Comparison")

# Get unique strategy base names (without lot size variations)
strategies_df['base_name'] = strategies_df['strategy_name'].str.replace(r'_lot_\d+\.\d+', '', regex=True)

# Select a strategy to analyze
unique_strategies = sorted(strategies_df['strategy_name'].unique().tolist())

selected_strategy = st.selectbox(
    "Select a strategy to compare across lot sizes",
    options=unique_strategies,
    index=0 if unique_strategies else None
)

if selected_strategy:
    # Get base name
    base_name = selected_strategy.split('_lot_')[0] if '_lot_' in selected_strategy else selected_strategy
    
    # Find all variations with different lot sizes
    strategy_variations = strategies_df[
        strategies_df['strategy_name'].str.contains(base_name, regex=False)
    ].sort_values('lot_size')
    
    if len(strategy_variations) > 1:
        st.subheader(f"Performance Comparison for {base_name}")
        
        # Display comparison table
        comparison_cols = ['lot_size', 'sharpe_ratio', 'total_return', 'win_rate', 
                         'max_drawdown', 'profit_factor', 'n_trades']
        
        if 'net_pnl' in strategy_variations.columns:
            comparison_cols.append('net_pnl')
        if 'total_commission' in strategy_variations.columns:
            comparison_cols.append('total_commission')
        
        available_cols = [col for col in comparison_cols if col in strategy_variations.columns]
        comparison_df = strategy_variations[available_cols].copy()
        
        # Format for display
        display_df = comparison_df.copy()
        for col in ['total_return', 'win_rate', 'max_drawdown']:
            if col in display_df.columns:
                if display_df[col].abs().max() <= 1:
                    display_df[col] = (display_df[col] * 100).round(2)
        
        st.dataframe(display_df, use_container_width=True)
        
        # Line charts comparing metrics
        st.subheader("Metric Trends Across Lot Sizes")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if 'sharpe_ratio' in comparison_df.columns:
                fig = create_line_chart(
                    comparison_df,
                    x='lot_size',
                    y='sharpe_ratio',
                    title="Sharpe Ratio vs Lot Size"
                )
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            if 'net_pnl' in comparison_df.columns:
                fig = create_line_chart(
                    comparison_df,
                    x='lot_size',
                    y='net_pnl',
                    title="Net PnL vs Lot Size"
                )
                st.plotly_chart(fig, use_container_width=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            if 'win_rate' in comparison_df.columns:
                wr_data = comparison_df.copy()
                if wr_data['win_rate'].abs().max() <= 1:
                    wr_data['win_rate'] = wr_data['win_rate'] * 100
                
                fig = create_line_chart(
                    wr_data,
                    x='lot_size',
                    y='win_rate',
                    title="Win Rate vs Lot Size"
                )
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            if 'max_drawdown' in comparison_df.columns:
                dd_data = comparison_df.copy()
                dd_data['drawdown_pct'] = dd_data['max_drawdown'].abs()
                if dd_data['drawdown_pct'].max() <= 1:
                    dd_data['drawdown_pct'] = dd_data['drawdown_pct'] * 100
                
                fig = create_line_chart(
                    dd_data,
                    x='lot_size',
                    y='drawdown_pct',
                    title="Max Drawdown vs Lot Size"
                )
                st.plotly_chart(fig, use_container_width=True)
        
        # Optimal lot size recommendation
        st.subheader("🎯 Optimal Lot Size Recommendation")
        
        # Find best lot size based on multiple criteria
        if 'sharpe_ratio' in comparison_df.columns:
            best_sharpe = comparison_df.loc[comparison_df['sharpe_ratio'].idxmax()]
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(
                    "Best by Sharpe Ratio",
                    f"{best_sharpe['lot_size']:.2f}",
                    delta=f"Sharpe: {best_sharpe['sharpe_ratio']:.2f}"
                )
            
            with col2:
                if 'net_pnl' in comparison_df.columns:
                    best_pnl = comparison_df.loc[comparison_df['net_pnl'].idxmax()]
                    st.metric(
                        "Best by Net PnL",
                        f"{best_pnl['lot_size']:.2f}",
                        delta=f"PnL: ${best_pnl['net_pnl']:,.2f}"
                    )
            
            with col3:
                if 'profit_factor' in comparison_df.columns:
                    best_pf = comparison_df.loc[comparison_df['profit_factor'].idxmax()]
                    st.metric(
                        "Best by Profit Factor",
                        f"{best_pf['lot_size']:.2f}",
                        delta=f"PF: {best_pf['profit_factor']:.2f}"
                    )
    
    else:
        st.info(f"Only one lot size variation found for {base_name}")

st.markdown("---")

# PnL Scaling Analysis
if 'net_pnl' in strategies_df.columns and 'lot_size' in strategies_df.columns:
    st.header("💰 PnL Scaling Analysis")
    
    st.subheader("Net PnL vs Lot Size (All Strategies)")
    
    fig = create_scatter_plot(
        strategies_df,
        x='lot_size',
        y='net_pnl',
        title="",
        color='sharpe_ratio',
        hover_name='strategy_name'
    )
    st.plotly_chart(fig, use_container_width=True)
    
    st.info("💡 **Expected**: PnL should scale linearly with lot size. Deviations may indicate commission impact or execution issues.")

st.markdown("---")

# Commission Impact by Lot Size
if 'total_commission' in strategies_df.columns and 'gross_pnl' in strategies_df.columns:
    st.header("💸 Commission Impact by Lot Size")
    
    commission_impact = strategies_df.groupby('lot_size').apply(
        lambda x: pd.Series({
            'avg_commission': x['total_commission'].mean(),
            'avg_gross_pnl': x['gross_pnl'].mean(),
            'commission_pct': (x['total_commission'].abs().mean() / x['gross_pnl'].abs().mean() * 100) if x['gross_pnl'].abs().mean() != 0 else 0
        })
    ).reset_index()
    
    st.dataframe(commission_impact, use_container_width=True)
    
    fig = create_bar_chart(
        commission_impact,
        x='lot_size',
        y='commission_pct',
        title="Commission as % of Gross PnL"
    )
    st.plotly_chart(fig, use_container_width=True)

# Footer
st.markdown("---")
st.markdown("💡 **Insight**: Optimal lot size balances profitability with risk management and commission impact")
