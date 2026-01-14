#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚡🌟💎 NECROZMA - Equity Curve Component 💎🌟⚡

Equity curve visualization for backtest results
"""

import plotly.graph_objects as go
import pandas as pd
import numpy as np
from typing import List, Dict, Optional


def render_equity_curve(
    trades: List[Dict],
    initial_capital: float = 10000.0
) -> go.Figure:
    """
    Generate equity curve chart from trades
    
    Args:
        trades: List of trade dictionaries with 'exit_time' and 'profit' keys
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
    
    # Convert trades to DataFrame
    df = pd.DataFrame(trades)
    
    # Sort by exit time
    df = df.sort_values('exit_time')
    
    # Calculate cumulative profit
    df['cumulative_profit'] = df['profit'].cumsum()
    df['equity'] = initial_capital + df['cumulative_profit']
    
    # Calculate peak (running maximum)
    df['peak'] = df['equity'].cummax()
    
    # Calculate drawdown
    df['drawdown'] = df['equity'] - df['peak']
    df['drawdown_pct'] = (df['drawdown'] / df['peak']) * 100
    
    # Stats
    final_equity = df['equity'].iloc[-1]
    peak_equity = df['peak'].max()
    max_drawdown = df['drawdown'].min()
    max_drawdown_pct = df['drawdown_pct'].min()
    total_return = ((final_equity - initial_capital) / initial_capital) * 100
    
    # Create figure
    fig = go.Figure()
    
    # Equity curve
    fig.add_trace(go.Scatter(
        x=df['exit_time'],
        y=df['equity'],
        mode='lines',
        name='Equity',
        line=dict(color='#667eea', width=2),
        hovertemplate='<b>Time:</b> %{x}<br><b>Equity:</b> $%{y:,.2f}<extra></extra>'
    ))
    
    # Peak equity (running high)
    fig.add_trace(go.Scatter(
        x=df['exit_time'],
        y=df['peak'],
        mode='lines',
        name='Peak',
        line=dict(color='#48bb78', width=1, dash='dash'),
        hovertemplate='<b>Time:</b> %{x}<br><b>Peak:</b> $%{y:,.2f}<extra></extra>'
    ))
    
    # Highlight drawdown periods (when equity < peak)
    drawdown_mask = df['equity'] < df['peak']
    if drawdown_mask.any():
        fig.add_trace(go.Scatter(
            x=df[drawdown_mask]['exit_time'],
            y=df[drawdown_mask]['equity'],
            mode='markers',
            name='Drawdown',
            marker=dict(color='#f56565', size=3),
            hovertemplate='<b>Time:</b> %{x}<br><b>Equity:</b> $%{y:,.2f}<br><b>DD:</b> %{customdata:.2f}%<extra></extra>',
            customdata=df[drawdown_mask]['drawdown_pct']
        ))
    
    # Layout
    fig.update_layout(
        title=dict(
            text=f'Equity Curve<br><sub>Final: ${final_equity:,.2f} | Peak: ${peak_equity:,.2f} | Return: {total_return:.2f}% | Max DD: {max_drawdown_pct:.2f}%</sub>',
            x=0.5,
            xanchor='center'
        ),
        xaxis_title='Time',
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
    
    return fig


if __name__ == "__main__":
    # Test with dummy data
    import datetime
    
    np.random.seed(42)
    n_trades = 100
    
    trades = []
    current_time = datetime.datetime(2025, 1, 1)
    
    for i in range(n_trades):
        # Random profit/loss
        profit = np.random.normal(50, 100)
        
        trades.append({
            'exit_time': current_time,
            'profit': profit
        })
        
        # Increment time
        current_time += datetime.timedelta(hours=np.random.randint(1, 24))
    
    fig = render_equity_curve(trades)
    fig.show()
