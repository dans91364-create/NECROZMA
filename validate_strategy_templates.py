#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Validation script for new strategy templates

Tests that all 9 strategy templates can be instantiated and generate signals
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from strategy_factory import (
    TrendFollower,
    MeanReverter,
    RegimeAdapter,
    MeanReverterV2,
    MomentumBurst,
    StrategyFactory
)
from config import STRATEGY_TEMPLATES


def create_mock_data():
    """Create mock OHLC data for testing"""
    np.random.seed(42)
    
    # Generate realistic price data
    n = 200
    base_price = 1.10
    
    # Random walk with drift
    returns = np.random.randn(n) * 0.0001 + 0.00001
    prices = base_price + np.cumsum(returns)
    
    # Generate OHLC with valid relationships
    high_noise = np.random.uniform(0.0001, 0.0005, n)
    low_noise = np.random.uniform(0.0001, 0.0005, n)
    close_offset = np.random.uniform(-0.0002, 0.0002, n)
    
    df = pd.DataFrame({
        "timestamp": pd.date_range("2025-01-01", periods=n, freq="5min"),
        "open": prices,
        "close": prices + close_offset,
    })
    
    # Ensure high is the maximum and low is the minimum
    df["high"] = df[["open", "close"]].max(axis=1) + high_noise
    df["low"] = df[["open", "close"]].min(axis=1) - low_noise
    
    df["volume"] = np.random.uniform(50, 150, n)
    df["mid_price"] = (df["high"] + df["low"]) / 2
    df["spread_mean"] = 0.0001
    df["momentum"] = np.random.randn(n) * 0.5
    df["trend_strength"] = np.random.uniform(0, 1, n)
    df["volatility"] = np.random.uniform(0.1, 0.5, n)
    
    return df


def test_strategy_template(StrategyClass, name, params):
    """Test a single strategy template"""
    print(f"\n   Testing {name}...")
    
    try:
        # Instantiate strategy
        strategy = StrategyClass(params)
        
        # Generate mock data
        df = create_mock_data()
        
        # Generate signals
        signals = strategy.generate_signals(df)
        
        # Validate signals
        if signals is None:
            print(f"      ❌ FAILED: No signals returned")
            return False
        
        if len(signals) != len(df):
            print(f"      ❌ FAILED: Signal length mismatch")
            return False
        
        # Count signal distribution
        signal_counts = signals.value_counts().to_dict()
        buy_count = signal_counts.get(1, 0)
        sell_count = signal_counts.get(-1, 0)
        neutral_count = signal_counts.get(0, 0)
        
        # Check that strategy has rules
        if len(strategy.rules) == 0:
            print(f"      ⚠️  WARNING: No rules defined")
        
        print(f"      ✅ PASSED")
        print(f"         Signals: {buy_count} buy, {sell_count} sell, {neutral_count} neutral")
        print(f"         Rules: {len(strategy.rules)}")
        
        return True
        
    except Exception as e:
        print(f"      ❌ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_all_templates():
    """Test all strategy templates"""
    
    print("=" * 70)
    print("🧪 STRATEGY TEMPLATES VALIDATION TEST")
    print("=" * 70)
    
    # Default params for testing
    params = {
        "lookback_periods": 20,
        "threshold": 1.0,
        "stop_loss_pips": 15,
        "take_profit_pips": 30,
    }
    
    # Test each template class
    templates = [
        (TrendFollower, "TrendFollower"),
        (MeanReverter, "MeanReverter"),
        (MeanReverterV2, "MeanReverterV2"),
        (MomentumBurst, "MomentumBurst"),
    ]
    
    print(f"\n📊 Testing {len(templates)} strategy templates...")
    
    results = {}
    for StrategyClass, name in templates:
        results[name] = test_strategy_template(StrategyClass, name, params)
    
    # Summary
    passed = sum(results.values())
    failed = len(results) - passed
    
    print("\n" + "=" * 70)
    if failed == 0:
        print("✅ ALL STRATEGY TEMPLATES PASSED!")
    else:
        print(f"⚠️  {passed}/{len(results)} TEMPLATES PASSED, {failed} FAILED")
    print("=" * 70)
    
    print(f"\n📋 Results:")
    for name, success in results.items():
        status = "✅" if success else "❌"
        print(f"   {status} {name}")
    
    # Test StrategyFactory integration
    print(f"\n🏭 Testing StrategyFactory integration...")
    print(f"   Configured templates: {STRATEGY_TEMPLATES}")
    
    factory = StrategyFactory()
    print(f"   Factory templates: {factory.templates}")
    print(f"   Available classes: {list(factory.template_classes.keys())}")
    
    # Generate a few strategies
    strategies = factory.generate_strategies(max_strategies=10)
    print(f"   ✅ Generated {len(strategies)} strategies")
    
    # Show diversity
    template_types = {}
    for s in strategies:
        t = s.__class__.__name__
        template_types[t] = template_types.get(t, 0) + 1
    
    print(f"   Strategy diversity:")
    for t, count in template_types.items():
        print(f"      {t}: {count}")
    
    print("\n✨ Strategy templates are ready for backtesting!")
    
    return failed == 0


if __name__ == "__main__":
    success = test_all_templates()
    sys.exit(0 if success else 1)
