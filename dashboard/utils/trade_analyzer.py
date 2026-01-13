#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚡🌟💎 NECROZMA DASHBOARD - TRADE ANALYZER 💎🌟⚡

Trade analysis and insight generation utilities
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from collections import defaultdict


def analyze_patterns(trades_df: pd.DataFrame) -> pd.DataFrame:
    """
    Analyze pattern performance from trades
    
    Args:
        trades_df: DataFrame with trade data
        
    Returns:
        DataFrame with pattern statistics
    """
    if trades_df.empty or 'pattern' not in trades_df.columns:
        return pd.DataFrame()
    
    pattern_stats = []
    
    for pattern in trades_df['pattern'].unique():
        if pd.isna(pattern):
            continue
            
        pattern_trades = trades_df[trades_df['pattern'] == pattern]
        
        wins = pattern_trades[pattern_trades['pnl_pips'] > 0]
        losses = pattern_trades[pattern_trades['pnl_pips'] < 0]
        
        pattern_stats.append({
            'pattern': pattern,
            'count': len(pattern_trades),
            'wins': len(wins),
            'losses': len(losses),
            'win_rate': len(wins) / len(pattern_trades) if len(pattern_trades) > 0 else 0,
            'avg_pnl': pattern_trades['pnl_pips'].mean(),
            'total_pnl': pattern_trades['pnl_pips'].sum(),
            'avg_win': wins['pnl_pips'].mean() if len(wins) > 0 else 0,
            'avg_loss': losses['pnl_pips'].mean() if len(losses) > 0 else 0,
        })
    
    return pd.DataFrame(pattern_stats).sort_values('total_pnl', ascending=False)


def analyze_market_conditions(trades_df: pd.DataFrame) -> Dict:
    """
    Analyze trades by market conditions
    
    Args:
        trades_df: DataFrame with trade data
        
    Returns:
        Dictionary with market condition insights
    """
    if trades_df.empty:
        return {}
    
    insights = {
        'volatility': {},
        'trend': {},
        'hour': {},
        'day_of_week': {}
    }
    
    # Volatility analysis
    if 'volatility' in trades_df.columns:
        # Bin volatility into low/medium/high
        trades_df['vol_category'] = pd.qcut(trades_df['volatility'], 
                                            q=3, 
                                            labels=['Low', 'Medium', 'High'],
                                            duplicates='drop')
        
        for vol in ['Low', 'Medium', 'High']:
            vol_trades = trades_df[trades_df['vol_category'] == vol]
            if len(vol_trades) > 0:
                insights['volatility'][vol] = {
                    'count': len(vol_trades),
                    'win_rate': (vol_trades['pnl_pips'] > 0).sum() / len(vol_trades),
                    'avg_pnl': vol_trades['pnl_pips'].mean()
                }
    
    # Trend analysis
    if 'trend_strength' in trades_df.columns:
        trades_df['trend_category'] = pd.qcut(trades_df['trend_strength'], 
                                              q=3, 
                                              labels=['Weak', 'Medium', 'Strong'],
                                              duplicates='drop')
        
        for trend in ['Weak', 'Medium', 'Strong']:
            trend_trades = trades_df[trades_df['trend_category'] == trend]
            if len(trend_trades) > 0:
                insights['trend'][trend] = {
                    'count': len(trend_trades),
                    'win_rate': (trend_trades['pnl_pips'] > 0).sum() / len(trend_trades),
                    'avg_pnl': trend_trades['pnl_pips'].mean()
                }
    
    # Hour analysis
    if 'hour_of_day' in trades_df.columns:
        hour_groups = trades_df.groupby('hour_of_day')['pnl_pips'].agg(['count', 'mean', lambda x: (x > 0).sum()])
        hour_groups.columns = ['count', 'avg_pnl', 'wins']
        hour_groups['win_rate'] = hour_groups['wins'] / hour_groups['count']
        insights['hour'] = hour_groups.to_dict('index')
    
    # Day of week analysis
    if 'day_of_week' in trades_df.columns:
        day_groups = trades_df.groupby('day_of_week')['pnl_pips'].agg(['count', 'mean', lambda x: (x > 0).sum()])
        day_groups.columns = ['count', 'avg_pnl', 'wins']
        day_groups['win_rate'] = day_groups['wins'] / day_groups['count']
        insights['day_of_week'] = day_groups.to_dict('index')
    
    return insights


def generate_insights(trades_df: pd.DataFrame, top_n: int = 5) -> List[str]:
    """
    Generate AI-style insights from trade data
    
    Args:
        trades_df: DataFrame with trade data
        top_n: Number of insights to generate
        
    Returns:
        List of insight strings
    """
    insights = []
    
    if trades_df.empty:
        return ["No trades available for analysis"]
    
    # Overall performance
    total_pnl = trades_df['pnl_pips'].sum() if 'pnl_pips' in trades_df else 0
    win_rate = (trades_df['pnl_pips'] > 0).sum() / len(trades_df) if 'pnl_pips' in trades_df else 0
    
    if win_rate > 0.6:
        insights.append(f"🎯 Strong win rate of {win_rate*100:.1f}% indicates good signal quality")
    elif win_rate < 0.4:
        insights.append(f"⚠️ Low win rate of {win_rate*100:.1f}% suggests signal refinement needed")
    
    # Best pattern
    if 'pattern' in trades_df.columns:
        pattern_perf = trades_df.groupby('pattern')['pnl_pips'].sum()
        if len(pattern_perf) > 0:
            best_pattern = pattern_perf.idxmax()
            best_pnl = pattern_perf.max()
            insights.append(f"💡 Pattern '{best_pattern}' is most profitable with {best_pnl:.1f} total pips")
    
    # Time-based insights
    if 'hour_of_day' in trades_df.columns:
        hour_perf = trades_df.groupby('hour_of_day')['pnl_pips'].mean()
        if len(hour_perf) > 0:
            best_hour = hour_perf.idxmax()
            insights.append(f"⏰ Hour {best_hour}:00 shows best performance - consider focusing trades here")
    
    # Market condition insights
    if 'volatility' in trades_df.columns:
        high_vol = trades_df[trades_df['volatility'] > trades_df['volatility'].quantile(0.75)]
        low_vol = trades_df[trades_df['volatility'] < trades_df['volatility'].quantile(0.25)]
        
        if len(high_vol) > 0 and len(low_vol) > 0:
            high_vol_pnl = high_vol['pnl_pips'].mean()
            low_vol_pnl = low_vol['pnl_pips'].mean()
            
            if high_vol_pnl > low_vol_pnl:
                insights.append(f"📈 Higher volatility conditions yield better results (+{high_vol_pnl-low_vol_pnl:.1f} pips)")
            else:
                insights.append(f"📉 Lower volatility conditions are more favorable (+{low_vol_pnl-high_vol_pnl:.1f} pips)")
    
    # Duration insights
    if 'duration_minutes' in trades_df.columns:
        wins = trades_df[trades_df['pnl_pips'] > 0]
        losses = trades_df[trades_df['pnl_pips'] < 0]
        
        if len(wins) > 0 and len(losses) > 0:
            avg_win_duration = wins['duration_minutes'].mean()
            avg_loss_duration = losses['duration_minutes'].mean()
            
            if avg_win_duration < avg_loss_duration:
                insights.append(f"⚡ Winning trades exit faster ({avg_win_duration:.0f}m vs {avg_loss_duration:.0f}m) - good exit discipline")
    
    return insights[:top_n]


def filter_trades(trades: List[Dict], 
                 pnl_range: Tuple[float, float] = None,
                 direction_filter: List[str] = None,
                 pattern_filter: List[str] = None) -> List[Dict]:
    """
    Filter trades based on criteria
    
    Args:
        trades: List of trade dictionaries
        pnl_range: Tuple of (min_pnl, max_pnl) in pips
        direction_filter: List of directions to include
        pattern_filter: List of patterns to include
        
    Returns:
        Filtered list of trades
    """
    filtered = trades
    
    if pnl_range:
        filtered = [t for t in filtered 
                   if pnl_range[0] <= t.get('pnl_pips', 0) <= pnl_range[1]]
    
    if direction_filter:
        filtered = [t for t in filtered 
                   if t.get('direction', '') in direction_filter]
    
    if pattern_filter:
        filtered = [t for t in filtered 
                   if t.get('market_context', {}).get('pattern_detected', '') in pattern_filter]
    
    return filtered
