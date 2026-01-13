#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚡🌟💎 NECROZMA DASHBOARD - OVERVIEW PAGE 💎🌟⚡

Global performance summary across all strategies
"""

import streamlit as st
import sys
from pathlib import Path

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from dashboard.utils.data_loader import load_all_results, get_universe_list
from dashboard.components.charts import create_bar_chart, create_pie_chart
from dashboard.components.metrics import calculate_summary_metrics, get_top_strategies
from dashboard.components.tables import format_strategies_table, create_sortable_table
from dashboard.utils.formatters import format_percentage, format_number

# Page config
st.set_page_config(page_title="Overview", page_icon="📊", layout="wide")

st.title("🏆 Performance Overview")
st.markdown("Global performance summary across all strategies and universes")

# Load data
with st.spinner("Loading backtest results..."):
    results = load_all_results()

if results['total_strategies'] == 0:
    st.error("❌ No backtest results found. Please run backtests first.")
    st.info("💡 Run `python run_sequential_backtest.py` to generate results")
    st.stop()

# Summary metrics
st.header("📈 Summary Metrics")

summary = calculate_summary_metrics(results.get('strategies_df'))

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
    st.metric(
        "Best Return",
        format_percentage(summary['max_return'] / 100, decimals=1)
    )

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
    st.metric(
        "Avg Return",
        format_percentage(summary['avg_return'] / 100, decimals=1)
    )

with col3:
    st.metric(
        "Avg Win Rate",
        format_percentage(summary['avg_win_rate'] / 100, decimals=1)
    )

with col4:
    st.metric(
        "Min Drawdown",
        format_percentage(summary['min_drawdown'] / 100, decimals=1)
    )

st.markdown("---")

# Top strategies
st.header("🏆 Top 20 Strategies by Sharpe Ratio")

strategies_df = results.get('strategies_df')

if strategies_df is not None and not strategies_df.empty:
    top_20 = get_top_strategies(strategies_df, by='sharpe_ratio', n=20)
    
    if not top_20.empty:
        # Display table
        display_cols = [
            'strategy_name', 'universe_name', 'sharpe_ratio', 
            'total_return_pct', 'win_rate_pct', 'max_drawdown_pct', 
            'n_trades', 'profit_factor'
        ]
        
        # Filter to available columns
        available_cols = [col for col in display_cols if col in top_20.columns]
        display_df = top_20[available_cols].copy()
        
        # Rename for better readability
        display_df = display_df.rename(columns={
            'total_return_pct': 'Return (%)',
            'win_rate_pct': 'Win Rate (%)',
            'max_drawdown_pct': 'Max DD (%)',
            'sharpe_ratio': 'Sharpe',
            'profit_factor': 'Profit Factor',
            'n_trades': 'Trades',
            'strategy_name': 'Strategy',
            'universe_name': 'Universe'
        })
        
        create_sortable_table(display_df, key="top_20_table", height=400)
        
        # Download button
        csv = display_df.to_csv(index=False)
        st.download_button(
            label="📥 Download Top 20 as CSV",
            data=csv,
            file_name="top_20_strategies.csv",
            mime="text/csv"
        )
        
        st.markdown("---")
        
        # Visualizations
        st.header("📊 Visualizations")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Top 20 by Sharpe Ratio")
            # Limit to top 20 for better visibility
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
        
        # Universe distribution
        st.subheader("Strategy Count by Universe")
        
        if 'universe_name' in strategies_df.columns:
            universe_counts = strategies_df['universe_name'].value_counts().head(20)
            
            import pandas as pd
            universe_df = pd.DataFrame({
                'universe': universe_counts.index,
                'count': universe_counts.values
            })
            
            fig = create_bar_chart(
                universe_df,
                x='universe',
                y='count',
                title="",
                orientation='v'
            )
            st.plotly_chart(fig, use_container_width=True)
    
    else:
        st.warning("No strategies found in results")
else:
    st.warning("No strategy data available")

# Footer
st.markdown("---")
st.markdown("💡 **Tip**: Navigate to other pages using the sidebar to explore universe comparisons, strategy deep dives, and more!")
