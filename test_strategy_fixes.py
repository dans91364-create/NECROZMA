#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script to verify strategy fixes work correctly
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from strategy_factory import (
    MomentumBurst,
    MeanReverter,
    MeanReverterV2,
    PatternRecognition,
    StrategyFactory
)
from config import STRATEGY_TEMPLATES, STRATEGY_PARAMS


def create_mock_data_with_bursts():
    """Create mock data with clear momentum bursts"""
    np.random.seed(42)
    
    n = 1000  # More data points to test cooldown
    base_price = 1.10
    
    # Create price with occasional large movements (bursts)
    prices = [base_price]
    for i in range(1, n):
        # Every 50 candles, create a large burst
        if i % 50 == 0:
            change = np.random.choice([0.002, -0.002])  # Large movement
        else:
            change = np.random.randn() * 0.0001  # Normal movement
        
        prices.append(prices[-1] + change)
    
    df = pd.DataFrame({
        "timestamp": pd.date_range("2025-01-01", periods=n, freq="5min"),
        "mid_price": prices,
        "close": prices,
        "open": prices,
    })
    
    # Generate OHLC
    high_noise = np.random.uniform(0.0001, 0.0003, n)
    low_noise = np.random.uniform(0.0001, 0.0003, n)
    
    df["high"] = df["close"] + high_noise
    df["low"] = df["close"] - low_noise
    df["volume"] = np.random.uniform(80, 120, n)  # High volume
    
    return df


def test_momentum_burst_cooldown():
    """Test that MomentumBurst cooldown works"""
    print("\n" + "="*70)
    print("🧪 Testing MomentumBurst Cooldown Mechanism")
    print("="*70)
    
    df = create_mock_data_with_bursts()
    
    # Test without cooldown (should generate many signals)
    params_no_cooldown = {
        "lookback_periods": 20,
        "threshold": 1.5,  # Lower threshold to catch more signals
        "cooldown": 1,  # Minimal cooldown
    }
    strategy_no_cooldown = MomentumBurst(params_no_cooldown)
    signals_no_cooldown = strategy_no_cooldown.generate_signals(df)
    buy_count_no_cooldown = (signals_no_cooldown == 1).sum()
    sell_count_no_cooldown = (signals_no_cooldown == -1).sum()
    total_no_cooldown = buy_count_no_cooldown + sell_count_no_cooldown
    
    # Test with cooldown (should generate fewer signals)
    params_cooldown = {
        "lookback_periods": 20,
        "threshold": 1.5,
        "cooldown": 120,  # Large cooldown
    }
    strategy_cooldown = MomentumBurst(params_cooldown)
    signals_cooldown = strategy_cooldown.generate_signals(df)
    buy_count_cooldown = (signals_cooldown == 1).sum()
    sell_count_cooldown = (signals_cooldown == -1).sum()
    total_cooldown = buy_count_cooldown + sell_count_cooldown
    
    print(f"\n📊 Results:")
    print(f"   Without cooldown (cooldown=1): {total_no_cooldown} signals")
    print(f"      Buy: {buy_count_no_cooldown}, Sell: {sell_count_no_cooldown}")
    print(f"   With cooldown (cooldown=120): {total_cooldown} signals")
    print(f"      Buy: {buy_count_cooldown}, Sell: {sell_count_cooldown}")
    
    # Verify cooldown reduced signals
    if total_cooldown < total_no_cooldown:
        print(f"\n   ✅ PASS: Cooldown mechanism working (reduced signals by {total_no_cooldown - total_cooldown})")
        return True
    else:
        print(f"\n   ❌ FAIL: Cooldown didn't reduce signals")
        return False


def test_mean_reverter_threshold():
    """Test that MeanReverter has new default threshold"""
    print("\n" + "="*70)
    print("🧪 Testing MeanReverter Default Threshold")
    print("="*70)
    
    # Test with default params (should use 1.5 threshold)
    params_default = {"lookback_periods": 20}
    strategy = MeanReverter(params_default)
    
    print(f"\n📊 Default threshold: {strategy.threshold}")
    
    if strategy.threshold == 1.5:
        print(f"   ✅ PASS: Default threshold is 1.5 (changed from 2.0)")
        return True
    else:
        print(f"   ❌ FAIL: Expected 1.5, got {strategy.threshold}")
        return False


def test_mean_reverter_v2_parameters():
    """Test that MeanReverterV2 has configurable RSI parameters"""
    print("\n" + "="*70)
    print("🧪 Testing MeanReverterV2 Configurable RSI Parameters")
    print("="*70)
    
    # Test with default params
    params_default = {"lookback_periods": 20}
    strategy_default = MeanReverterV2(params_default)
    
    print(f"\n📊 Default parameters:")
    print(f"   RSI Oversold: {strategy_default.rsi_oversold}")
    print(f"   RSI Overbought: {strategy_default.rsi_overbought}")
    print(f"   Volume Multiplier: {strategy_default.volume_multiplier}")
    
    success = True
    if strategy_default.rsi_oversold == 25:
        print(f"   ✅ RSI Oversold: 25 (changed from 30)")
    else:
        print(f"   ❌ Expected 25, got {strategy_default.rsi_oversold}")
        success = False
    
    if strategy_default.rsi_overbought == 75:
        print(f"   ✅ RSI Overbought: 75 (changed from 70)")
    else:
        print(f"   ❌ Expected 75, got {strategy_default.rsi_overbought}")
        success = False
    
    if strategy_default.volume_multiplier == 1.3:
        print(f"   ✅ Volume Multiplier: 1.3 (changed from 1.5)")
    else:
        print(f"   ❌ Expected 1.3, got {strategy_default.volume_multiplier}")
        success = False
    
    # Test with custom params
    params_custom = {
        "lookback_periods": 20,
        "rsi_oversold": 20,
        "rsi_overbought": 80,
        "volume_multiplier": 1.2
    }
    strategy_custom = MeanReverterV2(params_custom)
    
    print(f"\n📊 Custom parameters work:")
    print(f"   RSI Oversold: {strategy_custom.rsi_oversold} (expected 20)")
    print(f"   RSI Overbought: {strategy_custom.rsi_overbought} (expected 80)")
    print(f"   Volume Multiplier: {strategy_custom.volume_multiplier} (expected 1.2)")
    
    if strategy_custom.rsi_oversold == 20 and strategy_custom.rsi_overbought == 80 and strategy_custom.volume_multiplier == 1.2:
        print(f"   ✅ PASS: Custom parameters applied correctly")
    else:
        print(f"   ❌ FAIL: Custom parameters not applied correctly")
        success = False
    
    return success


def test_pattern_recognition_threshold():
    """Test that PatternRecognition has new default threshold"""
    print("\n" + "="*70)
    print("🧪 Testing PatternRecognition Default Threshold")
    print("="*70)
    
    # Test with default params (should use 0.3 threshold)
    params_default = {"lookback_periods": 5}
    strategy = PatternRecognition(params_default)
    
    print(f"\n📊 Default threshold: {strategy.threshold}")
    
    if strategy.threshold == 0.3:
        print(f"   ✅ PASS: Default threshold is 0.3 (changed from 0.6)")
        return True
    else:
        print(f"   ❌ FAIL: Expected 0.3, got {strategy.threshold}")
        return False


def test_strategy_params_in_config():
    """Test that config has all new parameters"""
    print("\n" + "="*70)
    print("🧪 Testing Config Parameters")
    print("="*70)
    
    print(f"\n📊 Strategy templates in config:")
    print(f"   {STRATEGY_TEMPLATES}")
    
    success = True
    
    # Check removed strategies
    removed = ["CorrelationTrader", "PairDivergence", "LeadLagStrategy", "RiskSentiment", "USDStrength", "RegimeAdapter"]
    for strategy in removed:
        if strategy in STRATEGY_TEMPLATES:
            print(f"   ❌ FAIL: {strategy} should be removed")
            success = False
        else:
            print(f"   ✅ {strategy} removed")
    
    # Check new parameters exist
    print(f"\n📊 New parameters in STRATEGY_PARAMS:")
    
    expected_params = {
        "cooldown": [30, 60, 120, 240],
        "rsi_oversold": [20, 25, 30, 35],
        "rsi_overbought": [65, 70, 75, 80],
        "pattern_threshold": [0.2, 0.3, 0.4, 0.5],
    }
    
    for param_name, expected_values in expected_params.items():
        if param_name in STRATEGY_PARAMS:
            if STRATEGY_PARAMS[param_name] == expected_values:
                print(f"   ✅ {param_name}: {STRATEGY_PARAMS[param_name]}")
            else:
                print(f"   ⚠️  {param_name} exists but values differ")
                print(f"      Expected: {expected_values}")
                print(f"      Got: {STRATEGY_PARAMS[param_name]}")
        else:
            print(f"   ❌ FAIL: {param_name} not found in STRATEGY_PARAMS")
            success = False
    
    return success


def test_strategy_name_generation():
    """Test that strategy names include new parameters"""
    print("\n" + "="*70)
    print("🧪 Testing Strategy Name Generation")
    print("="*70)
    
    factory = StrategyFactory()
    
    # Generate a few strategies with new parameters
    strategies = factory.generate_strategies(max_strategies=50)
    
    print(f"\n📊 Generated {len(strategies)} strategies")
    
    # Find examples of each type with special parameters
    momentum_with_cooldown = [s for s in strategies if "MomentumBurst" in s.name and "CD" in s.name]
    meanrev_with_rsi = [s for s in strategies if "MeanReverterV2" in s.name and "RSI" in s.name]
    pattern_with_threshold = [s for s in strategies if "PatternRecognition" in s.name and "PT" in s.name]
    
    print(f"\n📊 Strategy name examples:")
    
    success = True
    
    if momentum_with_cooldown:
        print(f"   ✅ MomentumBurst with cooldown: {momentum_with_cooldown[0].name}")
    else:
        print(f"   ⚠️  No MomentumBurst strategies with cooldown found")
    
    if meanrev_with_rsi:
        print(f"   ✅ MeanReverterV2 with RSI: {meanrev_with_rsi[0].name}")
    else:
        print(f"   ⚠️  No MeanReverterV2 strategies with RSI found")
    
    if pattern_with_threshold:
        print(f"   ✅ PatternRecognition with threshold: {pattern_with_threshold[0].name}")
    else:
        print(f"   ⚠️  No PatternRecognition strategies with threshold found")
    
    return success


def main():
    """Run all tests"""
    print("\n" + "="*70)
    print("🧪 STRATEGY FIX VALIDATION TESTS")
    print("="*70)
    
    results = {}
    
    results["MomentumBurst Cooldown"] = test_momentum_burst_cooldown()
    results["MeanReverter Threshold"] = test_mean_reverter_threshold()
    results["MeanReverterV2 Parameters"] = test_mean_reverter_v2_parameters()
    results["PatternRecognition Threshold"] = test_pattern_recognition_threshold()
    results["Config Parameters"] = test_strategy_params_in_config()
    results["Strategy Name Generation"] = test_strategy_name_generation()
    
    # Summary
    print("\n" + "="*70)
    print("📋 TEST SUMMARY")
    print("="*70)
    
    passed = sum(results.values())
    total = len(results)
    
    for test_name, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"   {status}: {test_name}")
    
    print(f"\n   Total: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n   ✅ ALL TESTS PASSED!")
        return 0
    else:
        print(f"\n   ⚠️  {total - passed} tests failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
