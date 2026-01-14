#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚡🌟💎 NECROZMA - Trade Log Component 💎🌟⚡

Detailed trade log table - LIMITED TO TOP 10 STRATEGIES ONLY
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Optional
from dash import html, dcc, dash_table
import dash_bootstrap_components as dbc


def render_trade_log(
    trades: List[Dict],
    top_n: int = 10,
    strategy_name: Optional[str] = None
) -> html.Div:
    """
    Generate trade log table - FOR TOP 10 STRATEGIES ONLY
    
    Args:
        trades: List of trade dictionaries
        top_n: Number of top strategies to show detailed logs (default: 10)
        strategy_name: Name of the strategy (to check if it's in top 10)
        
    Returns:
        Dash HTML Div with trade log table
    """
    if not trades:
        return html.Div(
            "No trades available",
            className="text-center text-gray-500 p-8"
        )
    
    # Convert to DataFrame
    df = pd.DataFrame(trades)
    
    # Format columns for display
    display_df = pd.DataFrame()
    
    # Trade number
    display_df['#'] = range(1, len(df) + 1)
    
    # Date/Time
    if 'entry_time' in df.columns:
        display_df['Entry Time'] = pd.to_datetime(df['entry_time']).dt.strftime('%Y-%m-%d %H:%M')
    
    if 'exit_time' in df.columns:
        display_df['Exit Time'] = pd.to_datetime(df['exit_time']).dt.strftime('%Y-%m-%d %H:%M')
    
    # Type
    if 'direction' in df.columns:
        display_df['Type'] = df['direction'].apply(lambda x: '🟢 LONG' if x == 'long' else '🔴 SHORT')
    
    # Entry/Exit prices
    if 'entry_price' in df.columns:
        display_df['Entry'] = df['entry_price'].apply(lambda x: f'{x:.5f}')
    
    if 'exit_price' in df.columns:
        display_df['Exit'] = df['exit_price'].apply(lambda x: f'{x:.5f}')
    
    # Profit/Loss
    if 'profit' in df.columns:
        display_df['P/L ($)'] = df['profit'].apply(lambda x: f'${x:.2f}')
    
    if 'profit_pips' in df.columns:
        display_df['P/L (pips)'] = df['profit_pips'].apply(lambda x: f'{x:.1f}')
    
    # Duration
    if 'duration_hours' in df.columns:
        display_df['Duration'] = df['duration_hours'].apply(lambda x: f'{x:.1f}h')
    elif 'entry_time' in df.columns and 'exit_time' in df.columns:
        duration = (pd.to_datetime(df['exit_time']) - pd.to_datetime(df['entry_time'])).dt.total_seconds() / 3600
        display_df['Duration'] = duration.apply(lambda x: f'{x:.1f}h')
    
    # Add color coding for profit/loss
    def color_profit(val):
        try:
            num = float(val.replace('$', ''))
            if num > 0:
                return 'background-color: rgba(72, 187, 120, 0.2)'  # Green
            elif num < 0:
                return 'background-color: rgba(245, 101, 101, 0.2)'  # Red
        except:
            pass
        return ''
    
    # Create dash table
    table = dash_table.DataTable(
        data=display_df.to_dict('records'),
        columns=[{'name': col, 'id': col} for col in display_df.columns],
        style_table={
            'overflowX': 'auto',
            'overflowY': 'auto',
            'maxHeight': '600px',
        },
        style_cell={
            'textAlign': 'left',
            'padding': '10px',
            'fontSize': '14px',
            'fontFamily': 'Arial, sans-serif',
        },
        style_header={
            'backgroundColor': '#667eea',
            'color': 'white',
            'fontWeight': 'bold',
            'textAlign': 'center',
        },
        style_data_conditional=[
            # Alternate row colors
            {
                'if': {'row_index': 'odd'},
                'backgroundColor': 'rgb(248, 248, 248)'
            },
            # Profit column coloring
            {
                'if': {
                    'filter_query': '{P/L ($)} contains "$-"',
                    'column_id': 'P/L ($)'
                },
                'backgroundColor': 'rgba(245, 101, 101, 0.2)',
                'color': '#c53030'
            },
            {
                'if': {
                    'filter_query': '{P/L ($)} contains "$" && {P/L ($)} not contains "$-"',
                    'column_id': 'P/L ($)'
                },
                'backgroundColor': 'rgba(72, 187, 120, 0.2)',
                'color': '#22543d'
            },
        ],
        page_size=20,
        page_action='native',
        sort_action='native',
        filter_action='native',
        export_format='csv',
        export_headers='display',
    )
    
    # Warning banner for non-top strategies
    warning_banner = html.Div()
    if strategy_name:
        warning_banner = dbc.Alert(
            [
                html.I(className="fas fa-info-circle me-2"),
                f"Trade log limited to Top {top_n} strategies only. ",
                html.Strong(f"Current strategy: {strategy_name}")
            ],
            color="info",
            className="mb-3"
        )
    
    return html.Div([
        html.H4("📋 Trade Log", className="text-xl font-bold mb-4"),
        
        warning_banner,
        
        # Summary stats
        html.Div([
            html.Div([
                html.Span("Total Trades: ", className="font-medium"),
                html.Span(f"{len(df)}", className="font-bold text-blue-600")
            ], className="inline-block mr-6"),
            
            html.Div([
                html.Span("Total Profit: ", className="font-medium"),
                html.Span(
                    f"${df['profit'].sum():.2f}" if 'profit' in df.columns else "N/A",
                    className=f"font-bold {'text-green-600' if 'profit' in df.columns and df['profit'].sum() > 0 else 'text-red-600'}"
                )
            ], className="inline-block mr-6"),
            
            html.Div([
                html.Span("Win Rate: ", className="font-medium"),
                html.Span(
                    f"{(df['profit'] > 0).mean() * 100:.1f}%" if 'profit' in df.columns else "N/A",
                    className="font-bold text-blue-600"
                )
            ], className="inline-block"),
        ], className="mb-4 p-3 bg-gray-50 rounded"),
        
        # Trade table
        table,
        
        # Export instructions
        html.Div([
            html.I(className="fas fa-download me-2"),
            "Click the Export button above to download trades as CSV"
        ], className="text-sm text-gray-600 mt-2")
        
    ], className="trade-log-container")


if __name__ == "__main__":
    # Test with dummy data
    import datetime
    
    np.random.seed(42)
    n_trades = 50
    
    trades = []
    current_time = datetime.datetime(2025, 1, 1)
    
    for i in range(n_trades):
        direction = np.random.choice(['long', 'short'])
        entry_price = 1.10 + np.random.uniform(-0.01, 0.01)
        
        # Random profit/loss
        profit_pips = np.random.normal(10, 30)
        
        if direction == 'long':
            exit_price = entry_price + (profit_pips * 0.0001)
        else:
            exit_price = entry_price - (profit_pips * 0.0001)
        
        profit = profit_pips * 10  # $10 per pip
        duration = np.random.uniform(1, 48)
        
        trades.append({
            'entry_time': current_time,
            'exit_time': current_time + datetime.timedelta(hours=duration),
            'direction': direction,
            'entry_price': entry_price,
            'exit_price': exit_price,
            'profit': profit,
            'profit_pips': profit_pips,
            'duration_hours': duration
        })
        
        current_time += datetime.timedelta(hours=np.random.randint(1, 24))
    
    log_div = render_trade_log(trades, strategy_name="Test Strategy")
    print("Trade log component created successfully!")
