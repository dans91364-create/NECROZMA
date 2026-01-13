#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚡🌟💎 NECROZMA DASHBOARD - DATA LOADER 💎🌟⚡

Utilities for loading backtest results from JSON files
"""

import json
import pandas as pd
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import streamlit as st


@st.cache_data
def load_all_results(results_dir: str = 'ultra_necrozma_results/backtest_results') -> Dict:
    """
    Load all backtest results from JSON files
    
    Args:
        results_dir: Directory containing backtest result JSON files
        
    Returns:
        Dictionary with aggregated results and metadata
    """
    results_path = Path(results_dir)
    
    if not results_path.exists():
        st.error(f"❌ Results directory not found: {results_dir}")
        return {
            'strategies': [],
            'universes': [],
            'total_strategies': 0,
            'viable_count': 0
        }
    
    # Load consolidated results if available
    consolidated_file = results_path / 'consolidated_backtest_results.json'
    
    all_strategies = []
    all_universes = []
    
    if consolidated_file.exists():
        try:
            with open(consolidated_file, 'r') as f:
                consolidated = json.load(f)
                
            # Extract strategies from consolidated results
            for universe in consolidated.get('universes', []):
                universe_name = universe.get('universe_name', 'unknown')
                universe_meta = universe.get('universe_metadata', {})
                
                for result in universe.get('results', []):
                    strategy_data = {
                        'universe_name': universe_name,
                        'interval': universe_meta.get('interval'),
                        'lookback': universe_meta.get('lookback'),
                        **result
                    }
                    all_strategies.append(strategy_data)
                
                all_universes.append(universe)
                
        except Exception as e:
            st.warning(f"⚠️ Error loading consolidated results: {e}")
    
    # Also load individual universe files
    for json_file in results_path.glob('universe_*_backtest.json'):
        try:
            with open(json_file, 'r') as f:
                data = json.load(f)
            
            universe_name = data.get('universe_name', json_file.stem)
            universe_meta = data.get('universe_metadata', {})
            
            # Add strategies from this universe
            for result in data.get('results', []):
                # Skip if already loaded from consolidated
                strategy_key = f"{universe_name}_{result.get('strategy_name', 'unknown')}"
                if not any(s.get('universe_name') == universe_name and 
                          s.get('strategy_name') == result.get('strategy_name') 
                          for s in all_strategies):
                    strategy_data = {
                        'universe_name': universe_name,
                        'interval': universe_meta.get('interval'),
                        'lookback': universe_meta.get('lookback'),
                        **result
                    }
                    all_strategies.append(strategy_data)
            
            # Add universe if not in list
            if not any(u.get('universe_name') == universe_name for u in all_universes):
                all_universes.append(data)
                
        except Exception as e:
            st.warning(f"⚠️ Error loading {json_file.name}: {e}")
    
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
        
        return {
            'strategies': all_strategies,
            'strategies_df': strategies_df,
            'universes': all_universes,
            'total_strategies': len(all_strategies),
            'viable_count': int(viable_count) if viable_count is not None else 0,
            'best_sharpe': strategies_df.loc[best_sharpe_idx, 'sharpe_ratio'] if len(strategies_df) > 0 else 0,
            'best_return': strategies_df.loc[best_return_idx, 'total_return'] if len(strategies_df) > 0 else 0,
            'best_sharpe_strategy': strategies_df.loc[best_sharpe_idx].to_dict() if len(strategies_df) > 0 else {},
            'best_return_strategy': strategies_df.loc[best_return_idx].to_dict() if len(strategies_df) > 0 else {},
        }
    
    return {
        'strategies': [],
        'universes': [],
        'total_strategies': 0,
        'viable_count': 0
    }


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
