import os
import json
import pandas as pd
from pathlib import Path
from typing import Dict, List, Any, Optional


def get_data_directory() -> Path:
    """Get the data directory path."""
    return Path(__file__).parent.parent.parent / "data"


def get_universe_list() -> List[str]:
    """
    Get list of available universes from the data directory.
    
    Returns:
        List of universe names
    """
    data_dir = get_data_directory()
    universes = []
    
    if not data_dir.exists():
        return universes
    
    # Look for universe directories or files
    for item in data_dir.iterdir():
        if item.is_dir():
            universes.append(item.name)
        elif item.is_file() and item.suffix == '.json':
            # Check if it's a universe file
            try:
                with open(item, 'r') as f:
                    data = json.load(f)
                    if 'universe' in data:
                        universes.append(data['universe'])
            except:
                pass
    
    return sorted(list(set(universes)))


def get_strategy_list(universe: Optional[str] = None) -> List[str]:
    """
    Get list of available strategies, optionally filtered by universe.
    
    Args:
        universe: Optional universe name to filter strategies
        
    Returns:
        List of strategy names
    """
    data_dir = get_data_directory()
    strategies = []
    
    if not data_dir.exists():
        return strategies
    
    # Look for strategy files or directories
    if universe:
        universe_dir = data_dir / universe
        if universe_dir.exists() and universe_dir.is_dir():
            for item in universe_dir.iterdir():
                if item.is_file() and item.suffix in ['.json', '.csv']:
                    strategy_name = item.stem
                    strategies.append(strategy_name)
                elif item.is_dir():
                    strategies.append(item.name)
    else:
        # Get all strategies across all universes
        for item in data_dir.rglob('*.json'):
            try:
                with open(item, 'r') as f:
                    data = json.load(f)
                    if 'strategy' in data:
                        strategies.append(data['strategy'])
            except:
                pass
    
    return sorted(list(set(strategies)))


def load_strategy_results(filepath: Path) -> Optional[Dict[str, Any]]:
    """
    Load results from a single strategy file.
    
    Args:
        filepath: Path to the strategy results file
        
    Returns:
        Dictionary containing strategy results or None if loading fails
    """
    try:
        if filepath.suffix == '.json':
            with open(filepath, 'r') as f:
                return json.load(f)
        elif filepath.suffix == '.csv':
            df = pd.read_csv(filepath)
            return {
                'data': df.to_dict('records'),
                'strategy': filepath.stem
            }
    except Exception as e:
        print(f"Error loading {filepath}: {e}")
        return None


def load_all_results(universe: Optional[str] = None, 
                     strategy: Optional[str] = None) -> Dict[str, Any]:
    """
    Load all trading results with proper structure.
    
    Args:
        universe: Optional universe filter
        strategy: Optional strategy filter
        
    Returns:
        Dictionary with structure:
        {
            'metadata': {
                'universe': str,
                'last_updated': str,
                'data_directory': str
            },
            'has_detailed_trades': bool,
            'all_results': List[Dict],
            'total_strategies': int
        }
    """
    data_dir = get_data_directory()
    all_results = []
    has_detailed_trades = False
    
    metadata = {
        'universe': universe or 'all',
        'last_updated': pd.Timestamp.now().isoformat(),
        'data_directory': str(data_dir)
    }
    
    if not data_dir.exists():
        return {
            'metadata': metadata,
            'has_detailed_trades': False,
            'all_results': [],
            'total_strategies': 0
        }
    
    # Determine search path
    if universe:
        search_paths = [data_dir / universe]
    else:
        search_paths = [data_dir]
    
    # Load results from all matching files
    for search_path in search_paths:
        if not search_path.exists():
            continue
            
        # Find all result files
        for filepath in search_path.rglob('*.json'):
            # Skip if strategy filter is specified and doesn't match
            if strategy and filepath.stem != strategy:
                continue
                
            result = load_strategy_results(filepath)
            if result:
                # Check if detailed trades are available
                if 'trades' in result or 'detailed_trades' in result:
                    has_detailed_trades = True
                
                # Ensure result has required fields
                if 'strategy' not in result:
                    result['strategy'] = filepath.stem
                if 'universe' not in result and universe:
                    result['universe'] = universe
                    
                all_results.append(result)
        
        # Also check for CSV files
        for filepath in search_path.rglob('*.csv'):
            if strategy and filepath.stem != strategy:
                continue
                
            result = load_strategy_results(filepath)
            if result:
                all_results.append(result)
    
    return {
        'metadata': metadata,
        'has_detailed_trades': has_detailed_trades,
        'all_results': all_results,
        'total_strategies': len(all_results)
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
    results = load_all_results(universe=universe, strategy=strategy_name)
    
    if results['total_strategies'] == 0:
        return None
    
    # Return the first matching result
    return results['all_results'][0] if results['all_results'] else None


def get_summary_statistics(universe: Optional[str] = None) -> Dict[str, Any]:
    """
    Get summary statistics across all strategies.
    
    Args:
        universe: Optional universe filter
        
    Returns:
        Dictionary of summary statistics
    """
    results = load_all_results(universe=universe)
    
    summary = {
        'total_strategies': results['total_strategies'],
        'has_detailed_trades': results['has_detailed_trades'],
        'universes': get_universe_list(),
        'strategies': []
    }
    
    # Extract basic stats from each strategy
    for result in results['all_results']:
        strategy_summary = {
            'name': result.get('strategy', 'unknown'),
            'universe': result.get('universe', 'unknown')
        }
        
        # Add common metrics if available
        for metric in ['total_return', 'sharpe_ratio', 'max_drawdown', 
                      'win_rate', 'num_trades']:
            if metric in result:
                strategy_summary[metric] = result[metric]
        
        summary['strategies'].append(strategy_summary)
    
    return summary
