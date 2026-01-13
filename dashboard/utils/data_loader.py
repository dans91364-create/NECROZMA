#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚡🌟💎 NECROZMA DASHBOARD - DATA LOADER 💎🌟⚡

Utilities for loading backtest results from JSON files
"""

import json
import re
import pandas as pd
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import streamlit as st


@st.cache_data
def load_all_results(results_dir: str = 'ultra_necrozma_results/backtest_results') -> Dict:
    """
    Load all backtest results including trades_detailed.
    
    Strategy:
    1. Load consolidated file for summary metrics
    2. Load individual universe files for trades_detailed
    3. Merge the data
    
    Args:
        results_dir: Directory containing backtest result JSON files
        
    Returns:
        Dictionary with aggregated results and metadata including:
        - all_results: List of all strategies with metrics + trades_detailed
        - metadata: Backtest metadata
        - universes: List of universe names
        - has_detailed_trades: bool indicating if detailed trade data is available
    """
    results_path = Path(results_dir)
    
    if not results_path.exists():
        st.error(f"❌ Results directory not found: {results_dir}")
        return _get_empty_results()
    
    # Load consolidated results if available
    consolidated_file = results_path / 'consolidated_backtest_results.json'
    consolidated_data = _load_consolidated(consolidated_file)
    
    # Load individual universe files for trades_detailed
    universe_files = sorted(results_path.glob('universe_*_backtest.json'))
    detailed_trades_by_strategy = _load_detailed_trades(universe_files)
    
    # Merge data
    all_strategies = _merge_results(consolidated_data, detailed_trades_by_strategy)
    
    # Convert to DataFrame for easier analysis
    if all_strategies:
        strategies_df = pd.DataFrame(all_strategies)
        
        # Calculate viable strategies (Sharpe > 1.0, win_rate > 0.5)
        viable_mask = (strategies_df.get('sharpe_ratio', 0) > 1.0) & \
                      (strategies_df.get('win_rate', 0) > 0.5)
        viable_count = viable_mask.sum()
        
        # Get best performers
        best_sharpe_idx = strategies_df['sharpe_ratio'].idxmax() if 'sharpe_ratio' in strategies_df else 0
        best_return_idx = strategies_df['total_return'].idxmax() if 'total_return' in strategies_df else 0
        
        # Build response with new structure
        return {
            'all_results': all_strategies,
            'strategies': all_strategies,  # Keep for backward compatibility
            'strategies_df': strategies_df,
            'universes': [u.get('universe_name', f'universe_{i+1}') 
                         for i, u in enumerate(consolidated_data.get('universes', []))],
            'metadata': {
                'backtest_timestamp': consolidated_data.get('backtest_timestamp', 'Unknown'),
                'total_universes': consolidated_data.get('total_universes', len(universe_files)),
                'total_strategies': len(all_strategies),
                'data_source': 'merged' if detailed_trades_by_strategy else 'consolidated_only'
            },
            'has_detailed_trades': bool(detailed_trades_by_strategy),
            'total_strategies': len(all_strategies),
            'viable_count': int(viable_count) if viable_count is not None else 0,
            'best_sharpe': strategies_df.loc[best_sharpe_idx, 'sharpe_ratio'] if len(strategies_df) > 0 else 0,
            'best_return': strategies_df.loc[best_return_idx, 'total_return'] if len(strategies_df) > 0 else 0,
            'best_sharpe_strategy': strategies_df.loc[best_sharpe_idx].to_dict() if len(strategies_df) > 0 else {},
            'best_return_strategy': strategies_df.loc[best_return_idx].to_dict() if len(strategies_df) > 0 else {},
        }
    
    return _get_empty_results()


@st.cache_data
def load_strategy_data(strategy_name: str, universe_name: str, 
                       results_dir: str = 'ultra_necrozma_results/backtest_results') -> Optional[Dict]:
    """
    Load detailed data for a specific strategy
    
    Args:
        strategy_name: Name of strategy
        universe_name: Name of universe
        results_dir: Directory containing results
        
    Returns:
        Dictionary with strategy details or None
    """
    results_path = Path(results_dir)
    
    # Look for universe file
    universe_file = results_path / f"{universe_name}_backtest.json"
    
    if not universe_file.exists():
        return None
    
    try:
        with open(universe_file, 'r') as f:
            data = json.load(f)
        
        # Find the strategy in results
        for result in data.get('results', []):
            if result.get('strategy_name') == strategy_name:
                return result
                
    except Exception as e:
        st.error(f"Error loading strategy data: {e}")
    
    return None


def get_universe_list(results: Dict) -> List[str]:
    """
    Get list of unique universe names
    
    Args:
        results: Results dictionary from load_all_results
        
    Returns:
        Sorted list of universe names
    """
    if 'strategies_df' in results and not results['strategies_df'].empty:
        return sorted(results['strategies_df']['universe_name'].unique().tolist())
    return []


def get_strategy_list(results: Dict, universe_name: Optional[str] = None) -> List[str]:
    """
    Get list of strategy names, optionally filtered by universe
    
    Args:
        results: Results dictionary from load_all_results
        universe_name: Optional universe filter
        
    Returns:
        Sorted list of strategy names
    """
    if 'strategies_df' not in results or results['strategies_df'].empty:
        return []
    
    df = results['strategies_df']
    
    if universe_name:
        df = df[df['universe_name'] == universe_name]
    
    if 'strategy_name' in df.columns:
        return sorted(df['strategy_name'].unique().tolist())
    
    return []


def extract_sl_tp_from_name(strategy_name):
    """
    Extract stop-loss and take-profit from strategy name.
    
    Supports multiple formats:
    - TrendFollower_L5_T0.5_SL10_TP50
    - strategy_sl_20_tp_40
    - MomentumStrategy_SL15_TP30
    
    Args:
        strategy_name (str): Strategy name
    
    Returns:
        tuple: (sl, tp) as integers, or (None, None) if not found
    
    Examples:
        >>> extract_sl_tp_from_name('TrendFollower_L5_T0.5_SL10_TP50')
        (10, 50)
        >>> extract_sl_tp_from_name('strategy_sl_20_tp_40')
        (20, 40)
        >>> extract_sl_tp_from_name('NoSLTP_Strategy')
        (None, None)
    """
    if not strategy_name:
        return None, None
    
    # Pattern 1: SL<number>_TP<number> (case-insensitive)
    # Matches: SL10_TP50, sl10_tp50, SL15_TP30
    match = re.search(r'SL(\d+)_TP(\d+)', strategy_name, re.IGNORECASE)
    if match:
        sl = int(match.group(1))
        tp = int(match.group(2))
        return sl, tp
    
    # Pattern 2: sl_<number>_tp_<number> (with underscores)
    # Matches: sl_20_tp_40, SL_15_TP_30
    match = re.search(r'sl[_-](\d+)[_-]tp[_-](\d+)', strategy_name, re.IGNORECASE)
    if match:
        sl = int(match.group(1))
        tp = int(match.group(2))
        return sl, tp
    
    # Pattern 3: sl<number>tp<number> (no separators)
    # Matches: sl10tp50, SL15TP30
    match = re.search(r'sl(\d+)tp(\d+)', strategy_name, re.IGNORECASE)
    if match:
        sl = int(match.group(1))
        tp = int(match.group(2))
        return sl, tp
    
    # No match found
    return None, None


# ═══════════════════════════════════════════════════════════════
# 🔧 HELPER FUNCTIONS FOR TRADES_DETAILED LOADING
# ═══════════════════════════════════════════════════════════════

def _load_consolidated(consolidated_path: Path) -> Dict:
    """Load consolidated backtest results."""
    if not consolidated_path.exists():
        return {}
    
    try:
        with open(consolidated_path, 'r') as f:
            data = json.load(f)
        
        # Validate structure
        if 'universes' not in data:
            print(f"⚠️  Warning: consolidated file missing 'universes' key")
            return {}
        
        return data
    
    except json.JSONDecodeError as e:
        print(f"❌ Error loading consolidated file: {e}")
        return {}
    except Exception as e:
        print(f"❌ Unexpected error loading consolidated: {e}")
        return {}


def _load_detailed_trades(universe_files: List[Path]) -> Dict[str, List[Dict]]:
    """
    Load trades_detailed from individual universe files.
    
    Args:
        universe_files: List of paths to universe JSON files
    
    Returns:
        dict: {strategy_name: [trades_detailed]}
    """
    trades_by_strategy = {}
    
    for universe_file in universe_files:
        try:
            with open(universe_file, 'r') as f:
                universe_data = json.load(f)
            
            # Extract results
            results = universe_data.get('results', [])
            
            for strategy in results:
                strategy_name = strategy.get('strategy_name')
                trades_detailed = strategy.get('trades_detailed', [])
                
                if strategy_name and trades_detailed:
                    # Aggregate trades from multiple universes
                    if strategy_name not in trades_by_strategy:
                        trades_by_strategy[strategy_name] = []
                    
                    trades_by_strategy[strategy_name].extend(trades_detailed)
        
        except Exception as e:
            print(f"⚠️  Warning: Could not load {universe_file.name}: {e}")
            continue
    
    return trades_by_strategy


def _merge_results(consolidated_data: Dict, detailed_trades: Dict[str, List]) -> List[Dict]:
    """
    Merge consolidated metrics with detailed trades.
    
    Args:
        consolidated_data: Data from consolidated_backtest_results.json
        detailed_trades: trades_detailed indexed by strategy_name
    
    Returns:
        List of strategies with full data
    """
    all_results = []
    
    # Extract strategies from consolidated
    universes = consolidated_data.get('universes', [])
    
    for universe in universes:
        universe_name = universe.get('universe_name', 'unknown')
        universe_meta = universe.get('universe_metadata', {})
        
        # Some consolidated files have results nested in universe
        strategies = universe.get('results', [])
        
        for strategy in strategies:
            strategy_name = strategy.get('strategy_name')
            
            # Build complete strategy data
            strategy_data = {
                'universe_name': universe_name,
                'interval': universe_meta.get('interval'),
                'lookback': universe_meta.get('lookback'),
                **strategy
            }
            
            # Add trades_detailed if available
            if strategy_name and strategy_name in detailed_trades:
                strategy_data['trades_detailed'] = detailed_trades[strategy_name]
                strategy_data['n_detailed_trades'] = len(detailed_trades[strategy_name])
            else:
                strategy_data['trades_detailed'] = []
                strategy_data['n_detailed_trades'] = 0
            
            all_results.append(strategy_data)
    
    # If no results in consolidated, try to build from detailed trades
    if not all_results and detailed_trades:
        for strategy_name, trades in detailed_trades.items():
            all_results.append({
                'strategy_name': strategy_name,
                'trades_detailed': trades,
                'n_detailed_trades': len(trades),
                'n_trades': len(trades),
                # Other metrics will be calculated from trades
                'total_return': _calculate_return_from_trades(trades),
                'win_rate': _calculate_win_rate(trades)
            })
    
    return all_results


def _calculate_return_from_trades(trades: List[Dict]) -> float:
    """Calculate total return from trades_detailed."""
    if not trades:
        return 0.0
    
    try:
        total_pnl_pct = sum(t.get('pnl_pct', 0) for t in trades)
        return total_pnl_pct
    except:
        return 0.0


def _calculate_win_rate(trades: List[Dict]) -> float:
    """Calculate win rate from trades_detailed."""
    if not trades:
        return 0.0
    
    try:
        winning_trades = sum(1 for t in trades if t.get('pnl_pips', 0) > 0)
        return (winning_trades / len(trades))
    except:
        return 0.0


def _get_empty_results() -> Dict:
    """Return empty results structure."""
    return {
        'all_results': [],
        'strategies': [],
        'metadata': {
            'backtest_timestamp': 'No data',
            'total_universes': 0,
            'total_strategies': 0,
            'data_source': 'none'
        },
        'universes': [],
        'has_detailed_trades': False,
        'total_strategies': 0,
        'viable_count': 0,
        'strategies_df': pd.DataFrame()
    }
