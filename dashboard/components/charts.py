#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚡🌟💎 NECROZMA DASHBOARD - CHARTS 💎🌟⚡

Plotly chart creation utilities
"""

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from typing import Dict, List, Optional


def create_bar_chart(df: pd.DataFrame, 
                     x: str, 
                     y: str, 
                     title: str = "",
                     color: str = None,
                     orientation: str = 'v') -> go.Figure:
    """
    Create interactive bar chart
    
    Args:
        df: DataFrame with data
        x: Column for x-axis
        y: Column for y-axis
        title: Chart title
        color: Column for color coding
        orientation: 'v' for vertical, 'h' for horizontal
        
    Returns:
        Plotly figure
    """
    fig = px.bar(df, x=x, y=y, title=title, color=color, orientation=orientation)
    
    fig.update_layout(
        template='plotly_white',
        hovermode='x unified',
        xaxis_title=x.replace('_', ' ').title(),
        yaxis_title=y.replace('_', ' ').title()
    )
    
    return fig


def create_scatter_plot(df: pd.DataFrame,
                       x: str,
                       y: str,
                       title: str = "",
                       color: str = None,
                       size: str = None,
                       hover_name: str = None) -> go.Figure:
    """
    Create scatter plot
    
    Args:
        df: DataFrame with data
        x: Column for x-axis
        y: Column for y-axis
        title: Chart title
        color: Column for color
        size: Column for size
        hover_name: Column for hover labels
        
    Returns:
        Plotly figure
    """
    fig = px.scatter(df, 
                     x=x, 
                     y=y, 
                     title=title,
                     color=color,
                     size=size,
                     hover_name=hover_name)
    
    fig.update_layout(
        template='plotly_white',
        xaxis_title=x.replace('_', ' ').title(),
        yaxis_title=y.replace('_', ' ').title()
    )
    
    return fig


def create_heatmap(data: pd.DataFrame,
                  title: str = "",
                  x_label: str = "",
                  y_label: str = "",
                  colorscale: str = 'RdYlGn') -> go.Figure:
    """
    Create heatmap
    
    Args:
        data: DataFrame with matrix data
        title: Chart title
        x_label: X-axis label
        y_label: Y-axis label
        colorscale: Color scale name
        
    Returns:
        Plotly figure
    """
    fig = go.Figure(data=go.Heatmap(
        z=data.values,
        x=data.columns,
        y=data.index,
        colorscale=colorscale,
        hoverongaps=False
    ))
    
    fig.update_layout(
        title=title,
        xaxis_title=x_label,
        yaxis_title=y_label,
        template='plotly_white'
    )
    
    return fig


def create_equity_curve(trades_df: pd.DataFrame, 
                       initial_capital: float = 10000) -> go.Figure:
    """
    Create equity curve from trades
    
    Args:
        trades_df: DataFrame with trade data (must have 'pnl' or 'pnl_usd')
        initial_capital: Starting capital
        
    Returns:
        Plotly figure
    """
    # Calculate cumulative P&L
    pnl_col = 'pnl_usd' if 'pnl_usd' in trades_df.columns else 'pnl'
    
    if pnl_col not in trades_df.columns:
        # Empty figure
        fig = go.Figure()
        fig.add_annotation(text="No P&L data available", 
                          xref="paper", yref="paper",
                          x=0.5, y=0.5, showarrow=False)
        return fig
    
    equity = [initial_capital] + (initial_capital + trades_df[pnl_col].cumsum()).tolist()
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        y=equity,
        mode='lines',
        name='Equity',
        line=dict(color='#2E86AB', width=2),
        fill='tozeroy',
        fillcolor='rgba(46, 134, 171, 0.1)'
    ))
    
    # Add benchmark line
    fig.add_hline(y=initial_capital, 
                  line_dash="dash", 
                  line_color="gray",
                  annotation_text="Initial Capital")
    
    fig.update_layout(
        title='Equity Curve',
        xaxis_title='Trade Number',
        yaxis_title='Equity ($)',
        template='plotly_white',
        hovermode='x unified'
    )
    
    return fig


def create_drawdown_chart(equity_curve: pd.Series) -> go.Figure:
    """
    Create drawdown chart
    
    Args:
        equity_curve: Series with equity values
        
    Returns:
        Plotly figure
    """
    if len(equity_curve) < 2:
        fig = go.Figure()
        fig.add_annotation(text="Insufficient data for drawdown chart", 
                          xref="paper", yref="paper",
                          x=0.5, y=0.5, showarrow=False)
        return fig
    
    # Calculate drawdown
    running_max = equity_curve.expanding().max()
    drawdown = (equity_curve - running_max) / running_max * 100
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        y=drawdown,
        mode='lines',
        name='Drawdown',
        line=dict(color='#E63946', width=2),
        fill='tozeroy',
        fillcolor='rgba(230, 57, 70, 0.2)'
    ))
    
    fig.update_layout(
        title='Underwater Equity Curve (Drawdown)',
        xaxis_title='Trade Number',
        yaxis_title='Drawdown (%)',
        template='plotly_white',
        hovermode='x unified'
    )
    
    return fig


def create_pie_chart(values: List[float], 
                    labels: List[str], 
                    title: str = "") -> go.Figure:
    """
    Create pie chart
    
    Args:
        values: List of values
        labels: List of labels
        title: Chart title
        
    Returns:
        Plotly figure
    """
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0.3
    )])
    
    fig.update_layout(
        title=title,
        template='plotly_white'
    )
    
    return fig


def create_histogram(data: pd.Series, 
                    title: str = "",
                    x_label: str = "",
                    bins: int = 30) -> go.Figure:
    """
    Create histogram
    
    Args:
        data: Series with data
        title: Chart title
        x_label: X-axis label
        bins: Number of bins
        
    Returns:
        Plotly figure
    """
    fig = go.Figure(data=[go.Histogram(
        x=data,
        nbinsx=bins,
        marker_color='#2E86AB'
    )])
    
    fig.update_layout(
        title=title,
        xaxis_title=x_label,
        yaxis_title='Frequency',
        template='plotly_white'
    )
    
    return fig


def create_box_plot(df: pd.DataFrame,
                   y: str,
                   x: str = None,
                   title: str = "") -> go.Figure:
    """
    Create box plot
    
    Args:
        df: DataFrame with data
        y: Column for y-axis
        x: Optional column for grouping
        title: Chart title
        
    Returns:
        Plotly figure
    """
    fig = px.box(df, y=y, x=x, title=title)
    
    fig.update_layout(
        template='plotly_white',
        yaxis_title=y.replace('_', ' ').title()
    )
    
    return fig


def create_line_chart(df: pd.DataFrame,
                     x: str,
                     y: str,
                     title: str = "",
                     color: str = None) -> go.Figure:
    """
    Create line chart
    
    Args:
        df: DataFrame with data
        x: Column for x-axis
        y: Column for y-axis
        title: Chart title
        color: Column for color grouping
        
    Returns:
        Plotly figure
    """
    fig = px.line(df, x=x, y=y, title=title, color=color)
    
    fig.update_layout(
        template='plotly_white',
        xaxis_title=x.replace('_', ' ').title(),
        yaxis_title=y.replace('_', ' ').title(),
        hovermode='x unified'
    )
    
    return fig
