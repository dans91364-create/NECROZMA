#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚡🌟💎 NECROZMA - Monte Carlo Simulation Component 💎🌟⚡

Monte Carlo simulation for strategy performance - LIMITED TO TOP 10 STRATEGIES ONLY
"""

import plotly.graph_objects as go
import pandas as pd
import numpy as np
from typing import List, Dict, Optional


def render_monte_carlo(
    trades: List[Dict],
    simulations: int = 1000,
    initial_capital: float = 10000.0
) -> go.Figure:
    """
    Generate Monte Carlo simulation chart - SÓ PARA TOP 10 ESTRATÉGIAS
    
    Simulates random trade order to show:
    - Pessimistic scenario (5th percentile)
    - Median scenario (50th percentile)
    - Optimistic scenario (95th percentile)
    - Probability of profit
    - Probability of ruin
    
    Args:
        trades: List of trade dictionaries with 'profit' key
        simulations: Number of Monte Carlo simulations (default: 1000)
        initial_capital: Starting capital
        
    Returns:
        Plotly figure object
    """
    if not trades:
        # Empty chart
        fig = go.Figure()
        fig.add_annotation(
            text="No trades available",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=20)
        )
        return fig
    
    # Extract profits
    profits = np.array([t['profit'] for t in trades])
    n_trades = len(profits)
    
    # Run Monte Carlo simulations
    simulated_equity_curves = []
    final_equities = []
    
    np.random.seed(42)
    
    for sim in range(simulations):
        # Randomly shuffle trade order
        shuffled_profits = np.random.choice(profits, size=n_trades, replace=True)
        
        # Calculate equity curve
        cumulative_profit = np.cumsum(shuffled_profits)
        equity_curve = initial_capital + cumulative_profit
        
        simulated_equity_curves.append(equity_curve)
        final_equities.append(equity_curve[-1])
    
    # Convert to array for percentile calculations
    simulated_equity_curves = np.array(simulated_equity_curves)
    
    # Calculate percentiles at each point
    p5 = np.percentile(simulated_equity_curves, 5, axis=0)    # Pessimistic
    p50 = np.percentile(simulated_equity_curves, 50, axis=0)   # Median
    p95 = np.percentile(simulated_equity_curves, 95, axis=0)   # Optimistic
    
    # Calculate statistics
    final_equities = np.array(final_equities)
    prob_profit = (final_equities > initial_capital).mean() * 100
    prob_ruin = (final_equities < initial_capital * 0.5).mean() * 100  # 50% loss = ruin
    
    median_final = np.median(final_equities)
    pessimistic_final = np.percentile(final_equities, 5)
    optimistic_final = np.percentile(final_equities, 95)
    
    # Create figure
    fig = go.Figure()
    
    # Trade numbers for x-axis
    trade_nums = list(range(1, n_trades + 1))
    
    # Optimistic scenario (95th percentile)
    fig.add_trace(go.Scatter(
        x=trade_nums,
        y=p95,
        mode='lines',
        name='Optimistic (95%)',
        line=dict(color='rgba(72, 187, 120, 0.8)', width=2),
        hovertemplate='<b>Trade:</b> %{x}<br><b>Equity:</b> $%{y:,.2f}<extra></extra>'
    ))
    
    # Median scenario (50th percentile)
    fig.add_trace(go.Scatter(
        x=trade_nums,
        y=p50,
        mode='lines',
        name='Median (50%)',
        line=dict(color='#667eea', width=3),
        hovertemplate='<b>Trade:</b> %{x}<br><b>Equity:</b> $%{y:,.2f}<extra></extra>'
    ))
    
    # Pessimistic scenario (5th percentile)
    fig.add_trace(go.Scatter(
        x=trade_nums,
        y=p5,
        mode='lines',
        name='Pessimistic (5%)',
        line=dict(color='rgba(245, 101, 101, 0.8)', width=2),
        hovertemplate='<b>Trade:</b> %{x}<br><b>Equity:</b> $%{y:,.2f}<extra></extra>'
    ))
    
    # Fill between optimistic and pessimistic
    fig.add_trace(go.Scatter(
        x=trade_nums + trade_nums[::-1],
        y=list(p95) + list(p5[::-1]),
        fill='toself',
        fillcolor='rgba(102, 126, 234, 0.1)',
        line=dict(color='rgba(255,255,255,0)'),
        showlegend=False,
        hoverinfo='skip'
    ))
    
    # Layout
    fig.update_layout(
        title=dict(
            text=f'Monte Carlo Simulation ({simulations:,} runs)<br>'
                 f'<sub>Profit Prob: {prob_profit:.1f}% | Ruin Prob: {prob_ruin:.1f}% | '
                 f'Median Final: ${median_final:,.0f}</sub>',
            x=0.5,
            xanchor='center'
        ),
        xaxis_title='Trade Number',
        yaxis_title='Equity ($)',
        hovermode='x unified',
        template='plotly_white',
        height=500,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    # Add horizontal line for initial capital
    fig.add_hline(
        y=initial_capital,
        line_dash="dot",
        line_color="gray",
        annotation_text="Initial Capital",
        annotation_position="right"
    )
    
    # Add ruin level (50% loss)
    fig.add_hline(
        y=initial_capital * 0.5,
        line_dash="dot",
        line_color="red",
        annotation_text="Ruin Level (-50%)",
        annotation_position="right"
    )
    
    return fig


def calculate_monte_carlo_stats(
    trades: List[Dict],
    simulations: int = 1000,
    initial_capital: float = 10000.0
) -> Dict:
    """
    Calculate Monte Carlo statistics without visualization
    
    Args:
        trades: List of trade dictionaries
        simulations: Number of simulations
        initial_capital: Starting capital
        
    Returns:
        Dictionary with Monte Carlo statistics
    """
    if not trades:
        return {}
    
    profits = np.array([t['profit'] for t in trades])
    n_trades = len(profits)
    
    final_equities = []
    max_drawdowns = []
    
    np.random.seed(42)
    
    for sim in range(simulations):
        shuffled_profits = np.random.choice(profits, size=n_trades, replace=True)
        cumulative_profit = np.cumsum(shuffled_profits)
        equity_curve = initial_capital + cumulative_profit
        
        # Final equity
        final_equities.append(equity_curve[-1])
        
        # Max drawdown
        peak = np.maximum.accumulate(equity_curve)
        drawdown = equity_curve - peak
        max_dd = drawdown.min()
        max_drawdowns.append(max_dd)
    
    final_equities = np.array(final_equities)
    max_drawdowns = np.array(max_drawdowns)
    
    return {
        'prob_profit': (final_equities > initial_capital).mean() * 100,
        'prob_ruin': (final_equities < initial_capital * 0.5).mean() * 100,
        'median_final': np.median(final_equities),
        'p5_final': np.percentile(final_equities, 5),
        'p95_final': np.percentile(final_equities, 95),
        'median_max_dd': np.median(max_drawdowns),
        'p95_max_dd': np.percentile(max_drawdowns, 95),
    }


if __name__ == "__main__":
    # Test with dummy data
    np.random.seed(42)
    n_trades = 100
    
    trades = []
    for i in range(n_trades):
        # Random profit/loss with positive expectancy
        profit = np.random.normal(50, 100)
        trades.append({'profit': profit})
    
    fig = render_monte_carlo(trades, simulations=1000)
    fig.show()
    
    stats = calculate_monte_carlo_stats(trades, simulations=1000)
    print("\nMonte Carlo Statistics:")
    for key, value in stats.items():
        print(f"  {key}: {value:.2f}")
