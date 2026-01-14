#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚡🌟💎 NECROZMA - Performance Heatmap Component 💎🌟⚡

Hour/Day performance heatmap for backtest results
"""

import plotly.graph_objects as go
import pandas as pd
import numpy as np
from typing import List, Dict


def render_performance_heatmap(trades: List[Dict]) -> go.Figure:
    """
    Generate performance heatmap by hour and day
    
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
    
    # Extract hour and day from exit_time
    df['exit_time'] = pd.to_datetime(df['exit_time'])
    df['hour'] = df['exit_time'].dt.hour
    df['day'] = df['exit_time'].dt.day_name()
    
    # Define hour bins (6 bins of 4 hours each)
    hour_bins = [
        (0, 4, '00:00-04:00'),
        (4, 8, '04:00-08:00'),
        (8, 12, '08:00-12:00'),
        (12, 16, '12:00-16:00'),
        (16, 20, '16:00-20:00'),
        (20, 24, '20:00-24:00'),
    ]
    
    # Map hours to bins
    def map_hour_to_bin(hour):
        for start, end, label in hour_bins:
            if start <= hour < end:
                return label
        return '00:00-04:00'
    
    df['hour_bin'] = df['hour'].apply(map_hour_to_bin)
    
    # Define day order
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    
    # Create pivot table
    pivot = df.pivot_table(
        values='profit',
        index='hour_bin',
        columns='day',
        aggfunc='sum',
        fill_value=0
    )
    
    # Reorder columns by day
    pivot = pivot.reindex(columns=[d for d in day_order if d in pivot.columns])
    
    # Reorder rows by hour bin
    hour_labels = [label for _, _, label in hour_bins]
    pivot = pivot.reindex([h for h in hour_labels if h in pivot.index])
    
    # Count trades per cell
    trade_counts = df.pivot_table(
        values='profit',
        index='hour_bin',
        columns='day',
        aggfunc='count',
        fill_value=0
    )
    trade_counts = trade_counts.reindex(columns=[d for d in day_order if d in trade_counts.columns])
    trade_counts = trade_counts.reindex([h for h in hour_labels if h in trade_counts.index])
    
    # Create hovertext
    hovertext = []
    for i, hour in enumerate(pivot.index):
        row = []
        for j, day in enumerate(pivot.columns):
            profit = pivot.iloc[i, j]
            count = trade_counts.iloc[i, j]
            row.append(f'Day: {day}<br>Time: {hour}<br>Trades: {int(count)}<br>Profit: ${profit:.2f}')
        hovertext.append(row)
    
    # Create heatmap
    fig = go.Figure(data=go.Heatmap(
        z=pivot.values,
        x=pivot.columns,
        y=pivot.index,
        colorscale=[
            [0, '#f56565'],      # Red for losses
            [0.5, '#ffffff'],    # White for neutral
            [1, '#48bb78']       # Green for profits
        ],
        zmid=0,
        text=hovertext,
        hovertemplate='%{text}<extra></extra>',
        colorbar=dict(title='Profit ($)')
    ))
    
    # Layout
    fig.update_layout(
        title=dict(
            text='Performance Heatmap<br><sub>Profit/Loss by Day and Time</sub>',
            x=0.5,
            xanchor='center'
        ),
        xaxis_title='Day of Week',
        yaxis_title='Time Period (UTC)',
        template='plotly_white',
        height=500,
    )
    
    return fig


if __name__ == "__main__":
    # Test with dummy data
    import datetime
    
    np.random.seed(42)
    n_trades = 200
    
    trades = []
    current_time = datetime.datetime(2025, 1, 6)  # Monday
    
    for i in range(n_trades):
        # Random profit/loss, with some patterns
        hour = current_time.hour
        day = current_time.weekday()
        
        # London session (8-16) tends to be profitable
        if 8 <= hour < 16:
            profit = np.random.normal(80, 50)
        # NY session (13-21) mixed
        elif 13 <= hour < 21:
            profit = np.random.normal(30, 70)
        # Tokyo session (0-8) less profitable
        else:
            profit = np.random.normal(-20, 60)
        
        trades.append({
            'exit_time': current_time,
            'profit': profit
        })
        
        # Increment time (random 1-12 hours)
        current_time += datetime.timedelta(hours=np.random.randint(1, 13))
    
    fig = render_performance_heatmap(trades)
    fig.show()
