#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚡🌟💎 NECROZMA - Drawdown Chart Component 💎🌟⚡

Drawdown visualization for backtest results
"""

import plotly.graph_objects as go
import pandas as pd
import numpy as np
from typing import List, Dict, Optional


def render_drawdown_chart(
    trades: List[Dict],
    initial_capital: float = 10000.0
) -> go.Figure:
    """
    Generate drawdown chart from trades
    
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
    
    # Calculate cumulative profit and equity
    df['cumulative_profit'] = df['profit'].cumsum()
    df['equity'] = initial_capital + df['cumulative_profit']
    
    # Calculate peak (running maximum)
    df['peak'] = df['equity'].cummax()
    
    # Calculate drawdown
    df['drawdown'] = df['equity'] - df['peak']
    df['drawdown_pct'] = (df['drawdown'] / df['peak']) * 100
    
    # Stats
    max_drawdown = df['drawdown'].min()
    max_drawdown_pct = df['drawdown_pct'].min()
    avg_drawdown = df[df['drawdown'] < 0]['drawdown'].mean() if (df['drawdown'] < 0).any() else 0
    avg_drawdown_pct = df[df['drawdown_pct'] < 0]['drawdown_pct'].mean() if (df['drawdown_pct'] < 0).any() else 0
    
    # Calculate recovery time (time spent in drawdown)
    in_drawdown = df['drawdown'] < 0
    total_time = (df['exit_time'].iloc[-1] - df['exit_time'].iloc[0]).total_seconds() / 3600  # hours
    underwater_periods = in_drawdown.sum()
    underwater_pct = (underwater_periods / len(df)) * 100 if len(df) > 0 else 0
    
    # Create figure
    fig = go.Figure()
    
    # Drawdown area chart
    fig.add_trace(go.Scatter(
        x=df['exit_time'],
        y=df['drawdown_pct'],
        mode='lines',
        name='Drawdown %',
        fill='tozeroy',
        line=dict(color='#f56565', width=2),
        fillcolor='rgba(245, 101, 101, 0.3)',
        hovertemplate='<b>Time:</b> %{x}<br><b>Drawdown:</b> %{y:.2f}%<br><b>Dollar:</b> $%{customdata:,.2f}<extra></extra>',
        customdata=df['drawdown']
    ))
    
    # Layout
    fig.update_layout(
        title=dict(
            text=f'Drawdown Chart<br><sub>Max DD: {max_drawdown_pct:.2f}% (${max_drawdown:,.2f}) | Avg DD: {avg_drawdown_pct:.2f}% | Underwater: {underwater_pct:.1f}% of time</sub>',
            x=0.5,
            xanchor='center'
        ),
        xaxis_title='Time',
        yaxis_title='Drawdown (%)',
        hovermode='x unified',
        template='plotly_white',
        height=400,
        showlegend=False
    )
    
    # Reverse y-axis so drawdowns appear as drops
    fig.update_yaxes(autorange='reversed')
    
    # Add horizontal line at 0
    fig.add_hline(
        y=0,
        line_dash="solid",
        line_color="gray",
        line_width=1
    )
    
    # Add max drawdown annotation
    if max_drawdown_pct < 0:
        max_dd_time = df[df['drawdown_pct'] == max_drawdown_pct]['exit_time'].iloc[0]
        fig.add_annotation(
            x=max_dd_time,
            y=max_drawdown_pct,
            text=f"Max DD: {max_drawdown_pct:.2f}%",
            showarrow=True,
            arrowhead=2,
            arrowcolor="#f56565",
            font=dict(color="#f56565", size=12),
            bgcolor="white",
            bordercolor="#f56565",
            borderwidth=1
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
        # Random profit/loss with some losing streaks
        if i % 10 < 3:
            profit = np.random.normal(-80, 30)  # Losing period
        else:
            profit = np.random.normal(50, 40)  # Winning period
        
        trades.append({
            'exit_time': current_time,
            'profit': profit
        })
        
        # Increment time
        current_time += datetime.timedelta(hours=np.random.randint(1, 24))
    
    fig = render_drawdown_chart(trades)
    fig.show()
