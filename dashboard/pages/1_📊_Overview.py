#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚡🌟💎 NECROZMA DASHBOARD - OVERVIEW PAGE 💎🌟⚡

Global performance summary across all strategies
Enhanced for batch processing data format
"""

import streamlit as st
import sys
from pathlib import Path

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from dashboard.utils.data_loader import load_all_results, detect_data_format, extract_strategy_template
from dashboard.components.charts import create_bar_chart, create_pie_chart, create_distribution_chart
from dashboard.components.metrics import calculate_summary_metrics, get_top_strategies
from dashboard.components.tables import create_sortable_table
from dashboard.components.filters import create_parquet_filters, apply_filters, show_filter_summary
from dashboard.utils.formatters import format_percentage, format_number

# Page config
st.set_page_config(page_title="Overview", page_icon="📊", layout="wide")

st.title("🏆 Performance Overview")
st.markdown("Global performance summary across all strategies")

# Load data
with st.spinner("Loading backtest results..."):
    results = load_all_results()
    data_format = detect_data_format()

if results['total_strategies'] == 0:
    st.error("❌ No backtest results found. Please run backtests first.")
    st.info("💡 Run batch processing or sequential backtest to generate results")
    st.stop()

strategies_df = results.get('strategies_df')

# Show data source
data_source = results['metadata'].get('data_source', 'unknown')
st.info(f"📊 Data Source: **{data_source}** | Format: **{data_format}**")

# Apply filters for parquet format
filtered_df = strategies_df.copy()
if data_format == 'parquet':
    filters = create_parquet_filters(strategies_df)
    
    # Apply filters
    if 'lot_size' in filters and filters['lot_size']:
        filtered_df = filtered_df[filtered_df['lot_size'].isin(filters['lot_size'])]
    
    if 'template' in filters and filters['template']:
        filtered_df['template'] = filtered_df['strategy_name'].apply(extract_strategy_template)
        filtered_df = filtered_df[filtered_df['template'].isin(filters['template'])]
    
    if 'sharpe_ratio' in filters:
        min_val, max_val = filters['sharpe_ratio']
        filtered_df = filtered_df[(filtered_df['sharpe_ratio'] >= min_val) & (filtered_df['sharpe_ratio'] <= max_val)]
    
    if 'win_rate' in filters:
        min_val, max_val = filters['win_rate']
        filtered_df = filtered_df[(filtered_df['win_rate'] >= min_val) & (filtered_df['win_rate'] <= max_val)]
    
    if 'n_trades' in filters:
        min_val, max_val = filters['n_trades']
        filtered_df = filtered_df[(filtered_df['n_trades'] >= min_val) & (filtered_df['n_trades'] <= max_val)]

# Show filter summary
show_filter_summary(len(strategies_df), len(filtered_df))

st.markdown("---")

# Summary metrics
st.header("📈 Summary Metrics")

summary = calculate_summary_metrics(filtered_df)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Total Strategies",
        format_number(summary['total_strategies'], decimals=0)
    )

with col2:
    st.metric(
        "Best Sharpe Ratio",
        f"{summary['max_sharpe']:.2f}"
    )

with col3:
    return_val = summary['max_return']
    # Handle both percentage and decimal formats
    if abs(return_val) > 10:  # Already in percentage
        st.metric("Best Return", f"{return_val:.1f}%")
    else:  # Decimal format
        st.metric("Best Return", format_percentage(return_val, decimals=1))

with col4:
    st.metric(
        "Viable Strategies",
        format_number(summary['viable_count'], decimals=0),
        delta=f"{(summary['viable_count'] / summary['total_strategies'] * 100):.1f}%" if summary['total_strategies'] > 0 else "0%"
    )

# Second row of metrics
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Avg Sharpe Ratio",
        f"{summary['avg_sharpe']:.2f}"
    )

with col2:
    avg_return = summary['avg_return']
    if abs(avg_return) > 10:
        st.metric("Avg Return", f"{avg_return:.1f}%")
    else:
        st.metric("Avg Return", format_percentage(avg_return, decimals=1))

with col3:
    avg_wr = summary['avg_win_rate']
    if avg_wr > 1:  # Already in percentage
        st.metric("Avg Win Rate", f"{avg_wr:.1f}%")
    else:
        st.metric("Avg Win Rate", format_percentage(avg_wr, decimals=1))

with col4:
    min_dd = summary['min_drawdown']
    if abs(min_dd) > 1:
        st.metric("Min Drawdown", f"{min_dd:.1f}%")
    else:
        st.metric("Min Drawdown", format_percentage(min_dd, decimals=1))

st.markdown("---")

# Top strategies
st.header("🏆 Top Strategies by Sharpe Ratio")

if filtered_df is not None and not filtered_df.empty:
    top_20 = get_top_strategies(filtered_df, by='sharpe_ratio', n=300)
    
    if not top_20.empty:
        # Display table
        display_cols = ['strategy_name']
        
        # Add columns based on availability
        optional_cols = [
            ('lot_size', 'Lot Size'),
            ('sharpe_ratio', 'Sharpe'),
            ('total_return', 'Return'),
            ('win_rate', 'Win Rate (%)'),
            ('max_drawdown', 'Max DD (%)'),
            ('n_trades', 'Trades'),
            ('profit_factor', 'Profit Factor'),
            ('net_pnl', 'Net PnL'),
        ]
        
        display_df = top_20[['strategy_name']].copy()
        
        for col, label in optional_cols:
            if col in top_20.columns:
                if col in ['total_return', 'win_rate', 'max_drawdown']:
                    # Convert to percentage if needed
                    if top_20[col].abs().max() <= 1:
                        display_df[label] = (top_20[col] * 100).round(2)
                    else:
                        display_df[label] = top_20[col].round(2)
                else:
                    display_df[label] = top_20[col]
        
        # Rename strategy column
        display_df = display_df.rename(columns={'strategy_name': 'Strategy'})
        
        create_sortable_table(display_df, key="top_20_table", height=400)
        
        # Download button
        csv = display_df.to_csv(index=False)
        st.download_button(
            label="📥 Download Top Strategies as CSV",
            data=csv,
            file_name="top_strategies.csv",
            mime="text/csv"
        )
        
        st.markdown("---")
        
        # Visualizations
        st.header("📊 Visualizations")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Top Strategies by Sharpe Ratio")
            chart_data = top_20.head(20).copy()
            chart_data['display_name'] = chart_data['strategy_name'].str[:30] + '...'
            
            fig = create_bar_chart(
                chart_data,
                x='sharpe_ratio',
                y='display_name',
                title="",
                orientation='h'
            )
            fig.update_layout(yaxis={'categoryorder': 'total ascending'})
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("Viable vs Non-Viable Strategies")
            viable_count = summary['viable_count']
            non_viable = summary['total_strategies'] - viable_count
            
            fig = create_pie_chart(
                values=[viable_count, non_viable],
                labels=['Viable (Sharpe>1, WR>50%)', 'Non-Viable'],
                title=""
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Distribution charts
        st.subheader("Metric Distributions")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if 'sharpe_ratio' in filtered_df.columns:
                fig = create_distribution_chart(
                    filtered_df['sharpe_ratio'].dropna(),
                    title="Sharpe Ratio Distribution",
                    x_label="Sharpe Ratio"
                )
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            if 'win_rate' in filtered_df.columns:
                wr_data = filtered_df['win_rate'].dropna()
                # Convert to percentage if needed
                if wr_data.abs().max() <= 1:
                    wr_data = wr_data * 100
                fig = create_distribution_chart(
                    wr_data,
                    title="Win Rate Distribution",
                    x_label="Win Rate (%)"
                )
                st.plotly_chart(fig, use_container_width=True)
        
        with col3:
            if 'max_drawdown' in filtered_df.columns:
                dd_data = filtered_df['max_drawdown'].dropna().abs()
                if dd_data.max() <= 1:
                    dd_data = dd_data * 100
                fig = create_distribution_chart(
                    dd_data,
                    title="Max Drawdown Distribution",
                    x_label="Max Drawdown (%)"
                )
                st.plotly_chart(fig, use_container_width=True)
    
    else:
        st.warning("No strategies found in results")
else:
    st.warning("No strategy data available")

# Footer
st.markdown("---")
st.markdown("💡 **Tip**: Navigate to other pages using the sidebar to explore performance matrices, strategy analysis, and more!")
