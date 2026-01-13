#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test data loader with mock backtest results structure
"""
import sys
import json
import tempfile
from pathlib import Path

sys.path.insert(0, 'dashboard/utils')

# Mock streamlit for testing
class MockStreamlit:
    @staticmethod
    def cache_data(ttl=None, **kwargs):
        def decorator(func):
            return func
        return decorator
    
    @staticmethod
    def error(msg):
        print(f"ERROR: {msg}")
    
    @staticmethod
    def warning(msg):
        print(f"WARNING: {msg}")

# Inject mock streamlit
sys.modules['streamlit'] = MockStreamlit()

from data_loader import load_all_results


def create_mock_data_structure(tmp_dir):
    """Create mock backtest results structure for testing"""
    
    # Create backtest_results directory
    backtest_dir = Path(tmp_dir) / "backtest_results"
    backtest_dir.mkdir(parents=True, exist_ok=True)
    
    # Create consolidated file (without trades_detailed)
    consolidated = {
        "backtest_timestamp": "2025-01-13T12:00:00",
        "total_universes": 2,
        "universes": [
            {
                "universe_name": "universe_001_5min_5lb",
                "universe_metadata": {
                    "interval": "5min",
                    "lookback": 5,
                    "total_patterns": 1000
                },
                "results": [
                    {
                        "strategy_name": "TrendFollower_L5_T0.5_SL10_TP20",
                        "n_trades": 100,
                        "win_rate": 0.65,
                        "total_return": 0.15,
                        "sharpe_ratio": 1.5,
                        "profit_factor": 2.3
                    },
                    {
                        "strategy_name": "MeanReverter_L10_T1.5_SL20_TP40",
                        "n_trades": 80,
                        "win_rate": 0.58,
                        "total_return": 0.12,
                        "sharpe_ratio": 1.2,
                        "profit_factor": 1.8
                    }
                ]
            },
            {
                "universe_name": "universe_002_15min_10lb",
                "universe_metadata": {
                    "interval": "15min",
                    "lookback": 10,
                    "total_patterns": 800
                },
                "results": [
                    {
                        "strategy_name": "TrendFollower_L5_T0.5_SL10_TP20",
                        "n_trades": 50,
                        "win_rate": 0.62,
                        "total_return": 0.10,
                        "sharpe_ratio": 1.3,
                        "profit_factor": 2.0
                    }
                ]
            }
        ]
    }
    
    consolidated_file = backtest_dir / "consolidated_backtest_results.json"
    with open(consolidated_file, 'w') as f:
        json.dump(consolidated, f, indent=2)
    
    # Create individual universe files (with trades_detailed)
    universe_001 = {
        "universe_name": "universe_001_5min_5lb",
        "universe_metadata": {
            "interval": "5min",
            "lookback": 5,
            "total_patterns": 1000
        },
        "backtest_timestamp": "2025-01-13T12:00:00",
        "results": [
            {
                "strategy_name": "TrendFollower_L5_T0.5_SL10_TP20",
                "n_trades": 100,
                "win_rate": 0.65,
                "total_return": 0.15,
                "sharpe_ratio": 1.5,
                "profit_factor": 2.3,
                "trades_detailed": [
                    {
                        "entry_time": "2025-01-01 00:05:00",
                        "exit_time": "2025-01-01 01:10:00",
                        "entry_price": 1.03534,
                        "exit_price": 1.03734,
                        "direction": "long",
                        "pnl_pips": 20.0,
                        "pnl_usd": 20.0,
                        "pnl_pct": 0.0019,
                        "duration_minutes": 65,
                        "exit_reason": "take_profit",
                        "market_context": {
                            "volatility": 0.0018,
                            "trend_strength": 0.75,
                            "volume_relative": 1.2,
                            "spread_pips": 1.5,
                            "pattern_detected": "ohl:H",
                            "hour_of_day": 0,
                            "day_of_week": 2
                        },
                        "price_history": {
                            "timestamps": ["2025-01-01 00:00:00", "2025-01-01 00:05:00"],
                            "open": [1.03500, 1.03534],
                            "high": [1.03550, 1.03600],
                            "low": [1.03480, 1.03520],
                            "close": [1.03534, 1.03734],
                            "volume": [100, 120]
                        }
                    },
                    {
                        "entry_time": "2025-01-01 02:00:00",
                        "exit_time": "2025-01-01 02:30:00",
                        "entry_price": 1.03800,
                        "exit_price": 1.03700,
                        "direction": "short",
                        "pnl_pips": -10.0,
                        "pnl_usd": -10.0,
                        "pnl_pct": -0.001,
                        "duration_minutes": 30,
                        "exit_reason": "stop_loss",
                        "market_context": {
                            "volatility": 0.0025,
                            "trend_strength": 0.45,
                            "volume_relative": 0.8,
                            "spread_pips": 2.0,
                            "pattern_detected": "ohl:L",
                            "hour_of_day": 2,
                            "day_of_week": 2
                        }
                    }
                ]
            },
            {
                "strategy_name": "MeanReverter_L10_T1.5_SL20_TP40",
                "n_trades": 80,
                "win_rate": 0.58,
                "total_return": 0.12,
                "sharpe_ratio": 1.2,
                "profit_factor": 1.8,
                "trades_detailed": [
                    {
                        "entry_time": "2025-01-01 03:00:00",
                        "exit_time": "2025-01-01 04:00:00",
                        "entry_price": 1.03900,
                        "exit_price": 1.04300,
                        "direction": "long",
                        "pnl_pips": 40.0,
                        "pnl_usd": 40.0,
                        "pnl_pct": 0.0038,
                        "duration_minutes": 60,
                        "exit_reason": "take_profit",
                        "market_context": {
                            "volatility": 0.0020,
                            "trend_strength": 0.60,
                            "pattern_detected": "ohl:HL"
                        }
                    }
                ]
            }
        ]
    }
    
    universe_001_file = backtest_dir / "universe_001_5min_5lb_backtest.json"
    with open(universe_001_file, 'w') as f:
        json.dump(universe_001, f, indent=2)
    
    universe_002 = {
        "universe_name": "universe_002_15min_10lb",
        "universe_metadata": {
            "interval": "15min",
            "lookback": 10,
            "total_patterns": 800
        },
        "results": [
            {
                "strategy_name": "TrendFollower_L5_T0.5_SL10_TP20",
                "n_trades": 50,
                "win_rate": 0.62,
                "total_return": 0.10,
                "sharpe_ratio": 1.3,
                "profit_factor": 2.0,
                "trades_detailed": [
                    {
                        "entry_time": "2025-01-02 00:00:00",
                        "exit_time": "2025-01-02 01:00:00",
                        "entry_price": 1.04000,
                        "exit_price": 1.04200,
                        "direction": "long",
                        "pnl_pips": 20.0,
                        "pnl_usd": 20.0,
                        "pnl_pct": 0.0019,
                        "duration_minutes": 60,
                        "exit_reason": "take_profit"
                    }
                ]
            }
        ]
    }
    
    universe_002_file = backtest_dir / "universe_002_15min_10lb_backtest.json"
    with open(universe_002_file, 'w') as f:
        json.dump(universe_002, f, indent=2)
    
    return backtest_dir


def test_data_loader():
    """Test that data loader correctly reads JSON structure"""
    
    print("🧪 Testing data loader with mock data...\n")
    
    # Create temporary directory with mock data
    with tempfile.TemporaryDirectory() as tmp_dir:
        backtest_dir = create_mock_data_structure(tmp_dir)
        
        print(f"📁 Created mock data in: {backtest_dir}\n")
        
        # Load data
        data = load_all_results(str(backtest_dir))
        
        # Validate structure
        print("🔍 Validating data structure...")
        assert 'all_results' in data, "Missing 'all_results' key"
        assert 'metadata' in data, "Missing 'metadata' key"
        assert 'has_detailed_trades' in data, "Missing 'has_detailed_trades' key"
        assert 'strategies_df' in data, "Missing 'strategies_df' key"
        print("   ✅ Data structure valid\n")
        
        # Check metadata
        print("📊 Metadata:")
        print(f"   Total strategies: {data['metadata']['total_strategies']}")
        print(f"   Total universes: {data['metadata']['total_universes']}")
        print(f"   Data source: {data['metadata']['data_source']}")
        print(f"   Has detailed trades: {data['has_detailed_trades']}\n")
        
        # Validate expected values
        assert data['metadata']['total_strategies'] == 3, f"Expected 3 strategies, got {data['metadata']['total_strategies']}"
        assert data['metadata']['total_universes'] == 2, f"Expected 2 universes, got {data['metadata']['total_universes']}"
        assert data['has_detailed_trades'] == True, "Expected detailed trades to be available"
        
        # Check trades_detailed
        if data['has_detailed_trades']:
            strategies_with_trades = [
                s for s in data['all_results'] 
                if s.get('trades_detailed') and len(s['trades_detailed']) > 0
            ]
            
            print(f"✅ Found {len(strategies_with_trades)} strategies with detailed trades\n")
            
            assert len(strategies_with_trades) == 3, f"Expected 3 strategies with trades, got {len(strategies_with_trades)}"
            
            # Check first strategy details
            first_strategy = strategies_with_trades[0]
            print(f"📊 First strategy: {first_strategy['strategy_name']}")
            print(f"   Universe: {first_strategy.get('universe_name', 'N/A')}")
            print(f"   Total trades: {first_strategy.get('n_detailed_trades', 0)}")
            print(f"   Win rate: {first_strategy.get('win_rate', 0):.1%}")
            print(f"   Sharpe ratio: {first_strategy.get('sharpe_ratio', 0):.2f}\n")
            
            # Check trade details
            if first_strategy['trades_detailed']:
                first_trade = first_strategy['trades_detailed'][0]
                print(f"🏆 First trade details:")
                print(f"   Entry: {first_trade.get('entry_time', 'N/A')} @ {first_trade.get('entry_price', 0):.5f}")
                print(f"   Exit: {first_trade.get('exit_time', 'N/A')} @ {first_trade.get('exit_price', 0):.5f}")
                print(f"   P&L: {first_trade.get('pnl_pips', 0)} pips")
                print(f"   Duration: {first_trade.get('duration_minutes', 0)} min")
                print(f"   Exit reason: {first_trade.get('exit_reason', 'N/A')}\n")
                
                # Validate trade has expected fields
                assert 'entry_time' in first_trade, "Missing entry_time in trade"
                assert 'exit_time' in first_trade, "Missing exit_time in trade"
                assert 'pnl_pips' in first_trade, "Missing pnl_pips in trade"
                
                if 'market_context' in first_trade:
                    ctx = first_trade['market_context']
                    print(f"📊 Market context:")
                    print(f"   Volatility: {ctx.get('volatility', 0):.4f}")
                    print(f"   Pattern: {ctx.get('pattern_detected', 'unknown')}")
                    print(f"   Trend strength: {ctx.get('trend_strength', 0):.2f}\n")
                
                if 'price_history' in first_trade:
                    print(f"📈 Price history: {len(first_trade['price_history']['timestamps'])} bars\n")
            
            # Test that trades are aggregated across universes
            trend_follower_strategies = [
                s for s in strategies_with_trades 
                if 'TrendFollower' in s['strategy_name']
            ]
            
            if len(trend_follower_strategies) > 0:
                # Count total trades for TrendFollower across all universes
                total_trades = sum(len(s['trades_detailed']) for s in trend_follower_strategies)
                print(f"✅ TrendFollower has {total_trades} total trades across {len(trend_follower_strategies)} universes\n")
        
        print("✅ ALL TESTS PASSED!")
        return True


if __name__ == '__main__':
    try:
        success = test_data_loader()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
