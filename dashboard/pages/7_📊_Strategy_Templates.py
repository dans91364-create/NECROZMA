#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚡🌟💎 NECROZMA DASHBOARD - STRATEGY TEMPLATES PAGE 💎🌟⚡

Analyze performance by strategy template type
"""

import streamlit as st
import sys
from pathlib import Path
import pandas as pd

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from dashboard.utils.data_loader import load_all_results, detect_data_format, extract_strategy_template
from dashboard.components.charts import create_bar_chart, create_box_plot, create_scatter_plot
from dashboard.components.metrics import calculate_template_performance
from dashboard.components.tables import create_sortable_table

# Page config
st.set_page_config(page_title="Strategy Templates", page_icon="📊", layout="wide")

st.title("📊 Strategy Template Analysis")
st.markdown("Analyze performance by strategy type and identify best templates")

# Load data
with st.spinner("Loading backtest results..."):
    results = load_all_results()
    data_format = detect_data_format()

if results['total_strategies'] == 0:
    st.error("❌ No backtest results found.")
    st.stop()

strategies_df = results.get('strategies_df')

# Extract template from strategy names
if 'strategy_name' in strategies_df.columns:
    strategies_df['template'] = strategies_df['strategy_name'].apply(extract_strategy_template)
else:
    st.error("Strategy name column not found")
    st.stop()

st.markdown("---")

# Template Performance Summary
st.header("📊 Template Performance Summary")

template_stats = calculate_template_performance(strategies_df)

if not template_stats.empty:
    st.subheader("Performance by Template")
    
    # Display statistics table
    st.dataframe(template_stats, use_container_width=True)
    
    # Download button
    csv = template_stats.to_csv(index=False)
    st.download_button(
        label="📥 Download Template Statistics",
        data=csv,
        file_name="template_statistics.csv",
        mime="text/csv"
    )

st.markdown("---")

# Visualizations
st.header("📈 Template Comparisons")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Average Sharpe Ratio by Template")
    if 'sharpe_ratio_mean' in template_stats.columns:
        top_templates = template_stats.nlargest(15, 'sharpe_ratio_mean')
        fig = create_bar_chart(
            top_templates,
            x='template',
            y='sharpe_ratio_mean',
            title=""
        )
        fig.update_layout(xaxis={'categoryorder': 'total descending'})
        st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("Strategy Count by Template")
    if 'sharpe_ratio_count' in template_stats.columns:
        top_counts = template_stats.nlargest(15, 'sharpe_ratio_count')
        fig = create_bar_chart(
            top_counts,
            x='template',
            y='sharpe_ratio_count',
            title=""
        )
        fig.update_layout(xaxis={'categoryorder': 'total descending'})
        st.plotly_chart(fig, use_container_width=True)

col1, col2 = st.columns(2)

with col1:
    st.subheader("Average Win Rate by Template")
    if 'win_rate_mean' in template_stats.columns:
        # Convert to percentage if needed
        display_stats = template_stats.copy()
        if display_stats['win_rate_mean'].max() <= 1:
            display_stats['win_rate_mean'] = display_stats['win_rate_mean'] * 100
        
        top_wr = display_stats.nlargest(15, 'win_rate_mean')
        fig = create_bar_chart(
            top_wr,
            x='template',
            y='win_rate_mean',
            title=""
        )
        fig.update_layout(xaxis={'categoryorder': 'total descending'})
        st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("Average Return by Template")
    if 'total_return_mean' in template_stats.columns:
        display_stats = template_stats.copy()
        if display_stats['total_return_mean'].abs().max() <= 1:
            display_stats['total_return_mean'] = display_stats['total_return_mean'] * 100
        
        top_return = display_stats.nlargest(15, 'total_return_mean')
        fig = create_bar_chart(
            top_return,
            x='template',
            y='total_return_mean',
            title=""
        )
        fig.update_layout(xaxis={'categoryorder': 'total descending'})
        st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# Distribution Analysis
st.header("📊 Template Distribution Analysis")

# Select metric to analyze
metric = st.selectbox(
    "Select Metric for Distribution Analysis",
    ['sharpe_ratio', 'total_return', 'win_rate', 'max_drawdown', 'profit_factor'],
    index=0
)

if metric in strategies_df.columns:
    st.subheader(f"{metric.replace('_', ' ').title()} Distribution by Template")
    
    # Get top 10 templates by count for clearer visualization
    top_10_templates = template_stats.nlargest(10, 'sharpe_ratio_count')['template'].tolist()
    filtered_for_box = strategies_df[strategies_df['template'].isin(top_10_templates)]
    
    if not filtered_for_box.empty:
        fig = create_box_plot(
            filtered_for_box,
            y=metric,
            x='template',
            title=""
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No data available for box plot")

st.markdown("---")

# Best Strategies per Template
st.header("🏆 Best Strategy per Template")

# Select template
available_templates = sorted(strategies_df['template'].unique().tolist())
selected_template = st.selectbox(
    "Select Template to Analyze",
    options=available_templates,
    index=0 if available_templates else None
)

if selected_template:
    template_data = strategies_df[strategies_df['template'] == selected_template]
    
    st.subheader(f"Top Strategies for {selected_template}")
    st.info(f"📊 Total strategies in this template: {len(template_data)}")
    
    # Get top strategies by Sharpe
    if 'sharpe_ratio' in template_data.columns:
        top_in_template = template_data.nlargest(20, 'sharpe_ratio')
        
        display_cols = ['strategy_name', 'sharpe_ratio']
        for col in ['total_return', 'win_rate', 'max_drawdown', 'profit_factor', 'n_trades']:
            if col in top_in_template.columns:
                display_cols.append(col)
        
        if 'lot_size' in top_in_template.columns:
            display_cols.insert(1, 'lot_size')
        
        display_df = top_in_template[display_cols].copy()
        
        # Format percentages
        for col in ['total_return', 'win_rate', 'max_drawdown']:
            if col in display_df.columns:
                if display_df[col].abs().max() <= 1:
                    display_df[col] = (display_df[col] * 100).round(2)
        
        # Rename columns
        rename_map = {
            'strategy_name': 'Strategy',
            'lot_size': 'Lot Size',
            'sharpe_ratio': 'Sharpe',
            'total_return': 'Return (%)',
            'win_rate': 'Win Rate (%)',
            'max_drawdown': 'Max DD (%)',
            'profit_factor': 'Profit Factor',
            'n_trades': 'Trades'
        }
        display_df = display_df.rename(columns=rename_map)
        
        create_sortable_table(display_df, key="template_top_table", height=400)
        
        # Download
        csv = display_df.to_csv(index=False)
        st.download_button(
            label=f"📥 Download Top {selected_template} Strategies",
            data=csv,
            file_name=f"top_{selected_template}_strategies.csv",
            mime="text/csv"
        )

st.markdown("---")

# Template Comparison (Risk vs Return)
st.header("🎯 Template Risk-Return Profile")

if 'sharpe_ratio' in strategies_df.columns and 'max_drawdown' in strategies_df.columns:
    st.subheader("Sharpe Ratio vs Max Drawdown by Template")
    
    # Create scatter plot with template as color
    scatter_df = strategies_df.copy()
    scatter_df['drawdown_pct'] = scatter_df['max_drawdown'].abs()
    if scatter_df['drawdown_pct'].max() <= 1:
        scatter_df['drawdown_pct'] = scatter_df['drawdown_pct'] * 100
    
    fig = create_scatter_plot(
        scatter_df,
        x='drawdown_pct',
        y='sharpe_ratio',
        title="",
        color='template',
        hover_name='strategy_name'
    )
    fig.update_layout(
        xaxis_title="Max Drawdown (%)",
        yaxis_title="Sharpe Ratio"
    )
    st.plotly_chart(fig, use_container_width=True)
    
    st.info("💡 **Insight**: Templates in the upper-left quadrant (low drawdown, high Sharpe) are optimal")

st.markdown("---")

# Parameter Sensitivity (if applicable)
st.header("🔬 Template Insights")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Most Consistent Templates")
    if 'sharpe_ratio_std' in template_stats.columns:
        most_consistent = template_stats.nsmallest(10, 'sharpe_ratio_std')[['template', 'sharpe_ratio_mean', 'sharpe_ratio_std']]
        most_consistent = most_consistent.rename(columns={
            'template': 'Template',
            'sharpe_ratio_mean': 'Avg Sharpe',
            'sharpe_ratio_std': 'Sharpe Std Dev'
        })
        st.dataframe(most_consistent, use_container_width=True)

with col2:
    st.subheader("Highest Peak Performance")
    if 'sharpe_ratio_max' in template_stats.columns:
        highest_peak = template_stats.nlargest(10, 'sharpe_ratio_max')[['template', 'sharpe_ratio_max', 'sharpe_ratio_mean']]
        highest_peak = highest_peak.rename(columns={
            'template': 'Template',
            'sharpe_ratio_max': 'Max Sharpe',
            'sharpe_ratio_mean': 'Avg Sharpe'
        })
        st.dataframe(highest_peak, use_container_width=True)

# Footer
st.markdown("---")
st.markdown("💡 **Insight**: Identify which strategy templates perform best for your trading style and market conditions")
