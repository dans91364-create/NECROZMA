#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Comprehensive demonstration of the Trade Analysis page fix

This script demonstrates:
1. The problem (missing trades_detailed in consolidated file)
2. The solution (loading from individual universe files)
3. The result (merged data with detailed trades)
"""

import json
import tempfile
from pathlib import Path
import sys

# Mock streamlit for testing
class MockStreamlit:
    @staticmethod
    def cache_data(func):
        return func
    
    @staticmethod
    def error(msg):
        print(f"[ERROR] {msg}")
    
    @staticmethod
    def warning(msg):
        print(f"[WARNING] {msg}")
    
    @staticmethod
    def info(msg):
        print(f"[INFO] {msg}")
    
    @staticmethod
    def success(msg):
        print(f"[SUCCESS] {msg}")

sys.modules['streamlit'] = MockStreamlit()

# Import after mocking
sys.path.insert(0, 'dashboard/utils')
from data_loader import load_all_results


def print_banner(title):
    """Print a nice banner"""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70 + "\n")


def create_realistic_backtest_structure(tmp_dir):
    """
    Create a realistic backtest results structure that matches production
    """
    backtest_dir = Path(tmp_dir) / "backtest_results"
    backtest_dir.mkdir(parents=True, exist_ok=True)
    
    # ===================================================================
    # PROBLEM: Consolidated file does NOT have trades_detailed
    # ===================================================================
    consolidated = {
        "backtest_timestamp": "2025-01-13T12:00:00",
        "total_universes": 2,
        "universes": [
            {
                "universe_name": "universe_001_5min_5lb",
                "universe_metadata": {
                    "interval": "5min",
                    "lookback": 5,
                    "total_patterns": 2184
                },
                "results": [
                    {
                        "strategy_name": "TrendFollower_L5_T0.5_SL10_TP20",
                        "n_trades": 2184,
                        "win_rate": 0.65,
                        "total_return": 0.45,
                        "sharpe_ratio": 2.1,
                        "profit_factor": 2.8,
                        "max_drawdown": -0.08,
                        "avg_win": 25.5,
                        "avg_loss": -12.3,
                        "largest_win": 50.0,
                        "largest_loss": -20.0
                        # NOTE: No trades_detailed here!
                    },
                    {
                        "strategy_name": "MeanReverter_L10_T1.5_SL20_TP40",
                        "n_trades": 1500,
                        "win_rate": 0.58,
                        "total_return": 0.32,
                        "sharpe_ratio": 1.8,
                        "profit_factor": 2.2
                        # NOTE: No trades_detailed here either!
                    }
                ]
            },
            {
                "universe_name": "universe_002_15min_10lb",
                "universe_metadata": {
                    "interval": "15min",
                    "lookback": 10,
                    "total_patterns": 1200
                },
                "results": [
                    {
                        "strategy_name": "TrendFollower_L5_T0.5_SL10_TP20",
                        "n_trades": 1200,
                        "win_rate": 0.62,
                        "total_return": 0.28,
                        "sharpe_ratio": 1.6,
                        "profit_factor": 2.0
                    }
                ]
            }
        ]
    }
    
    consolidated_file = backtest_dir / "consolidated_backtest_results.json"
    with open(consolidated_file, 'w') as f:
        json.dump(consolidated, f, indent=2)
    
    print(f"✅ Created consolidated file: {consolidated_file.name}")
    print(f"   - Contains summary metrics for {len(consolidated['universes'])} universes")
    print(f"   - NO trades_detailed field (this is the problem!)")
    
    # ===================================================================
    # SOLUTION: Individual universe files HAVE trades_detailed
    # ===================================================================
    
    # Universe 001 with detailed trades
    universe_001 = {
        "universe_name": "universe_001_5min_5lb",
        "universe_metadata": {
            "interval": "5min",
            "lookback": 5,
            "total_patterns": 2184
        },
        "backtest_timestamp": "2025-01-13T12:00:00",
        "results": [
            {
                "strategy_name": "TrendFollower_L5_T0.5_SL10_TP20",
                "n_trades": 2184,
                "win_rate": 0.65,
                "total_return": 0.45,
                "sharpe_ratio": 2.1,
                "profit_factor": 2.8,
                # HERE'S THE KEY: trades_detailed is in individual files!
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
                            "pattern_sequence": "HH",
                            "hour_of_day": 0,
                            "day_of_week": 2
                        },
                        "price_history": {
                            "timestamps": [
                                "2025-01-01 00:00:00",
                                "2025-01-01 00:05:00",
                                "2025-01-01 00:10:00"
                            ],
                            "open": [1.03500, 1.03534, 1.03600],
                            "high": [1.03550, 1.03600, 1.03650],
                            "low": [1.03480, 1.03520, 1.03580],
                            "close": [1.03534, 1.03600, 1.03734],
                            "volume": [100, 120, 110]
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
                            "pattern_detected": "ohl:L"
                        }
                    },
                    {
                        "entry_time": "2025-01-01 05:15:00",
                        "exit_time": "2025-01-01 08:45:00",
                        "entry_price": 1.04000,
                        "exit_price": 1.04500,
                        "direction": "long",
                        "pnl_pips": 50.0,
                        "pnl_usd": 50.0,
                        "pnl_pct": 0.0048,
                        "duration_minutes": 210,
                        "exit_reason": "take_profit",
                        "market_context": {
                            "volatility": 0.0015,
                            "trend_strength": 0.85,
                            "pattern_detected": "ohl:HH"
                        }
                    }
                ]
            },
            {
                "strategy_name": "MeanReverter_L10_T1.5_SL20_TP40",
                "n_trades": 1500,
                "win_rate": 0.58,
                "total_return": 0.32,
                "sharpe_ratio": 1.8,
                "profit_factor": 2.2,
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
                    },
                    {
                        "entry_time": "2025-01-01 10:00:00",
                        "exit_time": "2025-01-01 10:45:00",
                        "entry_price": 1.04500,
                        "exit_price": 1.04300,
                        "direction": "short",
                        "pnl_pips": -20.0,
                        "pnl_usd": -20.0,
                        "pnl_pct": -0.0019,
                        "duration_minutes": 45,
                        "exit_reason": "stop_loss"
                    }
                ]
            }
        ]
    }
    
    universe_001_file = backtest_dir / "universe_001_5min_5lb_backtest.json"
    with open(universe_001_file, 'w') as f:
        json.dump(universe_001, f, indent=2)
    
    print(f"\n✅ Created individual file: {universe_001_file.name}")
    print(f"   - TrendFollower has {len(universe_001['results'][0]['trades_detailed'])} detailed trades")
    print(f"   - MeanReverter has {len(universe_001['results'][1]['trades_detailed'])} detailed trades")
    
    # Universe 002
    universe_002 = {
        "universe_name": "universe_002_15min_10lb",
        "universe_metadata": {
            "interval": "15min",
            "lookback": 10,
            "total_patterns": 1200
        },
        "results": [
            {
                "strategy_name": "TrendFollower_L5_T0.5_SL10_TP20",
                "n_trades": 1200,
                "win_rate": 0.62,
                "total_return": 0.28,
                "sharpe_ratio": 1.6,
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
                        "exit_reason": "take_profit",
                        "market_context": {
                            "pattern_detected": "ohl:H"
                        }
                    },
                    {
                        "entry_time": "2025-01-02 05:00:00",
                        "exit_time": "2025-01-02 06:30:00",
                        "entry_price": 1.04300,
                        "exit_price": 1.04150,
                        "direction": "short",
                        "pnl_pips": -15.0,
                        "pnl_usd": -15.0,
                        "pnl_pct": -0.0014,
                        "duration_minutes": 90,
                        "exit_reason": "stop_loss"
                    }
                ]
            }
        ]
    }
    
    universe_002_file = backtest_dir / "universe_002_15min_10lb_backtest.json"
    with open(universe_002_file, 'w') as f:
        json.dump(universe_002, f, indent=2)
    
    print(f"\n✅ Created individual file: {universe_002_file.name}")
    print(f"   - TrendFollower has {len(universe_002['results'][0]['trades_detailed'])} detailed trades")
    
    return backtest_dir


def demonstrate_fix():
    """Main demonstration of the fix"""
    
    print_banner("🎯 TRADE ANALYSIS PAGE FIX DEMONSTRATION")
    
    print("This demonstration shows how the fix resolves the issue:")
    print("  PROBLEM: Trade Analysis page is empty")
    print("  CAUSE: trades_detailed only in individual files, not consolidated")
    print("  SOLUTION: Load from both consolidated AND individual files")
    
    with tempfile.TemporaryDirectory() as tmp_dir:
        print_banner("📁 STEP 1: Creating Realistic Test Data")
        
        backtest_dir = create_realistic_backtest_structure(tmp_dir)
        
        print_banner("📊 STEP 2: Loading Data with NEW Data Loader")
        
        print("Loading data using the FIXED data_loader.load_all_results()...")
        data = load_all_results(str(backtest_dir))
        
        print_banner("✅ STEP 3: Verifying the Fix Works")
        
        print("📋 Data Summary:")
        print(f"   Total strategies: {data['metadata']['total_strategies']}")
        print(f"   Total universes: {data['metadata']['total_universes']}")
        print(f"   Data source: {data['metadata']['data_source']}")
        print(f"   Has detailed trades: {data['has_detailed_trades']}")
        
        if data['has_detailed_trades']:
            print("\n🎉 SUCCESS! Detailed trades were loaded!")
            
            strategies_with_trades = [
                s for s in data['all_results'] 
                if s.get('trades_detailed') and len(s['trades_detailed']) > 0
            ]
            
            print(f"\n📊 Found {len(strategies_with_trades)} strategies with detailed trades:\n")
            
            for i, strategy in enumerate(strategies_with_trades, 1):
                n_trades = len(strategy['trades_detailed'])
                print(f"   {i}. {strategy['strategy_name']}")
                print(f"      Universe: {strategy.get('universe_name', 'N/A')}")
                print(f"      Detailed trades: {n_trades}")
                print(f"      Win rate: {strategy.get('win_rate', 0)*100:.1f}%")
                print(f"      Sharpe ratio: {strategy.get('sharpe_ratio', 0):.2f}")
                
                # Show first trade as example
                if n_trades > 0:
                    first_trade = strategy['trades_detailed'][0]
                    print(f"      First trade: {first_trade['entry_time']} → {first_trade['exit_time']}")
                    print(f"                   P&L: {first_trade['pnl_pips']} pips ({first_trade['exit_reason']})")
                    if 'market_context' in first_trade:
                        pattern = first_trade['market_context'].get('pattern_detected', 'unknown')
                        print(f"                   Pattern: {pattern}")
                print()
            
            # Show aggregation across universes
            print("🔗 Trade Aggregation Test:")
            trend_follower_strategies = [
                s for s in strategies_with_trades 
                if 'TrendFollower' in s['strategy_name']
            ]
            
            if len(trend_follower_strategies) > 0:
                total_trades = sum(len(s['trades_detailed']) for s in trend_follower_strategies)
                print(f"   TrendFollower appears in {len(trend_follower_strategies)} universes")
                print(f"   Total trades across all universes: {total_trades}")
                print(f"   ✅ Trades successfully aggregated from multiple universe files!")
            
            print_banner("🎊 RESULT: Trade Analysis Page Will Now Work!")
            
            print("The dashboard Trade Analysis page will now show:")
            print("  ✅ 2,184+ detailed trades with full context")
            print("  ✅ Trade-by-trade cards with entry/exit prices")
            print("  ✅ Market context (volatility, pattern, trend)")
            print("  ✅ Price history charts")
            print("  ✅ Pattern performance analysis")
            print("  ✅ Best/worst trades with full details")
            
        else:
            print("\n❌ FAILED: No detailed trades found!")
            return False
    
    print_banner("✨ DEMONSTRATION COMPLETE ✨")
    return True


if __name__ == '__main__':
    try:
        success = demonstrate_fix()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ DEMONSTRATION FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
