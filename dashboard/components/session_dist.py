#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚡🌟💎 NECROZMA - Session Distribution Component 💎🌟⚡

Trading session distribution and performance analysis
"""

import plotly.graph_objects as go
import pandas as pd
import numpy as np
from typing import List, Dict


def render_session_distribution(trades: List[Dict]) -> go.Figure:
    """
    Generate session distribution chart
    
    Sessions:
    - London: 08:00-16:00 UTC
    - New York: 13:00-21:00 UTC
    - Tokyo: 00:00-08:00 UTC
    - Overlap periods
    
    Args:
        trades: List of trade dictionaries with 'exit_time' and 'profit' keys
        
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
    
    # Convert to DataFrame
    df = pd.DataFrame(trades)
    df['exit_time'] = pd.to_datetime(df['exit_time'])
    df['hour'] = df['exit_time'].dt.hour
    
    # Define sessions
    def classify_session(hour):
        sessions = []
        
        # Tokyo: 00:00-08:00
        if 0 <= hour < 8:
            sessions.append('Tokyo')
        
        # London: 08:00-16:00
        if 8 <= hour < 16:
            sessions.append('London')
        
        # New York: 13:00-21:00
        if 13 <= hour < 21:
            sessions.append('New York')
        
        # Overlaps
        if 13 <= hour < 16:
            return 'London-NY Overlap'
        elif len(sessions) > 1:
            return '-'.join(sessions)
        elif len(sessions) == 1:
            return sessions[0]
        else:
            return 'Off-Hours'
    
    df['session'] = df['hour'].apply(classify_session)
    
    # Calculate stats per session
    session_stats = df.groupby('session').agg({
        'profit': ['sum', 'count', 'mean']
    }).reset_index()
    
    session_stats.columns = ['session', 'total_profit', 'trade_count', 'avg_profit']
    
    # Calculate win rate
    wins_per_session = df[df['profit'] > 0].groupby('session').size()
    session_stats['win_rate'] = session_stats.apply(
        lambda row: (wins_per_session.get(row['session'], 0) / row['trade_count'] * 100) 
        if row['trade_count'] > 0 else 0,
        axis=1
    )
    
    # Sort by total profit
    session_stats = session_stats.sort_values('total_profit', ascending=True)
    
    # Create figure with subplots
    from plotly.subplots import make_subplots
    
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=(
            'Total Profit by Session',
            'Trade Count by Session',
            'Average Profit per Trade',
            'Win Rate by Session'
        ),
        specs=[
            [{'type': 'bar'}, {'type': 'bar'}],
            [{'type': 'bar'}, {'type': 'bar'}]
        ]
    )
    
    # Total profit
    fig.add_trace(
        go.Bar(
            x=session_stats['total_profit'],
            y=session_stats['session'],
            orientation='h',
            marker_color=['#48bb78' if x > 0 else '#f56565' for x in session_stats['total_profit']],
            text=[f'${x:.0f}' for x in session_stats['total_profit']],
            textposition='auto',
            hovertemplate='<b>%{y}</b><br>Profit: $%{x:.2f}<extra></extra>'
        ),
        row=1, col=1
    )
    
    # Trade count
    fig.add_trace(
        go.Bar(
            x=session_stats['trade_count'],
            y=session_stats['session'],
            orientation='h',
            marker_color='#667eea',
            text=[f'{int(x)}' for x in session_stats['trade_count']],
            textposition='auto',
            hovertemplate='<b>%{y}</b><br>Trades: %{x}<extra></extra>'
        ),
        row=1, col=2
    )
    
    # Average profit
    fig.add_trace(
        go.Bar(
            x=session_stats['avg_profit'],
            y=session_stats['session'],
            orientation='h',
            marker_color=['#48bb78' if x > 0 else '#f56565' for x in session_stats['avg_profit']],
            text=[f'${x:.0f}' for x in session_stats['avg_profit']],
            textposition='auto',
            hovertemplate='<b>%{y}</b><br>Avg: $%{x:.2f}<extra></extra>'
        ),
        row=2, col=1
    )
    
    # Win rate
    fig.add_trace(
        go.Bar(
            x=session_stats['win_rate'],
            y=session_stats['session'],
            orientation='h',
            marker_color=['#48bb78' if x > 50 else '#f56565' for x in session_stats['win_rate']],
            text=[f'{x:.0f}%' for x in session_stats['win_rate']],
            textposition='auto',
            hovertemplate='<b>%{y}</b><br>Win Rate: %{x:.1f}%<extra></extra>'
        ),
        row=2, col=2
    )
    
    # Update axes
    fig.update_xaxes(title_text="Profit ($)", row=1, col=1)
    fig.update_xaxes(title_text="Trades", row=1, col=2)
    fig.update_xaxes(title_text="Avg Profit ($)", row=2, col=1)
    fig.update_xaxes(title_text="Win Rate (%)", row=2, col=2)
    
    # Layout
    fig.update_layout(
        title=dict(
            text='Session Distribution Analysis<br><sub>Performance across London, New York, and Tokyo sessions</sub>',
            x=0.5,
            xanchor='center'
        ),
        showlegend=False,
        template='plotly_white',
        height=700,
    )
    
    return fig


if __name__ == "__main__":
    # Test with dummy data
    import datetime
    
    np.random.seed(42)
    n_trades = 300
    
    trades = []
    current_time = datetime.datetime(2025, 1, 1)
    
    for i in range(n_trades):
        hour = current_time.hour
        
        # Session-based profitability patterns
        if 13 <= hour < 16:  # London-NY overlap
            profit = np.random.normal(100, 50)
        elif 8 <= hour < 16:  # London
            profit = np.random.normal(60, 60)
        elif 13 <= hour < 21:  # New York
            profit = np.random.normal(40, 70)
        elif 0 <= hour < 8:  # Tokyo
            profit = np.random.normal(20, 50)
        else:  # Off-hours
            profit = np.random.normal(-30, 40)
        
        trades.append({
            'exit_time': current_time,
            'profit': profit
        })
        
        # Increment time
        current_time += datetime.timedelta(hours=np.random.randint(1, 6))
    
    fig = render_session_distribution(trades)
    fig.show()
