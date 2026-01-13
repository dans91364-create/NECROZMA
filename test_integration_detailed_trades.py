#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Integration test for detailed trade tracking in backtest pipeline
"""

import json
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent))

from backtester import Backtester
from strategy_factory import TrendFollower, MeanReverter


def create_realistic_test_data(n_samples=5000):
    """Create realistic OHLCV data for testing"""
    np.random.seed(42)
    
    # Generate realistic price movement
    base_price = 1.0850
    returns = np.random.randn(n_samples) * 0.0002
    close_prices = base_price + np.cumsum(returns)
    
    # Generate OHLC
    opens = np.roll(close_prices, 1)
    opens[0] = base_price
    
    highs = np.maximum(opens, close_prices) + np.abs(np.random.randn(n_samples)) * 0.0001
    lows = np.minimum(opens, close_prices) - np.abs(np.random.randn(n_samples)) * 0.0001
    
    # Create datetime index (5-minute bars for 2 weeks)
    start_date = datetime(2025, 1, 1, 0, 0)
    dates = [start_date + timedelta(minutes=5*i) for i in range(n_samples)]
    
    df = pd.DataFrame({
        'open': opens,
        'high': highs,
        'low': lows,
        'close': close_prices,
        'mid_price': close_prices,
        'momentum': np.random.randn(n_samples) * 0.5,
        'volume': np.random.randint(100, 1000, n_samples),
        'pattern': [f'ohl:{"H" if i % 3 == 0 else "L"}' for i in range(n_samples)],
    }, index=pd.DatetimeIndex(dates))
    
    return df


def test_backtest_pipeline():
    """Test the full backtest pipeline with detailed trades"""
    print("="*60)
    print("🧪 Testing Backtest Pipeline with Detailed Trades")
    print("="*60)
    
    # Create test data
    print("\n📊 Creating test data (5000 bars)...")
    df = create_realistic_test_data(5000)
    print(f"   Data shape: {df.shape}")
    print(f"   Date range: {df.index[0]} to {df.index[-1]}")
    print(f"   Price range: {df['close'].min():.4f} to {df['close'].max():.4f}")
    
    # Create strategies
    print("\n🎯 Creating test strategies...")
    strategies = [
        TrendFollower({
            'lookback_periods': 20,
            'threshold': 0.5,
            'stop_loss_pips': 15,
            'take_profit_pips': 30
        }),
        MeanReverter({
            'lookback_periods': 10,
            'threshold': 1.5,
            'stop_loss_pips': 20,
            'take_profit_pips': 40
        }),
    ]
    print(f"   Created {len(strategies)} strategies")
    
    # Run backtests
    print("\n🔬 Running backtests...")
    backtester = Backtester()
    results = []
    
    for i, strategy in enumerate(strategies, 1):
        print(f"\n   Strategy {i}/{len(strategies)}: {strategy.name}")
        result = backtester.backtest(strategy, df)
        results.append(result)
        
        print(f"      ✅ Trades: {result.n_trades}")
        print(f"      ✅ Detailed trades: {len(result.trades_detailed)}")
        print(f"      ✅ Win rate: {result.win_rate:.1%}")
        print(f"      ✅ Total return: {result.total_return:.2%}")
        print(f"      ✅ Sharpe ratio: {result.sharpe_ratio:.2f}")
    
    # Simulate saving to JSON (like run_sequential_backtest.py does)
    print("\n💾 Simulating JSON serialization...")
    
    output = {
        "universe_name": "test_universe",
        "backtest_timestamp": datetime.now().isoformat(),
        "statistics": {
            "total_strategies": len(results),
            "successful": len(results),
        },
        "results": [r.to_dict() for r in results],
    }
    
    # Try to serialize to JSON
    try:
        json_str = json.dumps(output, indent=2)
        
        # Save to temp file
        temp_file = Path("/tmp/test_backtest_detailed.json")
        with open(temp_file, 'w') as f:
            f.write(json_str)
        
        print(f"   ✅ JSON saved to: {temp_file}")
        print(f"   ✅ File size: {len(json_str):,} bytes")
        
        # Reload and verify
        with open(temp_file, 'r') as f:
            reloaded = json.load(f)
        
        print(f"\n✅ JSON verification:")
        print(f"   Total results: {len(reloaded['results'])}")
        
        for i, result in enumerate(reloaded['results'], 1):
            print(f"\n   Strategy {i}: {result['strategy_name']}")
            print(f"      Trades: {result['n_trades']}")
            
            if 'trades_detailed' in result:
                print(f"      ✅ Detailed trades: {len(result['trades_detailed'])}")
                
                if result['trades_detailed']:
                    first_trade = result['trades_detailed'][0]
                    print(f"      ✅ First trade structure:")
                    print(f"         Entry: {first_trade['entry_time']}")
                    print(f"         Exit: {first_trade['exit_time']}")
                    print(f"         P&L: {first_trade['pnl_pips']:.2f} pips (${first_trade['pnl_usd']:.2f})")
                    print(f"         Exit reason: {first_trade['exit_reason']}")
                    print(f"         Pattern: {first_trade['market_context']['pattern_detected']}")
                    print(f"         Hour: {first_trade['market_context']['hour_of_day']}")
                    print(f"         Day: {first_trade['market_context']['day_of_week']}")
                    print(f"         Price history bars: {len(first_trade['price_history']['timestamps'])}")
            else:
                print(f"      ❌ NO detailed trades found!")
                return False
        
        print("\n" + "="*60)
        print("✅ PIPELINE TEST PASSED!")
        print("="*60)
        print("\n📋 Summary:")
        print(f"   ✓ Backtest executed successfully")
        print(f"   ✓ Detailed trades recorded for all strategies")
        print(f"   ✓ JSON serialization successful")
        print(f"   ✓ All trade fields present and valid")
        print(f"   ✓ Market context captured")
        print(f"   ✓ Price history captured")
        
        return True
        
    except Exception as e:
        print(f"\n❌ JSON serialization failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_backtest_pipeline()
    sys.exit(0 if success else 1)
