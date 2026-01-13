#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚡🌟💎 NECROZMA DASHBOARD - DATA LOADER 💎🌟⚡

Load backtest results from universe_*_backtest.json files and smart storage
"""

import os
import json
import pandas as pd
import re
import streamlit as st
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple


def get_data_directory() -> Path:
    """Get the backtest results directory path."""
    # Look for ultra_necrozma_results/backtest_results/ directory
    base_dir = Path(__file__).parent.parent.parent
    results_dir = base_dir / "ultra_necrozma_results" / "backtest_results"
    
    # Fallback to data directory if results_dir doesn't exist
    if not results_dir.exists():
        results_dir = base_dir / "data"
    
    return results_dir


# ═══════════════════════════════════════════════════════════════
# 🗄️ SMART STORAGE FUNCTIONS (NEW)
# ═══════════════════════════════════════════════════════════════

@st.cache_data(ttl=300)
def load_all_strategies_metrics(results_dir: Optional[str] = None) -> pd.DataFrame:
    """
    Load lightweight metrics for ALL strategies (Tier 1)
    Fast loading: ~50 MB for 10,000 strategies
    
    Args:
        results_dir: Optional custom results directory path
        
    Returns:
        DataFrame with all strategy metrics
    """
    if results_dir:
        data_dir = Path(results_dir)
    else:
        data_dir = get_data_directory()
    
    metrics_file = data_dir / "all_strategies_metrics.json"
    
    if not metrics_file.exists():
        return pd.DataFrame()
    
    try:
        with open(metrics_file) as f:
            data = json.load(f)
        
        strategies = data.get("strategies", [])
        
        if not strategies:
            return pd.DataFrame()
        
        # Convert to DataFrame
        df = pd.DataFrame(strategies)
        
        # Flatten metrics dict into columns
        if 'metrics' in df.columns:
            metrics_df = pd.json_normalize(df['metrics'])
            df = pd.concat([df[['strategy_name', 'universe']], metrics_df], axis=1)
        
        return df
        
    except Exception as e:
        print(f"Error loading metrics file: {e}")
        return pd.DataFrame()


@st.cache_data(ttl=300)
def load_strategy_detailed_trades(strategy_name: str, results_dir: Optional[str] = None) -> Optional[Dict]:
    """
    Load detailed trades for ONE strategy (Tier 2, on-demand)
    Only available for top 50 strategies per universe
    
    Args:
        strategy_name: Name of the strategy
        results_dir: Optional custom results directory path
        
    Returns:
        Dictionary with strategy data or None if not found
    """
    if results_dir:
        data_dir = Path(results_dir)
    else:
        data_dir = get_data_directory()
    
    trade_file = data_dir / "detailed_trades" / f"{strategy_name}.json"
    
    if not trade_file.exists():
        return None
    
    try:
        with open(trade_file) as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading trades for {strategy_name}: {e}")
        return None


def get_strategies_with_trades(results_dir: Optional[str] = None) -> List[str]:
    """
    Get list of strategies that have detailed trades available
    
    Args:
        results_dir: Optional custom results directory path
        
    Returns:
        List of strategy names with detailed trades
    """
    if results_dir:
        data_dir = Path(results_dir)
    else:
        data_dir = get_data_directory()
    
    trades_dir = data_dir / "detailed_trades"
    
    if not trades_dir.exists():
        return []
    
    return [f.stem for f in trades_dir.glob("*.json")]


# ═══════════════════════════════════════════════════════════════
# 📊 LEGACY FUNCTIONS (BACKWARD COMPATIBLE)
# ═══════════════════════════════════════════════════════════════


def extract_sl_tp_from_name(strategy_name: str) -> Tuple[Optional[int], Optional[int]]:
    """
    Extract SL and TP parameters from strategy name using regex.
    
    Supports formats:
    - TrendFollower_L5_T0.5_SL10_TP50
    - strategy_sl_20_tp_40
    - BreakoutStrategy_sl10tp50
    - SL5_TP25_Strategy
    
    Args:
        strategy_name: Strategy name string
        
    Returns:
        Tuple of (sl, tp) as integers, or (None, None) if not found
    """
    if not strategy_name:
        return None, None
    
    # Pattern 1: SL10_TP50 or sl10_tp50 (with separators like _ or space)
    # Matches: [optional separator] SL [optional separator] digits [separator] TP [optional separator] digits
    pattern1 = r'[_\s]?[sS][lL][\s_]?(\d+)[\s_]+[tT][pP][\s_]?(\d+)'
    match = re.search(pattern1, strategy_name)
    
    if match:
        return int(match.group(1)), int(match.group(2))
    
    # Pattern 2: sl10tp50 (no separators between SL/TP and values)
    # Matches: SL digits TP digits (all concatenated)
    pattern2 = r'[sS][lL](\d+)[tT][pP](\d+)'
    match = re.search(pattern2, strategy_name)
    
    if match:
        return int(match.group(1)), int(match.group(2))
    
    return None, None


def get_universe_list() -> List[str]:
    """
    Extract unique universe names from universe_*_backtest.json files.
    
    Returns:
        List of universe names
    """
    data_dir = get_data_directory()
    universes = []
    
    if not data_dir.exists():
        return universes
    
    # Look for universe_*_backtest.json files
    for filepath in data_dir.glob('universe_*_backtest.json'):
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
                universe_name = data.get('universe_name')
                if universe_name:
                    universes.append(universe_name)
        except Exception as e:
            print(f"Error reading {filepath}: {e}")
    
    return sorted(list(set(universes)))


def get_strategy_list(universe: Optional[str] = None) -> List[str]:
    """
    Extract unique strategy names from loaded results.
    
    Args:
        universe: Optional universe name to filter strategies
        
    Returns:
        List of unique strategy names
    """
    results = load_all_results()
    strategies = set()
    
    for result in results.get('all_results', []):
        if universe and result.get('universe_name') != universe:
            continue
        
        strategy_name = result.get('strategy_name')
        if strategy_name:
            strategies.add(strategy_name)
    
    return sorted(list(strategies))


def get_strategy_data(strategy_name: str, universe: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """
    Get specific strategy data including detailed trades if available.
    
    Args:
        strategy_name: Name of the strategy
        universe: Optional universe name to filter
        
    Returns:
        Dictionary with strategy data or None if not found
    """
    results = load_all_results()
    
    for result in results.get('all_results', []):
        if result.get('strategy_name') == strategy_name:
            if universe and result.get('universe_name') != universe:
                continue
            return result
    
    return None


@st.cache_data(ttl=300)
def load_all_results(results_dir: Optional[str] = None) -> Dict[str, Any]:
    """
    Load all backtest results from smart storage or legacy format.
    
    This function now prioritizes smart storage (all_strategies_metrics.json)
    but falls back to legacy universe_*_backtest.json files for backward compatibility.
    
    Args:
        results_dir: Optional custom results directory path
        
    Returns:
        Dictionary with structure:
        {
            'metadata': {
                'total_strategies': int,
                'total_universes': int,
                'data_source': str,
                'last_updated': str
            },
            'has_detailed_trades': bool,
            'all_results': List[Dict],  # Raw results from all strategies
            'strategies_df': pd.DataFrame  # Complete DataFrame with all metrics
        }
    """
    # Try loading from smart storage first
    metrics_df = load_all_strategies_metrics(results_dir)
    
    if not metrics_df.empty:
        # Smart storage found!
        strategies_with_trades = get_strategies_with_trades(results_dir)
        
        # Convert DataFrame to list of dicts for backward compatibility
        all_results = metrics_df.to_dict('records')
        
        # Get unique universes
        universes = metrics_df['universe'].nunique() if 'universe' in metrics_df.columns else 0
        
        metadata = {
            'total_strategies': len(metrics_df),
            'total_universes': universes,
            'data_source': 'smart_storage',
            'last_updated': pd.Timestamp.now().isoformat()
        }
        
        return {
            'metadata': metadata,
            'has_detailed_trades': len(strategies_with_trades) > 0,
            'all_results': all_results,
            'strategies_df': metrics_df,
            'total_strategies': len(metrics_df)  # For backward compatibility
        }
    
    # Fall back to legacy format
    if results_dir:
        data_dir = Path(results_dir)
    else:
        data_dir = get_data_directory()
    
    all_results = []
    has_detailed_trades = False
    total_universes = 0
    
    if not data_dir.exists():
        return {
            'metadata': {
                'total_strategies': 0,
                'total_universes': 0,
                'data_source': str(data_dir),
                'last_updated': pd.Timestamp.now().isoformat()
            },
            'has_detailed_trades': False,
            'all_results': [],
            'strategies_df': pd.DataFrame()
        }
    
    # Scan for universe_*_backtest.json files
    universe_files = list(data_dir.glob('universe_*_backtest.json'))
    total_universes = len(universe_files)
    
    for filepath in universe_files:
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            universe_name = data.get('universe_name', filepath.stem)
            universe_metadata = data.get('universe_metadata', {})
            
            # Extract results from this universe
            for strategy_result in data.get('results', []):
                # Add universe context to each strategy
                strategy_result['universe_name'] = universe_name
                strategy_result['interval'] = universe_metadata.get('interval', 'unknown')
                strategy_result['lookback'] = universe_metadata.get('lookback', 0)
                
                # Check for detailed trades
                if 'trades_detailed' in strategy_result:
                    has_detailed_trades = True
                    strategy_result['n_detailed_trades'] = len(strategy_result['trades_detailed'])
                
                all_results.append(strategy_result)
                
        except Exception as e:
            print(f"Error loading {filepath}: {e}")
            continue
    
    # Create DataFrame with proper numeric conversion
    if all_results:
        strategies_df = pd.DataFrame(all_results)
        
        # Convert numeric columns to proper types
        numeric_columns = [
            'total_return', 'sharpe_ratio', 'sortino_ratio', 'calmar_ratio',
            'max_drawdown', 'win_rate', 'profit_factor', 'expectancy',
            'n_trades', 'avg_win', 'avg_loss', 'largest_win', 'largest_loss',
            'avg_win_size', 'avg_loss_size', 'lookback'
        ]
        
        for col in numeric_columns:
            if col in strategies_df.columns:
                strategies_df[col] = pd.to_numeric(strategies_df[col], errors='coerce')
    else:
        strategies_df = pd.DataFrame()
    
    metadata = {
        'total_strategies': len(all_results),
        'total_universes': total_universes,
        'data_source': str(data_dir),
        'last_updated': pd.Timestamp.now().isoformat()
    }
    
    return {
        'metadata': metadata,
        'has_detailed_trades': has_detailed_trades,
        'all_results': all_results,
        'strategies_df': strategies_df
    }


def get_strategy_metrics(strategy_name: str, universe: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """
    Get metrics for a specific strategy.
    
    Args:
        strategy_name: Name of the strategy
        universe: Optional universe name
        
    Returns:
        Dictionary of strategy metrics or None if not found
    """
    return get_strategy_data(strategy_name, universe)


def get_summary_statistics(universe: Optional[str] = None) -> Dict[str, Any]:
    """
    Get summary statistics across all strategies.
    
    Args:
        universe: Optional universe filter
        
    Returns:
        Dictionary of summary statistics
    """
    results = load_all_results()
    strategies_df = results.get('strategies_df', pd.DataFrame())
    
    # Filter by universe if specified
    if universe and not strategies_df.empty:
        strategies_df = strategies_df[strategies_df['universe_name'] == universe]
    
    if strategies_df.empty:
        return {
            'total_strategies': 0,
            'has_detailed_trades': False,
            'universes': [],
            'avg_sharpe': 0.0,
            'avg_return': 0.0,
            'avg_win_rate': 0.0
        }
    
    summary = {
        'total_strategies': len(strategies_df),
        'has_detailed_trades': results['has_detailed_trades'],
        'universes': get_universe_list(),
        'avg_sharpe': strategies_df.get('sharpe_ratio', pd.Series([0])).mean(),
        'avg_return': strategies_df.get('total_return', pd.Series([0])).mean(),
        'avg_win_rate': strategies_df.get('win_rate', pd.Series([0])).mean(),
        'max_sharpe': strategies_df.get('sharpe_ratio', pd.Series([0])).max(),
        'max_return': strategies_df.get('total_return', pd.Series([0])).max(),
    }
    
    return summary
