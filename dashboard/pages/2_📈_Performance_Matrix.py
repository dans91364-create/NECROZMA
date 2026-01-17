#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚡🌟💎 NECROZMA DASHBOARD - PERFORMANCE MATRIX PAGE 💎🌟⚡

Heatmap analysis of strategy performance across templates and lot sizes
"""

import streamlit as st
import sys
from pathlib import Path
import pandas as pd

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from dashboard.utils.data_loader import load_all_results, detect_data_format, extract_strategy_template
from dashboard.components.charts import create_performance_matrix, create_bar_chart
from dashboard.components.metrics import calculate_template_performance, calculate_lot_size_impact
from dashboard.components.filters import create_parquet_filters, show_filter_summary

# Page config
st.set_page_config(page_title="Performance Matrix", page_icon="📈", layout="wide")

st.title("📈 Performance Matrix")
st.markdown("Analyze strategy performance across templates and lot sizes")

# Load data
with st.spinner("Loading backtest results..."):
    results = load_all_results()
    data_format = detect_data_format()

if results['total_strategies'] == 0:
    st.error("❌ No backtest results found.")
    st.stop()

strategies_df = results.get('strategies_df')

# Add template column
if 'strategy_name' in strategies_df.columns:
    strategies_df['template'] = strategies_df['strategy_name'].apply(extract_strategy_template)

# Apply filters
filtered_df = strategies_df.copy()
if data_format == 'parquet':
    filters = create_parquet_filters(strategies_df)
    
    if 'lot_size' in filters and filters['lot_size']:
        filtered_df = filtered_df[filtered_df['lot_size'].isin(filters['lot_size'])]
    
    if 'template' in filters and filters['template']:
        filtered_df['template'] = filtered_df['strategy_name'].apply(extract_strategy_template)
        filtered_df = filtered_df[filtered_df['template'].isin(filters['template'])]

show_filter_summary(len(strategies_df), len(filtered_df))

st.markdown("---")

# Performance Matrix Heatmap
st.header("🔥 Performance Heatmap")

metric_choice = st.selectbox(
    "Select Metric",
    ['sharpe_ratio', 'total_return', 'win_rate', 'profit_factor', 'max_drawdown'],
    index=0
)

# Check if we have lot_size data (parquet format)
if 'lot_size' in filtered_df.columns and 'template' in filtered_df.columns:
    if metric_choice in filtered_df.columns:
        st.subheader(f"{metric_choice.replace('_', ' ').title()} by Template and Lot Size")
        
        try:
            fig = create_performance_matrix(
                filtered_df,
                index_col='template',
                columns_col='lot_size',
                values_col=metric_choice,
                title="",
                colorscale='RdYlGn' if metric_choice != 'max_drawdown' else 'RdYlGn_r'
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Summary statistics
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Best Template per Lot Size")
                best_by_lot = filtered_df.groupby('lot_size').apply(
                    lambda x: x.nlargest(1, metric_choice)[['template', metric_choice]]
                ).reset_index(drop=True)
                st.dataframe(best_by_lot, use_container_width=True)
            
            with col2:
                st.subheader("Best Lot Size per Template")
                best_by_template = filtered_df.groupby('template').apply(
                    lambda x: x.nlargest(1, metric_choice)[['lot_size', metric_choice]]
                ).reset_index(drop=True)
                st.dataframe(best_by_template, use_container_width=True)
        
        except Exception as e:
            st.error(f"Error creating heatmap: {e}")
    else:
        st.warning(f"Metric '{metric_choice}' not available in data")
else:
    st.info("📊 Lot size data not available. Showing template performance only.")

st.markdown("---")

# Template Performance Analysis
st.header("📊 Template Performance Analysis")

template_stats = calculate_template_performance(filtered_df)

if not template_stats.empty:
    st.subheader("Performance by Strategy Template")
    st.dataframe(template_stats, use_container_width=True)
    
    # Visualize top templates
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Avg Sharpe Ratio by Template")
        if 'sharpe_ratio_mean' in template_stats.columns:
            fig = create_bar_chart(
                template_stats.head(10),
                x='template',
                y='sharpe_ratio_mean',
                title=""
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Strategy Count by Template")
        if 'sharpe_ratio_count' in template_stats.columns:
            fig = create_bar_chart(
                template_stats.head(10),
                x='template',
                y='sharpe_ratio_count',
                title=""
            )
            st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# Lot Size Impact Analysis
if 'lot_size' in filtered_df.columns:
    st.header("🔧 Lot Size Impact Analysis")
    
    lot_stats = calculate_lot_size_impact(filtered_df)
    
    if not lot_stats.empty:
        st.subheader("Performance Metrics by Lot Size")
        st.dataframe(lot_stats, use_container_width=True)
        
        # Visualize lot size impact
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Avg Sharpe by Lot Size")
            if 'sharpe_ratio_mean' in lot_stats.columns:
                fig = create_bar_chart(
                    lot_stats,
                    x='lot_size',
                    y='sharpe_ratio_mean',
                    title=""
                )
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("Avg Win Rate by Lot Size")
            if 'win_rate_mean' in lot_stats.columns:
                # Convert to percentage if needed
                lot_stats_display = lot_stats.copy()
                if lot_stats_display['win_rate_mean'].max() <= 1:
                    lot_stats_display['win_rate_mean'] = lot_stats_display['win_rate_mean'] * 100
                
                fig = create_bar_chart(
                    lot_stats_display,
                    x='lot_size',
                    y='win_rate_mean',
                    title=""
                )
                st.plotly_chart(fig, use_container_width=True)

# Footer
st.markdown("---")
st.markdown("💡 **Insight**: Use this matrix to identify which strategy templates perform best at different lot sizes")
