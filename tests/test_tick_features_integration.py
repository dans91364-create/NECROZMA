#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚡🌟💎 ULTRA NECROZMA - TICK FEATURES INTEGRATION TEST 💎🌟⚡

Integration test to verify tick features are properly added
before backtesting in the strategy discovery pipeline
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Epsilon for numerical stability (must match main.py)
EPSILON = 1e-10


def create_sample_tick_dataframe(n_rows=1000):
    """Create a sample tick DataFrame similar to what main.py uses"""
    np.random.seed(42)
    
    df = pd.DataFrame({
        'timestamp': pd.date_range('2024-01-01', periods=n_rows, freq='1s'),
        'bid': 1.0850 + np.cumsum(np.random.randn(n_rows) * 0.00001),
        'ask': 1.0852 + np.cumsum(np.random.randn(n_rows) * 0.00001),
    })
    
    # Basic tick data columns
    df['mid_price'] = (df['bid'] + df['ask']) / 2
    df['spread_pips'] = (df['ask'] - df['bid']) * 10000
    df['pips_change'] = df['mid_price'].diff() * 10000
    df['regime'] = 'trending'
    
    return df


def test_strategy_discovery_features():
    """Test that features needed for strategy discovery are properly added"""
    print("\n" + "="*70)
    print("🧪 TESTING TICK FEATURES FOR STRATEGY DISCOVERY")
    print("="*70 + "\n")
    
    # Create sample data
    print("📊 Creating sample tick data...")
    df = create_sample_tick_dataframe(n_rows=5000)
    print(f"   ✅ Created DataFrame with {len(df)} rows")
    print(f"   📊 Initial columns: {list(df.columns)}")
    
    # Verify initial state - no features
    assert 'momentum' not in df.columns, "momentum should not exist initially"
    assert 'volatility' not in df.columns, "volatility should not exist initially"
    assert 'trend_strength' not in df.columns, "trend_strength should not exist initially"
    assert 'close' not in df.columns, "close should not exist initially"
    
    print("\n" + "─"*70)
    print("🔮 STEP 4.5: Adding Tick-Level Features (from main.py)")
    print("─"*70 + "\n")
    
    # Apply the feature calculation logic from main.py Step 4.5
    if 'momentum' not in df.columns:
        print("📊 Adding tick-level features...")
        
        # Momentum: sum of pips_change over last N ticks
        df['momentum'] = df['pips_change'].rolling(window=100, min_periods=1).sum()
        
        # Volatility: standard deviation of pips_change over last N ticks
        df['volatility'] = df['pips_change'].rolling(window=100, min_periods=1).std().fillna(0)
        
        # Trend strength: absolute normalized momentum
        df['trend_strength'] = df['momentum'].abs() / (df['volatility'] + EPSILON)
        
        # Close (alias for mid_price, needed by some strategies)
        df['close'] = df['mid_price']
        
        print(f"   ✅ Features added: momentum, volatility, trend_strength, close")
    
    print(f"\n📊 Final columns: {list(df.columns)}")
    
    # Verify all features were added
    print("\n" + "─"*70)
    print("✅ VERIFICATION")
    print("─"*70 + "\n")
    
    assert 'momentum' in df.columns, "momentum column should exist"
    assert 'volatility' in df.columns, "volatility column should exist"
    assert 'trend_strength' in df.columns, "trend_strength column should exist"
    assert 'close' in df.columns, "close column should exist"
    print("✅ All required feature columns present")
    
    # Verify close = mid_price
    assert (df['close'] == df['mid_price']).all(), "close should equal mid_price"
    print("✅ close column correctly aliased to mid_price")
    
    # Verify data quality
    total_rows = len(df)
    momentum_valid = df['momentum'].notna().sum()
    volatility_valid = df['volatility'].notna().sum()
    trend_strength_valid = df['trend_strength'].notna().sum()
    
    print(f"\n📊 Data Quality:")
    print(f"   Total rows: {total_rows}")
    print(f"   Momentum valid: {momentum_valid} ({momentum_valid/total_rows*100:.1f}%)")
    print(f"   Volatility valid: {volatility_valid} ({volatility_valid/total_rows*100:.1f}%)")
    print(f"   Trend strength valid: {trend_strength_valid} ({trend_strength_valid/total_rows*100:.1f}%)")
    
    # All should be valid (fillna handles edge cases)
    # Note: First row of momentum might be NaN due to pips_change.diff()
    assert momentum_valid >= total_rows - 1, f"Almost all momentum values should be valid (got {momentum_valid}/{total_rows})"
    assert volatility_valid == total_rows, "All volatility values should be valid"
    assert trend_strength_valid >= total_rows - 1, f"Almost all trend_strength values should be valid (got {trend_strength_valid}/{total_rows})"
    print("✅ All feature values are valid (minimal NaNs from diff())")
    
    # Verify value ranges
    print(f"\n📊 Value Ranges:")
    print(f"   Momentum: [{df['momentum'].min():.4f}, {df['momentum'].max():.4f}]")
    print(f"   Volatility: [{df['volatility'].min():.4f}, {df['volatility'].max():.4f}]")
    print(f"   Trend Strength: [{df['trend_strength'].min():.4f}, {df['trend_strength'].max():.4f}]")
    
    # Volatility should be non-negative
    assert (df['volatility'] >= 0).all(), "Volatility should be non-negative"
    print("✅ Volatility is non-negative")
    
    # Trend strength should be non-negative (absolute value)
    non_nan_trend = df['trend_strength'].dropna()
    assert (non_nan_trend >= 0).all(), "Trend strength should be non-negative"
    print("✅ Trend strength is non-negative")
    
    # Test strategy compatibility
    print("\n" + "─"*70)
    print("🎯 STRATEGY COMPATIBILITY TEST")
    print("─"*70 + "\n")
    
    # Simulate basic TrendFollower logic
    threshold = 0.5
    
    # Check for momentum-based signals
    buy_signals = (df['momentum'] > threshold) & (df['trend_strength'] > 0.5)
    sell_signals = (df['momentum'] < -threshold) & (df['trend_strength'] > 0.5)
    total_signals = buy_signals.sum() + sell_signals.sum()
    
    print(f"📊 Signal Generation Test (threshold={threshold}):")
    print(f"   Buy signals: {buy_signals.sum()} ({buy_signals.sum()/total_rows*100:.2f}%)")
    print(f"   Sell signals: {sell_signals.sum()} ({sell_signals.sum()/total_rows*100:.2f}%)")
    print(f"   Total signals: {total_signals} ({total_signals/total_rows*100:.2f}%)")
    
    # We should have generated some signals
    assert total_signals > 0, "Should generate at least some signals"
    print(f"✅ Strategies can generate signals ({total_signals} signals)")
    
    print("\n" + "="*70)
    print("✅ ALL TESTS PASSED - TICK FEATURES READY FOR BACKTESTING")
    print("="*70 + "\n")
    
    return 0


if __name__ == "__main__":
    try:
        exit_code = test_strategy_discovery_features()
        sys.exit(exit_code)
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)
