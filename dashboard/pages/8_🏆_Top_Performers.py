#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚡🌟💎 NECROZMA DASHBOARD - COMPOSITE RANKING PAGE 💎🌟⚡

Multi-factor composite score analysis for finding best overall strategies
"""

import streamlit as st
import sys
from pathlib import Path
import pandas as pd
import numpy as np
import json

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from dashboard.utils.data_loader import load_all_results
from dashboard.components.charts import create_bar_chart
from dashboard.utils.formatters import format_percentage, format_number

# Page config
st.set_page_config(page_title="Composite Ranking", page_icon="🏆", layout="wide")

st.title("🏆 Composite Score Ranking")
st.markdown("Multi-factor analysis to find strategies that excel across ALL dimensions")

# Information box
st.info("""
📌 **Composite Score Methodology**

The composite score is calculated from 4 equally-weighted components (25% each):

1. **Return Score (25%)** - Total return normalized to [0, 1]
2. **Risk Score (25%)** - Inverse of max drawdown (lower drawdown = higher score)
3. **Consistency Score (25%)** - Win rate percentage
4. **Robustness Score (25%)** - Based on number of trades (statistical significance)

**Why This Matters:**
- Sharpe ratio alone can be misleading (e.g., high Sharpe but low absolute return)
- Composite score finds strategies that excel across ALL dimensions
- Balances return, risk, consistency, and statistical robustness
""")

# Load data
with st.spinner("Loading backtest results..."):
    results = load_all_results()

if results['metadata']['total_strategies'] == 0:
    st.error("❌ No backtest results found. Please run backtests first.")
    st.stop()

strategies_df = results.get('strategies_df')

if strategies_df is None or strategies_df.empty:
    st.error("❌ No strategy data available")
    st.stop()

st.success(f"✅ Loaded {len(strategies_df)} strategies from {results['metadata']['total_universes']} universes")

# Try to load pre-calculated composite scores if available
composite_file = Path(__file__).parent.parent.parent / "ultra_necrozma_results" / "top_strategies_ranked.json"
use_precalculated = False

if composite_file.exists():
    try:
        with open(composite_file, 'r') as f:
            composite_data = json.load(f)
        
        # Extract top strategies
        top_strategies_list = composite_data.get('top_strategies', [])
        
        if top_strategies_list:
            composite_df = pd.DataFrame(top_strategies_list)
            use_precalculated = True
            st.info(f"📊 Using pre-calculated composite scores from `top_strategies_ranked.json`")
    except Exception as e:
        st.warning(f"⚠️ Could not load pre-calculated scores: {e}")

# Calculate composite scores on-the-fly if not available
if not use_precalculated:
    st.info("📊 Calculating composite scores from loaded strategies...")
    
    # Ensure required columns exist
    required_cols = ['total_return', 'max_drawdown', 'win_rate', 'n_trades']
    missing_cols = [col for col in required_cols if col not in strategies_df.columns]
    
    if missing_cols:
        st.error(f"❌ Missing required columns: {missing_cols}")
        st.stop()
    
    # Normalize scores to [0, 1]
    calc_df = strategies_df.copy()
    
    # Return score (normalize to 0-1)
    calc_df['return_score'] = (calc_df['total_return'] - calc_df['total_return'].min()) / \
                               (calc_df['total_return'].max() - calc_df['total_return'].min() + 1e-10)
    
    # Risk score (inverse of drawdown, normalized)
    calc_df['risk_score'] = 1 - ((calc_df['max_drawdown'] - calc_df['max_drawdown'].min()) / \
                                  (calc_df['max_drawdown'].max() - calc_df['max_drawdown'].min() + 1e-10))
    
    # Consistency score (win rate is already 0-1)
    calc_df['consistency_score'] = calc_df['win_rate']
    
    # Robustness score (based on number of trades, cap at 200)
    calc_df['robustness_score'] = np.minimum(calc_df['n_trades'] / 200.0, 1.0)
    
    # Composite score (equal weight)
    calc_df['composite_score'] = (
        calc_df['return_score'] * 0.25 +
        calc_df['risk_score'] * 0.25 +
        calc_df['consistency_score'] * 0.25 +
        calc_df['robustness_score'] * 0.25
    )
    
    # Sort by composite score
    composite_df = calc_df.nlargest(20, 'composite_score').copy()

# Display top 20 strategies
st.header("🏆 Top 20 Strategies by Composite Score")

# Create display dataframe
display_cols = ['strategy_name', 'composite_score']

# Add score breakdown if available
if 'return_score' in composite_df.columns:
    display_cols.extend(['return_score', 'risk_score', 'consistency_score', 'robustness_score'])

# Add key metrics
metric_cols = ['total_return', 'sharpe_ratio', 'win_rate', 'max_drawdown', 'profit_factor', 'n_trades', 'expectancy']
for col in metric_cols:
    if col in composite_df.columns:
        display_cols.append(col)

# Filter to available columns
display_cols = [col for col in display_cols if col in composite_df.columns]
display_df = composite_df[display_cols].copy()

# Format for display
if 'composite_score' in display_df.columns:
    display_df['composite_score'] = display_df['composite_score'].round(3)

if 'total_return' in display_df.columns:
    display_df['total_return_pct'] = (display_df['total_return'] * 100).round(2)
    
if 'win_rate' in display_df.columns:
    display_df['win_rate_pct'] = (display_df['win_rate'] * 100).round(2)
    
if 'max_drawdown' in display_df.columns:
    display_df['max_drawdown_pct'] = (display_df['max_drawdown'] * 100).round(2)

# Highlight best strategy
if not display_df.empty:
    best_strategy = display_df.iloc[0]
    
    st.success(f"""
    🥇 **Best Overall Strategy**: `{best_strategy.get('strategy_name', 'Unknown')}`
    - Composite Score: **{best_strategy.get('composite_score', 0):.3f}**
    - Total Return: **{best_strategy.get('total_return_pct', 0):.2f}%**
    - Sharpe Ratio: **{best_strategy.get('sharpe_ratio', 0):.2f}**
    - Win Rate: **{best_strategy.get('win_rate_pct', 0):.2f}%**
    """)

# Show table
st.dataframe(
    display_df,
    use_container_width=True,
    height=600,
    hide_index=True
)

# Score breakdown visualization
if 'return_score' in composite_df.columns:
    st.header("📊 Score Breakdown - Top 10 Strategies")
    
    top_10 = composite_df.head(10).copy()
    
    # Create stacked bar chart data
    score_data = []
    for _, row in top_10.iterrows():
        score_data.append({
            'Strategy': row['strategy_name'][:30] + '...' if len(row['strategy_name']) > 30 else row['strategy_name'],
            'Return': row.get('return_score', 0) * 0.25,
            'Risk': row.get('risk_score', 0) * 0.25,
            'Consistency': row.get('consistency_score', 0) * 0.25,
            'Robustness': row.get('robustness_score', 0) * 0.25,
        })
    
    score_breakdown_df = pd.DataFrame(score_data)
    
    # Create stacked bar chart
    import plotly.graph_objects as go
    
    fig = go.Figure()
    
    for component in ['Return', 'Risk', 'Consistency', 'Robustness']:
        fig.add_trace(go.Bar(
            name=component,
            x=score_breakdown_df['Strategy'],
            y=score_breakdown_df[component],
            text=score_breakdown_df[component].apply(lambda x: f'{x:.3f}'),
            textposition='inside'
        ))
    
    fig.update_layout(
        barmode='stack',
        title='Composite Score Components (Each component max 0.25)',
        xaxis_title='Strategy',
        yaxis_title='Score Contribution',
        height=500,
        showlegend=True,
        hovermode='x unified'
    )
    
    st.plotly_chart(fig, use_container_width=True)

# Download button
st.markdown("---")
st.header("📥 Export Data")

csv = display_df.to_csv(index=False)
st.download_button(
    label="📥 Download Top Strategies as CSV",
    data=csv,
    file_name="composite_ranking_top_strategies.csv",
    mime="text/csv"
)

# Insights
st.markdown("---")
st.header("💡 Key Insights")

col1, col2, col3 = st.columns(3)

with col1:
    if not composite_df.empty:
        avg_composite = composite_df['composite_score'].mean()
        st.metric("Avg Composite Score (Top 20)", f"{avg_composite:.3f}")

with col2:
    if 'total_return' in composite_df.columns:
        avg_return = composite_df['total_return'].mean() * 100
        st.metric("Avg Return (Top 20)", f"{avg_return:.2f}%")

with col3:
    if 'sharpe_ratio' in composite_df.columns:
        avg_sharpe = composite_df['sharpe_ratio'].mean()
        st.metric("Avg Sharpe (Top 20)", f"{avg_sharpe:.2f}")

st.markdown("""
### 🎯 How to Use This Page

1. **Compare with Sharpe Ranking**: Check if top composite strategies differ from top Sharpe strategies
2. **Look for Balance**: Best strategies should score well across all 4 components
3. **Avoid Extremes**: Strategies with 1.0 in one area but 0.0 in others may be risky
4. **Statistical Significance**: Higher robustness score = more reliable backtesting results

### 📈 Next Steps

- **Universe Analysis**: See if top strategies cluster in specific timeframes
- **Strategy Deep Dive**: Analyze the #1 composite strategy in detail
- **Risk Analysis**: Examine drawdown patterns of top performers
""")
