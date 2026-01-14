#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚡🌟💎 NECROZMA - Trade Statistics Component 💎🌟⚡

Detailed trade statistics for backtest results
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Optional
from dash import html, dcc
import plotly.graph_objects as go


def render_trade_stats(trades: List[Dict]) -> html.Div:
    """
    Generate detailed trade statistics
    
    Args:
        trades: List of trade dictionaries
        
    Returns:
        Dash HTML Div with statistics
    """
    if not trades:
        return html.Div("No trades available", className="text-center text-gray-500")
    
    # Convert to DataFrame
    df = pd.DataFrame(trades)
    
    # Separate wins and losses
    wins = df[df['profit'] > 0]
    losses = df[df['profit'] < 0]
    
    # Basic stats
    total_trades = len(df)
    winning_trades = len(wins)
    losing_trades = len(losses)
    win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
    
    # Profit stats
    avg_win = wins['profit'].mean() if len(wins) > 0 else 0
    avg_loss = losses['profit'].mean() if len(losses) > 0 else 0
    largest_win = df['profit'].max()
    largest_loss = df['profit'].min()
    
    # Duration stats (if available)
    if 'duration_hours' in df.columns:
        avg_duration_win = wins['duration_hours'].mean() if len(wins) > 0 else 0
        avg_duration_loss = losses['duration_hours'].mean() if len(losses) > 0 else 0
    else:
        avg_duration_win = 0
        avg_duration_loss = 0
    
    # Consecutive wins/losses
    df['is_win'] = df['profit'] > 0
    df['streak'] = (df['is_win'] != df['is_win'].shift()).cumsum()
    streaks = df.groupby(['streak', 'is_win']).size()
    
    max_consecutive_wins = streaks[streaks.index.get_level_values(1) == True].max() if (streaks.index.get_level_values(1) == True).any() else 0
    max_consecutive_losses = streaks[streaks.index.get_level_values(1) == False].max() if (streaks.index.get_level_values(1) == False).any() else 0
    
    # Session analysis (if available)
    session_stats = {}
    if 'session' in df.columns:
        for session in df['session'].unique():
            session_trades = df[df['session'] == session]
            session_stats[session] = {
                'trades': len(session_trades),
                'profit': session_trades['profit'].sum(),
                'win_rate': (session_trades['profit'] > 0).mean() * 100
            }
    
    # Expectancy
    expectancy = (win_rate / 100 * avg_win) + ((1 - win_rate / 100) * avg_loss)
    
    # Profit factor
    gross_profit = wins['profit'].sum() if len(wins) > 0 else 0
    gross_loss = abs(losses['profit'].sum()) if len(losses) > 0 else 1
    profit_factor = gross_profit / gross_loss if gross_loss > 0 else 0
    
    # Create layout
    return html.Div([
        # Header
        html.H4("📊 Trade Statistics", className="text-xl font-bold mb-4"),
        
        # Grid layout for stats
        html.Div([
            # Column 1: Basic Stats
            html.Div([
                html.H5("Basic Metrics", className="font-semibold mb-2 text-gray-700"),
                _stat_row("Total Trades", f"{total_trades}"),
                _stat_row("Winning Trades", f"{winning_trades}"),
                _stat_row("Losing Trades", f"{losing_trades}"),
                _stat_row("Win Rate", f"{win_rate:.2f}%", 
                         color="green" if win_rate > 50 else "red"),
            ], className="p-4 bg-gray-50 rounded"),
            
            # Column 2: Profit Stats
            html.Div([
                html.H5("Profit Metrics", className="font-semibold mb-2 text-gray-700"),
                _stat_row("Avg Win", f"${avg_win:.2f}", color="green"),
                _stat_row("Avg Loss", f"${avg_loss:.2f}", color="red"),
                _stat_row("Largest Win", f"${largest_win:.2f}", color="green"),
                _stat_row("Largest Loss", f"${largest_loss:.2f}", color="red"),
            ], className="p-4 bg-gray-50 rounded"),
            
            # Column 3: Performance Metrics
            html.Div([
                html.H5("Performance Metrics", className="font-semibold mb-2 text-gray-700"),
                _stat_row("Expectancy", f"${expectancy:.2f}", 
                         color="green" if expectancy > 0 else "red"),
                _stat_row("Profit Factor", f"{profit_factor:.2f}",
                         color="green" if profit_factor > 1 else "red"),
                _stat_row("Max Consecutive Wins", f"{max_consecutive_wins}"),
                _stat_row("Max Consecutive Losses", f"{max_consecutive_losses}"),
            ], className="p-4 bg-gray-50 rounded"),
            
            # Column 4: Duration Stats
            html.Div([
                html.H5("Duration Metrics", className="font-semibold mb-2 text-gray-700"),
                _stat_row("Avg Win Duration", f"{avg_duration_win:.1f}h"),
                _stat_row("Avg Loss Duration", f"{avg_duration_loss:.1f}h"),
                _stat_row("", ""),
                _stat_row("", ""),
            ], className="p-4 bg-gray-50 rounded"),
        ], className="grid grid-cols-4 gap-4 mb-6"),
        
        # Session breakdown (if available)
        html.Div([
            html.H5("Session Breakdown", className="font-semibold mb-2 text-gray-700"),
            html.Div([
                _session_card(session, stats)
                for session, stats in session_stats.items()
            ], className="grid grid-cols-3 gap-4")
        ], className="p-4 bg-gray-50 rounded") if session_stats else html.Div(),
        
    ], className="trade-stats-container")


def _stat_row(label: str, value: str, color: Optional[str] = None) -> html.Div:
    """Helper to create a stat row"""
    color_class = ""
    if color == "green":
        color_class = "text-green-600"
    elif color == "red":
        color_class = "text-red-600"
    
    return html.Div([
        html.Span(f"{label}: ", className="font-medium text-gray-600"),
        html.Span(value, className=f"font-bold {color_class}")
    ], className="mb-1")


def _session_card(session: str, stats: Dict) -> html.Div:
    """Helper to create a session stats card"""
    return html.Div([
        html.H6(session, className="font-semibold mb-2"),
        _stat_row("Trades", f"{stats['trades']}"),
        _stat_row("Profit", f"${stats['profit']:.2f}", 
                 color="green" if stats['profit'] > 0 else "red"),
        _stat_row("Win Rate", f"{stats['win_rate']:.1f}%",
                 color="green" if stats['win_rate'] > 50 else "red"),
    ], className="p-3 bg-white rounded shadow-sm")


if __name__ == "__main__":
    # Test with dummy data
    np.random.seed(42)
    n_trades = 100
    
    trades = []
    for i in range(n_trades):
        profit = np.random.normal(50, 100)
        duration = np.random.uniform(1, 24)
        session = np.random.choice(['London', 'New York', 'Tokyo'])
        
        trades.append({
            'profit': profit,
            'duration_hours': duration,
            'session': session
        })
    
    stats_div = render_trade_stats(trades)
    print("Trade stats component created successfully!")
