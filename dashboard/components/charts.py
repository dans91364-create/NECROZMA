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


def create_performance_matrix(df: pd.DataFrame,
                              index_col: str,
                              columns_col: str,
                              values_col: str,
                              title: str = "",
                              colorscale: str = 'RdYlGn') -> go.Figure:
    """
    Create performance matrix heatmap (e.g., Strategy Templates vs Lot Sizes)
    
    Args:
        df: DataFrame with data
        index_col: Column for y-axis (rows)
        columns_col: Column for x-axis (columns)
        values_col: Column for values to display
        title: Chart title
        colorscale: Color scale
        
    Returns:
        Plotly figure
    """
    # Create pivot table
    pivot = df.pivot_table(
        values=values_col,
        index=index_col,
        columns=columns_col,
        aggfunc='mean'
    )
    
    fig = go.Figure(data=go.Heatmap(
        z=pivot.values,
        x=pivot.columns,
        y=pivot.index,
        colorscale=colorscale,
        hoverongaps=False,
        text=pivot.values.round(2),
        texttemplate='%{text}',
        textfont={"size": 10}
    ))
    
    fig.update_layout(
        title=title,
        xaxis_title=columns_col.replace('_', ' ').title(),
        yaxis_title=index_col.replace('_', ' ').title(),
        template='plotly_white'
    )
    
    return fig


def create_distribution_chart(data: pd.Series,
                             title: str = "",
                             x_label: str = "",
                             bins: int = 30,
                             show_stats: bool = True) -> go.Figure:
    """
    Create distribution histogram with optional statistics overlay
    
    Args:
        data: Series with data
        title: Chart title
        x_label: X-axis label
        bins: Number of bins
        show_stats: Whether to show mean/median lines
        
    Returns:
        Plotly figure
    """
    fig = go.Figure(data=[go.Histogram(
        x=data,
        nbinsx=bins,
        marker_color='#667eea',
        name='Distribution'
    )])
    
    if show_stats and len(data) > 0:
        mean_val = data.mean()
        median_val = data.median()
        
        # Add mean line
        fig.add_vline(
            x=mean_val,
            line_dash="dash",
            line_color="red",
            annotation_text=f"Mean: {mean_val:.2f}",
            annotation_position="top"
        )
        
        # Add median line
        fig.add_vline(
            x=median_val,
            line_dash="dot",
            line_color="green",
            annotation_text=f"Median: {median_val:.2f}",
            annotation_position="bottom"
        )
    
    fig.update_layout(
        title=title,
        xaxis_title=x_label,
        yaxis_title='Frequency',
        template='plotly_white',
        showlegend=False
    )
    
    return fig


def create_comparison_chart(df: pd.DataFrame,
                           strategies: List[str],
                           metrics: List[str],
                           title: str = "Strategy Comparison") -> go.Figure:
    """
    Create grouped bar chart comparing strategies across metrics
    
    Args:
        df: DataFrame with strategy data
        strategies: List of strategy names to compare
        metrics: List of metric columns to show
        title: Chart title
        
    Returns:
        Plotly figure
    """
    # Filter to selected strategies
    comparison_df = df[df['strategy_name'].isin(strategies)][['strategy_name'] + metrics]
    
    # Melt for grouped bar chart
    melted = comparison_df.melt(
        id_vars=['strategy_name'],
        value_vars=metrics,
        var_name='Metric',
        value_name='Value'
    )
    
    fig = px.bar(
        melted,
        x='Metric',
        y='Value',
        color='strategy_name',
        barmode='group',
        title=title
    )
    
    fig.update_layout(
        template='plotly_white',
        xaxis_title='Metric',
        yaxis_title='Value',
        legend_title='Strategy'
    )
    
    return fig


def create_pareto_chart(df: pd.DataFrame,
                       x: str,
                       y: str,
                       title: str = "Pareto Frontier") -> go.Figure:
    """
    Create Pareto frontier scatter plot
    
    Args:
        df: DataFrame with data
        x: Column for x-axis (typically risk metric)
        y: Column for y-axis (typically return metric)
        title: Chart title
        
    Returns:
        Plotly figure
    """
    fig = px.scatter(
        df,
        x=x,
        y=y,
        title=title,
        hover_name='strategy_name' if 'strategy_name' in df.columns else None,
        color=y,
        size=y,
        color_continuous_scale='Viridis'
    )
    
    fig.update_layout(
        template='plotly_white',
        xaxis_title=x.replace('_', ' ').title(),
        yaxis_title=y.replace('_', ' ').title()
    )
    
    return fig
