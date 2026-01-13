#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚡🌟💎 NECROZMA DASHBOARD - RISK ANALYSIS PAGE 💎🌟⚡

Analyze risk-adjusted returns and drawdowns
"""

import streamlit as st
import sys
from pathlib import Path
import pandas as pd

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from dashboard.utils.data_loader import load_all_results
from dashboard.components.charts import (
    create_scatter_plot, create_histogram, create_box_plot
)
from dashboard.components.metrics import (
    identify_efficient_frontier, calculate_risk_metrics
)
from dashboard.utils.formatters import format_percentage

# Page config
st.set_page_config(page_title="Risk Analysis", page_icon="⚠️", layout="wide")

st.title("⚠️ Risk Analysis")
st.markdown("Analyze risk-adjusted returns and identify efficient strategies")

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

# Risk metrics summary
st.header("📊 Risk Metrics Summary")

risk_metrics = calculate_risk_metrics(strategies_df)

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
            st.metric("Average Drawdown", format_percentage(risk_metrics['avg_drawdown'] / 100))
    
    with col4:
        if 'max_drawdown' in risk_metrics:
            st.metric("Maximum Drawdown", format_percentage(risk_metrics['max_drawdown'] / 100))

st.markdown("---")

# Return vs Risk scatter
st.header("📈 Return vs Risk Analysis")

if 'max_drawdown' in strategies_df.columns and 'total_return' in strategies_df.columns:
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Return vs Maximum Drawdown")
        
        # Prepare data
        plot_df = strategies_df.copy()
        plot_df['total_return_pct'] = plot_df['total_return'] * 100
        plot_df['max_drawdown_pct'] = plot_df['max_drawdown'] * 100
        
        # Create scatter plot
        fig = create_scatter_plot(
            plot_df.head(200),  # Limit for performance
            x='max_drawdown_pct',
            y='total_return_pct',
            title="",
            color='sharpe_ratio' if 'sharpe_ratio' in plot_df else None,
            size='n_trades' if 'n_trades' in plot_df else None,
            hover_name='strategy_name' if 'strategy_name' in plot_df else None
        )
        
        fig.update_layout(
            xaxis_title="Maximum Drawdown (%)",
            yaxis_title="Total Return (%)"
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("""
        **Interpretation**:
        - Top-left quadrant: High return, low drawdown (ideal)
        - Bottom-right: Low return, high drawdown (avoid)
        - Point size = number of trades
        - Color = Sharpe ratio (green = better)
        """)
    
    with col2:
        st.subheader("Risk Categories")
        
        # Categorize strategies by risk
        def categorize_risk(dd):
            if dd < 0.05:
                return 'Low Risk (<5%)'
            elif dd < 0.15:
                return 'Medium Risk (5-15%)'
            else:
                return 'High Risk (>15%)'
        
        plot_df['risk_category'] = plot_df['max_drawdown'].apply(categorize_risk)
        
        risk_counts = plot_df['risk_category'].value_counts()
        
        for category, count in risk_counts.items():
            pct = (count / len(plot_df)) * 100
            st.metric(category, f"{count} ({pct:.1f}%)")
        
        st.markdown("---")
        
        # Best risk-adjusted
        if 'sharpe_ratio' in plot_df.columns:
            best_idx = plot_df['sharpe_ratio'].idxmax()
            best = plot_df.loc[best_idx]
            
            st.success(f"""
            **Best Risk-Adjusted**:
            
            {best.get('strategy_name', 'N/A')[:30]}...
            
            - Sharpe: {best.get('sharpe_ratio', 0):.2f}
            - Return: {best.get('total_return_pct', 0):.1f}%
            - DD: {best.get('max_drawdown_pct', 0):.1f}%
            """)

else:
    st.warning("Return and drawdown data not available")

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
